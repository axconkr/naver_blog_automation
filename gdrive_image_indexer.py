"""
구글 드라이브 이미지 인덱서 및 메타데이터 생성기

네이버 블로그 작성 시 문맥에 맞는 이미지를 추천하기 위해
구글 드라이브의 이미지를 분석하고 인덱스를 생성합니다.
"""

import os
import json
import google.generativeai as genai
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pickle

# Google Drive API 스코프
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GDriveImageIndexer:
    """구글 드라이브 이미지 인덱서"""

    def __init__(self, gemini_api_key: str, folder_id: str = None):
        """
        Args:
            gemini_api_key: Gemini API 키
            folder_id: 구글 드라이브 폴더 ID
        """
        self.gemini_api_key = gemini_api_key
        self.folder_id = folder_id
        self.service = None
        self.index_file = "image_index.json"

        # Gemini 설정
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def authenticate(self, credentials_path: str = 'credentials.json'):
        """구글 드라이브 인증"""
        creds = None
        token_path = 'token.pickle'

        # 저장된 토큰이 있으면 로드
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # 유효한 인증 정보가 없으면 새로 인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)
        print("✅ 구글 드라이브 인증 완료")

    def extract_folder_id_from_url(self, url: str) -> str:
        """구글 드라이브 URL에서 폴더 ID 추출"""
        # https://drive.google.com/drive/u/0/folders/1-5Ra55iS8j1HEj0AZxrSE0xpvAhya6pZ
        if '/folders/' in url:
            return url.split('/folders/')[-1].split('?')[0]
        return url

    def list_images_in_folder(self, folder_id: str = None) -> List[Dict]:
        """폴더 내 이미지 파일 목록 가져오기"""
        if not self.service:
            raise Exception("먼저 authenticate()를 호출하세요")

        folder_id = folder_id or self.folder_id

        # 이미지 MIME 타입
        image_mimes = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'image/webp', 'image/bmp', 'image/svg+xml'
        ]

        query = f"'{folder_id}' in parents and trashed=false"
        query += " and (" + " or ".join([f"mimeType='{mime}'" for mime in image_mimes]) + ")"

        results = self.service.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, thumbnailLink)"
        ).execute()

        items = results.get('files', [])

        print(f"📁 폴더에서 {len(items)}개의 이미지를 찾았습니다")
        return items

    def download_image_temp(self, file_id: str) -> Optional[bytes]:
        """이미지를 임시로 다운로드 (메모리)"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO()
            downloader = MediaIoBaseDownload(file_bytes, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()

            return file_bytes.getvalue()
        except Exception as e:
            print(f"⚠️ 이미지 다운로드 실패: {e}")
            return None

    def analyze_image_with_gemini(self, image_bytes: bytes, filename: str) -> Dict:
        """Gemini를 사용해 이미지 내용 분석"""
        try:
            # 이미지를 Gemini에 전달
            prompt = """이 이미지를 분석해서 다음 정보를 JSON 형식으로 제공해주세요:

{
  "description": "이미지에 대한 상세한 설명 (한국어, 2-3문장)",
  "tags": ["관련 키워드 5-10개"],
  "category": "카테고리 (예: 음식, 여행, 제품, 사람, 풍경, 동물 등)",
  "colors": ["주요 색상 3개"],
  "mood": "분위기/느낌 (예: 밝은, 어두운, 따뜻한, 시원한, 활기찬 등)",
  "subjects": ["이미지의 주요 대상/피사체"],
  "context": "이 이미지가 어울릴 만한 블로그 주제나 문맥"
}

