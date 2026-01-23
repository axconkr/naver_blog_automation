from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import pyperclip
import platform
import time
import os

load_dotenv()

NAVER_ID = os.getenv("NAVER_ID")
NAVER_PW = os.getenv("NAVER_PW")

print(f"NAVER_ID: {NAVER_ID}")
print(f"NAVER_PW: {'*' * len(NAVER_PW) if NAVER_PW else 'NOT SET'}")

PASTE_KEY = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL
print(f"Platform: {platform.system()}, PASTE_KEY: {'Command' if platform.system() == 'Darwin' else 'Control'}")

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

try:
    print("\n1. 네이버 로그인 페이지 접속...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(3)
    
    print("2. 아이디 입력 필드 찾기...")
    id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id"))
    )
    
    print("3. 아이디 입력 시도 (방법 1: pyperclip + paste)...")
    id_input.click()
    time.sleep(0.5)
    pyperclip.copy(NAVER_ID)
    id_input.send_keys(PASTE_KEY, 'v')
    time.sleep(1)
    
    current_id = id_input.get_attribute('value')
    print(f"   입력된 아이디: '{current_id}'")
    
    if not current_id:
        print("   방법 1 실패. 방법 2 시도 (JavaScript)...")
        driver.execute_script(f"arguments[0].value = '{NAVER_ID}';", id_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", id_input)
        time.sleep(0.5)
        current_id = id_input.get_attribute('value')
        print(f"   JavaScript로 입력된 아이디: '{current_id}'")
    
    print("4. 비밀번호 입력 필드 찾기...")
    pw_input = driver.find_element(By.ID, "pw")
    
    print("5. 비밀번호 입력 시도...")
    pw_input.click()
    time.sleep(0.5)
    pyperclip.copy(NAVER_PW)
    pw_input.send_keys(PASTE_KEY, 'v')
    time.sleep(1)
    
    current_pw = pw_input.get_attribute('value')
    print(f"   입력된 비밀번호 길이: {len(current_pw) if current_pw else 0}")
    
    if not current_pw:
        print("   방법 1 실패. 방법 2 시도 (JavaScript)...")
        driver.execute_script(f"arguments[0].value = '{NAVER_PW}';", pw_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", pw_input)
        time.sleep(0.5)
        current_pw = pw_input.get_attribute('value')
        print(f"   JavaScript로 입력된 비밀번호 길이: {len(current_pw) if current_pw else 0}")
    
    print("\n6. 로그인 버튼 클릭...")
    login_button = driver.find_element(By.ID, "log.login")
    login_button.click()
    
    print("7. 로그인 처리 대기 (3초)...")
    time.sleep(3)
    
    current_url = driver.current_url
    print(f"8. 현재 URL: {current_url}")
    
    if "nidlogin" not in current_url:
        print("   ✅ 로그인 성공!")
    else:
        print("   ❌ 로그인 실패 (여전히 로그인 페이지)")
    
    print("\n9. 블로그 글쓰기 페이지 이동 테스트...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(3)
    
    current_url = driver.current_url
    print(f"   현재 URL: {current_url}")
    
    print("\n테스트 완료. 브라우저를 닫으려면 Enter를 누르세요...")
    input()
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()
    input("Enter를 눌러 종료...")
finally:
    driver.quit()
