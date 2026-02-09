"""
Modern Main Window for QuestLock v1.0.0
Created by Dangel
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable

from ..core.models import ValidationResult


class ModernButton(tk.Canvas):
    """모던한 버튼 위젯"""
    
    def __init__(self, parent, text, command, bg_color, fg_color="#ffffff", width=200, height=50, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = self._lighten_color(bg_color)
        self.fg_color = fg_color
        self.text = text
        self.enabled = True
        
        # 버튼 그리기
        self.rect = self.create_rectangle(2, 2, width-2, height-2, fill=bg_color, outline="", width=0)
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg_color, font=("Arial", 12, "bold"))
        
        # 이벤트 바인딩
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _lighten_color(self, color):
        """색상 밝게"""
        if color.startswith('#'):
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def _on_enter(self, event):
        if self.enabled:
            self.itemconfig(self.rect, fill=self.hover_color)
    
    def _on_leave(self, event):
        if self.enabled:
            self.itemconfig(self.rect, fill=self.bg_color)
    
    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()
    
    def set_state(self, state):
        """버튼 상태 설정"""
        self.enabled = (state == "normal")
        if self.enabled:
            self.itemconfig(self.rect, fill=self.bg_color)
            self.itemconfig(self.text_id, fill=self.fg_color)
        else:
            self.itemconfig(self.rect, fill="#555555")
            self.itemconfig(self.text_id, fill="#888888")


class MainWindow:
    """메인 윈도우"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔒 QuestLock v1.0.0")
        self.root.geometry("950x850")
        self.root.resizable(True, True)
        
        # 그라데이션 배경
        self.root.configure(bg="#0f0f0f")
        
        # 콜백 함수들
        self.on_folder_selected: Optional[Callable[[Path], ValidationResult]] = None
        self.on_start_encryption: Optional[Callable[[], None]] = None
        self.on_open_recovery: Optional[Callable[[], None]] = None
        
        self.selected_folder: Optional[Path] = None
        self.validation_result: Optional[ValidationResult] = None
        
        self._create_widgets()
        self._show_warning_message()
    
    def _create_widgets(self):
        """위젯 생성"""
        # 헤더 프레임
        header_frame = tk.Frame(self.root, bg="#1a1a1a", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # 제목 with 그림자 효과
        title_shadow = tk.Label(
            header_frame,
            text="� QuestLock",
            font=("Arial", 24, "bold"),
            fg="#330000",
            bg="#1a1a1a"
        )
        title_shadow.place(x=152, y=32)
        
        title_label = tk.Label(
            header_frame,
            text="🔒 QuestLock",
            font=("Arial", 24, "bold"),
            fg="#ff4444",
            bg="#1a1a1a"
        )
        title_label.place(x=150, y=30)
        
        subtitle = tk.Label(
            header_frame,
            text="v1.0.0 | RSA-4096 암호화 | 3가지 게임 클리어 필수 | Created by Dangel",
            font=("Arial", 10),
            fg="#888888",
            bg="#1a1a1a"
        )
        subtitle.place(x=250, y=65)
        
        # 스크롤 가능한 메인 영역 생성
        main_canvas = tk.Canvas(self.root, bg="#0f0f0f", highlightthickness=0)
        main_canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 메인 컨텐츠 프레임
        content_frame = tk.Frame(main_canvas, bg="#0f0f0f")
        canvas_window = main_canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # 캔버스 크기 조정 이벤트
        def configure_scroll_region(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            # 캔버스 너비에 맞춰 프레임 너비 조정
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)
        
        content_frame.bind("<Configure>", configure_scroll_region)
        main_canvas.bind("<Configure>", configure_scroll_region)
        
        # 마우스 휠 스크롤
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 컨텐츠 프레임에 패딩 추가
        content_inner = tk.Frame(content_frame, bg="#0f0f0f")
        content_inner.pack(fill="both", expand=True, padx=30, pady=20)
        
        # 경고 카드
        warning_card = tk.Frame(content_inner, bg="#2a1a00", relief="flat", bd=0)
        warning_card.pack(fill="x", pady=(0, 20))
        
        warning_border = tk.Frame(warning_card, bg="#ffaa00", height=4)
        warning_border.pack(fill="x")
        
        warning_content = tk.Frame(warning_card, bg="#2a1a00")
        warning_content.pack(fill="x", padx=20, pady=15)
        
        warning_icon = tk.Label(
            warning_content,
            text="⚠️",
            font=("Arial", 32),
            bg="#2a1a00",
            fg="#ffaa00"
        )
        warning_icon.pack(side="left", padx=(0, 15))
        
        warning_text_frame = tk.Frame(warning_content, bg="#2a1a00")
        warning_text_frame.pack(side="left", fill="x", expand=True)
        
        warning_title = tk.Label(
            warning_text_frame,
            text="경고: 실제 파일 암호화",
            font=("Arial", 14, "bold"),
            fg="#ffaa00",
            bg="#2a1a00",
            anchor="w"
        )
        warning_title.pack(fill="x")
        
        warning_desc = tk.Label(
            warning_text_frame,
            text="파일이 RSA-4096으로 암호화됩니다. 3가지 게임을 모두 클리어해야 복구 가능합니다.",
            font=("Arial", 9),
            fg="#cccccc",
            bg="#2a1a00",
            anchor="w",
            wraplength=550,
            justify="left"
        )
        warning_desc.pack(fill="x", pady=(5, 0))
        
        # 폴더 선택 카드
        folder_card = tk.Frame(content_inner, bg="#1a1a1a", relief="flat", bd=0)
        folder_card.pack(fill="x", pady=(0, 20))
        
        folder_header = tk.Frame(folder_card, bg="#252525", height=40)
        folder_header.pack(fill="x")
        folder_header.pack_propagate(False)
        
        folder_title = tk.Label(
            folder_header,
            text="📁  암호화할 폴더 선택",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#252525"
        )
        folder_title.pack(side="left", padx=20, pady=10)
        
        folder_content = tk.Frame(folder_card, bg="#1a1a1a")
        folder_content.pack(fill="x", padx=20, pady=20)
        
        # 폴더 경로 표시
        path_frame = tk.Frame(folder_content, bg="#2a2a2a", relief="flat", bd=0)
        path_frame.pack(fill="x", pady=(0, 15))
        
        self.folder_path_var = tk.StringVar(value="폴더를 선택하세요...")
        folder_path_label = tk.Label(
            path_frame,
            textvariable=self.folder_path_var,
            anchor="w",
            bg="#2a2a2a",
            fg="#aaaaaa",
            font=("Consolas", 10),
            padx=15,
            pady=12
        )
        folder_path_label.pack(fill="x")
        
        # 폴더 선택 버튼
        self.select_btn = ModernButton(
            folder_content,
            "📂 폴더 선택",
            self._select_folder,
            "#007bff",
            width=180,
            height=45
        )
        self.select_btn.pack()
        
        # 폴더 정보 카드 (처음에는 숨김)
        self.info_card = tk.Frame(content_inner, bg="#1a1a1a", relief="flat", bd=0)
        
        info_header = tk.Frame(self.info_card, bg="#252525", height=40)
        info_header.pack(fill="x")
        info_header.pack_propagate(False)
        
        info_title = tk.Label(
            info_header,
            text="📊  폴더 정보",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#252525"
        )
        info_title.pack(side="left", padx=20, pady=10)
        
        info_content = tk.Frame(self.info_card, bg="#1a1a1a")
        info_content.pack(fill="x", padx=20, pady=20)
        
        self.info_text = tk.Text(
            info_content,
            height=5,
            state="disabled",
            bg="#2a2a2a",
            fg="#ffffff",
            font=("Consolas", 11),
            relief="flat",
            padx=20,
            pady=15,
            wrap="word"
        )
        self.info_text.pack(fill="x")
        
        # 버튼 프레임
        button_frame = tk.Frame(content_inner, bg="#0f0f0f")
        button_frame.pack(pady=20)
        
        # 시작 버튼
        self.start_btn = ModernButton(
            button_frame,
            "🔐 암호화 시작",
            self._start_encryption,
            "#dc3545",
            width=200,
            height=55
        )
        self.start_btn.set_state("disabled")
        self.start_btn.pack(side="left", padx=10)
        
        # 복구 버튼
        self.recovery_btn = ModernButton(
            button_frame,
            "🔧 파일 복구",
            self._open_recovery,
            "#fd7e14",
            width=200,
            height=55
        )
        # 처음에는 표시하지 않음
        
        # 진행 상황 표시
        self.progress_frame = tk.Frame(content_inner, bg="#1a1a1a", relief="flat", bd=0)
        
        progress_header = tk.Frame(self.progress_frame, bg="#252525", height=40)
        progress_header.pack(fill="x")
        progress_header.pack_propagate(False)
        
        progress_title = tk.Label(
            progress_header,
            text="⏳  진행 상황",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#252525"
        )
        progress_title.pack(side="left", padx=20, pady=10)
        
        progress_content = tk.Frame(self.progress_frame, bg="#1a1a1a")
        progress_content.pack(fill="x", padx=20, pady=25)
        
        self.progress_label = tk.Label(
            progress_content,
            text="",
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Arial", 13, "bold")
        )
        self.progress_label.pack(pady=(0, 15))
        
        # 진행률 퍼센트 표시
        self.progress_percent_label = tk.Label(
            progress_content,
            text="0%",
            bg="#1a1a1a",
            fg="#00ff88",
            font=("Arial", 20, "bold")
        )
        self.progress_percent_label.pack(pady=(0, 15))
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#2a2a2a',
            background='#00ff88',
            bordercolor='#1a1a1a',
            lightcolor='#00ff88',
            darkcolor='#00ff88',
            thickness=30
        )
        
        # 복호화용 스타일
        style.configure(
            "Decrypt.Horizontal.TProgressbar",
            troughcolor='#2a2a2a',
            background='#ffaa00',
            bordercolor='#1a1a1a',
            lightcolor='#ffaa00',
            darkcolor='#ffaa00',
            thickness=30
        )
        
        self.progress_bar = ttk.Progressbar(
            progress_content,
            mode="determinate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", ipady=15)
    
    def _show_warning_message(self):
        """시작 시 면책조항 표시"""
        disclaimer = """
╔══════════════════════════════════════════════════════════╗
║                    ⚠️  면책조항  ⚠️                      ║
╚══════════════════════════════════════════════════════════╝

본 프로그램은 교육 목적으로만 제작되었습니다.

【주의사항】
1. 이 프로그램은 실제로 파일을 RSA-4096으로 암호화합니다.
2. 중요한 데이터가 있는 폴더는 절대 선택하지 마세요.
3. 반드시 테스트용 폴더를 만들어서 사용하세요.
4. 게임을 클리어하지 못하면 파일을 복구할 수 없습니다.

【면책사항】
• 본 프로그램 사용으로 인한 모든 데이터 손실 및 피해는
  사용자 본인의 책임입니다.
• 개발자는 어떠한 법적 책임도 지지 않습니다.
• 불법적인 목적으로 사용할 수 없습니다.
• 타인의 컴퓨터에 무단으로 사용할 수 없습니다.

【권장사항】
✓ 중요하지 않은 테스트 파일만 사용하세요.
✓ 백업이 있는 파일로만 테스트하세요.
✓ 가상 머신 환경에서 테스트하는 것을 권장합니다.

위 내용을 모두 이해하고 동의하십니까?
"""
        
        result = messagebox.askyesno(
            "면책조항 - 반드시 읽어주세요",
            disclaimer,
            icon='warning'
        )
        
        if not result:
            messagebox.showinfo(
                "프로그램 종료",
                "면책조항에 동의하지 않으셨습니다.\n프로그램을 종료합니다."
            )
            self.root.destroy()
            exit(0)
    
    def _select_folder(self):
        """폴더 선택"""
        folder_path = filedialog.askdirectory(title="암호화할 폴더를 선택하세요")
        
        if folder_path:
            self.selected_folder = Path(folder_path)
            self.folder_path_var.set(str(self.selected_folder))
            
            # 폴더 검증
            if self.on_folder_selected:
                self.validation_result = self.on_folder_selected(self.selected_folder)
                self._display_folder_info()
    
    def _display_folder_info(self):
        """폴더 정보 표시"""
        if not self.validation_result:
            return
        
        self.info_card.pack(fill="x", pady=(0, 20))
        
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        
        if self.validation_result.is_valid:
            info = f"✅ 유효한 폴더입니다.\n\n"
            info += f"📄 파일 개수: {self.validation_result.file_count}개\n"
            info += f"💾 총 크기: {self._format_size(self.validation_result.total_size)}\n"
            info += f"🎮 난이도: {self._get_difficulty_text(self.validation_result.file_count)}\n"
            
            if self.validation_result.warnings:
                info += f"\n⚠️ 경고:\n"
                for warning in self.validation_result.warnings:
                    info += f"  • {warning}\n"
            
            self.start_btn.set_state("normal")
        else:
            # 시스템 폴더 선택 시 경고 창 표시
            if "시스템 폴더" in self.validation_result.error_message or "시스템 디렉토리" in self.validation_result.error_message:
                messagebox.showerror(
                    "⛔ 시스템 폴더 선택 불가",
                    self.validation_result.error_message
                )
            
            info = f"❌ 폴더를 사용할 수 없습니다.\n\n"
            info += f"오류: {self.validation_result.error_message}\n"
            self.start_btn.set_state("disabled")
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state="disabled")
    
    def _get_difficulty_text(self, file_count: int) -> str:
        """파일 개수에 따른 난이도 텍스트"""
        if file_count <= 10:
            return "쉬움 (EASY)"
        elif file_count <= 50:
            return "보통 (MEDIUM)"
        else:
            return "어려움 (HARD)"
    
    def _format_size(self, size_bytes: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _start_encryption(self):
        """암호화 시작"""
        if not self.selected_folder or not self.validation_result or not self.validation_result.is_valid:
            messagebox.showerror("오류", "유효한 폴더를 선택해주세요.")
            return
        
        # 최종 확인
        confirm_msg = f"다음 폴더를 암호화하시겠습니까?\n\n"
        confirm_msg += f"📁 폴더: {self.selected_folder}\n"
        confirm_msg += f"📄 파일 개수: {self.validation_result.file_count}개\n"
        confirm_msg += f"💾 총 크기: {self._format_size(self.validation_result.total_size)}\n\n"
        confirm_msg += "⚠️ 이 작업은 실제로 파일을 암호화합니다!\n"
        confirm_msg += "중요한 파일이 있다면 취소하세요."
        
        if messagebox.askyesno("최종 확인", confirm_msg):
            if self.on_start_encryption:
                self.on_start_encryption()
    
    def show_progress(self, title: str, current: int, total: int):
        """진행 상황 표시"""
        self.progress_frame.pack(fill="x", pady=(0, 20))
        
        # 진행률 계산
        percent = int((current / total * 100)) if total > 0 else 0
        
        self.progress_label.config(text=f"{title}: {current}/{total}")
        self.progress_percent_label.config(text=f"{percent}%")
        self.progress_bar.config(maximum=total, value=current)
        self.root.update()
    
    def set_progress_style(self, style_name: str):
        """진행 바 스타일 변경 (암호화/복호화)"""
        if style_name == "encrypt":
            self.progress_bar.config(style="Custom.Horizontal.TProgressbar")
            self.progress_percent_label.config(fg="#00ff88")
        elif style_name == "decrypt":
            self.progress_bar.config(style="Decrypt.Horizontal.TProgressbar")
            self.progress_percent_label.config(fg="#ffaa00")
    
    def hide_progress(self):
        """진행 상황 숨김"""
        self.progress_frame.pack_forget()
    
    def show_error(self, title: str, message: str):
        """오류 메시지 표시"""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """정보 메시지 표시"""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str):
        """경고 메시지 표시"""
        messagebox.showwarning(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """예/아니오 질문"""
        return messagebox.askyesno(title, message)
    
    def _open_recovery(self):
        """복구 도구 열기"""
        if self.on_open_recovery:
            self.on_open_recovery()
    
    def run(self):
        """메인 루프 실행"""
        self.root.mainloop()
    
    def close(self):
        """윈도우 닫기"""
        self.root.destroy()