반드시 유효한 JSON만 반환하고 다른 설명은 추가하지 마세요."""

            # 임시 파일로 저장
            temp_path = f"/tmp/{filename}"
            with open(temp_path, 'wb') as f:
                f.write(image_bytes)

            # Gemini에 이미지 업로드
            uploaded_file = genai.upload_file(temp_path)

            # 분석 요청
            response = self.model.generate_content([prompt, uploaded_file])

            # 임시 파일 삭제
            os.remove(temp_path)

            # JSON 파싱
            result_text = response.text.strip()

            # ```json ... ``` 형식 제거
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]

            result = json.loads(result_text.strip())
            return result

        except Exception as e:
            print(f"⚠️ 이미지 분석 실패 ({filename}): {e}")
            return {
                "description": "분석 실패",
                "tags": [],
                "category": "unknown",
                "colors": [],
                "mood": "unknown",
                "subjects": [],
                "context": "분석 실패"
            }

    def build_index(self, folder_url: str = None, sample_size: int = None) -> Dict:
        """이미지 인덱스 생성"""
        if folder_url:
            self.folder_id = self.extract_folder_id_from_url(folder_url)

        print(f"🔍 폴더 ID: {self.folder_id}")

        # 1. 이미지 목록 가져오기
        images = self.list_images_in_folder()

        if not images:
            print("❌ 폴더에 이미지가 없습니다")
            return {}

        # 샘플링 (테스트용)
        if sample_size and sample_size < len(images):
            images = images[:sample_size]
            print(f"📊 샘플링: {sample_size}개 이미지만 분석합니다")

        # 2. 각 이미지 분석
        index = {
            "folder_id": self.folder_id,
            "created_at": datetime.now().isoformat(),
            "total_images": len(images),
            "images": []
        }

        for i, img in enumerate(images, 1):
            print(f"\n[{i}/{len(images)}] 분석 중: {img['name']}")

            # 메타데이터 추출
            metadata = {
                "id": img['id'],
                "filename": img['name'],
                "mime_type": img['mimeType'],
                "size": int(img.get('size', 0)),
                "created_time": img.get('createdTime'),
                "modified_time": img.get('modifiedTime'),
                "web_view_link": img.get('webViewLink'),
                "thumbnail_link": img.get('thumbnailLink')
            }

            # 이미지 다운로드 및 AI 분석
            image_bytes = self.download_image_temp(img['id'])

            if image_bytes:
                ai_analysis = self.analyze_image_with_gemini(image_bytes, img['name'])
                metadata.update(ai_analysis)

            index['images'].append(metadata)

            print(f"  ✅ {img['name']}: {metadata.get('description', 'N/A')[:50]}...")

        # 3. 인덱스 저장
        self.save_index(index)

        return index

    def save_index(self, index: Dict, filename: str = None):
        """인덱스를 JSON 파일로 저장"""
        filename = filename or self.index_file

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        print(f"\n💾 인덱스 저장 완료: {filename}")
        print(f"   총 {len(index['images'])}개 이미지 인덱싱됨")

    def load_index(self, filename: str = None) -> Dict:
        """저장된 인덱스 로드"""
        filename = filename or self.index_file

        if not os.path.exists(filename):
            print(f"❌ 인덱스 파일이 없습니다: {filename}")
            return {}

        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search_images_by_context(self, context: str, top_k: int = 5) -> List[Dict]:
        """문맥에 맞는 이미지 검색"""
        index = self.load_index()

        if not index or 'images' not in index:
            print("❌ 인덱스가 비어있습니다")
            return []

        # 간단한 키워드 매칭 (향후 임베딩 기반으로 개선 가능)
        context_lower = context.lower()
        scored_images = []

        for img in index['images']:
            score = 0

            # 설명에서 매칭
            if context_lower in img.get('description', '').lower():
                score += 3

            # 태그에서 매칭
            for tag in img.get('tags', []):
                if context_lower in tag.lower() or tag.lower() in context_lower:
                    score += 2

            # 카테고리 매칭
            if context_lower in img.get('category', '').lower():
                score += 1

            # 문맥 매칭
            if context_lower in img.get('context', '').lower():
                score += 2

            if score > 0:
                img_copy = img.copy()
                img_copy['relevance_score'] = score
                scored_images.append(img_copy)

        # 점수 기준 정렬
        scored_images.sort(key=lambda x: x['relevance_score'], reverse=True)

        return scored_images[:top_k]


def main():
    """테스트 실행"""
    from dotenv import load_dotenv
    load_dotenv()

    gemini_api_key = os.getenv('GEMINI_API_KEY')
    folder_url = "https://drive.google.com/drive/u/0/folders/1-5Ra55iS8j1HEj0AZxrSE0xpvAhya6pZ"

    indexer = GDriveImageIndexer(gemini_api_key)

    # 인증
    indexer.authenticate()

    # 인덱스 생성 (처음 5개만 테스트)
    index = indexer.build_index(folder_url, sample_size=5)

    print("\n" + "="*60)
    print("인덱싱 완료!")
    print("="*60)

    # 검색 테스트
    print("\n🔍 검색 테스트: '음식'")
    results = indexer.search_images_by_context("음식", top_k=3)

    for i, img in enumerate(results, 1):
        print(f"\n{i}. {img['filename']}")
        print(f"   설명: {img.get('description', 'N/A')}")
        print(f"   관련도: {img.get('relevance_score', 0)}")
        print(f"   링크: {img.get('web_view_link', 'N/A')}")


if __name__ == "__main__":
    main()
