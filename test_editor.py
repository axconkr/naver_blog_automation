from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import pyperclip
import platform
import time
import os

load_dotenv()

NAVER_ID = os.getenv("NAVER_ID")
NAVER_PW = os.getenv("NAVER_PW")
PASTE_KEY = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

try:
    print("1. 네이버 로그인...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(3)
    
    id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id"))
    )
    id_input.click()
    time.sleep(0.5)
    pyperclip.copy(NAVER_ID)
    id_input.send_keys(PASTE_KEY, 'v')
    time.sleep(1)
    
    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    time.sleep(0.5)
    pyperclip.copy(NAVER_PW)
    pw_input.send_keys(PASTE_KEY, 'v')
    time.sleep(1)
    
    login_button = driver.find_element(By.ID, "log.login")
    login_button.click()
    time.sleep(3)
    
    print("2. 블로그 글쓰기 페이지 이동...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(3)
    
    print("3. iframe 전환 시도...")
    try:
        main_frame = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mainFrame"))
        )
        driver.switch_to.frame(main_frame)
        print("   ✅ mainFrame으로 전환 성공")
    except Exception as e:
        print(f"   ❌ mainFrame 전환 실패: {e}")
        
        print("   다른 iframe 찾기 시도...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   발견된 iframe 수: {len(iframes)}")
        for i, iframe in enumerate(iframes):
            print(f"   iframe[{i}]: id='{iframe.get_attribute('id')}', name='{iframe.get_attribute('name')}'")
    
    time.sleep(2)
    
    print("\n4. 페이지 내 주요 요소 탐색...")
    
    selectors_to_test = [
        (".se-section-documentTitle", "제목 영역 (구버전)"),
        (".se-section-text", "본문 영역 (구버전)"),
        (".save_btn__bzc5B", "저장 버튼 (구버전)"),
        ("[class*='title']", "제목 관련 요소"),
        ("[class*='editor']", "에디터 관련 요소"),
        ("[class*='content']", "콘텐츠 관련 요소"),
        ("[class*='save']", "저장 관련 요소"),
        ("[class*='publish']", "발행 관련 요소"),
        (".se-component", "SE 컴포넌트"),
        (".se-text-paragraph", "SE 텍스트 단락"),
    ]
    
    for selector, description in selectors_to_test:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ {description}: {len(elements)}개 발견")
                for i, el in enumerate(elements[:3]):
                    class_name = el.get_attribute('class')[:50] if el.get_attribute('class') else 'N/A'
                    print(f"      [{i}] class: {class_name}...")
            else:
                print(f"   ❌ {description}: 없음")
        except Exception as e:
            print(f"   ❌ {description}: 에러 - {e}")
    
    print("\n5. 전체 HTML 구조 일부 출력...")
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        html_content = body.get_attribute('innerHTML')[:2000]
        print(html_content)
    except Exception as e:
        print(f"   HTML 가져오기 실패: {e}")
    
    print("\n\n브라우저를 닫으려면 Enter를 누르세요...")
    input()
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()
    input("Enter를 눌러 종료...")
finally:
    driver.quit()
