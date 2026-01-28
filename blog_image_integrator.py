"""
블로그 작성 시 이미지 자동 삽입 통합 모듈

구글 드라이브 이미지 인덱스를 활용해서
네이버 블로그 작성 시 문맥에 맞는 이미지를 자동으로 추천하고 삽입합니다.
"""

import os
from typing import List, Dict, Optional
from gdrive_image_indexer import GDriveImageIndexer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class BlogImageIntegrator:
    """블로그 이미지 통합 관리자"""

    def __init__(self, gemini_api_key: str, index_file: str = "image_index.json"):
        """
        Args:
            gemini_api_key: Gemini API 키
            index_file: 이미지 인덱스 파일 경로
        """
        self.indexer = GDriveImageIndexer(gemini_api_key)
        self.index_file = index_file
        self.index_data = None

    def load_index(self):
        """이미지 인덱스 로드"""
        self.index_data = self.indexer.load_index(self.index_file)

        if not self.index_data:
            raise Exception(f"인덱스 파일을 찾을 수 없습니다: {self.index_file}")

        print(f"✅ 이미지 인덱스 로드 완료: {len(self.index_data.get('images', []))}개 이미지")

    def suggest_images_for_text(self, text: str, top_k: int = 3) -> List[Dict]:
        """
        텍스트 내용을 분석해서 적합한 이미지 추천

        Args:
            text: 블로그 본문 텍스트
            top_k: 추천할 이미지 개수

        Returns:
            추천 이미지 목록
        """
        if not self.index_data:
            self.load_index()

        # 키워드 추출 (간단한 방법)
        # TODO: 향후 NLP 기반 키워드 추출로 개선
        keywords = self._extract_keywords(text)

        # 각 키워드로 이미지 검색
        all_matches = []
        for keyword in keywords:
            matches = self.indexer.search_images_by_context(keyword, top_k=10)
            all_matches.extend(matches)

        # 중복 제거 및 점수 합산
        image_scores = {}
        for match in all_matches:
            img_id = match['id']
            if img_id not in image_scores:
                image_scores[img_id] = {
                    'image': match,
                    'score': 0
                }
            image_scores[img_id]['score'] += match.get('relevance_score', 0)

        # 점수 기준 정렬
        sorted_images = sorted(
            image_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        return [item['image'] for item in sorted_images[:top_k]]

    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출 (간단한 방법)"""
        # 간단한 명사 추출 (향후 개선 필요)
        # 여기서는 공백으로 분리하고 2글자 이상만 사용
        words = text.split()
        keywords = [word for word in words if len(word) >= 2]

        # 상위 10개만 반환
        return keywords[:10]

    def analyze_blog_content_and_suggest(self, blog_text: str) -> Dict:
        """
        블로그 내용 전체를 분석하고 섹션별로 이미지 추천

        Args:
            blog_text: 블로그 전체 텍스트

        Returns:
            섹션별 이미지 추천 결과
        """
        # 간단한 섹션 분리 (문단 기준)
        sections = blog_text.split('\n\n')

        suggestions = {
            'total_sections': len(sections),
            'suggestions': []
        }

        for i, section in enumerate(sections):
            if len(section.strip()) < 20:  # 너무 짧은 섹션은 건너뛰기
                continue

            recommended_images = self.suggest_images_for_text(section, top_k=2)

            suggestions['suggestions'].append({
                'section_index': i,
                'section_text': section[:100] + '...',  # 미리보기
                'recommended_images': recommended_images
            })

        return suggestions

    def insert_image_to_naver_blog(self, driver: webdriver, image_url: str, position: str = "end"):
        """
        네이버 블로그 에디터에 이미지 삽입

        Args:
            driver: Selenium WebDriver
            image_url: 삽입할 이미지 URL
            position: 삽입 위치 (start, end, cursor)
        """
        try:
            # 이미지 업로드 버튼 클릭
            wait = WebDriverWait(driver, 10)

            # 스마트에디터 iframe으로 전환
            driver.switch_to.frame("mainFrame")

            # 이미지 삽입 버튼 찾기
            image_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.se-image-toolbar-button"))
            )
            image_btn.click()

            time.sleep(1)

            # URL로 이미지 추가 탭 선택
            url_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'URL')]"))
            )
            url_tab.click()

            # URL 입력
            url_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']"))
            )
            url_input.clear()
            url_input.send_keys(image_url)

            # 추가 버튼 클릭
            add_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '추가')]"))
            )
            add_btn.click()

            time.sleep(1)

            # iframe에서 나오기
            driver.switch_to.default_content()

            print(f"✅ 이미지 삽입 완료: {image_url}")

        except Exception as e:
            print(f"⚠️ 이미지 삽입 실패: {e}")
            driver.switch_to.default_content()

    def get_image_summary(self, image_data: Dict) -> str:
        """이미지 정보 요약"""
        return f"""
📸 {image_data.get('filename', 'Unknown')}
   설명: {image_data.get('description', 'N/A')}
   태그: {', '.join(image_data.get('tags', [])[:5])}
   분위기: {image_data.get('mood', 'N/A')}
   카테고리: {image_data.get('category', 'N/A')}
   링크: {image_data.get('web_view_link', 'N/A')}
        """.strip()


def main():
    """테스트 실행"""
    from dotenv import load_dotenv
    load_dotenv()

    gemini_api_key = os.getenv('GEMINI_API_KEY')

    integrator = BlogImageIntegrator(gemini_api_key)
    integrator.load_index()

    # 샘플 블로그 텍스트
    sample_text = """
    오늘은 맛있는 음식을 먹으러 갔습니다.

    특히 파스타가 정말 맛있었어요. 크림 소스가 일품이었습니다.
    분위기도 좋고 서비스도 친절했습니다.

    다음에는 피자도 먹어보고 싶네요.
    여러분도 꼭 가보세요!
    """

    print("🔍 블로그 내용 분석 및 이미지 추천")
    print("="*60)

    suggestions = integrator.analyze_blog_content_and_suggest(sample_text)

    print(f"\n총 {suggestions['total_sections']}개 섹션 분석")

    for suggestion in suggestions['suggestions']:
        print(f"\n📝 섹션 {suggestion['section_index'] + 1}:")
        print(f"   내용: {suggestion['section_text']}")
        print(f"\n   추천 이미지:")

        for img in suggestion['recommended_images']:
            print(integrator.get_image_summary(img))
            print()


if __name__ == "__main__":
    main()
