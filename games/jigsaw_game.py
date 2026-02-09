"""
Jigsaw puzzle game implementation
"""

import random
from typing import List, Tuple
from PIL import Image, ImageDraw

from .base_game import Game
from ..core.models import Difficulty


class PuzzlePiece:
    """퍼즐 조각 클래스"""
    
    def __init__(self, image_data: Image.Image, correct_position: Tuple[int, int], piece_id: int):
        self.image_data = image_data
        self.correct_position = correct_position
        self.current_position = correct_position
        self.piece_id = piece_id
        self.placed = False


class JigsawGame(Game):
    """직소 퍼즐 게임"""
    
    def __init__(self, difficulty: Difficulty):
        super().__init__(difficulty)
        self.piece_count = self._calculate_piece_count(difficulty)
        self.grid_size = self._calculate_grid_size(difficulty)
        self.image = self._create_sample_image()
        self.pieces = self._create_pieces()
        self._scramble_pieces()
    
    def _calculate_piece_count(self, difficulty: Difficulty) -> int:
        """난이도에 따른 조각 개수 계산"""
        if difficulty == Difficulty.EASY:
            return 9  # 3x3
        elif difficulty == Difficulty.MEDIUM:
            return 16  # 4x4
        else:  # HARD
            return 25  # 5x5
    
    def _calculate_grid_size(self, difficulty: Difficulty) -> Tuple[int, int]:
        """난이도에 따른 그리드 크기 계산"""
        if difficulty == Difficulty.EASY:
            return (3, 3)
        elif difficulty == Difficulty.MEDIUM:
            return (4, 4)
        else:  # HARD
            return (5, 5)
    
    def _create_sample_image(self) -> Image.Image:
        """샘플 이미지 생성"""
        width, height = 400, 400
        image = Image.new('RGB', (width, height), 'lightblue')
        draw = ImageDraw.Draw(image)
        
        # 복잡한 패턴 그리기
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown']
        
        # 원형 패턴
        for i in range(8):
            angle = i * 45
            x = 200 + 120 * (i % 2) * (1 if i < 4 else -1)
            y = 200 + 120 * (i % 2) * (1 if i % 4 < 2 else -1)
            draw.ellipse([x-30, y-30, x+30, y+30], fill=colors[i])
        
        # 중앙 원
        draw.ellipse([170, 170, 230, 230], fill='white')
        draw.text((190, 190), "퍼즐", fill='black')
        
        # 테두리 선
        for i in range(self.grid_size[0] + 1):
            x = i * (width // self.grid_size[0])
            draw.line([(x, 0), (x, height)], fill='black', width=2)
        
        for i in range(self.grid_size[1] + 1):
            y = i * (height // self.grid_size[1])
            draw.line([(0, y), (width, y)], fill='black', width=2)
        
        return image
    
    def _create_pieces(self) -> List[PuzzlePiece]:
        """퍼즐 조각 생성"""
        pieces = []
        piece_width = self.image.width // self.grid_size[0]
        piece_height = self.image.height // self.grid_size[1]
        
        piece_id = 0
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                left = col * piece_width
                top = row * piece_height
                right = left + piece_width
                bottom = top + piece_height
                
                piece_image = self.image.crop((left, top, right, bottom))
                piece = PuzzlePiece(piece_image, (row, col), piece_id)
                pieces.append(piece)
                piece_id += 1
        
        return pieces
    
    def _scramble_pieces(self) -> None:
        """조각 섞기"""
        positions = [(row, col) for row in range(self.grid_size[1]) 
                    for col in range(self.grid_size[0])]
        random.shuffle(positions)
        
        for i, piece in enumerate(self.pieces):
            piece.current_position = positions[i]
            piece.placed = False
    
    def place_piece(self, piece_id: int, position: Tuple[int, int]) -> bool:
        """조각 배치"""
        if piece_id >= len(self.pieces):
            return False
        
        # 위치가 유효한지 확인
        if (position[0] < 0 or position[0] >= self.grid_size[1] or
            position[1] < 0 or position[1] >= self.grid_size[0]):
            return False
        
        # 해당 위치에 다른 조각이 있는지 확인
        for other_piece in self.pieces:
            if other_piece.piece_id != piece_id and other_piece.current_position == position:
                # 위치 교환
                old_position = self.pieces[piece_id].current_position
                other_piece.current_position = old_position
                other_piece.placed = False
                break
        
        self.pieces[piece_id].current_position = position
        
        # 올바른 위치에 배치되었는지 확인
        if position == self.pieces[piece_id].correct_position:
            self.pieces[piece_id].placed = True
        else:
            self.pieces[piece_id].placed = False
        
        return True
    
    def check_solution(self) -> bool:
        """해답 확인"""
        for piece in self.pieces:
            if piece.current_position != piece.correct_position:
                return False
        return True
    
    def reset(self) -> None:
        """게임 리셋"""
        self.attempts = 0
        self.completed = False
        self._scramble_pieces()
    
    def get_current_state(self) -> List[Tuple[int, Tuple[int, int], bool]]:
        """현재 상태 반환 (조각 ID, 위치, 올바른 배치 여부)"""
        return [(piece.piece_id, piece.current_position, piece.placed) 
                for piece in self.pieces]
    
    def get_correctly_placed_count(self) -> int:
        """올바르게 배치된 조각 개수"""
        return sum(1 for piece in self.pieces if piece.placed)