"""
컴퓨터 지식 퀴즈 게임
"""

import random
from typing import Optional
from .base_game import Game
from ..core.models import Difficulty


class RiddleGame(Game):
    """컴퓨터 지식 퀴즈 게임"""
    
    # 난이도별 컴퓨터 퀴즈 (문제, 정답, 힌트)
    RIDDLES = {
        Difficulty.EASY: [
            ("HTTP의 기본 포트 번호는?", "80", "웹 브라우저가 사용하는 기본 포트"),
            ("HTTPS의 기본 포트 번호는?", "443", "보안 웹 연결의 포트"),
            ("1KB는 몇 바이트인가?", "1024", "2의 10승"),
            ("IP 주소 127.0.0.1은 무엇을 의미하는가?", "localhost", "자기 자신을 가리키는 주소"),
            ("HTML의 약자는?", "HyperText Markup Language", "웹 페이지를 만드는 언어"),
            ("CPU의 약자는?", "Central Processing Unit", "컴퓨터의 두뇌"),
            ("RAM의 약자는?", "Random Access Memory", "임시 저장 메모리"),
            ("URL의 약자는?", "Uniform Resource Locator", "웹 주소"),
            ("DNS의 약자는?", "Domain Name System", "도메인을 IP로 변환"),
            ("FTP의 기본 포트 번호는?", "21", "파일 전송 프로토콜"),
        ],
        Difficulty.MEDIUM: [
            ("SQL Injection 공격을 방어하는 기법은?", "Prepared Statement", "쿼리를 미리 준비하는 방법"),
            ("RSA 암호화는 어떤 방식인가?", "비대칭키", "공개키와 개인키를 사용"),
            ("XSS의 약자는?", "Cross Site Scripting", "웹 사이트 간 스크립트 공격"),
            ("CSRF의 약자는?", "Cross Site Request Forgery", "사이트 간 요청 위조"),
            ("SHA-256에서 256은 무엇을 의미하는가?", "비트", "해시 출력 길이"),
            ("TCP의 3-way handshake 순서는?", "SYN-SYNACK-ACK", "연결 수립 과정"),
            ("OSI 7계층 중 가장 하위 계층은?", "물리계층", "Physical Layer"),
            ("IPv4 주소는 몇 비트인가?", "32", "4개의 옥텟"),
            ("Base64 인코딩은 몇 개의 문자를 사용하는가?", "64", "A-Z, a-z, 0-9, +, /"),
            ("UTF-8에서 한글은 몇 바이트인가?", "3", "유니코드 인코딩"),
        ],
        Difficulty.HARD: [
            ("AES-256의 블록 크기는 몇 비트인가?", "128", "키 크기와 블록 크기는 다름"),
            ("SHA-1의 출력 길이는 몇 비트인가?", "160", "20바이트"),
            ("RSA-2048에서 2048은 무엇인가?", "키길이", "비트 단위의 키 크기"),
            ("PBKDF2의 목적은?", "키유도", "패스워드 기반 키 유도 함수"),
            ("Rainbow Table 공격을 방어하는 방법은?", "Salt", "무작위 값 추가"),
            ("Diffie-Hellman의 목적은?", "키교환", "안전한 키 교환 프로토콜"),
            ("HMAC의 약자는?", "Hash-based Message Authentication Code", "해시 기반 메시지 인증"),
            ("TLS 1.3의 핸드셰이크는 몇 RTT인가?", "1", "왕복 시간"),
            ("Bcrypt의 주요 특징은?", "느린속도", "의도적으로 느린 해싱"),
            ("ECDSA의 E는 무엇인가?", "Elliptic", "타원 곡선 암호"),
        ]
    }
    
    def __init__(self, difficulty: Difficulty):
        super().__init__(difficulty)
        self.question, self.answer, self.hint = self._select_riddle()
        self.user_answer: Optional[str] = None
        self.hint_used = False
    
    def _select_riddle(self) -> tuple:
        """난이도에 맞는 컴퓨터 퀴즈 문제 선택"""
        riddles = self.RIDDLES[self.difficulty]
        return random.choice(riddles)
    
    def get_hint(self) -> str:
        """힌트 반환"""
        self.hint_used = True
        return self.hint
    
    def submit_answer(self, answer: str) -> bool:
        """정답 제출"""
        self.user_answer = answer.strip()
        return self.check_solution()
    
    def check_solution(self) -> bool:
        """정답 확인"""
        if self.user_answer is None:
            return False
        
        # 대소문자 구분 없이, 공백 제거하고 비교
        user_ans = self.user_answer.replace(" ", "").lower()
        correct_ans = self.answer.replace(" ", "").lower()
        
        return user_ans == correct_ans
    
    def reset(self):
        """게임 리셋"""
        self.question, self.answer, self.hint = self._select_riddle()
        self.user_answer = None
        self.attempts = 0
        self.completed = False
        self.hint_used = False
    
    def get_state(self) -> dict:
        """게임 상태 반환"""
        return {
            "question": self.question,
            "answer": self.answer,
            "hint": self.hint,
            "user_answer": self.user_answer,
            "attempts": self.attempts,
            "completed": self.completed,
            "hint_used": self.hint_used
        }
    
    def load_state(self, state: dict):
        """게임 상태 로드"""
        self.question = state.get("question", "")
        self.answer = state.get("answer", "")
        self.hint = state.get("hint", "")
        self.user_answer = state.get("user_answer")
        self.attempts = state.get("attempts", 0)
        self.completed = state.get("completed", False)
        self.hint_used = state.get("hint_used", False)
