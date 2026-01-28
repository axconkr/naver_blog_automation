"""
워드 파일에서 이미지 추출 후 네이버 블로그 업로드 테스트
- pyautogui로 파일 다이얼로그 제어
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from docx import Document
from dotenv import load_dotenv
import pyautogui
import zipfile
import pyperclip
import platform
import tempfile
import time
import os

load_dotenv()

NAVER_ID = os.getenv("NAVER_ID")
NAVER_PW = os.getenv("NAVER_PW")
PASTE_KEY = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL

# pyautogui 설정
pyautogui.FAILSAFE = True  # 마우스를 화면 모서리로 이동하면 중지
pyautogui.PAUSE = 0.3  # 각 동작 사이 대기

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)


def extract_from_word(docx_path, temp_dir):
    """워드 파일에서 본문과 이미지 추출"""
    doc = Document(docx_path)
    content = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    
    image_paths = []
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            for i, name in enumerate(z.namelist()):
                if name.startswith('word/media/'):
                    ext = os.path.splitext(name)[1]
                    img_filename = f"img_{i}{ext}"
                    img_path = os.path.join(temp_dir, img_filename)
                    with z.open(name) as src, open(img_path, 'wb') as dst:
                        dst.write(src.read())
                    image_paths.append(img_path)
                    print(f"  추출된 이미지: {img_path}")
    except Exception as e:
        print(f"  이미지 추출 오류: {e}")
    
    return content, image_paths


def login():
    print("1. 네이버 로그인...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(3)
    
    try:
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
        time.sleep(4)
    except:
        pass
    
    # 로그인 확인
    current_url = driver.current_url
    if "nidlogin" in current_url:
        print("\n   ⚠️  자동 로그인 실패 - 수동 로그인 필요")
        input("   로그인 완료 후 Enter...")
    else:
        print("   자동 로그인 성공!")


def upload_image_with_dialog(image_path):
    """
    이미지 업로드 - pyautogui로 파일 다이얼로그 제어
    한글 경로 지원: 클립보드로 경로 붙여넣기
    """
    if not image_path or not os.path.exists(image_path):
        print(f"  - 이미지 파일 없음: {image_path}")
        return False
    
    abs_path = os.path.abspath(image_path)
    print(f"  이미지 업로드: {os.path.basename(image_path)}")
    print(f"    경로: {abs_path}")
    
    try:
        # 1. 이미지 버튼 클릭
        image_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-name='image']"))
        )
        driver.execute_script("arguments[0].click();", image_btn)
        print(f"    이미지 버튼 클릭")
        time.sleep(2)  # 파일 다이얼로그 열릴 때까지 대기
        
        # 2. macOS 파일 다이얼로그 제어 (클립보드 사용)
        if platform.system() == 'Darwin':
            # Cmd+Shift+G: "폴더로 이동" 열기
            pyautogui.hotkey('command', 'shift', 'g')
            time.sleep(1)
            
            # 클립보드에 경로 복사 후 붙여넣기
            pyperclip.copy(abs_path)
            pyautogui.hotkey('command', 'v')
            time.sleep(0.5)
            
            # Enter (이동)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Enter (열기)
            pyautogui.press('enter')
            time.sleep(3)
            
            print(f"    이미지 업로드 완료!")
            return True
        else:
            # Windows: 클립보드로 경로 붙여넣기
            pyperclip.copy(abs_path)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(3)
            return True
            
    except Exception as e:
        print(f"    업로드 실패: {e}")
        # ESC로 다이얼로그 닫기
        pyautogui.press('escape')
        time.sleep(0.5)
        return False


def test_upload():
    # 워드 파일에서 이미지 추출
    docx_path = "output/test_document_with_images.docx"
    temp_dir = tempfile.mkdtemp()
    
    print(f"\n2. 워드 파일에서 이미지 추출: {docx_path}")
    content, image_paths = extract_from_word(docx_path, temp_dir)
    print(f"   본문 길이: {len(content)}자")
    print(f"   이미지 수: {len(image_paths)}개")
    
    # 블로그 글쓰기 페이지 이동
    print("\n3. 블로그 글쓰기 페이지 이동...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(5)
    
    # iframe 전환
    print("4. iframe 전환...")
    main_frame = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "mainFrame"))
    )
    driver.switch_to.frame(main_frame)
    print("   mainFrame 전환 성공")
    time.sleep(3)
    
    # 팝업 닫기
    print("   팝업 닫기...")
    for selector in [".se-popup-button-cancel", ".se-help-panel-close-button"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            if el.is_displayed():
                driver.execute_script("arguments[0].click();", el)
                time.sleep(0.3)
        except:
            pass
    
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    
    # 제목 입력
    print("\n5. 제목 입력...")
    title_paragraph = driver.find_element(By.CSS_SELECTOR, ".se-section-documentTitle .se-text-paragraph")
    driver.execute_script("arguments[0].click();", title_paragraph)
    time.sleep(0.5)
    
    pyperclip.copy("테스트 글 - 워드 이미지 업로드")
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(1)
    print("   제목 입력 완료")
    
    # 본문 입력
    print("\n6. 본문 입력...")
    text_paragraph = driver.find_element(By.CSS_SELECTOR, ".se-section-text .se-text-paragraph")
    driver.execute_script("arguments[0].click();", text_paragraph)
    time.sleep(0.5)
    
    pyperclip.copy(content[:500] if content else "테스트 본문입니다.")
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(1)
    print("   본문 입력 완료")
    
    # 이미지 업로드 (pyautogui 사용)
    if image_paths:
        print("\n7. 이미지 업로드 (파일 다이얼로그 제어)...")
        print("   ⚠️  마우스/키보드를 건드리지 마세요!")
        time.sleep(2)
        
        for i, img_path in enumerate(image_paths):
            print(f"\n  [{i+1}/{len(image_paths)}]")
            success = upload_image_with_dialog(img_path)
            if not success:
                print(f"    실패 - 건너뜀")
            time.sleep(2)
    
    print("\n\n테스트 완료! 브라우저를 확인하세요.")
    print("브라우저를 닫으려면 Enter를 누르세요...")
    input()


try:
    login()
    test_upload()
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()
    input("Enter를 눌러 종료...")
finally:
    driver.quit()
