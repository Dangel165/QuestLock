#!/usr/bin/env python3
"""
복구 도구 - 복호화 실패한 파일을 수동으로 복구
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional
import logging

from .crypto.crypto_manager import CryptoManager
from .core.models import KeyPair


class RecoveryWindow:
    """복구 도구 윈도우"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        self.root.title("파일 복구 도구")
        self.root.geometry("900x650")
        
        self.crypto_manager = CryptoManager()
        self.key_pair: Optional[KeyPair] = None
        self.encrypted_files: List[Path] = []
        
        self._create_widgets()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _create_widgets(self):
        """위젯 생성"""
        # 제목
        title_label = tk.Label(
            self.root,
            text="파일 복구 도구",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # 설명
        desc_label = tk.Label(
            self.root,
            text="복호화에 실패한 파일을 수동으로 복구합니다.",
            font=("Arial", 10)
        )
        desc_label.pack(pady=5)
        
        # 키 파일 선택
        key_frame = tk.LabelFrame(self.root, text="1. 키 파일 선택", padx=10, pady=10)
        key_frame.pack(fill="x", padx=20, pady=10)
        
        self.key_path_var = tk.StringVar(value="키 파일을 선택하세요")
        key_path_label = tk.Label(key_frame, textvariable=self.key_path_var)
        key_path_label.pack(side="left", fill="x", expand=True)
        
        key_btn = tk.Button(
            key_frame,
            text="키 파일 선택",
            command=self._select_key_file,
            bg="lightblue"
        )
        key_btn.pack(side="right", padx=5)
        
        # 폴더 선택
        folder_frame = tk.LabelFrame(self.root, text="2. 암호화된 파일이 있는 폴더 선택", padx=10, pady=10)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        self.folder_path_var = tk.StringVar(value="폴더를 선택하세요")
        folder_path_label = tk.Label(folder_frame, textvariable=self.folder_path_var)
        folder_path_label.pack(side="left", fill="x", expand=True)
        
        folder_btn = tk.Button(
            folder_frame,
            text="폴더 선택",
            command=self._select_folder,
            bg="lightblue"
        )
        folder_btn.pack(side="right", padx=5)
        
        # 파일 목록
        list_frame = tk.LabelFrame(self.root, text="3. 암호화된 파일 목록", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 검색 프레임
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill="x", pady=5)
        
        tk.Label(search_frame, text="검색:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_files())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=5)
        
        # 스크롤바
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.MULTIPLE,
            font=("Courier", 9)
        )
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # 파일 개수 표시
        self.file_count_var = tk.StringVar(value="파일: 0개")
        file_count_label = tk.Label(list_frame, textvariable=self.file_count_var, font=("Arial", 9))
        file_count_label.pack(pady=5)
        
        # 버튼 영역
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        select_all_btn = tk.Button(
            button_frame,
            text="전체 선택",
            command=self._select_all_files,
            bg="lightyellow"
        )
        select_all_btn.pack(side="left", padx=5)
        
        deselect_all_btn = tk.Button(
            button_frame,
            text="선택 해제",
            command=self._deselect_all_files,
            bg="lightyellow"
        )
        deselect_all_btn.pack(side="left", padx=5)
        
        # 개별 파일 선택 버튼
        select_files_btn = tk.Button(
            button_frame,
            text="파일 직접 선택",
            command=self._select_individual_files,
            bg="lightblue"
        )
        select_files_btn.pack(side="left", padx=5)
        
        self.recover_btn = tk.Button(
            button_frame,
            text="선택한 파일 복구",
            command=self._recover_selected_files,
            bg="lightgreen",
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.recover_btn.pack(side="right", padx=5)
        
        # 진행 상황
        self.progress_var = tk.StringVar(value="")
        self.progress_label = tk.Label(self.root, textvariable=self.progress_var, font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate')
        self.progress_bar.pack(fill="x", padx=20, pady=5)
    
    def _select_key_file(self):
        """키 파일 선택"""
        key_dir = Path.home() / ".game_ransomware" / "keys"
        
        file_path = filedialog.askopenfilename(
            title="키 파일 선택",
            initialdir=str(key_dir) if key_dir.exists() else str(Path.home()),
            filetypes=[("PEM 파일", "*.pem"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            try:
                # 키 로드 시도
                key_path = Path(file_path)
                session_id = key_path.stem
                
                self.key_pair = self.crypto_manager.load_keys(session_id)
                
                if self.key_pair:
                    self.key_path_var.set(str(key_path))
                    messagebox.showinfo("성공", "키 파일을 성공적으로 로드했습니다.")
                    self._update_recover_button_state()
                else:
                    messagebox.showerror("오류", "키 파일을 로드할 수 없습니다.")
                    
            except Exception as e:
                messagebox.showerror("오류", f"키 파일 로드 중 오류: {str(e)}")
    
    def _select_folder(self):
        """폴더 선택"""
        folder_path = filedialog.askdirectory(
            title="암호화된 파일이 있는 폴더 선택"
        )
        
        if folder_path:
            folder = Path(folder_path)
            self.folder_path_var.set(str(folder))
            
            # 암호화된 파일 찾기
            self.encrypted_files = list(folder.rglob("*.encrypted"))
            
            # 리스트박스 업데이트
            self._update_file_list()
            
            if self.encrypted_files:
                messagebox.showinfo(
                    "파일 검색 완료",
                    f"{len(self.encrypted_files)}개의 암호화된 파일을 찾았습니다."
                )
            else:
                messagebox.showwarning(
                    "파일 없음",
                    "암호화된 파일을 찾을 수 없습니다."
                )
            
            self._update_recover_button_state()
    
    def _update_file_list(self):
        """파일 목록 업데이트"""
        self.file_listbox.delete(0, tk.END)
        
        if self.encrypted_files:
            folder = Path(self.folder_path_var.get())
            search_text = self.search_var.get().lower()
            
            displayed_count = 0
            for file in self.encrypted_files:
                relative_path = file.relative_to(folder)
                file_str = str(relative_path)
                
                # 검색 필터 적용
                if not search_text or search_text in file_str.lower():
                    self.file_listbox.insert(tk.END, file_str)
                    displayed_count += 1
            
            self.file_count_var.set(f"파일: {displayed_count}/{len(self.encrypted_files)}개")
        else:
            self.file_count_var.set("파일: 0개")
    
    def _filter_files(self):
        """파일 필터링"""
        self._update_file_list()
    
    def _select_individual_files(self):
        """개별 파일 직접 선택"""
        file_paths = filedialog.askopenfilenames(
            title="복구할 파일 선택",
            filetypes=[("암호화된 파일", "*.encrypted"), ("모든 파일", "*.*")]
        )
        
        if file_paths:
            # 선택한 파일들을 encrypted_files에 추가
            new_files = [Path(f) for f in file_paths]
            
            # 중복 제거
            existing_paths = {str(f) for f in self.encrypted_files}
            for new_file in new_files:
                if str(new_file) not in existing_paths:
                    self.encrypted_files.append(new_file)
            
            # 폴더 경로 업데이트 (공통 부모 디렉토리)
            if self.encrypted_files:
                common_parent = self.encrypted_files[0].parent
                self.folder_path_var.set(str(common_parent))
            
            # 리스트 업데이트
            self._update_file_list()
            
            messagebox.showinfo(
                "파일 추가 완료",
                f"{len(file_paths)}개의 파일을 추가했습니다.\n총 {len(self.encrypted_files)}개"
            )
            
            self._update_recover_button_state()
    
    def _select_all_files(self):
        """전체 선택"""
        self.file_listbox.select_set(0, tk.END)
    
    def _deselect_all_files(self):
        """선택 해제"""
        self.file_listbox.selection_clear(0, tk.END)
    
    def _update_recover_button_state(self):
        """복구 버튼 상태 업데이트"""
        if self.key_pair and self.encrypted_files:
            self.recover_btn.config(state="normal")
        else:
            self.recover_btn.config(state="disabled")
    
    def _recover_selected_files(self):
        """선택한 파일 복구"""
        if not self.key_pair:
            messagebox.showerror("오류", "키 파일을 먼저 선택하세요.")
            return
        
        selected_indices = self.file_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("경고", "복구할 파일을 선택하세요.")
            return
        
        # 확인
        if not messagebox.askyesno(
            "확인",
            f"{len(selected_indices)}개의 파일을 복구하시겠습니까?"
        ):
            return
        
        # 복구 시작
        total_files = len(selected_indices)
        success_count = 0
        failed_files = []
        checksum_mismatch_files = []
        
        self.progress_bar['maximum'] = total_files
        self.progress_bar['value'] = 0
        
        for i, index in enumerate(selected_indices):
            file_path = self.encrypted_files[index]
            
            self.progress_var.set(f"복구 중: {file_path.name} ({i+1}/{total_files})")
            self.root.update()
            
            try:
                result = self.crypto_manager.decrypt_file(
                    file_path,
                    self.key_pair.private_key
                )
                
                if result.success:
                    success_count += 1
                    self.logger.info(f"복구 성공: {file_path}")
                    
                    # 체크섬 불일치 경고
                    if not result.checksum_match:
                        checksum_mismatch_files.append({
                            'path': str(file_path),
                            'error': '체크섬 불일치 - 파일이 손상되었을 수 있음'
                        })
                        self.logger.warning(f"체크섬 불일치: {file_path}")
                else:
                    failed_files.append({
                        'path': str(file_path),
                        'error': result.error or '알 수 없는 오류'
                    })
                    self.logger.error(f"복구 실패: {file_path} - {result.error}")
                    
            except Exception as e:
                failed_files.append({
                    'path': str(file_path),
                    'error': f'예외 발생: {str(e)}'
                })
                self.logger.error(f"복구 중 오류: {file_path} - {str(e)}")
            
            self.progress_bar['value'] = i + 1
        
        # 완료 메시지
        self.progress_var.set("복구 완료")
        
        result_msg = f"복구 완료!\n\n"
        result_msg += f"총 파일: {total_files}개\n"
        result_msg += f"성공: {success_count}개\n"
        result_msg += f"실패: {len(failed_files)}개\n"
        
        if checksum_mismatch_files:
            result_msg += f"체크섬 불일치: {len(checksum_mismatch_files)}개\n"
        
        if failed_files or checksum_mismatch_files:
            result_msg += "\n자세한 오류 내용은 '오류 로그 보기' 버튼을 클릭하세요."
        
        messagebox.showinfo("복구 완료", result_msg)
        
        # 오류 로그 표시 (실패한 파일이 있는 경우)
        if failed_files or checksum_mismatch_files:
            self._show_error_log(failed_files, checksum_mismatch_files)
        
        # 리스트 새로고침
        if success_count > 0:
            # 성공한 파일들을 목록에서 제거
            for index in reversed(list(selected_indices)):
                file_path = self.encrypted_files[index]
                # 완전히 실패한 파일만 남기기 (체크섬 불일치는 복구 성공으로 간주)
                if not any(str(file_path) == f['path'] for f in failed_files):
                    del self.encrypted_files[index]
            
            self._update_file_list()
    
    def _show_error_log(self, failed_files: list, checksum_mismatch_files: list):
        """오류 로그 표시"""
        log_window = tk.Toplevel(self.root)
        log_window.title("오류 로그")
        log_window.geometry("800x600")
        
        # 제목
        title_label = tk.Label(
            log_window,
            text="복구 오류 상세 로그",
            font=("Arial", 14, "bold"),
            bg="#ff6b6b",
            fg="white",
            pady=10
        )
        title_label.pack(fill="x")
        
        # 탭 생성
        notebook = ttk.Notebook(log_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 실패 탭
        if failed_files:
            failed_frame = tk.Frame(notebook)
            notebook.add(failed_frame, text=f"복구 실패 ({len(failed_files)}개)")
            
            # 스크롤바
            failed_scrollbar = tk.Scrollbar(failed_frame)
            failed_scrollbar.pack(side="right", fill="y")
            
            # 텍스트 위젯
            failed_text = tk.Text(
                failed_frame,
                wrap=tk.WORD,
                yscrollcommand=failed_scrollbar.set,
                font=("Courier", 9),
                bg="#fff5f5"
            )
            failed_text.pack(fill="both", expand=True)
            failed_scrollbar.config(command=failed_text.yview)
            
            # 오류 내용 추가
            for i, file_info in enumerate(failed_files, 1):
                file_path = Path(file_info['path'])
                error_msg = file_info['error']
                
                failed_text.insert(tk.END, f"[{i}] ", "index")
                failed_text.insert(tk.END, f"{file_path.name}\n", "filename")
                failed_text.insert(tk.END, f"    경로: {file_path}\n", "path")
                failed_text.insert(tk.END, f"    오류: {error_msg}\n\n", "error")
            
            # 태그 설정
            failed_text.tag_config("index", foreground="#666", font=("Courier", 9, "bold"))
            failed_text.tag_config("filename", foreground="#c92a2a", font=("Courier", 10, "bold"))
            failed_text.tag_config("path", foreground="#495057")
            failed_text.tag_config("error", foreground="#e03131")
            
            failed_text.config(state="disabled")
        
        # 체크섬 불일치 탭
        if checksum_mismatch_files:
            checksum_frame = tk.Frame(notebook)
            notebook.add(checksum_frame, text=f"체크섬 불일치 ({len(checksum_mismatch_files)}개)")
            
            # 경고 메시지
            warning_label = tk.Label(
                checksum_frame,
                text="⚠️ 다음 파일들은 복구되었지만 체크섬이 일치하지 않습니다.\n파일이 손상되었을 수 있으니 확인이 필요합니다.",
                font=("Arial", 9),
                bg="#fff3bf",
                fg="#f08c00",
                pady=10
            )
            warning_label.pack(fill="x")
            
            # 스크롤바
            checksum_scrollbar = tk.Scrollbar(checksum_frame)
            checksum_scrollbar.pack(side="right", fill="y")
            
            # 텍스트 위젯
            checksum_text = tk.Text(
                checksum_frame,
                wrap=tk.WORD,
                yscrollcommand=checksum_scrollbar.set,
                font=("Courier", 9),
                bg="#fffbf0"
            )
            checksum_text.pack(fill="both", expand=True)
            checksum_scrollbar.config(command=checksum_text.yview)
            
            # 내용 추가
            for i, file_info in enumerate(checksum_mismatch_files, 1):
                file_path = Path(file_info['path'])
                
                checksum_text.insert(tk.END, f"[{i}] ", "index")
                checksum_text.insert(tk.END, f"{file_path.name}\n", "filename")
                checksum_text.insert(tk.END, f"    경로: {file_path}\n", "path")
                checksum_text.insert(tk.END, f"    상태: 복구됨 (체크섬 불일치)\n\n", "warning")
            
            # 태그 설정
            checksum_text.tag_config("index", foreground="#666", font=("Courier", 9, "bold"))
            checksum_text.tag_config("filename", foreground="#f59f00", font=("Courier", 10, "bold"))
            checksum_text.tag_config("path", foreground="#495057")
            checksum_text.tag_config("warning", foreground="#f08c00")
            
            checksum_text.config(state="disabled")
        
        # 도움말 탭
        help_frame = tk.Frame(notebook)
        notebook.add(help_frame, text="도움말")
        
        help_text = tk.Text(help_frame, wrap=tk.WORD, font=("Arial", 10), bg="#f8f9fa")
        help_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_content = """
복구 오류 해결 방법

1. 파일이 존재하지 않습니다
   → 파일이 삭제되었거나 이동되었습니다. 파일 경로를 확인하세요.

2. 파일이 손상되었거나 암호화 파일이 아닙니다
   → 파일 크기가 너무 작거나 헤더가 손상되었습니다.
   → 올바른 암호화 파일인지 확인하세요.

3. 헤더 파싱 실패
   → 암호화 파일의 헤더가 손상되었습니다.
   → 다른 프로그램으로 암호화된 파일일 수 있습니다.

4. AES 키 복호화 실패
   → 잘못된 개인키를 사용했거나 키가 손상되었습니다.
   → 올바른 키 파일을 선택했는지 확인하세요.

5. 체크섬 불일치
   → 파일은 복구되었지만 원본과 다를 수 있습니다.
   → 파일을 열어서 정상적으로 작동하는지 확인하세요.
   → 중요한 파일인 경우 백업에서 복원하는 것을 권장합니다.

6. 암호화된 데이터가 없습니다
   → 파일이 비어있거나 데이터 영역이 손상되었습니다.

7. 복호화 오류
   → 암호화 알고리즘 오류 또는 파일 손상입니다.
   → 파일을 다시 암호화하거나 백업에서 복원하세요.

추가 도움이 필요하면 로그 파일을 확인하거나 개발자에게 문의하세요.
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state="disabled")
        
        # 닫기 버튼
        close_btn = tk.Button(
            log_window,
            text="닫기",
            command=log_window.destroy,
            bg="lightgray",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)
        
        # 창 중앙 배치
        log_window.transient(self.root)
        log_window.grab_set()
    
    def show(self):
        """윈도우 표시"""
        self.root.grab_set()  # 모달 윈도우로 설정
        self.root.focus_set()


def main():
    """메인 함수 (독립 실행용)"""
    print("파일 복구 도구")
    print("=" * 50)
    
    try:
        tool = RecoveryWindow()
        tool.root.mainloop()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
