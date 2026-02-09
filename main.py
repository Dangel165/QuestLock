#!/usr/bin/env python3
"""
QuestLock v1.0.0
Created by Dangel

RSA-4096 암호화를 사용하여 파일을 암호화하고, 게임을 클리어하면 복호화됩니다.
"""

import logging
import sys
import tkinter as tk
from pathlib import Path

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_dir = Path.home() / ".game_ransomware" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "ransomware.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_dependencies():
    """의존성 확인"""
    try:
        import cryptography
        import PIL
        return True
    except ImportError as e:
        print(f"필수 라이브러리가 설치되지 않았습니다: {e}")
        print("다음 명령어로 설치하세요:")
        print("pip install -r requirements.txt")
        return False


def show_disclaimer():
    """경고 표시"""
    disclaimer = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   ⚠️  QuestLock v1.0.0  ⚠️                   ║
    ║                    Created by Dangel                         ║
    ╚══════════════════════════════════════════════════════════════╝
    
    【경고】
    이 프로그램은 실제로 파일을 RSA-4096으로 암호화합니다.
    3가지 게임(비트맵, ASCII, 컴퓨터 퀴즈)을 모두 클리어해야 복구됩니다.
    
    【주의사항】
    • 중요한 파일이 있는 폴더는 절대 선택하지 마세요
    • 반드시 테스트용 폴더를 만들어서 사용하세요
    • 게임을 클리어하지 못하면 파일을 복구할 수 없습니다
    
    【면책】
    본 프로그램 사용으로 인한 모든 데이터 손실은 사용자 책임입니다.
    교육 목적으로만 사용하세요.
    """
    print(disclaimer)
    
    response = input("위 내용을 이해하고 계속하시겠습니까? (yes/no): ").lower().strip()
    return response in ['yes', 'y', '예', 'ㅇ']


def main():
    """메인 함수"""
    print("QuestLock v1.0.0")
    print("Created by Dangel")
    print("=" * 50)
    
    # 경고
    if not show_disclaimer():
        print("프로그램을 종료합니다.")
        return
    
    # 의존성 확인
    if not check_dependencies():
        return
    
    # 로깅 설정
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("프로그램 시작")
        
        # 컨트롤러 import 및 실행
        from .core.simulator_controller import SimulatorController
        
        controller = SimulatorController()
        controller.run()
        
        logger.info("프로그램 종료")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        print("\n프로그램이 중단되었습니다.")
        
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        print(f"오류가 발생했습니다: {e}")
        
        # Tkinter 오류인 경우 GUI 환경 확인
        if "tkinter" in str(e).lower():
            print("\nGUI 환경을 확인해주세요:")
            print("- Windows: 정상적으로 설치된 Python 사용")
            print("- Linux: python3-tk 패키지 설치 필요")
            print("- macOS: 정상적으로 설치된 Python 사용")


if __name__ == "__main__":
    main()