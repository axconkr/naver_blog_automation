"""
네이버 블로그 포스트 상세 분석기

각 블로그의 카테고리, 최근 포스트를 분석하고
실제 포스팅된 글의 편집 스타일을 파악합니다.
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


class BlogPostAnalyzer:
    """네이버 블로그 포스트 분석기"""

    def __init__(self, gemini_api_key: str, headless: bool = False):
        """
        Args:
            gemini_api_key: Gemini API 키
            headless: 헤드리스 모드 실행 여부
        """
        self.gemini_api_key = gemini_api_key
        self.headless = headless
        self.driver = None

        # Gemini 설정
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def init_driver(self):
        """WebDriver 초기화"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(options=options)
        print("✅ WebDriver 초기화 완료")

    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver 종료")

    def get_blog_categories(self, blog_id: str) -> List[Dict]:
        """블로그 카테고리 목록 가져오기"""
        if not self.driver:
            self.init_driver()

        blog_url = f"https://blog.naver.com/{blog_id}"
        self.driver.get(blog_url)
        time.sleep(3)

        categories = []

        try:
            # iframe으로 전환
            self.driver.switch_to.frame("mainFrame")
            time.sleep(2)

            # 카테고리 찾기 (여러 선택자 시도)
            selectors = [
                "div.category_title",
                "a.category_item",
                "div.cate_item",
                "ul.cate_list a",
                "div.category_box a"
            ]

            for selector in selectors:
                try:
                    category_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if category_elements:
                        for elem in category_elements[:20]:  # 최대 20개
                            try:
                                name = elem.text.strip()
                                url = elem.get_attribute('href')
                                if name and len(name) > 0:
                                    categories.append({
                                        'name': name,
                                        'url': url
                                    })
                            except:
                                continue
                        if categories:
                            break
                except:
                    continue

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"⚠️ 카테고리 수집 중 오류: {e}")
            self.driver.switch_to.default_content()

        print(f"📂 {len(categories)}개의 카테고리 발견")
        return categories

    def get_recent_post_urls(self, blog_id: str, max_posts: int = 3) -> List[str]:
        """최근 포스트 URL 가져오기"""
        if not self.driver:
            self.init_driver()

        # 블로그 메인 페이지
        blog_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}"
        self.driver.get(blog_url)
        time.sleep(3)

        post_urls = []

        try:
            # iframe으로 전환
            self.driver.switch_to.frame("mainFrame")
            time.sleep(2)

            # 여러 선택자 시도
            selectors = [
                "a.link_title",
                "a.pcol1",
                "div.post_title a",
                "div.post-item a",
                "div.blog_list a.tit"
            ]

            for selector in selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        for link in links[:max_posts]:
                            url = link.get_attribute('href')
                            if url and 'PostView' in url:
                                post_urls.append(url)
                        if post_urls:
                            break
                except:
                    continue

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"⚠️ 포스트 URL 수집 중 오류: {e}")
            self.driver.switch_to.default_content()

        # URL 중복 제거
        post_urls = list(set(post_urls))[:max_posts]

        print(f"📝 {len(post_urls)}개의 포스트 URL 수집됨")
        return post_urls

    def analyze_post_style(self, post_url: str) -> Dict:
        """포스트의 편집 스타일 상세 분석"""
        if not self.driver:
            self.init_driver()

        self.driver.get(post_url)
        time.sleep(3)

        style_data = {
            'url': post_url,
            'title': '',
            'content_preview': '',
            'html_structure': {},
            'style_features': {},
            'analyzed_at': datetime.now().isoformat()
        }

        try:
            # iframe으로 전환
            self.driver.switch_to.frame("mainFrame")
            time.sleep(2)

            # 제목
            try:
                title_elem = self.driver.find_element(By.CSS_SELECTOR, "div.se-title-text, h3.se_textarea")
                style_data['title'] = title_elem.text
            except:
                pass

            # 본문 컨테이너
            try:
                content_container = self.driver.find_element(By.CSS_SELECTOR, "div.se-main-container, div.se_component_wrap")

                # 전체 HTML
                style_data['raw_html'] = content_container.get_attribute('innerHTML')[:5000]  # 처음 5000자

                # 본문 텍스트
                style_data['content_preview'] = content_container.text[:500]

                # HTML 구조 분석
                style_data['html_structure'] = self._analyze_html_structure(content_container)

                # 스타일 특징 분석
                style_data['style_features'] = self._analyze_style_features(content_container)

            except Exception as e:
                print(f"⚠️ 본문 분석 중 오류: {e}")

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"⚠️ 포스트 분석 중 오류: {e}")
            self.driver.switch_to.default_content()

        return style_data

    def _analyze_html_structure(self, container) -> Dict:
        """HTML 구조 분석"""
        structure = {
            'total_components': 0,
            'text_components': 0,
            'image_components': 0,
            'video_components': 0,
            'link_components': 0,
            'table_components': 0,
            'divider_components': 0,
            'quote_components': 0
        }

        try:
            # 스마트에디터 컴포넌트 분석
            components = container.find_elements(By.CSS_SELECTOR, "[class*='se-component']")
            structure['total_components'] = len(components)

            for comp in components:
                class_name = comp.get_attribute('class')

                if 'se-text' in class_name:
                    structure['text_components'] += 1
                elif 'se-image' in class_name:
                    structure['image_components'] += 1
                elif 'se-video' in class_name:
                    structure['video_components'] += 1
                elif 'se-link' in class_name:
                    structure['link_components'] += 1
                elif 'se-table' in class_name:
                    structure['table_components'] += 1
                elif 'se-divider' in class_name:
                    structure['divider_components'] += 1
                elif 'se-quote' in class_name:
                    structure['quote_components'] += 1

        except Exception as e:
            print(f"⚠️ HTML 구조 분석 중 오류: {e}")

        return structure

    def _analyze_style_features(self, container) -> Dict:
        """스타일 특징 분석"""
        features = {
            'font_sizes': [],
            'font_colors': [],
            'bg_colors': [],
            'text_aligns': [],
            'has_bold': False,
            'has_italic': False,
            'has_underline': False,
            'has_strikethrough': False,
            'line_heights': [],
            'letter_spacings': []
        }

        try:
            # 텍스트 요소들 분석
            text_elements = container.find_elements(By.CSS_SELECTOR, "[class*='se-text'], p, span, div")

            for elem in text_elements[:50]:  # 처음 50개만
                try:
                    # 폰트 크기
                    font_size = elem.value_of_css_property('font-size')
                    if font_size and font_size not in features['font_sizes']:
                        features['font_sizes'].append(font_size)

                    # 폰트 색상
                    color = elem.value_of_css_property('color')
                    if color and color not in features['font_colors']:
                        features['font_colors'].append(color)

                    # 배경색
                    bg_color = elem.value_of_css_property('background-color')
                    if bg_color and bg_color not in features['bg_colors']:
                        features['bg_colors'].append(bg_color)

                    # 정렬
                    text_align = elem.value_of_css_property('text-align')
                    if text_align and text_align not in features['text_aligns']:
                        features['text_aligns'].append(text_align)

                    # 볼드
                    font_weight = elem.value_of_css_property('font-weight')
                    if font_weight and int(font_weight) >= 700:
                        features['has_bold'] = True

                    # 이탤릭
                    font_style = elem.value_of_css_property('font-style')
                    if font_style == 'italic':
                        features['has_italic'] = True

                    # 밑줄
                    text_decoration = elem.value_of_css_property('text-decoration')
                    if 'underline' in text_decoration:
                        features['has_underline'] = True
                    if 'line-through' in text_decoration:
                        features['has_strikethrough'] = True

                    # 줄간격
                    line_height = elem.value_of_css_property('line-height')
                    if line_height and line_height not in features['line_heights']:
                        features['line_heights'].append(line_height)

                    # 자간
                    letter_spacing = elem.value_of_css_property('letter-spacing')
                    if letter_spacing and letter_spacing not in features['letter_spacings']:
                        features['letter_spacings'].append(letter_spacing)

                except:
                    continue

        except Exception as e:
            print(f"⚠️ 스타일 특징 분석 중 오류: {e}")

        return features

    def analyze_blog_comprehensive(self, blog_id: str, max_posts: int = 3) -> Dict:
        """블로그 종합 분석"""
        print(f"\n{'='*60}")
        print(f"🔍 블로그 종합 분석: {blog_id}")
        print(f"{'='*60}\n")

        analysis = {
            'blog_id': blog_id,
            'blog_url': f"https://blog.naver.com/{blog_id}",
            'categories': [],
            'posts': [],
            'style_summary': {},
            'analyzed_at': datetime.now().isoformat()
        }

        # 1. 카테고리 분석
        print("📂 카테고리 수집 중...")
        analysis['categories'] = self.get_blog_categories(blog_id)

        for cat in analysis['categories'][:10]:
            print(f"   - {cat['name']}")

        # 2. 최근 포스트 URL 수집
        print(f"\n📝 최근 {max_posts}개 포스트 수집 중...")
        post_urls = self.get_recent_post_urls(blog_id, max_posts)

        # 3. 각 포스트 상세 분석
        for i, url in enumerate(post_urls, 1):
            print(f"\n[{i}/{len(post_urls)}] 포스트 분석 중...")
            print(f"   URL: {url}")

            post_style = self.analyze_post_style(url)

            if post_style['title']:
                print(f"   제목: {post_style['title'][:50]}...")
                print(f"   컴포넌트: {post_style['html_structure'].get('total_components', 0)}개")
                print(f"   텍스트: {post_style['html_structure'].get('text_components', 0)}개")
                print(f"   이미지: {post_style['html_structure'].get('image_components', 0)}개")

                analysis['posts'].append(post_style)

            time.sleep(2)

        # 4. 스타일 요약 생성
        if analysis['posts']:
            analysis['style_summary'] = self._generate_style_summary(analysis['posts'])

        return analysis

    def _generate_style_summary(self, posts: List[Dict]) -> Dict:
        """포스트들의 스타일 요약"""
        summary = {
            'avg_components': 0,
            'common_font_sizes': [],
            'common_colors': [],
            'common_alignment': '',
            'uses_bold': False,
            'uses_images': False,
            'uses_dividers': False
        }

        if not posts:
            return summary

        # 평균 컴포넌트 수
        total_comps = sum(p['html_structure'].get('total_components', 0) for p in posts)
        summary['avg_components'] = total_comps / len(posts)

        # 이미지 사용 여부
        summary['uses_images'] = any(p['html_structure'].get('image_components', 0) > 0 for p in posts)

        # 볼드 사용 여부
        summary['uses_bold'] = any(p['style_features'].get('has_bold', False) for p in posts)

        # 구분선 사용 여부
        summary['uses_dividers'] = any(p['html_structure'].get('divider_components', 0) > 0 for p in posts)

        # 공통 폰트 크기
        all_font_sizes = []
        for post in posts:
            all_font_sizes.extend(post['style_features'].get('font_sizes', []))
        summary['common_font_sizes'] = list(set(all_font_sizes))[:5]

        # 공통 색상
        all_colors = []
        for post in posts:
            all_colors.extend(post['style_features'].get('font_colors', []))
        summary['common_colors'] = list(set(all_colors))[:5]

        return summary

    def save_analysis(self, analysis: Dict, filename: str = None):
        """분석 결과 저장"""
        if not filename:
            filename = f"blog_analysis_{analysis['blog_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        print(f"\n💾 분석 결과 저장: {filename}")
        return filename


