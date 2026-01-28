"""
네이버 블로그 에디터에서 이미지 업로드 요소 분석 스크립트
"""
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

def login():
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
    print("   로그인 완료")

def analyze_image_upload_elements():
    print("\n2. 블로그 글쓰기 페이지 이동...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(3)
    
    print("3. iframe 전환...")
    main_frame = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mainFrame"))
    )
    driver.switch_to.frame(main_frame)
    time.sleep(2)
    
    # 팝업 닫기
    try:
        cancel_button = driver.find_element(By.CSS_SELECTOR, ".se-popup-button-cancel")
        cancel_button.click()
        print("   팝업 취소 버튼 클릭")
        time.sleep(0.5)
    except:
        pass
    
    try:
        close_button = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
        close_button.click()
        print("   도움말 패널 닫기")
        time.sleep(0.5)
    except:
        pass
    
    print("\n4. 이미지 업로드 관련 요소 분석...")
    
    # 툴바 관련 selector 테스트
    toolbar_selectors = [
        # 이미지 버튼 관련
        ("button.se-image-toolbar-button", "이미지 툴바 버튼"),
        ("button[data-name='image']", "data-name='image' 버튼"),
        (".se-toolbar-item-image", "이미지 툴바 아이템"),
        (".se-toolbar button[data-log='image']", "data-log='image' 버튼"),
        
        # 일반 툴바
        (".se-toolbar", "SE 툴바"),
        (".se-toolbar-item", "SE 툴바 아이템"),
        (".se-toolbar button", "SE 툴바 버튼 전체"),
        
        # 사진 관련
        ("button.se-photo-toolbar-button", "사진 툴바 버튼"),
        ("[data-name='photo']", "data-name='photo'"),
        
        # 파일 입력
        ("input[type='file']", "파일 입력 (모든)"),
        ("input[type='file'][accept*='image']", "이미지 파일 입력"),
        
        # 기타 이미지 관련
        (".se-image-uploader", "이미지 업로더"),
        (".se-component-image", "이미지 컴포넌트"),
        ("[class*='image']", "image 포함 클래스"),
        ("[class*='photo']", "photo 포함 클래스"),
        ("[class*='upload']", "upload 포함 클래스"),
    ]
    
    for selector, description in toolbar_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ {description}: {len(elements)}개")
                for i, el in enumerate(elements[:5]):
                    tag = el.tag_name
                    class_name = el.get_attribute('class') or 'N/A'
                    data_name = el.get_attribute('data-name') or ''
                    text = el.text[:30] if el.text else ''
                    visible = el.is_displayed()
                    print(f"      [{i}] <{tag}> class='{class_name[:60]}' data-name='{data_name}' text='{text}' visible={visible}")
            else:
                print(f"   ❌ {description}: 없음")
        except Exception as e:
            print(f"   ❌ {description}: 에러 - {str(e)[:50]}")
    
    print("\n5. 모든 버튼 요소 확인...")
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, ".se-toolbar button")
        print(f"   툴바 내 버튼 수: {len(buttons)}")
        for i, btn in enumerate(buttons):
            class_name = btn.get_attribute('class') or ''
            data_name = btn.get_attribute('data-name') or ''
            data_log = btn.get_attribute('data-log') or ''
            aria_label = btn.get_attribute('aria-label') or ''
            print(f"   [{i}] class='{class_name[:50]}' data-name='{data_name}' data-log='{data_log}' aria-label='{aria_label}'")
    except Exception as e:
        print(f"   버튼 분석 실패: {e}")
    
    print("\n6. 이미지 버튼 클릭 시도...")
    
    # 여러 방법으로 이미지 버튼 찾기 시도
    image_btn = None
    
    try:
        # 방법 1: data-name='image'
        image_btn = driver.find_element(By.CSS_SELECTOR, "button[data-name='image']")
        print("   방법1: data-name='image' 버튼 발견!")
    except:
        pass
    
    if not image_btn:
        try:
            # 방법 2: se-image 클래스
            image_btn = driver.find_element(By.CSS_SELECTOR, "button[class*='image']")
            print("   방법2: class에 'image' 포함 버튼 발견!")
        except:
            pass
    
    if not image_btn:
        try:
            # 방법 3: aria-label로 찾기
            buttons = driver.find_elements(By.CSS_SELECTOR, ".se-toolbar button")
            for btn in buttons:
                aria = btn.get_attribute('aria-label') or ''
                if '이미지' in aria or 'image' in aria.lower() or '사진' in aria:
                    image_btn = btn
                    print(f"   방법3: aria-label='{aria}' 버튼 발견!")
                    break
        except:
            pass
    
    if image_btn:
        print("   이미지 버튼 클릭 시도...")
        driver.execute_script("arguments[0].click();", image_btn)
        time.sleep(2)
        
        print("\n7. 이미지 버튼 클릭 후 파일 입력 요소 확인...")
        try:
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            print(f"   파일 입력 요소 수: {len(file_inputs)}")
            for i, fi in enumerate(file_inputs):
                accept = fi.get_attribute('accept') or ''
                name = fi.get_attribute('name') or ''
                visible = fi.is_displayed()
                print(f"   [{i}] accept='{accept}' name='{name}' visible={visible}")
        except Exception as e:
            print(f"   파일 입력 분석 실패: {e}")
        
        # 레이어/팝업 확인
        print("\n8. 이미지 업로드 레이어/팝업 확인...")
        layer_selectors = [
            (".se-image-selection-layer", "이미지 선택 레이어"),
            (".se-layer", "SE 레이어"),
            (".se-popup", "SE 팝업"),
            ("[class*='layer']", "layer 포함 클래스"),
            ("[class*='popup']", "popup 포함 클래스"),
            ("[class*='modal']", "modal 포함 클래스"),
            (".se-image-uploader-layer", "이미지 업로더 레이어"),
        ]
        
        for selector, description in layer_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ {description}: {len(elements)}개")
                    for i, el in enumerate(elements[:3]):
                        class_name = el.get_attribute('class') or ''
                        visible = el.is_displayed()
                        print(f"      [{i}] class='{class_name[:60]}' visible={visible}")
            except:
                pass
    else:
        print("   ❌ 이미지 버튼을 찾지 못함")
    
    print("\n\n분석 완료. 브라우저를 닫으려면 Enter를 누르세요...")
    input()

try:
    login()
    analyze_image_upload_elements()
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()
    input("Enter를 눌러 종료...")
finally:
    driver.quit()
