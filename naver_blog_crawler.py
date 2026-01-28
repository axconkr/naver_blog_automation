"""
네이버 블로그 크롤러

특정 네이버 블로그의 포스트를 수집하고 스타일을 분석합니다.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import google.generativeai as genai


class NaverBlogCrawler:
    """네이버 블로그 크롤러"""

    def __init__(self, headless: bool = False):
        """
        Args:
            headless: 헤드리스 모드 실행 여부
        """
        self.headless = headless
        self.driver = None

    def init_driver(self):
        """WebDriver 초기화"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=options)
        print("✅ WebDriver 초기화 완료")

    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver 종료")

    def get_blog_post_urls(self, blog_id: str, max_posts: int = 10) -> List[str]:
        """
        블로그의 포스트 URL 목록 가져오기

        Args:
            blog_id: 네이버 블로그 ID (예: chikkqueen)
            max_posts: 수집할 최대 포스트 개수

        Returns:
            포스트 URL 목록
        """
        if not self.driver:
            self.init_driver()

        blog_url = f"https://blog.naver.com/{blog_id}"
        self.driver.get(blog_url)
        time.sleep(3)

        post_urls = []

        try:
            # iframe으로 전환
            self.driver.switch_to.frame("mainFrame")

            # 포스트 링크 찾기
            post_links = self.driver.find_elements(By.CSS_SELECTOR, "a.link_title")

            for link in post_links[:max_posts]:
                url = link.get_attribute('href')
                if url:
                    post_urls.append(url)

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"⚠️ 포스트 URL 수집 실패: {e}")
            self.driver.switch_to.default_content()

        print(f"📝 {len(post_urls)}개의 포스트 URL 수집됨")
        return post_urls

    def extract_post_content(self, post_url: str) -> Dict:
        """
        포스트 내용 추출

        Args:
            post_url: 포스트 URL

        Returns:
            포스트 데이터 (제목, 본문, 이미지 등)
        """
        if not self.driver:
            self.init_driver()

        self.driver.get(post_url)
        time.sleep(2)

        post_data = {
            'url': post_url,
            'title': '',
            'content': '',
            'raw_html': '',
            'images': [],
            'structure': {},
            'crawled_at': datetime.now().isoformat()
        }

        try:
            # iframe으로 전환
            self.driver.switch_to.frame("mainFrame")

            # 제목
            try:
                title_elem = self.driver.find_element(By.CSS_SELECTOR, ".se-title-text")
                post_data['title'] = title_elem.text
            except NoSuchElementException:
                pass

            # 본문 내용 (텍스트)
            try:
                content_elem = self.driver.find_element(By.CSS_SELECTOR, ".se-main-container")
                post_data['content'] = content_elem.text
                post_data['raw_html'] = content_elem.get_attribute('innerHTML')
            except NoSuchElementException:
                pass

            # 이미지 URL 수집
            try:
                images = self.driver.find_elements(By.CSS_SELECTOR, "img.se-image-resource")
                for img in images:
                    img_url = img.get_attribute('src')
                    if img_url:
                        post_data['images'].append(img_url)
            except NoSuchElementException:
                pass

            # 구조 분석 (문단, 제목 등)
            post_data['structure'] = self._analyze_structure()

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"⚠️ 포스트 내용 추출 실패: {e}")
            self.driver.switch_to.default_content()

        return post_data

    def _analyze_structure(self) -> Dict:
        """포스트 구조 분석 (iframe 내부에서 호출)"""
        structure = {
            'has_heading': False,
            'has_subheading': False,
            'has_bold': False,
            'has_italic': False,
            'has_list': False,
            'has_link': False,
            'has_quote': False,
            'paragraph_count': 0,
            'image_count': 0,
            'text_align': 'left'  # 기본값
        }

        try:
            # 제목 태그
            if self.driver.find_elements(By.CSS_SELECTOR, ".se-text-heading"):
                structure['has_heading'] = True

            # 부제목
            if self.driver.find_elements(By.CSS_SELECTOR, ".se-text-subheading"):
                structure['has_subheading'] = True

            # 볼드
            if self.driver.find_elements(By.CSS_SELECTOR, "strong, b"):
                structure['has_bold'] = True

            # 이탤릭
            if self.driver.find_elements(By.CSS_SELECTOR, "em, i"):
                structure['has_italic'] = True

            # 리스트
            if self.driver.find_elements(By.CSS_SELECTOR, "ul, ol"):
                structure['has_list'] = True

            # 링크
            if self.driver.find_elements(By.CSS_SELECTOR, "a"):
                structure['has_link'] = True

            # 인용구
            if self.driver.find_elements(By.CSS_SELECTOR, "blockquote"):
                structure['has_quote'] = True

            # 문단 수
            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, ".se-text-paragraph")
            structure['paragraph_count'] = len(paragraphs)

            # 이미지 수
            images = self.driver.find_elements(By.CSS_SELECTOR, "img.se-image-resource")
            structure['image_count'] = len(images)

            # 텍스트 정렬 (첫 번째 문단 기준)
            if paragraphs:
                text_align = paragraphs[0].value_of_css_property('text-align')
                structure['text_align'] = text_align

        except Exception as e:
            print(f"⚠️ 구조 분석 중 오류: {e}")

        return structure

    def crawl_blog(self, blog_id: str, max_posts: int = 5) -> List[Dict]:
        """
        블로그 전체 크롤링

        Args:
            blog_id: 블로그 ID
            max_posts: 수집할 최대 포스트 개수

        Returns:
            포스트 데이터 리스트
        """
        print(f"\n🕷️ 블로그 크롤링 시작: {blog_id}")
        print("="*60)

        # 포스트 URL 수집
        post_urls = self.get_blog_post_urls(blog_id, max_posts)

        if not post_urls:
            print("❌ 수집된 포스트가 없습니다")
            return []

        # 각 포스트 내용 추출
        posts = []
        for i, url in enumerate(post_urls, 1):
            print(f"\n[{i}/{len(post_urls)}] 크롤링: {url}")
            post_data = self.extract_post_content(url)

            if post_data['title']:
                print(f"  ✅ 제목: {post_data['title'][:50]}...")
                print(f"     본문: {len(post_data['content'])}자")
                print(f"     이미지: {len(post_data['images'])}개")
                posts.append(post_data)
            else:
                print("  ⚠️ 내용 추출 실패")

            time.sleep(2)  # 요청 간격

        return posts

    def save_to_json(self, blog_id: str, posts: List[Dict], filename: str = None):
        """크롤링 결과를 JSON으로 저장"""
        if not filename:
            filename = f"blog_crawl_{blog_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            'blog_id': blog_id,
            'crawled_at': datetime.now().isoformat(),
            'post_count': len(posts),
            'posts': posts
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 저장 완료: {filename}")
        return filename


