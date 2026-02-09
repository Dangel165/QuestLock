"""
Unit tests for JigsawGame
"""

import pytest
from PIL import Image

from game_ransomware_simulator.games.jigsaw_game import JigsawGame, PuzzlePiece
from game_ransomware_simulator.core.models import Difficulty


class TestJigsawGame:
    """JigsawGame 단위 테스트"""
    
    def test_piece_generation_easy_difficulty(self):
        """Easy 난이도 조각 생성 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # Easy: 3x3 = 9 pieces
        assert game.piece_count == 9
        assert game.grid_size == (3, 3)
        assert len(game.pieces) == 9
        
        # 모든 조각이 올바른 ID를 가지는지 확인
        piece_ids = [piece.piece_id for piece in game.pieces]
        assert piece_ids == list(range(9))
        
        # 모든 조각이 올바른 correct_position을 가지는지 확인
        expected_positions = [(row, col) for row in range(3) for col in range(3)]
        actual_positions = [piece.correct_position for piece in game.pieces]
        assert sorted(actual_positions) == sorted(expected_positions)
    
    def test_piece_generation_medium_difficulty(self):
        """Medium 난이도 조각 생성 테스트"""
        game = JigsawGame(Difficulty.MEDIUM)
        
        # Medium: 4x4 = 16 pieces
        assert game.piece_count == 16
        assert game.grid_size == (4, 4)
        assert len(game.pieces) == 16
        
        # 모든 조각이 올바른 ID를 가지는지 확인
        piece_ids = [piece.piece_id for piece in game.pieces]
        assert piece_ids == list(range(16))
        
        # 모든 조각이 올바른 correct_position을 가지는지 확인
        expected_positions = [(row, col) for row in range(4) for col in range(4)]
        actual_positions = [piece.correct_position for piece in game.pieces]
        assert sorted(actual_positions) == sorted(expected_positions)
    
    def test_piece_generation_hard_difficulty(self):
        """Hard 난이도 조각 생성 테스트"""
        game = JigsawGame(Difficulty.HARD)
        
        # Hard: 5x5 = 25 pieces
        assert game.piece_count == 25
        assert game.grid_size == (5, 5)
        assert len(game.pieces) == 25
        
        # 모든 조각이 올바른 ID를 가지는지 확인
        piece_ids = [piece.piece_id for piece in game.pieces]
        assert piece_ids == list(range(25))
        
        # 모든 조각이 올바른 correct_position을 가지는지 확인
        expected_positions = [(row, col) for row in range(5) for col in range(5)]
        actual_positions = [piece.correct_position for piece in game.pieces]
        assert sorted(actual_positions) == sorted(expected_positions)
    
    def test_pieces_have_image_data(self):
        """모든 조각이 이미지 데이터를 가지는지 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        for piece in game.pieces:
            assert isinstance(piece.image_data, Image.Image)
            assert piece.image_data.width > 0
            assert piece.image_data.height > 0
    
    def test_pieces_are_scrambled_initially(self):
        """초기에 조각들이 섞여있는지 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 모든 조각이 올바른 위치에 있지 않아야 함 (섞여있어야 함)
        correctly_placed = sum(1 for piece in game.pieces 
                             if piece.current_position == piece.correct_position)
        
        # 모든 조각이 올바른 위치에 있을 확률은 매우 낮음 (1/9! for easy)
        # 하지만 가능성이 있으므로, 대부분이 섞여있는지만 확인
        assert correctly_placed < len(game.pieces)
    
    def test_win_condition_detection_initially_false(self):
        """초기 상태에서 승리 조건이 false인지 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 초기에는 조각들이 섞여있으므로 승리 조건이 false여야 함
        assert not game.check_solution()
    
    def test_win_condition_detection_when_solved(self):
        """모든 조각이 올바른 위치에 있을 때 승리 조건 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 모든 조각을 올바른 위치에 배치
        for piece in game.pieces:
            piece.current_position = piece.correct_position
            piece.placed = True
        
        # 승리 조건이 true여야 함
        assert game.check_solution()
    
    def test_win_condition_detection_partially_solved(self):
        """일부 조각만 올바른 위치에 있을 때 승리 조건 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 첫 번째 조각만 올바른 위치에 배치
        game.pieces[0].current_position = game.pieces[0].correct_position
        game.pieces[0].placed = True
        
        # 나머지 조각들은 잘못된 위치에 배치
        for i in range(1, len(game.pieces)):
            # 다른 위치로 이동 (순환 이동)
            next_idx = (i + 1) % len(game.pieces)
            game.pieces[i].current_position = game.pieces[next_idx].correct_position
            game.pieces[i].placed = False
        
        # 승리 조건이 false여야 함
        assert not game.check_solution()
    
    def test_place_piece_valid_position(self):
        """유효한 위치에 조각 배치 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 첫 번째 조각을 (1, 1) 위치에 배치
        result = game.place_piece(0, (1, 1))
        
        assert result is True
        assert game.pieces[0].current_position == (1, 1)
    
    def test_place_piece_invalid_position(self):
        """유효하지 않은 위치에 조각 배치 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 범위를 벗어난 위치에 배치 시도
        result = game.place_piece(0, (5, 5))  # Easy는 3x3이므로 유효하지 않음
        
        assert result is False
        
        # 음수 위치에 배치 시도
        result = game.place_piece(0, (-1, 0))
        
        assert result is False
    
    def test_place_piece_invalid_piece_id(self):
        """유효하지 않은 조각 ID로 배치 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 존재하지 않는 조각 ID로 배치 시도
        result = game.place_piece(99, (1, 1))
        
        assert result is False
    
    def test_place_piece_correct_position_updates_placed_status(self):
        """올바른 위치에 배치했을 때 placed 상태 업데이트 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 첫 번째 조각의 올바른 위치 확인
        correct_pos = game.pieces[0].correct_position
        
        # 올바른 위치에 배치
        game.place_piece(0, correct_pos)
        
        assert game.pieces[0].placed is True
        assert game.pieces[0].current_position == correct_pos
    
    def test_place_piece_wrong_position_updates_placed_status(self):
        """잘못된 위치에 배치했을 때 placed 상태 업데이트 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 첫 번째 조각의 올바른 위치가 아닌 다른 위치에 배치
        correct_pos = game.pieces[0].correct_position
        wrong_pos = (correct_pos[0], (correct_pos[1] + 1) % 3)  # 다른 위치
        
        # 잘못된 위치에 배치
        game.place_piece(0, wrong_pos)
        
        assert game.pieces[0].placed is False
        assert game.pieces[0].current_position == wrong_pos
    
    def test_get_correctly_placed_count(self):
        """올바르게 배치된 조각 개수 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 초기에는 0개
        assert game.get_correctly_placed_count() == 0
        
        # 첫 번째 조각을 올바른 위치에 배치
        correct_pos = game.pieces[0].correct_position
        game.place_piece(0, correct_pos)
        
        assert game.get_correctly_placed_count() == 1
        
        # 두 번째 조각을 올바른 위치에 배치
        correct_pos = game.pieces[1].correct_position
        game.place_piece(1, correct_pos)
        
        assert game.get_correctly_placed_count() == 2
    
    def test_reset_game(self):
        """게임 리셋 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 일부 조각을 올바른 위치에 배치하고 시도 횟수 증가
        game.place_piece(0, game.pieces[0].correct_position)
        game.increment_attempts()
        game.mark_completed()
        
        # 리셋 전 상태 확인
        assert game.attempts > 0
        assert game.completed is True
        assert game.get_correctly_placed_count() > 0
        
        # 리셋
        game.reset()
        
        # 리셋 후 상태 확인
        assert game.attempts == 0
        assert game.completed is False
        # 조각들이 다시 섞여있어야 함 (모든 조각이 올바른 위치에 있지 않아야 함)
        correctly_placed = sum(1 for piece in game.pieces 
                             if piece.current_position == piece.correct_position)
        assert correctly_placed < len(game.pieces)
    
    def test_get_current_state(self):
        """현재 상태 반환 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 첫 번째 조각을 올바른 위치에 배치
        correct_pos = game.pieces[0].correct_position
        game.place_piece(0, correct_pos)
        
        state = game.get_current_state()
        
        # 상태가 올바른 형식인지 확인
        assert len(state) == len(game.pieces)
        
        for piece_id, position, placed in state:
            assert isinstance(piece_id, int)
            assert isinstance(position, tuple)
            assert len(position) == 2
            assert isinstance(placed, bool)
            
            # 첫 번째 조각은 올바르게 배치되어야 함
            if piece_id == 0:
                assert placed is True
                assert position == correct_pos
    
    def test_hint_system_provides_hints(self):
        """힌트 시스템이 힌트를 제공하는지 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 다양한 시도 횟수에 대해 힌트 테스트
        for attempt_count in [1, 3, 5, 7, 10]:
            hint = game.get_hint(attempt_count)
            assert isinstance(hint, str)
            assert len(hint) > 0
    
    def test_piece_position_exchange(self):
        """조각 위치 교환 테스트"""
        game = JigsawGame(Difficulty.EASY)
        
        # 두 조각의 초기 위치 저장
        piece1_initial_pos = game.pieces[0].current_position
        piece2_initial_pos = game.pieces[1].current_position
        
        # 첫 번째 조각을 두 번째 조각의 위치로 이동
        game.place_piece(0, piece2_initial_pos)
        
        # 위치가 교환되었는지 확인
        assert game.pieces[0].current_position == piece2_initial_pos
        assert game.pieces[1].current_position == piece1_initial_pos