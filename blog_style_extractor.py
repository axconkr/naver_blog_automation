"""
네이버 블로그 포스트 직접 분석 및 스타일 Skills 생성

특정 포스트 URL을 받아서 스타일을 분석하고
블로그별 편집 Skills를 생성합니다.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import google.generativeai as genai


class BlogStyleExtractor:
    """블로그 스타일 추출기"""

    def __init__(self, gemini_api_key: str, headless: bool = False):
        self.gemini_api_key = gemini_api_key
        self.headless = headless
        self.driver = None

        # Gemini 설정
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def init_driver(self):
        """WebDriver 초기화"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=options)
        print("✅ WebDriver 초기화 완료")

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def extract_post_html(self, post_url: str) -> Dict:
        """포스트 HTML 직접 추출"""
        if not self.driver:
            self.init_driver()

        print(f"\n🔍 포스트 분석: {post_url}")
        self.driver.get(post_url)
        time.sleep(5)

        post_data = {
            'url': post_url,
            'title': '',
            'html_content': '',
            'text_content': '',
            'style_analysis': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            # iframe 전환 시도 (여러 방법)
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.frame_to_be_available_and_switch_to_it("mainFrame")
                )
                print("  ✅ mainFrame iframe으로 전환")
            except:
                # iframe 없이 직접 접근
                print("  ℹ️ iframe 없이 직접 접근")

            # 제목 추출
            title_selectors = [
                "div.se-title-text",
                "h3.se_textarea",
                "div.pcol1",
                ".post_title",
                ".se-title"
            ]

            for selector in title_selectors:
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    post_data['title'] = title_elem.text.strip()
                    if post_data['title']:
                        print(f"  📝 제목: {post_data['title'][:50]}...")
                        break
                except:
                    continue

            # 본문 HTML 추출
            content_selectors = [
                "div.se-main-container",
                "div.se_component_wrap",
                "div#postViewArea",
                "div.post-view",
                ".post_ct"
            ]

            for selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    post_data['html_content'] = content_elem.get_attribute('innerHTML')
                    post_data['text_content'] = content_elem.text

                    if post_data['html_content']:
                        print(f"  ✅ 본문 추출 성공: {len(post_data['html_content'])}자")
                        break
                except:
                    continue

            # 페이지 전체 HTML (fallback)
            if not post_data['html_content']:
                post_data['html_content'] = self.driver.page_source
                print("  ⚠️ 전체 페이지 소스 사용")

            # 스타일 분석
            post_data['style_analysis'] = self._analyze_styles()

        except Exception as e:
            print(f"  ❌ 오류: {e}")

        finally:
            try:
                self.driver.switch_to.default_content()
            except:
                pass

        return post_data

    def _analyze_styles(self) -> Dict:
        """현재 페이지의 스타일 분석"""
        analysis = {
            'font_sizes': set(),
            'font_families': set(),
            'colors': set(),
            'bg_colors': set(),
            'text_aligns': set(),
            'line_heights': set(),
            'has_bold': False,
            'has_italic': False,
            'has_underline': False,
            'has_highlight': False,
            'image_count': 0,
            'component_types': []
        }

        try:
            # 모든 텍스트 요소
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, span, div, h1, h2, h3, h4, h5, h6")

            for elem in all_elements[:100]:  # 처음 100개만
                try:
                    # 스타일 수집
                    font_size = elem.value_of_css_property('font-size')
                    font_family = elem.value_of_css_property('font-family')
                    color = elem.value_of_css_property('color')
                    bg_color = elem.value_of_css_property('background-color')
                    text_align = elem.value_of_css_property('text-align')
                    line_height = elem.value_of_css_property('line-height')
                    font_weight = elem.value_of_css_property('font-weight')
                    font_style = elem.value_of_css_property('font-style')
                    text_decoration = elem.value_of_css_property('text-decoration')

                    if font_size and font_size != 'auto':
                        analysis['font_sizes'].add(font_size)
                    if font_family:
                        analysis['font_families'].add(font_family.split(',')[0].strip())
                    if color and color != 'rgba(0, 0, 0, 0)':
                        analysis['colors'].add(color)
                    if bg_color and bg_color not in ['rgba(0, 0, 0, 0)', 'transparent']:
                        analysis['bg_colors'].add(bg_color)
                    if text_align:
                        analysis['text_aligns'].add(text_align)
                    if line_height and line_height != 'normal':
                        analysis['line_heights'].add(line_height)

                    # 텍스트 스타일
                    if font_weight and int(float(font_weight)) >= 700:
                        analysis['has_bold'] = True
                    if font_style == 'italic':
                        analysis['has_italic'] = True
                    if 'underline' in text_decoration:
                        analysis['has_underline'] = True

                except:
                    continue

            # 이미지 개수
            images = self.driver.find_elements(By.TAG_NAME, "img")
            analysis['image_count'] = len(images)

            # 스마트에디터 컴포넌트
            components = self.driver.find_elements(By.CSS_SELECTOR, "[class*='se-component']")
            for comp in components[:50]:
                class_name = comp.get_attribute('class')
                if 'se-text' in class_name:
                    analysis['component_types'].append('text')
                elif 'se-image' in class_name:
                    analysis['component_types'].append('image')
                elif 'se-video' in class_name:
                    analysis['component_types'].append('video')
                elif 'se-divider' in class_name:
                    analysis['component_types'].append('divider')

        except Exception as e:
            print(f"  ⚠️ 스타일 분석 중 오류: {e}")

        # set을 list로 변환
        analysis['font_sizes'] = list(analysis['font_sizes'])
        analysis['font_families'] = list(analysis['font_families'])
        analysis['colors'] = list(analysis['colors'])
        analysis['bg_colors'] = list(analysis['bg_colors'])
        analysis['text_aligns'] = list(analysis['text_aligns'])
        analysis['line_heights'] = list(analysis['line_heights'])

        return analysis

    def generate_style_skills(self, blog_id: str, post_data: Dict) -> Dict:
        """Gemini를 사용해 스타일 Skills 생성"""
        print(f"\n🤖 Gemini로 스타일 Skills 생성 중...")

        # HTML과 분석 데이터를 Gemini에 전달
        prompt = f"""다음은 네이버 블로그 포스트의 HTML과 스타일 분석 데이터입니다.
이 블로그의 고유한 편집 스타일을 파악하고, 구글 독스 → 네이버 블로그 변환 시
적용할 수 있는 "Style Skills"를 JSON 형식으로 생성해주세요.

# 블로그 정보
- 블로그 ID: {blog_id}
- 포스트 URL: {post_data['url']}
- 제목: {post_data['title']}

# 스타일 분석
- 사용된 폰트 크기: {post_data['style_analysis'].get('font_sizes', [])}
- 사용된 폰트: {post_data['style_analysis'].get('font_families', [])}
- 사용된 색상: {post_data['style_analysis'].get('colors', [])[:5]}
- 텍스트 정렬: {post_data['style_analysis'].get('text_aligns', [])}
- 줄간격: {post_data['style_analysis'].get('line_heights', [])}
- 볼드 사용: {post_data['style_analysis'].get('has_bold', False)}
- 이미지 개수: {post_data['style_analysis'].get('image_count', 0)}
- 컴포넌트 타입: {post_data['style_analysis'].get('component_types', [])}

# 본문 미리보기 (처음 1000자)
{post_data['text_content'][:1000]}

다음 JSON 형식으로 Style Skills를 생성해주세요:

{{
  "blog_id": "{blog_id}",
  "blog_name": "블로그 이름 추정",
  "style_profile": {{
    "tone": "어투 (예: 친근한, 전문적인, 캐주얼한)",
    "formality": "격식 수준 (1-5, 1=매우 캐주얼, 5=매우 격식)",
    "emoji_usage": "이모지 사용 빈도 (없음/가끔/자주/매우 자주)"
  }},
  "formatting_rules": {{
    "default_font_size": "기본 폰트 크기 (예: 16px, 14px)",
    "default_font_family": "기본 폰트 (예: 맑은 고딕, 나눔고딕)",
    "default_text_color": "기본 텍스트 색상 (hex 또는 rgb)",
    "default_line_height": "기본 줄간격 (예: 1.6, 1.8, 2.0)",
    "text_align": "기본 텍스트 정렬 (left/center/right)",
    "paragraph_spacing": "문단 간격 (small/medium/large)"
  }},
  "emphasis_style": {{
    "uses_bold": true or false,
    "uses_italic": true or false,
    "uses_underline": true or false,
    "uses_color_highlight": true or false,
    "highlight_color": "강조 색상"
  }},
  "structure_patterns": {{
    "uses_headings": true or false,
    "heading_style": "제목 스타일 설명",
    "uses_dividers": true or false,
    "uses_quotes": true or false,
    "uses_lists": true or false
  }},
  "image_style": {{
    "image_frequency": "이미지 사용 빈도 (없음/적음/보통/많음)",
    "image_placement": "이미지 배치 (상단/중간중간/하단/전체)",
    "image_alignment": "이미지 정렬 (left/center/right)",
    "uses_captions": true or false
  }},
  "opening_pattern": "글 시작 패턴 (예: 인사말로 시작, 바로 본론, 질문으로 시작)",
  "closing_pattern": "글 마무리 패턴 (예: 감사인사, 질문, 다음 글 예고)",
  "special_characteristics": ["이 블로그만의 특별한 스타일 특징들"]
}}

반드시 유효한 JSON만 반환하고, 추가 설명은 하지 마세요."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # JSON 추출
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]

            skills = json.loads(result_text.strip())
            print(f"  ✅ Style Skills 생성 완료")
            return skills

        except Exception as e:
            print(f"  ❌ Gemini 분석 실패: {e}")
            return self._create_fallback_skills(blog_id, post_data)

    def _create_fallback_skills(self, blog_id: str, post_data: Dict) -> Dict:
        """Gemini 실패 시 기본 Skills 생성"""
        return {
            "blog_id": blog_id,
            "blog_name": blog_id,
            "style_profile": {
                "tone": "분석 필요",
                "formality": 3,
                "emoji_usage": "분석 필요"
            },
            "formatting_rules": {
                "default_font_size": post_data['style_analysis'].get('font_sizes', ['16px'])[0] if post_data['style_analysis'].get('font_sizes') else '16px',
                "default_text_color": "#000000",
                "text_align": "left"
            },
            "special_characteristics": ["자동 분석 실패 - 수동 검토 필요"]
        }

    def process_blog(self, blog_id: str, post_url: str) -> Dict:
        """블로그 포스트 분석 및 Skills 생성"""
        print(f"\n{'='*60}")
        print(f"📊 블로그 분석: {blog_id}")
        print(f"{'='*60}")

        # 1. HTML 추출
        post_data = self.extract_post_html(post_url)

        # 2. Skills 생성
        skills = self.generate_style_skills(blog_id, post_data)

        # 3. 결과 통합
        result = {
            'blog_id': blog_id,
            'analyzed_post_url': post_url,
            'post_title': post_data['title'],
            'raw_analysis': post_data['style_analysis'],
            'style_skills': skills,
            'generated_at': datetime.now().isoformat()
        }

        return result

    def save_skills(self, skills: Dict, filename: str = None):
        """Skills JSON 저장"""
        if not filename:
            filename = f"blog_skills_{skills['blog_id']}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(skills, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Skills 저장: {filename}")
        return filename


def main():
    """테스트 실행"""
    from dotenv import load_dotenv
    load_dotenv()

    gemini_api_key = os.getenv('GEMINI_API_KEY')

    # 각 블로그의 대표 포스트
    blogs = [
        {
            'blog_id': 'chikkqueen',
            'post_url': 'https://blog.naver.com/chikkqueen/223992802848'
        },
        {
            'blog_id': 'chick_king',
            'post_url': 'https://blog.naver.com/chick_king/224148907959'
        },
        {
            'blog_id': 'chick_queen',
            'post_url': 'https://blog.naver.com/chick_queen/224148820167'
        },
        {
            'blog_id': '1234ssem',
            'post_url': 'https://blog.naver.com/1234ssem'  # 메인 페이지에서 포스트 찾기
        }
    ]

    extractor = BlogStyleExtractor(gemini_api_key, headless=False)

    try:
        for blog in blogs:
            # 분석 및 Skills 생성
            result = extractor.process_blog(blog['blog_id'], blog['post_url'])

            # 저장
            extractor.save_skills(result)

            # 요약 출력
            print(f"\n{'='*60}")
            print(f"✅ {blog['blog_id']} 완료")
            print(f"   제목: {result['post_title']}")
            print(f"   어투: {result['style_skills'].get('style_profile', {}).get('tone', 'N/A')}")
            print(f"   폰트: {result['style_skills'].get('formatting_rules', {}).get('default_font_size', 'N/A')}")
            print(f"{'='*60}\n")

            time.sleep(3)

    finally:
        extractor.close_driver()


if __name__ == "__main__":
    main()
