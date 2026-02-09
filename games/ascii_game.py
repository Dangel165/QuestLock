"""
ASCII code word puzzle game implementation
"""

import random
from typing import List, Optional

from .base_game import Game
from ..core.models import Difficulty


class ASCIIGame(Game):
    """ASCII 코드 단어 퍼즐 게임"""
    
    def __init__(self, difficulty: Difficulty):
        super().__init__(difficulty)
        self.word_lists = self._get_word_lists()
        self.target_word = self._select_word(difficulty)
        self.user_inputs = [None, None, None, None]  # 4글자
    
    def _get_word_lists(self) -> dict:
        """난이도별 단어 목록"""
        return {
            Difficulty.EASY: [
                "LOVE", "HOPE", "LIFE", "TIME", "GAME", "PLAY", "HELP", "GOOD",
                "NICE", "COOL", "WARM", "SAFE", "HOME", "WORK", "FOOD", "BOOK"
            ],
            Difficulty.MEDIUM: [
                "BYTE", "CODE", "DATA", "FILE", "HASH", "LOOP", "NODE", "PATH",
                "PORT", "ROOT", "SCAN", "SYNC", "TEST", "USER", "VOID", "ZONE"
            ],
            Difficulty.HARD: [
                "NULL", "HEAP", "FORK", "PIPE", "SOCK", "PROC", "EXEC", "KILL",
                "TRAP", "CORE", "DUMP", "LOCK", "RACE", "DEAD", "LEAK", "FUZZ"
            ]
        }
    
    def _select_word(self, difficulty: Difficulty) -> str:
        """난이도에 따른 단어 선택"""
        words = self.word_lists[difficulty]
        return random.choice(words)
    
    def submit_ascii_code(self, position: int, ascii_code: int) -> bool:
        """ASCII 코드 입력"""
        if position < 0 or position >= 4:
            return False
        
        if ascii_code < 0 or ascii_code > 127:
            return False
        
        self.user_inputs[position] = ascii_code
        return True
    
    def check_solution(self) -> bool:
        """해답 확인"""
        if None in self.user_inputs:
            return False
        
        for i, char in enumerate(self.target_word):
            if self.user_inputs[i] != ord(char):
                return False
        
        return True
    
    def reset(self) -> None:
        """게임 리셋"""
        self.attempts = 0
        self.completed = False
        self.target_word = self._select_word(self.difficulty)
        self.user_inputs = [None, None, None, None]
    
    def get_current_inputs(self) -> List[Optional[int]]:
        """현재 입력 상태 반환"""
        return self.user_inputs.copy()
    
    def get_target_word(self) -> str:
        """목표 단어 반환 (디버그용)"""
        return self.target_word
    
    def get_correct_ascii_codes(self) -> List[int]:
        """정답 ASCII 코드 목록 반환"""
        return [ord(char) for char in self.target_word]