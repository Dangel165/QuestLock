"""
Game windows for the Game-Clear Ransomware
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from PIL import Image, ImageTk

from ..games.base_game import Game
from ..games.bitmap_game import BitmapGame
from ..games.ascii_game import ASCIIGame
from ..games.riddle_game import RiddleGame
from ..core.models import GameType


class GameWindow:
    """게임 윈도우 베이스 클래스"""
    
    def __init__(self, game: Game, game_type: GameType):
        self.game = game
        self.game_type = game_type
        self.root = tk.Toplevel()
        self.root.title(f"게임 클리어 - {game_type.value.upper()}")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 콜백 함수
        self.on_game_completed: Optional[Callable[[], None]] = None
        
        self._create_common_widgets()
    
    def _create_common_widgets(self):
        """공통 위젯 생성"""
        # 제목
        title_text = f"{self.game_type.value.upper()} 게임 - {self.game.difficulty.value.upper()} 난이도"
        title_label = tk.Label(
            self.root,
            text=title_text,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # 시도 횟수 표시
        self.attempts_var = tk.StringVar(value=f"시도 횟수: {self.game.attempts}")
        attempts_label = tk.Label(self.root, textvariable=self.attempts_var, font=("Arial", 12))
        attempts_label.pack()
        
        # 버튼 영역 - 먼저 생성하여 하단에 고정
        button_frame = tk.Frame(self.root, bg="#f0f0f0", relief="raised", bd=2, height=80)
        button_frame.pack(side="bottom", fill="x", padx=20, pady=15)
        button_frame.pack_propagate(False)  # 크기 고정
        
        self.reset_btn = tk.Button(
            button_frame,
            text="🔄 리셋",
            command=self._reset_game,
            bg="#ffc107",
            fg="black",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            relief="raised",
            cursor="hand2"
        )
        self.reset_btn.pack(side="left", padx=10, pady=10)
        
        self.check_btn = tk.Button(
            button_frame,
            text="✓ 정답 확인",
            command=self._check_solution,
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            relief="raised",
            cursor="hand2"
        )
        self.check_btn.pack(side="right", padx=10, pady=10)
        
        # 게임 영역 (하위 클래스에서 구현) - 버튼 영역 위에 배치
        self.game_frame = tk.Frame(self.root, relief="solid", bd=2)
        self.game_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    
    def _reset_game(self):
        """게임 리셋"""
        if messagebox.askyesno("확인", "게임을 리셋하시겠습니까?"):
            self.game.reset()
            self._update_display()
    
    def _check_solution(self):
        """정답 확인"""
        self.game.increment_attempts()
        self._update_attempts()
        
        if self.game.check_solution():
            self.game.mark_completed()
            messagebox.showinfo("축하합니다!", "게임을 완료했습니다!\n창이 자동으로 닫힙니다.")
            if self.on_game_completed:
                self.on_game_completed()
            # 짧은 지연 후 창 닫기
            self.root.after(500, self.root.destroy)
        else:
            messagebox.showwarning("틀렸습니다", "다시 시도해보세요.")
    
    def _update_attempts(self):
        """시도 횟수 업데이트"""
        self.attempts_var.set(f"시도 횟수: {self.game.attempts}")
    
    def _update_display(self):
        """화면 업데이트 (하위 클래스에서 구현)"""
        self._update_attempts()
    
    def show(self):
        """윈도우 표시"""
        self.root.grab_set()  # 모달 윈도우로 설정
        self.root.focus_set()


class BitmapGameWindow(GameWindow):
    """비트맵 게임 윈도우"""
    
    def __init__(self, game: BitmapGame):
        super().__init__(game, GameType.BITMAP)
        self.bitmap_game = game
        self.tile_buttons = []
        self.selected_tile = None
        self._create_bitmap_widgets()
        self._update_display()
    
    def _create_bitmap_widgets(self):
        """비트맵 게임 위젯 생성"""
        # 설명
        instruction = tk.Label(
            self.game_frame,
            text="타일을 클릭해서 선택한 후, 다른 타일과 위치를 바꿔보세요.",
            font=("Arial", 10)
        )
        instruction.pack(pady=5)
        
        # 그리드 프레임
        canvas_frame = tk.Frame(self.game_frame)
        canvas_frame.pack(fill="both", expand=True, pady=5)
        
        self.grid_frame = tk.Frame(canvas_frame)
        self.grid_frame.pack()
        
        # 타일 버튼 생성
        rows, cols = self.bitmap_game.grid_size
        for row in range(rows):
            button_row = []
            for col in range(cols):
                btn = tk.Button(
                    self.grid_frame,
                    width=8,
                    height=3,
                    command=lambda r=row, c=col: self._tile_clicked(r, c),
                    font=("Arial", 9)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(btn)
            self.tile_buttons.append(button_row)
    
    def _tile_clicked(self, row: int, col: int):
        """타일 클릭 처리"""
        if self.selected_tile is None:
            # 첫 번째 타일 선택
            self.selected_tile = (row, col)
            self.tile_buttons[row][col].config(bg="yellow")
        else:
            # 두 번째 타일 선택 - 위치 교환
            if self.selected_tile == (row, col):
                # 같은 타일 클릭 - 선택 해제
                self.tile_buttons[row][col].config(bg="SystemButtonFace")
                self.selected_tile = None
            else:
                # 다른 타일 클릭 - 위치 교환
                old_row, old_col = self.selected_tile
                
                # 타일 찾기
                tile1 = None
                tile2 = None
                for tile in self.bitmap_game.tiles:
                    if tile.current_position == (old_row, old_col):
                        tile1 = tile
                    elif tile.current_position == (row, col):
                        tile2 = tile
                
                if tile1 and tile2:
                    # 위치 교환
                    tile1.current_position, tile2.current_position = tile2.current_position, tile1.current_position
                
                self.selected_tile = None
                self._update_display()
    
    def _update_display(self):
        """화면 업데이트"""
        super()._update_display()
        
        # 모든 버튼 초기화
        for row in self.tile_buttons:
            for btn in row:
                btn.config(bg="SystemButtonFace")
        
        # 타일 정보 업데이트
        for tile in self.bitmap_game.tiles:
            row, col = tile.current_position
            if row < len(self.tile_buttons) and col < len(self.tile_buttons[0]):
                btn = self.tile_buttons[row][col]
                btn.config(text=f"타일 {tile.tile_id + 1}")
                
                # 올바른 위치에 있으면 녹색으로 표시
                if tile.current_position == tile.correct_position:
                    btn.config(bg="lightgreen")


class ASCIIGameWindow(GameWindow):
    """ASCII 게임 윈도우"""
    
    def __init__(self, game: ASCIIGame):
        super().__init__(game, GameType.ASCII)
        self.ascii_game = game
        self.entry_widgets = []
        self._create_ascii_widgets()
        self._update_display()
    
    def _create_ascii_widgets(self):
        """ASCII 게임 위젯 생성"""
        # 설명
        instruction = tk.Label(
            self.game_frame,
            text=f"단어 '{self.ascii_game.target_word}'의 각 문자에 해당하는 ASCII 코드를 입력하세요.",
            font=("Arial", 12, "bold")
        )
        instruction.pack(pady=20)
        
        # 입력 영역
        input_frame = tk.Frame(self.game_frame)
        input_frame.pack(expand=True)
        
        for i in range(4):
            char_frame = tk.Frame(input_frame)
            char_frame.pack(side="left", padx=20)
            
            # 문자 표시
            char_label = tk.Label(
                char_frame,
                text=f"'{self.ascii_game.target_word[i]}'",
                font=("Arial", 24, "bold")
            )
            char_label.pack()
            
            # ASCII 코드 입력
            entry = tk.Entry(
                char_frame,
                width=10,
                font=("Arial", 14),
                justify="center"
            )
            entry.pack(pady=10)
            entry.bind('<KeyRelease>', lambda e, idx=i: self._on_entry_change(idx, e))
            self.entry_widgets.append(entry)
            
            # 정답 표시 (처음에는 숨김)
            answer_label = tk.Label(
                char_frame,
                text="",
                font=("Arial", 10),
                fg="green"
            )
            answer_label.pack()
    
    def _on_entry_change(self, index: int, event):
        """입력 변경 처리"""
        try:
            value = int(self.entry_widgets[index].get())
            self.ascii_game.submit_ascii_code(index, value)
        except ValueError:
            pass
    
    def _update_display(self):
        """화면 업데이트"""
        super()._update_display()
        
        # 입력 필드 초기화
        for i, entry in enumerate(self.entry_widgets):
            current_input = self.ascii_game.get_current_inputs()[i]
            if current_input is not None:
                entry.delete(0, tk.END)
                entry.insert(0, str(current_input))
            else:
                entry.delete(0, tk.END)
    
    def _reset_game(self):
        """게임 리셋 (새 단어로 위젯 재생성)"""
        if messagebox.askyesno("확인", "게임을 리셋하시겠습니까?\n(새로운 단어가 나옵니다)"):
            self.game.reset()
            
            # 기존 위젯 제거
            for widget in self.game_frame.winfo_children():
                widget.destroy()
            
            # 새 위젯 생성
            self.entry_widgets = []
            self._create_ascii_widgets()
            self._update_attempts()


class RiddleGameWindow(GameWindow):
    """컴퓨터 지식 퀴즈 게임 윈도우"""
    
    def __init__(self, game: RiddleGame):
        super().__init__(game, GameType.RIDDLE)
        self.riddle_game = game
        self._create_riddle_widgets()
        self._update_display()
    
    def _create_riddle_widgets(self):
        """컴퓨터 지식 퀴즈 위젯 생성"""
        # 문제 표시
        question_frame = tk.Frame(self.game_frame, bg="#2a2a2a")
        question_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        question_label = tk.Label(
            question_frame,
            text="💻 컴퓨터 지식 퀴즈",
            font=("Arial", 18, "bold"),
            bg="#2a2a2a",
            fg="#ffeb3b"
        )
        question_label.pack(pady=(20, 10))
        
        self.question_text = tk.Label(
            question_frame,
            text=self.riddle_game.question,
            font=("Arial", 16),
            bg="#2a2a2a",
            fg="white",
            wraplength=700,
            justify="center"
        )
        self.question_text.pack(pady=20)
        
        # 힌트 표시 영역
        self.hint_label = tk.Label(
            question_frame,
            text="",
            font=("Arial", 12, "italic"),
            bg="#2a2a2a",
            fg="#ffeb3b",
            wraplength=700,
            justify="center"
        )
        self.hint_label.pack(pady=10)
        
        # 힌트 버튼
        hint_btn = tk.Button(
            question_frame,
            text="💡 힌트 보기",
            command=self._show_hint,
            bg="#17a2b8",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        hint_btn.pack(pady=10)
        
        # 답변 입력
        answer_frame = tk.Frame(question_frame, bg="#2a2a2a")
        answer_frame.pack(pady=30)
        
        answer_label = tk.Label(
            answer_frame,
            text="정답:",
            font=("Arial", 14),
            bg="#2a2a2a",
            fg="white"
        )
        answer_label.pack(side="left", padx=10)
        
        self.answer_entry = tk.Entry(
            answer_frame,
            width=30,
            font=("Arial", 14),
            bg="#3a3a3a",
            fg="white",
            insertbackground="white"
        )
        self.answer_entry.pack(side="left", padx=10)
        self.answer_entry.focus_set()
        
        # Enter 키로 제출
        self.answer_entry.bind('<Return>', lambda e: self._check_solution())
    
    def _show_hint(self):
        """힌트 표시"""
        hint = self.riddle_game.get_hint()
        self.hint_label.config(text=f"💡 힌트: {hint}")
    
    def _update_display(self):
        """화면 업데이트"""
        super()._update_display()
        # 문제 텍스트 업데이트
        self.question_text.config(text=self.riddle_game.question)
        # 힌트 초기화
        self.hint_label.config(text="")
        # 답변 입력 필드 초기화
        if self.riddle_game.user_answer:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.insert(0, self.riddle_game.user_answer)
        else:
            self.answer_entry.delete(0, tk.END)
    
    def _check_solution(self):
        """정답 확인"""
        answer = self.answer_entry.get()
        self.riddle_game.submit_answer(answer)
        self.game.increment_attempts()
        self._update_attempts()
        
        if self.game.check_solution():
            self.game.mark_completed()
            messagebox.showinfo("축하합니다!", "정답입니다!\n창이 자동으로 닫힙니다.")
            if self.on_game_completed:
                self.on_game_completed()
            # 짧은 지연 후 창 닫기
            self.root.after(500, self.root.destroy)
        else:
            messagebox.showwarning("틀렸습니다", f"정답이 아닙니다.\n다시 시도해보세요!")
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus_set()
    
    def _reset_game(self):
        """게임 리셋"""
        if messagebox.askyesno("확인", "게임을 리셋하시겠습니까?\n(새로운 문제가 나옵니다)"):
            self.game.reset()
            self._update_display()
            self.answer_entry.focus_set()


def create_game_window(game: Game, game_type: GameType) -> GameWindow:
    """게임 타입에 따른 윈도우 생성"""
    if game_type == GameType.BITMAP:
        return BitmapGameWindow(game)
    elif game_type == GameType.ASCII:
        return ASCIIGameWindow(game)
    elif game_type == GameType.RIDDLE:
        return RiddleGameWindow(game)
    else:
        raise ValueError(f"지원하지 않는 게임 타입: {game_type}")