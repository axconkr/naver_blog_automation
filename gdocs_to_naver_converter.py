"""
구글 독스 → 네이버 블로그 스타일 변환 엔진

구글 독스의 내용을 읽어서 각 블로그의 스타일 Skills를 적용하여
네이버 블로그에 업로드 가능한 형식으로 변환합니다.
"""

import os
import json
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle


# Google Docs API 스코프
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']


class GDocsToNaverConverter:
    """구글 독스 → 네이버 블로그 변환기"""

    def __init__(self, blog_skills_path: str):
        """
        Args:
            blog_skills_path: 블로그 Skills JSON 파일 경로
        """
        self.blog_skills_path = blog_skills_path
        self.blog_skills = self.load_blog_skills()
        self.docs_service = None

    def load_blog_skills(self) -> Dict:
        """블로그 스타일 Skills 로드"""
        with open(self.blog_skills_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def authenticate_gdocs(self, credentials_path: str = 'credentials.json'):
        """구글 독스 API 인증"""
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
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.docs_service = build('docs', 'v1', credentials=creds)
        print("✅ 구글 독스 인증 완료")

    def extract_document_id_from_url(self, url: str) -> str:
        """구글 독스 URL에서 문서 ID 추출"""
        # https://docs.google.com/document/d/DOCUMENT_ID/edit
        if '/d/' in url:
            return url.split('/d/')[1].split('/')[0]
        return url

    def read_gdocs_content(self, document_id: str) -> Dict:
        """구글 독스 내용 읽기"""
        print(f"\n📄 구글 독스 읽기: {document_id}")

        document = self.docs_service.documents().get(documentId=document_id).execute()

        doc_title = document.get('title')
        content = document.get('body').get('content')

        print(f"  📝 제목: {doc_title}")

        # 문서 내용 파싱
        parsed_content = self._parse_document_structure(content)

        return {
            'title': doc_title,
            'document_id': document_id,
            'raw_content': content,
            'parsed_content': parsed_content
        }

    def _parse_document_structure(self, content: List) -> List[Dict]:
        """구글 독스 구조 파싱"""
        parsed = []

        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                para_data = self._parse_paragraph(paragraph)
                if para_data:
                    parsed.append(para_data)

            elif 'table' in element:
                # 테이블 처리 (향후 구현)
                parsed.append({
                    'type': 'table',
                    'content': '(테이블)'
                })

        return parsed

    def _parse_paragraph(self, paragraph: Dict) -> Optional[Dict]:
        """단락 파싱"""
        elements = paragraph.get('elements', [])

        if not elements:
            return None

        text_parts = []
        styles = {
            'bold': False,
            'italic': False,
            'underline': False,
            'font_size': None,
            'foreground_color': None
        }

        for elem in elements:
            text_run = elem.get('textRun')
            if not text_run:
                continue

            content = text_run.get('content', '')
            text_style = text_run.get('textStyle', {})

            # 스타일 정보 추출
            if text_style.get('bold'):
                styles['bold'] = True
            if text_style.get('italic'):
                styles['italic'] = True
            if text_style.get('underline'):
                styles['underline'] = True

            font_size = text_style.get('fontSize', {}).get('magnitude')
            if font_size:
                styles['font_size'] = font_size

            fg_color = text_style.get('foregroundColor', {}).get('color', {}).get('rgbColor')
            if fg_color:
                styles['foreground_color'] = fg_color

            text_parts.append({
                'text': content,
                'style': text_style
            })

        # 전체 텍스트
        full_text = ''.join([part['text'] for part in text_parts])

        if not full_text.strip():
            return None

        # 단락 정렬
        para_style = paragraph.get('paragraphStyle', {})
        alignment = para_style.get('alignment', 'START')

        return {
            'type': 'paragraph',
            'text': full_text,
            'text_parts': text_parts,
            'styles': styles,
            'alignment': alignment
        }

    def apply_blog_style(self, parsed_content: List[Dict]) -> Dict:
        """블로그 스타일 적용"""
        print(f"\n🎨 블로그 스타일 적용: {self.blog_skills['blog_id']}")

        styled_content = {
            'blog_id': self.blog_skills['blog_id'],
            'formatting_rules': self.blog_skills['formatting_rules'],
            'styled_paragraphs': []
        }

        for para in parsed_content:
            if para['type'] == 'paragraph':
                styled_para = self._style_paragraph(para)
                styled_content['styled_paragraphs'].append(styled_para)

        return styled_content

    def _style_paragraph(self, para: Dict) -> Dict:
        """단락에 블로그 스타일 적용"""
        rules = self.blog_skills['formatting_rules']

        # 기본 스타일 적용
        styled = {
            'text': para['text'],
            'html': '',
            'naver_style': {}
        }

        # 폰트 크기
        font_size = rules.get('default_font_size', '13px')
        styled['naver_style']['font_size'] = font_size

        # 폰트 패밀리
        font_family = rules.get('default_font_family', '나눔고딕')
        styled['naver_style']['font_family'] = font_family

        # 텍스트 색상
        text_color = rules.get('default_text_color', '#444444')
        styled['naver_style']['color'] = text_color

        # 정렬
        text_align = rules.get('text_align', 'left')
        styled['naver_style']['text_align'] = text_align

        # 줄간격
        line_height = rules.get('default_line_height', '1.8')
        styled['naver_style']['line_height'] = line_height

        # HTML 생성
        styled['html'] = self._generate_naver_html(para, styled['naver_style'])

        return styled

    def _generate_naver_html(self, para: Dict, naver_style: Dict) -> str:
        """네이버 블로그 HTML 생성"""
        # 스타일 문자열 생성
        style_parts = []
        style_parts.append(f"font-size: {naver_style['font_size']}")
        style_parts.append(f"font-family: {naver_style['font_family']}")
        style_parts.append(f"color: {naver_style['color']}")
        style_parts.append(f"line-height: {naver_style['line_height']}")
        style_parts.append(f"text-align: {naver_style['text_align']}")

        style_str = '; '.join(style_parts)

        # HTML 생성
        text = para['text']

        # 볼드 처리
        if para['styles'].get('bold'):
            text = f"<strong>{text}</strong>"

        # 이탤릭 처리
        if para['styles'].get('italic'):
            text = f"<em>{text}</em>"

        # 밑줄 처리
        if para['styles'].get('underline'):
            text = f"<u>{text}</u>"

        # 최종 HTML
        html = f'<p style="{style_str}">{text}</p>'

        return html

    def convert_document(self, document_id: str) -> Dict:
        """구글 독스 문서 전체 변환"""
        print("="*60)
        print("📄 구글 독스 → 네이버 블로그 변환")
        print("="*60)

        # 1. 구글 독스 읽기
        doc_content = self.read_gdocs_content(document_id)

        # 2. 블로그 스타일 적용
        styled_content = self.apply_blog_style(doc_content['parsed_content'])

        # 3. 최종 HTML 생성
        final_html = self._generate_final_html(styled_content)

        result = {
            'title': doc_content['title'],
            'blog_id': self.blog_skills['blog_id'],
            'styled_content': styled_content,
            'final_html': final_html
        }

        return result

    def _generate_final_html(self, styled_content: Dict) -> str:
        """최종 HTML 생성"""
        html_parts = []

        for para in styled_content['styled_paragraphs']:
            html_parts.append(para['html'])

        return '\n'.join(html_parts)

    def save_converted_content(self, result: Dict, filename: str = None):
        """변환 결과 저장"""
        if not filename:
            filename = f"converted_{result['blog_id']}_{result['title'][:20]}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n💾 변환 결과 저장: {filename}")

        # HTML 파일도 저장
        html_filename = filename.replace('.json', '.html')
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(result['final_html'])

        print(f"💾 HTML 저장: {html_filename}")

        return filename


def main():
    """테스트 실행"""

    # 블로그 Skills 선택
    blog_skills_path = "blog_skills_complete_chikkqueen.json"

    # 변환기 초기화
    converter = GDocsToNaverConverter(blog_skills_path)

    # 구글 독스 인증
    converter.authenticate_gdocs()

    # 테스트용 문서 ID (실제 문서 ID로 교체 필요)
    document_id = "YOUR_DOCUMENT_ID"  # 구글 독스 URL에서 추출

    # 변환 실행
    result = converter.convert_document(document_id)

    # 저장
    converter.save_converted_content(result)

    print("\n" + "="*60)
    print("✅ 변환 완료!")
    print("="*60)
    print(f"제목: {result['title']}")
    print(f"블로그: {result['blog_id']}")
    print(f"단락 수: {len(result['styled_content']['styled_paragraphs'])}")


if __name__ == "__main__":
    main()
