"""
구글 드라이브 이미지 인덱싱 실행 스크립트
"""

from gdrive_image_indexer import GDriveImageIndexer
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    folder_url = 'https://drive.google.com/drive/u/0/folders/1-5Ra55iS8j1HEj0AZxrSE0xpvAhya6pZ'

    print("="*60)
    print("📸 구글 드라이브 이미지 인덱싱")
    print("="*60)

    indexer = GDriveImageIndexer(gemini_api_key)

    # 1. 인증 (최초 1회 브라우저 열림)
    print('\n🔐 구글 드라이브 인증...')
    indexer.authenticate()

    # 2. 이미지 인덱싱 (처음 10개만 테스트)
    print('\n📸 이미지 분석 시작...')
    print('   (처음 10개만 테스트)')

    index = indexer.build_index(folder_url, sample_size=10)

    # 3. 결과 출력
    print("\n" + "="*60)
    print("✅ 인덱싱 완료!")
    print("="*60)
    print(f"총 {len(index['images'])}개 이미지 분석됨")
    print(f"저장 파일: image_index.json")

    # 4. 샘플 출력
    if index['images']:
        print("\n📊 첫 번째 이미지 예시:")
        first_img = index['images'][0]
        print(f"  파일명: {first_img['filename']}")
        print(f"  설명: {first_img.get('description', 'N/A')[:100]}...")
        print(f"  태그: {', '.join(first_img.get('tags', [])[:5])}")

if __name__ == "__main__":
    main()
