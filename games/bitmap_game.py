"""
Bitmap matching game implementation
"""

import random
from typing import List, Tuple
from PIL import Image, ImageDraw

from .base_game import Game
from ..core.models import Difficulty


class Tile:
    """타일 클래스"""
    
    def __init__(self, image_data: Image.Image, correct_position: Tuple[int, int], tile_id: int):
        self.image_data = image_data
        self.correct_position = correct_position
        self.current_position = correct_position
        self.tile_id = tile_id


class BitmapGame(Game):
    """비트맵 맞추기 게임"""
    
    def __init__(self, difficulty: Difficulty):
        super().__init__(difficulty)
        self.grid_size = self._calculate_grid_size(difficulty)
        self.image = self._create_sample_image()
        self.tiles = self._create_tiles()
        self._scramble_tiles()
    
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
        width, height = 300, 300
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 간단한 패턴 그리기
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        
        for i in range(6):
            x = (i % 3) * 100
            y = (i // 3) * 150
            draw.rectangle([x, y, x + 100, y + 150], fill=colors[i])
            draw.text((x + 40, y + 70), str(i + 1), fill='white')
        
        return image
    
    def _create_tiles(self) -> List[Tile]:
        """타일 생성"""
        tiles = []
        tile_width = self.image.width // self.grid_size[0]
        tile_height = self.image.height // self.grid_size[1]
        
        tile_id = 0
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                left = col * tile_width
                top = row * tile_height
                right = left + tile_width
                bottom = top + tile_height
                
                tile_image = self.image.crop((left, top, right, bottom))
                tile = Tile(tile_image, (row, col), tile_id)
                tiles.append(tile)
                tile_id += 1
        
        return tiles
    
    def _scramble_tiles(self) -> None:
        """타일 섞기"""
        positions = [(row, col) for row in range(self.grid_size[1]) 
                    for col in range(self.grid_size[0])]
        random.shuffle(positions)
        
        for i, tile in enumerate(self.tiles):
            tile.current_position = positions[i]
    
    def move_tile(self, tile_id: int, new_position: Tuple[int, int]) -> bool:
        """타일 이동"""
        if tile_id >= len(self.tiles):
            return False
        
        # 위치가 유효한지 확인
        if (new_position[0] < 0 or new_position[0] >= self.grid_size[1] or
            new_position[1] < 0 or new_position[1] >= self.grid_size[0]):
            return False
        
        # 해당 위치에 다른 타일이 있는지 확인
        for other_tile in self.tiles:
            if other_tile.tile_id != tile_id and other_tile.current_position == new_position:
                # 위치 교환
                old_position = self.tiles[tile_id].current_position
                other_tile.current_position = old_position
                break
        
        self.tiles[tile_id].current_position = new_position
        return True
    
    def check_solution(self) -> bool:
        """해답 확인"""
        for tile in self.tiles:
            if tile.current_position != tile.correct_position:
                return False
        return True
    
    def reset(self) -> None:
        """게임 리셋"""
        self.attempts = 0
        self.completed = False
        self._scramble_tiles()
    
    def get_current_state(self) -> List[Tuple[int, Tuple[int, int]]]:
        """현재 상태 반환 (타일 ID와 위치)"""
        return [(tile.tile_id, tile.current_position) for tile in self.tiles]