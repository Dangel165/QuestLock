"""
Game manager for the Game-Clear Ransomware
"""

import random
from typing import Optional

from .base_game import Game
from .bitmap_game import BitmapGame
from .ascii_game import ASCIIGame
from .riddle_game import RiddleGame
from .difficulty import calculate_difficulty
from ..core.models import GameType, Difficulty


class GameManager:
    """게임 관리자"""
    
    def __init__(self):
        self.current_game: Optional[Game] = None
    
    def select_game_type(self, completed_games: list = None) -> GameType:
        """완료하지 않은 게임 타입 선택"""
        if completed_games is None:
            completed_games = []
        
        all_games = [GameType.BITMAP, GameType.ASCII, GameType.RIDDLE]
        remaining_games = [g for g in all_games if g.value not in completed_games]
        
        if not remaining_games:
            # 모든 게임 완료
            return None
        
        return random.choice(remaining_games)
    
    def create_game(self, game_type: GameType, difficulty: Difficulty) -> Game:
        """게임 인스턴스 생성"""
        if game_type == GameType.BITMAP:
            game = BitmapGame(difficulty)
        elif game_type == GameType.ASCII:
            game = ASCIIGame(difficulty)
        elif game_type == GameType.RIDDLE:
            game = RiddleGame(difficulty)
        else:
            raise ValueError(f"지원하지 않는 게임 타입: {game_type}")
        
        self.current_game = game
        return game
    
    def create_game_by_file_count(self, file_count: int, completed_games: list = None) -> tuple[Game, GameType, Difficulty]:
        """파일 개수에 따른 게임 생성"""
        difficulty = calculate_difficulty(file_count)
        game_type = self.select_game_type(completed_games)
        
        if game_type is None:
            return None, None, difficulty
        
        game = self.create_game(game_type, difficulty)
        
        return game, game_type, difficulty
    
    def check_win_condition(self, game: Game) -> bool:
        """승리 조건 확인"""
        return game.check_solution()
    
    def get_game_description(self, game_type: GameType, difficulty: Difficulty) -> str:
        """게임 설명 반환"""
        descriptions = {
            GameType.BITMAP: {
                Difficulty.EASY: "3x3 비트맵 타일 맞추기 게임",
                Difficulty.MEDIUM: "4x4 비트맵 타일 맞추기 게임",
                Difficulty.HARD: "5x5 비트맵 타일 맞추기 게임"
            },
            GameType.ASCII: {
                Difficulty.EASY: "쉬운 4글자 단어의 ASCII 코드 맞추기",
                Difficulty.MEDIUM: "중간 난이도 4글자 단어의 ASCII 코드 맞추기",
                Difficulty.HARD: "어려운 4글자 단어의 ASCII 코드 맞추기"
            },
            GameType.RIDDLE: {
                Difficulty.EASY: "쉬운 컴퓨터 지식 퀴즈",
                Difficulty.MEDIUM: "중간 난이도 컴퓨터 지식 퀴즈",
                Difficulty.HARD: "어려운 컴퓨터 지식 퀴즈"
            }
        }
        
        return descriptions.get(game_type, {}).get(difficulty, "알 수 없는 게임")
    
    def get_completion_message(self, game_type: GameType) -> str:
        """완료 메시지 반환"""
        messages = {
            GameType.BITMAP: "축하합니다! 비트맵 퍼즐을 완성했습니다!",
            GameType.ASCII: "축하합니다! ASCII 코드 퍼즐을 해결했습니다!",
            GameType.RIDDLE: "축하합니다! 컴퓨터 지식 퀴즈를 맞췄습니다!"
        }
        
        return messages.get(game_type, "축하합니다! 게임을 완료했습니다!")
    
    def reset_current_game(self) -> bool:
        """현재 게임 리셋"""
        if self.current_game:
            self.current_game.reset()
            return True
        return False