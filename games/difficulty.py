"""
Difficulty calculation for games
"""

from ..core.models import Difficulty


def calculate_difficulty(file_count: int) -> Difficulty:
    """파일 개수에 따른 난이도 계산"""
    if file_count <= 10:
        return Difficulty.EASY
    elif file_count <= 50:
        return Difficulty.MEDIUM
    else:
        return Difficulty.HARD