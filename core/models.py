"""
Core data models for the Game-Clear Ransomware
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from cryptography.hazmat.primitives.asymmetric import rsa


class GameType(Enum):
    """게임 타입"""
    BITMAP = "bitmap"
    ASCII = "ascii"
    RIDDLE = "riddle"


class Difficulty(Enum):
    """난이도"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class FileInfo:
    """파일 정보"""
    path: Path
    size: int
    extension: str
    modified_time: datetime
    checksum: str


@dataclass
class ValidationResult:
    """폴더 검증 결과"""
    is_valid: bool
    error_message: Optional[str]
    warnings: List[str]
    file_count: int
    total_size: int


@dataclass
class EncryptionResult:
    """암호화 결과"""
    success: bool
    encrypted_file: Path
    original_checksum: str
    error: Optional[str]


@dataclass
class DecryptionResult:
    """복호화 결과"""
    success: bool
    decrypted_file: Path
    checksum_match: bool
    error: Optional[str]


@dataclass
class KeyPair:
    """RSA 키 쌍"""
    public_key: rsa.RSAPublicKey
    private_key: rsa.RSAPrivateKey
    key_size: int = 4096


@dataclass
class GameState:
    """게임 상태"""
    game_type: GameType
    difficulty: Difficulty
    attempts: int
    completed: bool
    current_progress: Dict[str, Any]


@dataclass
class EncryptionStatus:
    """암호화 상태"""
    total_files: int
    encrypted_files: int
    failed_files: List[str]


@dataclass
class KeyStorage:
    """키 저장 정보"""
    key_file: str


@dataclass
class Progress:
    """진행 상황"""
    current: int
    total: int
    percentage: float
    status_message: str


@dataclass
class SessionInfo:
    """세션 정보"""
    session_id: str
    timestamp: datetime
    target_folder: Path
    completed: bool


@dataclass
class SimulatorState:
    """전체 상태"""
    session_id: str
    timestamp: datetime
    target_folder: Path
    backup_location: Optional[Path]
    encryption_status: EncryptionStatus
    game_state: GameState
    key_storage: KeyStorage
    completed_games: List[str] = None  # 완료한 게임 목록
    
    def __post_init__(self):
        if self.completed_games is None:
            self.completed_games = []
