"""
네이버 스마트에디터 기능 및 이모지 확인

실제 네이버 블로그 에디터에서 사용 가능한 기능과 이모지를 확인합니다.
"""

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class NaverEditorInspector:
    """네이버 스마트에디터 기능 검사기"""

    def __init__(self, naver_id: str, naver_pw: str):
        self.naver_id = naver_id
        self.naver_pw = naver_pw
        self.driver = None

    def init_driver(self):
        """WebDriver 초기화"""
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=options)
        print("✅ WebDriver 초기화 완료")

    def login_naver(self):
        """네이버 로그인"""
        print("\n🔐 네이버 로그인 중...")
        self.driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)

        # ID 입력
        id_input = self.driver.find_element(By.ID, "id")
        id_input.send_keys(self.naver_id)

        # PW 입력
        pw_input = self.driver.find_element(By.ID, "pw")
        pw_input.send_keys(self.naver_pw)
        pw_input.send_keys(Keys.RETURN)

        time.sleep(3)
        print("✅ 로그인 완료")

    def open_blog_editor(self, blog_id: str):
        """블로그 글쓰기 페이지 열기"""
        print(f"\n📝 블로그 에디터 열기: {blog_id}")
        editor_url = f"https://blog.naver.com/{blog_id}/postwrite"
        self.driver.get(editor_url)
        time.sleep(5)

        # iframe으로 전환
        try:
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it("mainFrame")
            )
            print("  ✅ 에디터 iframe 전환 완료")
        except:
            print("  ℹ️ iframe 없이 직접 접근")

    def inspect_editor_features(self) -> dict:
        """에디터 기능 검사"""
        print("\n🔍 에디터 기능 검사 중...")

        features = {
            'toolbar_buttons': [],
            'available_emojis': [],
            'font_options': [],
            'color_options': [],
            'alignment_options': [],
            'special_features': []
        }

        try:
            # 툴바 버튼들 찾기
            toolbar = self.driver.find_element(By.CSS_SELECTOR, ".se-toolbar, .editor_toolbar")
            buttons = toolbar.find_elements(By.CSS_SELECTOR, "button, .btn")

            for btn in buttons:
                try:
                    title = btn.get_attribute('title') or btn.get_attribute('aria-label')
                    if title:
                        features['toolbar_buttons'].append(title)
                except:
                    continue

            print(f"  📌 툴바 버튼: {len(features['toolbar_buttons'])}개")

        except Exception as e:
            print(f"  ⚠️ 툴바 검사 실패: {e}")

        return features

    def inspect_emoji_panel(self) -> list:
        """이모지 패널 검사"""
        print("\n😊 이모지 검사 중...")

        emojis = []

        try:
            # 이모지 버튼 찾기 및 클릭
            emoji_selectors = [
                "button[aria-label*='이모티콘']",
                "button[title*='이모티콘']",
                ".emoji-button",
                ".emoticon-button"
            ]

            for selector in emoji_selectors:
                try:
                    emoji_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    emoji_btn.click()
                    time.sleep(2)
                    print("  ✅ 이모지 패널 열림")
                    break
                except:
                    continue

            # 이모지 목록 수집
            emoji_elements = self.driver.find_elements(By.CSS_SELECTOR, ".emoji-item, .emoticon-item, img[alt*='이모티콘']")

            for elem in emoji_elements[:100]:  # 최대 100개
                try:
                    emoji_data = {
                        'src': elem.get_attribute('src'),
                        'alt': elem.get_attribute('alt'),
                        'title': elem.get_attribute('title')
                    }
                    emojis.append(emoji_data)
                except:
                    continue

            print(f"  😊 발견된 이모지: {len(emojis)}개")

        except Exception as e:
            print(f"  ⚠️ 이모지 검사 실패: {e}")

        return emojis

    def get_editor_structure(self) -> dict:
        """에디터 HTML 구조 분석"""
        print("\n🏗️ 에디터 구조 분석 중...")

        structure = {
            'editor_type': 'unknown',
            'main_container': None,
            'toolbar_class': None,
            'content_area_class': None,
            'available_components': []
        }

        try:
            # 에디터 타입 확인
            if self.driver.find_elements(By.CSS_SELECTOR, ".se-component"):
                structure['editor_type'] = 'SmartEditor'
                structure['main_container'] = '.se-main-container'
                structure['content_area_class'] = '.se-component'
                print("  ✅ SmartEditor 확인")

            # 사용 가능한 컴포넌트
            component_types = ['text', 'image', 'video', 'link', 'divider', 'quote', 'table', 'file']
            for comp_type in component_types:
                selector = f".se-{comp_type}, [data-type='{comp_type}']"
                if self.driver.find_elements(By.CSS_SELECTOR, selector):
                    structure['available_components'].append(comp_type)

            print(f"  🧩 사용 가능 컴포넌트: {', '.join(structure['available_components'])}")

        except Exception as e:
            print(f"  ⚠️ 구조 분석 실패: {e}")

        return structure

    def capture_editor_screenshot(self, filename: str = "naver_editor_screenshot.png"):
        """에디터 스크린샷 캡처"""
        try:
            self.driver.save_screenshot(filename)
            print(f"\n📸 스크린샷 저장: {filename}")
        except Exception as e:
            print(f"⚠️ 스크린샷 실패: {e}")

    def full_inspection(self, blog_id: str) -> dict:
        """전체 검사 실행"""
        print("="*60)
        print("🔍 네이버 스마트에디터 전체 검사")
        print("="*60)

        self.init_driver()

        try:
            # 로그인
            self.login_naver()

            # 에디터 열기
            self.open_blog_editor(blog_id)

            # 기능 검사
            features = self.inspect_editor_features()

            # 이모지 검사
            emojis = self.inspect_emoji_panel()

            # 구조 분석
            structure = self.get_editor_structure()

            # 스크린샷
            self.capture_editor_screenshot()

            # 결과 통합
            result = {
                'blog_id': blog_id,
                'inspection_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'editor_features': features,
                'available_emojis': emojis,
                'editor_structure': structure
            }

            # JSON 저장
            with open('naver_editor_features.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print("\n💾 검사 결과 저장: naver_editor_features.json")

            return result

        finally:
            input("\n⏸️ 에디터를 직접 확인하세요. 완료 후 Enter를 누르세요...")
            self.driver.quit()


def main():
    """테스트 실행"""
    from dotenv import load_dotenv
    load_dotenv()

    naver_id = os.getenv('NAVER_ID')
    naver_pw = os.getenv('NAVER_PW')

    if not naver_id or not naver_pw:
        print("❌ .env 파일에 NAVER_ID와 NAVER_PW를 설정해주세요")
        return

    inspector = NaverEditorInspector(naver_id, naver_pw)

    # chikkqueen 블로그로 검사
    result = inspector.full_inspection('chikkqueen')

    print("\n" + "="*60)
    print("✅ 검사 완료!")
    print("="*60)
    print(f"툴바 버튼: {len(result['editor_features']['toolbar_buttons'])}개")
    print(f"이모지: {len(result['available_emojis'])}개")
    print(f"에디터 타입: {result['editor_structure']['editor_type']}")
    print(f"사용 가능 컴포넌트: {', '.join(result['editor_structure']['available_components'])}")


if __name__ == "__main__":
    main()
