"""
원고 구글 독스를 읽어서 네이버 블로그용 구글 독스 생성

1. 원고 읽기
2. 블로그 스타일 적용
3. 새 구글 독스 생성
4. 이미지 추천
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

# Google Docs API 스코프 (읽기 + 쓰기)
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]


class BlogPostCreator:
    """블로그 포스트 생성기"""

    def __init__(self, blog_skills_path: str, image_index_path: str = None):
        self.blog_skills = self.load_blog_skills(blog_skills_path)
        self.docs_service = None
        self.drive_service = None
        self.image_index = None
        self.image_index_path = image_index_path

        # Claude (Anthropic) 설정
        anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not anthropic_api_key:
            print("⚠️ ANTHROPIC_API_KEY가 설정되지 않았습니다")
            print("   코드에 직접 API 키를 입력하거나 환경 변수를 설정하세요")
        self.claude = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None

        # 이미지 인덱스 로드 (있으면)
        if image_index_path and os.path.exists(image_index_path):
            self._load_image_index()

    def load_blog_skills(self, path: str) -> dict:
        """블로그 스타일 Skills 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_image_index(self):
        """이미지 인덱스 로드"""
        try:
            with open(self.image_index_path, 'r', encoding='utf-8') as f:
                self.image_index = json.load(f)
            print(f"✅ 이미지 인덱스 로드: {len(self.image_index.get('images', []))}개")
        except Exception as e:
            print(f"⚠️ 이미지 인덱스 로드 실패: {e}")

    def _suggest_images_for_section(self, section_text: str, top_k: int = 3) -> List[Dict]:
        """섹션 내용에 맞는 이미지 추천"""
        if not self.image_index:
            return []

        # 간단한 키워드 매칭
        keywords = section_text.split()[:10]  # 상위 10개 단어

        matches = []
        for image in self.image_index.get('images', []):
            score = 0
            description = image.get('description', '').lower()
            tags = ' '.join(image.get('tags', [])).lower()

            for keyword in keywords:
                if len(keyword) < 2:
                    continue
                keyword_lower = keyword.lower()
                if keyword_lower in description:
                    score += 2
                if keyword_lower in tags:
                    score += 1

            if score > 0:
                matches.append({
                    **image,
                    'relevance_score': score
                })

        # 점수 기준 정렬
        matches.sort(key=lambda x: x['relevance_score'], reverse=True)
        return matches[:top_k]

    def authenticate(self):
        """구글 API 인증"""
        creds = None
        token_path = 'token_docs.pickle'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.docs_service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
        print("✅ 구글 API 인증 완료")

    def extract_document_id(self, url: str) -> str:
        """URL에서 문서 ID 추출"""
        if '/d/' in url:
            return url.split('/d/')[1].split('/')[0]
        return url

    def read_source_document(self, doc_id: str) -> dict:
        """원고 문서 읽기"""
        print(f"\n📄 원고 읽기: {doc_id}")

        document = self.docs_service.documents().get(documentId=doc_id).execute()
        title = document.get('title')
        content = document.get('body').get('content')

        # 텍스트 추출
        text_parts = []
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    text_run = elem.get('textRun')
                    if text_run:
                        text_parts.append(text_run.get('content', ''))

        full_text = ''.join(text_parts)

        print(f"  📝 제목: {title}")
        print(f"  📏 길이: {len(full_text)}자")

        return {
            'title': title,
            'text': full_text,
            'raw_content': content
        }

    def transform_to_blog_style(self, source_content: dict) -> dict:
        """원고를 블로그 스타일로 변환"""
        print(f"\n🎨 블로그 스타일 변환: {self.blog_skills['blog_id']}")

        # 이미지 빈도 가이드
        image_freq = self.blog_skills.get('image_style', {}).get('image_frequency', '보통')

        prompt = f"""다음은 원고 텍스트입니다. 이것을 네이버 블로그 포스트로 변환해주세요.

# 원고
제목: {source_content['title']}

{source_content['text'][:2000]}

# 블로그 스타일 가이드
- 블로그: {self.blog_skills['blog_name']}
- 어투: {self.blog_skills['style_profile']['tone']}
- 격식: {self.blog_skills['style_profile']['formality']}/5
- 타겟: {self.blog_skills['content_strategy']['target_audience']}
- 목적: {self.blog_skills['content_strategy']['primary_purpose']}
- 이미지 빈도: {image_freq}

# 요구사항
1. 제목을 블로그에 적합하게 재작성 (SEO 고려, 클릭 유도)
2. 본문을 블로그 스타일로 재작성
3. 이미지가 들어갈 위치에 [이미지: 설명] 표시 (이미지 빈도: {image_freq})
4. 단락은 짧고 간결하게 (2-3문장)
5. 볼드로 강조할 부분은 **텍스트** 표시
6. 이 블로그의 어투와 스타일을 정확히 따를 것

다음 JSON 형식으로 반환:
{{
  "blog_title": "블로그 제목",
  "sections": [
    {{
      "type": "text",
      "content": "단락 내용"
    }},
    {{
      "type": "image_placeholder",
      "description": "이미지 설명 (검색용)"
    }}
  ],
  "seo_keywords": ["키워드1", "키워드2", "키워드3"]
}}

반드시 유효한 JSON만 반환하세요."""

        try:
            # Claude API 호출
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            result_text = response.content[0].text.strip()

            # JSON 추출
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]

            transformed = json.loads(result_text.strip())
            print(f"  ✅ 변환 완료")
            print(f"     제목: {transformed['blog_title']}")
            print(f"     섹션: {len(transformed['sections'])}개")

            return transformed

        except Exception as e:
            print(f"  ❌ 변환 실패: {e}")
            return {
                "blog_title": source_content['title'],
                "sections": [
                    {"type": "text", "content": source_content['text']}
                ],
                "seo_keywords": []
            }

    def create_new_document(self, title: str) -> str:
        """새 구글 독스 생성"""
        print(f"\n📝 새 문서 생성: {title}")

        doc = self.docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')

        print(f"  ✅ 문서 ID: {doc_id}")
        print(f"  🔗 URL: https://docs.google.com/document/d/{doc_id}/edit")

        return doc_id

    def write_to_document(self, doc_id: str, blog_content: dict):
        """문서에 블로그 콘텐츠 작성"""
        print(f"\n✍️ 문서 작성 중...")

        requests = []

        # 제목은 자동으로 설정되므로 본문부터 시작
        index = 1

        for section in blog_content['sections']:
            if section['type'] == 'text':
                content = section['content']

                # 볼드 처리 (**텍스트**)
                # 간단한 처리: 일단 텍스트만 삽입
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': content + '\n\n'
                    }
                })

                # 볼드 처리는 향후 구현
                index += len(content) + 2

            elif section['type'] == 'image_placeholder':
                # 이미지 추천 (인덱스가 있으면)
                suggested_images = self._suggest_images_for_section(
                    section.get('description', ''), top_k=3
                )

                if suggested_images:
                    # 추천 이미지 정보 포함
                    img_text = f"\n[이미지 위치: {section['description']}]\n"
                    img_text += "추천 이미지:\n"
                    for i, img in enumerate(suggested_images[:3], 1):
                        img_text += f"{i}. {img.get('filename', 'N/A')} (점수: {img.get('relevance_score', 0)})\n"
                        img_text += f"   {img.get('web_view_link', 'N/A')}\n"
                    img_text += "\n"
                else:
                    img_text = f"\n[이미지 위치: {section['description']}]\n\n"

                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': img_text
                    }
                })
                index += len(img_text)

        # 문서 업데이트
        if requests:
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

        print(f"  ✅ 작성 완료")

    def create_blog_post(self, source_url: str) -> str:
        """전체 프로세스 실행"""
        print("="*60)
        print("📰 네이버 블로그 포스트 생성")
        print("="*60)

        # 1. 인증
        self.authenticate()

        # 2. 원고 읽기
        doc_id = self.extract_document_id(source_url)
        source_content = self.read_source_document(doc_id)

        # 3. 블로그 스타일 변환
        blog_content = self.transform_to_blog_style(source_content)

        # 4. 새 문서 생성
        new_title = f"[블로그] {blog_content['blog_title']}"
        new_doc_id = self.create_new_document(new_title)

        # 5. 문서 작성
        self.write_to_document(new_doc_id, blog_content)

        # 6. 결과 저장
        result = {
            'source_url': source_url,
            'new_doc_id': new_doc_id,
            'new_doc_url': f"https://docs.google.com/document/d/{new_doc_id}/edit",
            'blog_title': blog_content['blog_title'],
            'blog_id': self.blog_skills['blog_id'],
            'sections_count': len(blog_content['sections']),
            'seo_keywords': blog_content['seo_keywords']
        }

        with open('blog_post_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("\n" + "="*60)
        print("✅ 완료!")
        print("="*60)
        print(f"새 문서: {result['new_doc_url']}")

        return result['new_doc_url']


def main():
    """실행"""
    # 원고 URL
    source_url = "https://docs.google.com/document/d/1pB5UoCDicLigBEOBTPyoazxX3uTQ9RJGXwNUqNsVOjg/edit?tab=t.0"

    # 블로그 선택 (chikkqueen 예시)
    blog_skills_path = "blog_skills_complete_chikkqueen.json"

    # 이미지 인덱스 (있으면)
    image_index_path = "image_index.json" if os.path.exists("image_index.json") else None

    # 생성
    creator = BlogPostCreator(blog_skills_path, image_index_path)
    new_doc_url = creator.create_blog_post(source_url)

    print(f"\n🎉 새 블로그 포스트가 생성되었습니다!")
    print(f"🔗 {new_doc_url}")


if __name__ == "__main__":
    main()