class BlogStyleAnalyzer:
    """블로그 스타일 분석기"""

    def __init__(self, gemini_api_key: str):
        """
        Args:
            gemini_api_key: Gemini API 키
        """
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_blog_style(self, posts: List[Dict]) -> Dict:
        """
        블로그 포스트들을 분석해서 스타일 추출

        Args:
            posts: 포스트 데이터 리스트

        Returns:
            스타일 분석 결과
        """
        if not posts:
            return {}

        print("\n🔍 블로그 스타일 분석 중...")

        # 전체 포스트 정보 요약
        summary = {
            'total_posts': len(posts),
            'avg_content_length': sum(len(p['content']) for p in posts) / len(posts),
            'avg_image_count': sum(len(p['images']) for p in posts) / len(posts),
            'structure_patterns': self._aggregate_structures([p['structure'] for p in posts])
        }

        # 샘플 텍스트 추출 (처음 3개 포스트)
        sample_texts = []
        for post in posts[:3]:
            sample_texts.append({
                'title': post['title'],
                'content': post['content'][:500]  # 처음 500자만
            })

        # Gemini로 스타일 분석
        ai_analysis = self._analyze_with_gemini(sample_texts, summary)

        # 최종 결과 통합
        style_profile = {
            'blog_summary': summary,
            'ai_analysis': ai_analysis,
            'analyzed_at': datetime.now().isoformat()
        }

        return style_profile

    def _aggregate_structures(self, structures: List[Dict]) -> Dict:
        """구조 패턴 집계"""
        if not structures:
            return {}

        total = len(structures)
        aggregated = {
            'heading_usage': sum(s.get('has_heading', False) for s in structures) / total * 100,
            'bold_usage': sum(s.get('has_bold', False) for s in structures) / total * 100,
            'list_usage': sum(s.get('has_list', False) for s in structures) / total * 100,
            'avg_paragraph_count': sum(s.get('paragraph_count', 0) for s in structures) / total,
            'avg_image_count': sum(s.get('image_count', 0) for s in structures) / total,
            'common_text_align': self._most_common([s.get('text_align', 'left') for s in structures])
        }

        return aggregated

    def _most_common(self, items: List) -> str:
        """가장 많이 사용된 항목"""
        if not items:
            return ''
        return max(set(items), key=items.count)

    def _analyze_with_gemini(self, sample_texts: List[Dict], summary: Dict) -> Dict:
        """Gemini를 사용한 스타일 분석"""
        prompt = f"""다음은 네이버 블로그 포스트 샘플입니다. 이 블로그의 작성 스타일을 분석해주세요.

# 포스트 샘플
{json.dumps(sample_texts, ensure_ascii=False, indent=2)}

# 구조 통계
- 평균 본문 길이: {summary['avg_content_length']:.0f}자
- 평균 이미지 수: {summary['avg_image_count']:.1f}개
- 제목 사용률: {summary['structure_patterns'].get('heading_usage', 0):.0f}%
- 볼드 사용률: {summary['structure_patterns'].get('bold_usage', 0):.0f}%

다음 JSON 형식으로 분석 결과를 제공해주세요:

{{
  "tone": "어투 및 톤 (예: 친근한, 전문적인, 캐주얼한, 격식있는)",
  "sentence_style": "문장 스타일 (예: 짧고 간결, 길고 상세, 대화체, 설명체)",
  "paragraph_style": "문단 구성 (예: 짧은 문단 선호, 긴 문단, 한 문장씩 줄바꿈)",
  "emoji_usage": "이모지 사용 패턴 (예: 자주 사용, 가끔 사용, 사용 안함)",
  "formatting_preferences": ["자주 사용하는 포맷팅 스타일들"],
  "opening_style": "글 시작 스타일 (예: 인사말, 바로 본론, 질문으로 시작)",
  "closing_style": "글 마무리 스타일 (예: 질문으로 마무리, 감사인사, 해시태그)",
  "special_patterns": ["특이한 패턴이나 습관"],
  "keyword_patterns": ["자주 사용하는 단어나 표현"],
  "image_placement": "이미지 배치 패턴 (예: 중간중간 삽입, 문단마다, 상단 집중)",
  "overall_impression": "전체적인 느낌 한 문장 요약"
}}

반드시 유효한 JSON만 반환하세요."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # JSON 파싱
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]

            return json.loads(result_text.strip())

        except Exception as e:
            print(f"⚠️ Gemini 분석 실패: {e}")
            return {
                'tone': 'unknown',
                'sentence_style': 'unknown',
                'overall_impression': '분석 실패'
            }


def main():
    """테스트 실행"""
    from dotenv import load_dotenv
    load_dotenv()

    # 블로그 ID 목록
    blog_ids = [
        'chikkqueen',
        'chick_king',
        'chick_queen',
        '1234ssem'
    ]

    crawler = NaverBlogCrawler(headless=False)
    analyzer = BlogStyleAnalyzer(os.getenv('GEMINI_API_KEY'))

    try:
        for blog_id in blog_ids:
            # 크롤링
            posts = crawler.crawl_blog(blog_id, max_posts=5)

            if posts:
                # JSON 저장
                json_file = crawler.save_to_json(blog_id, posts)

                # 스타일 분석
                style_profile = analyzer.analyze_blog_style(posts)

                # 스타일 프로필 저장
                style_file = f"blog_style_{blog_id}.json"
                with open(style_file, 'w', encoding='utf-8') as f:
                    json.dump(style_profile, f, ensure_ascii=False, indent=2)

                print(f"✅ 스타일 프로필 저장: {style_file}")
                print(f"\n전체 인상: {style_profile['ai_analysis'].get('overall_impression', 'N/A')}")

            print("\n" + "="*60 + "\n")

    finally:
        crawler.close_driver()


if __name__ == "__main__":
    main()
