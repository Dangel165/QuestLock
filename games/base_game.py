"""
Base game classes for the Game-Clear Ransomware
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from ..core.models import Difficulty


class Game(ABC):
    """게임 베이스 클래스"""
    
    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.attempts = 0
        self.completed = False
        self.current_progress: Dict[str, Any] = {}
    
    @abstractmethod
    def check_solution(self) -> bool:
        """해답 확인"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """게임 리셋"""
        pass
    
    def increment_attempts(self) -> None:
        """시도 횟수 증가"""
        self.attempts += 1
    
    def mark_completed(self) -> None:
        """완료 표시"""
        self.completed = True