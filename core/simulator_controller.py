"""
Main controller for the Game-Clear Ransomware
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .file_manager import FileManager
from .models import ValidationResult, SimulatorState, EncryptionStatus, GameState, KeyStorage
from ..crypto.crypto_manager import CryptoManager
from ..games.game_manager import GameManager
from ..ui.main_window import MainWindow
from ..ui.game_windows import create_game_window


class SimulatorController:
    """메인 컨트롤러"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.crypto_manager = CryptoManager()
        self.game_manager = GameManager()
        
        self.current_session_id: Optional[str] = None
        self.current_state: Optional[SimulatorState] = None
        
        # UI 초기화
        self.main_window = MainWindow()
        self.main_window.on_folder_selected = self._on_folder_selected
        self.main_window.on_start_encryption = self._on_start_encryption
        self.main_window.on_open_recovery = self._on_open_recovery
    
    def _on_folder_selected(self, folder_path: Path) -> ValidationResult:
        """폴더 선택 처리"""
        return self.file_manager.validator.validate_folder(folder_path)
    
    def _on_start_encryption(self):
        """암호화 시작"""
        if not self.main_window.selected_folder or not self.main_window.validation_result:
            return
        
        try:
            # 새 세션 시작
            self.current_session_id = str(uuid.uuid4())
            
            # 암호화 스타일 설정
            self.main_window.set_progress_style("encrypt")
            
            # RSA 키 생성
            self.main_window.show_progress("🔑 키 생성 중", 0, 2)
            key_pair = self.crypto_manager.generate_key_pair()
            self.crypto_manager.save_keys(key_pair, self.current_session_id)
            
            # 파일 암호화
            files = self.file_manager.get_file_list(self.main_window.selected_folder)
            total_files = len(files)
            encrypted_files = 0
            failed_files = []
            
            for i, file_info in enumerate(files):
                self.main_window.show_progress(f"🔐 암호화 중", i + 1, total_files)
                
                result = self.crypto_manager.encrypt_file(file_info.path, key_pair.public_key)
                if result.success:
                    encrypted_files += 1
                else:
                    failed_files.append(str(file_info.path))
            
            self.main_window.hide_progress()
            
            # 게임 생성 및 시작 (3개 게임 모두 클리어해야 함)
            game, game_type, difficulty = self.game_manager.create_game_by_file_count(total_files, [])
            
            # 상태 저장
            self.current_state = SimulatorState(
                session_id=self.current_session_id,
                timestamp=datetime.now(),
                target_folder=self.main_window.selected_folder,
                backup_location=None,
                encryption_status=EncryptionStatus(
                    total_files=total_files,
                    encrypted_files=encrypted_files,
                    failed_files=failed_files
                ),
                game_state=GameState(
                    game_type=game_type,
                    difficulty=difficulty,
                    attempts=0,
                    completed=False,
                    current_progress={}
                ),
                key_storage=KeyStorage(
                    key_file=str(self.crypto_manager.key_storage_path / f"{self.current_session_id}.pem")
                ),
                completed_games=[]
            )
            
            # 암호화 완료 메시지
            completion_msg = f"암호화가 완료되었습니다!\n\n"
            completion_msg += f"총 파일: {total_files}개\n"
            completion_msg += f"암호화 성공: {encrypted_files}개\n"
            if failed_files:
                completion_msg += f"암호화 실패: {len(failed_files)}개\n"
            completion_msg += f"\n⚠️ 3가지 게임을 모두 클리어해야 복호화됩니다!\n"
            completion_msg += f"첫 번째 게임: {game_type.value.upper()}\n"
            completion_msg += f"난이도: {difficulty.value.upper()}"
            
            self.main_window.show_info("암호화 완료", completion_msg)
            
            # 게임 윈도우 열기
            self._start_game(game, game_type)
            
        except Exception as e:
            self.main_window.hide_progress()
            self.main_window.show_error("오류", f"암호화 중 오류가 발생했습니다: {str(e)}")
    
    def _start_game(self, game, game_type):
        """게임 시작"""
        game_window = create_game_window(game, game_type)
        game_window.on_game_completed = self._on_game_completed
        game_window.show()
    
    def _on_game_completed(self):
        """게임 완료 처리"""
        if not self.current_session_id or not self.current_state:
            return
        
        # 완료한 게임 추가
        current_game_type = self.current_state.game_state.game_type.value
        if current_game_type not in self.current_state.completed_games:
            self.current_state.completed_games.append(current_game_type)
        
        # 완료한 게임 수 확인
        completed_count = len(self.current_state.completed_games)
        
        if completed_count < 3:
            # 다음 게임 시작
            remaining = 3 - completed_count
            self.main_window.show_info(
                "게임 완료!",
                f"축하합니다! {current_game_type.upper()} 게임을 완료했습니다!\n\n"
                f"완료한 게임: {completed_count}/3\n"
                f"남은 게임: {remaining}개\n\n"
                f"다음 게임을 시작합니다..."
            )
            
            # 다음 게임 생성
            game, game_type, difficulty = self.game_manager.create_game_by_file_count(
                self.current_state.encryption_status.total_files,
                self.current_state.completed_games
            )
            
            if game:
                self.current_state.game_state.game_type = game_type
                self.current_state.game_state.difficulty = difficulty
                self._start_game(game, game_type)
            return
        
        # 모든 게임 완료 - 복호화 시작
        self.main_window.show_info(
            "모든 게임 완료!",
            "축하합니다! 3가지 게임을 모두 완료했습니다!\n\n"
            "파일 복호화를 시작합니다..."
        )
        
        try:
            # 키 로드
            key_pair = self.crypto_manager.load_keys(self.current_session_id)
            if not key_pair:
                self.main_window.show_error("오류", "복호화 키를 찾을 수 없습니다.")
                return
            
            # 복호화 스타일 설정
            self.main_window.set_progress_style("decrypt")
            
            # 암호화된 파일 찾기
            encrypted_files = list(self.current_state.target_folder.rglob("*.encrypted"))
            total_files = len(encrypted_files)
            
            if total_files == 0:
                self.main_window.show_info("완료", "복호화할 파일이 없습니다.")
                return
            
            # 파일 복호화
            decrypted_files = 0
            failed_files = []
            
            for i, encrypted_file in enumerate(encrypted_files):
                self.main_window.show_progress("🔓 복호화 중", i + 1, total_files)
                
                result = self.crypto_manager.decrypt_file(encrypted_file, key_pair.private_key)
                if result.success:
                    decrypted_files += 1
                else:
                    failed_files.append(str(encrypted_file))
            
            self.main_window.hide_progress()
            
            # 완료 메시지
            completion_msg = f"복호화가 완료되었습니다!\n\n"
            completion_msg += f"총 파일: {total_files}개\n"
            completion_msg += f"복호화 성공: {decrypted_files}개\n"
            if failed_files:
                completion_msg += f"복호화 실패: {len(failed_files)}개\n"
                completion_msg += f"\n⚠️ 복호화에 실패한 파일이 있습니다!\n"
                completion_msg += f"메인 화면의 '파일 복구' 버튼을 눌러\n"
                completion_msg += f"수동으로 복구할 수 있습니다.\n"
            else:
                completion_msg += f"\n✅ 모든 파일이 원래 상태로 복원되었습니다.\n\n"
                completion_msg += f"💡 혹시 복호화되지 않은 파일이 있다면\n"
                completion_msg += f"메인 화면의 '파일 복구' 버튼을 눌러주세요."
            
            self.main_window.show_info("복호화 완료", completion_msg)
            
            # 복구 버튼 활성화
            self.enable_recovery_button()
            
            # 세션 정리
            self._cleanup_session()
            
        except Exception as e:
            self.main_window.hide_progress()
            self.main_window.show_error("복호화 오류", f"복호화 중 오류가 발생했습니다: {str(e)}")
    
    def _cleanup_session(self):
        """세션 정리"""
        if self.current_session_id:
            # 키 파일 삭제 (선택사항)
            key_file = self.crypto_manager.key_storage_path / f"{self.current_session_id}.pem"
            if key_file.exists():
                key_file.unlink()
        
        self.current_session_id = None
        self.current_state = None
    
    def _on_open_recovery(self):
        """복구 도구 열기"""
        from ..recovery_tool import RecoveryWindow
        
        recovery_window = RecoveryWindow(self.main_window.root)
        recovery_window.show()
    
    def enable_recovery_button(self):
        """복구 버튼 활성화 (3개 게임 모두 완료 후)"""
        self.main_window.recovery_btn.pack(side="left", padx=10)
    
    def run(self):
        """프로그램 실행"""
        self.main_window.run()
    
    def shutdown(self):
        """프로그램 종료"""
        self.main_window.close()