def main():
    """테스트 실행"""
    from dotenv import load_dotenv
    load_dotenv()

    gemini_api_key = os.getenv('GEMINI_API_KEY')

    blog_ids = [
        'chikkqueen',
        'chick_king',
        'chick_queen',
        '1234ssem'
    ]

    analyzer = BlogPostAnalyzer(gemini_api_key, headless=False)

    try:
        for blog_id in blog_ids:
            # 종합 분석
            analysis = analyzer.analyze_blog_comprehensive(blog_id, max_posts=3)

            # 저장
            analyzer.save_analysis(analysis)

            # 요약 출력
            print(f"\n{'='*60}")
            print(f"📊 {blog_id} 분석 요약")
            print(f"{'='*60}")
            print(f"카테고리: {len(analysis['categories'])}개")
            print(f"분석한 포스트: {len(analysis['posts'])}개")
            print(f"평균 컴포넌트 수: {analysis['style_summary'].get('avg_components', 0):.1f}개")
            print(f"이미지 사용: {'예' if analysis['style_summary'].get('uses_images') else '아니오'}")
            print(f"볼드 사용: {'예' if analysis['style_summary'].get('uses_bold') else '아니오'}")
            print(f"\n")

            time.sleep(5)

    finally:
        analyzer.close_driver()


if __name__ == "__main__":
    main()
