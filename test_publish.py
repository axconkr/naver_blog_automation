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
    print("=== 1. 네이버 로그인 ===")
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
    
    current_id = id_input.get_attribute('value')
    if not current_id:
        print("   클립보드 방식 실패, JavaScript 방식 시도...")
        driver.execute_script(f"arguments[0].value = '{NAVER_ID}';", id_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", id_input)
        time.sleep(0.5)
    print(f"   아이디 입력: {id_input.get_attribute('value')}")
    
    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    time.sleep(0.5)
    pyperclip.copy(NAVER_PW)
    pw_input.send_keys(PASTE_KEY, 'v')
    time.sleep(1)
    
    current_pw = pw_input.get_attribute('value')
    if not current_pw:
        print("   클립보드 방식 실패, JavaScript 방식 시도...")
        driver.execute_script(f"arguments[0].value = '{NAVER_PW}';", pw_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", pw_input)
        time.sleep(0.5)
    print(f"   비밀번호 입력 완료 (길이: {len(pw_input.get_attribute('value'))})")
    
    login_button = driver.find_element(By.ID, "log.login")
    login_button.click()
    time.sleep(3)
    
    current_url = driver.current_url
    if "nidlogin" not in current_url:
        print("   ✅ 로그인 성공!")
    else:
        print("   ❌ 로그인 실패 - 수동 확인 필요")
    
    print("\n=== 2. 블로그 글쓰기 페이지 이동 ===")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(3)
    
    print("\n=== 3. iframe 전환 ===")
    main_frame = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mainFrame"))
    )
    driver.switch_to.frame(main_frame)
    time.sleep(1)
    print("   iframe 전환 완료")
    
    print("\n=== 4. 팝업 닫기 ===")
    try:
        cancel_button = driver.find_element(By.CSS_SELECTOR, ".se-popup-button-cancel")
        cancel_button.click()
        print("   팝업 닫기 완료")
    except:
        print("   팝업 없음")
    time.sleep(0.5)
    
    print("\n=== 5. 제목 입력 ===")
    title_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
    )
    title_element.click()
    time.sleep(0.5)
    
    title_paragraph = driver.find_element(By.CSS_SELECTOR, ".se-section-documentTitle .se-text-paragraph")
    title_paragraph.click()
    time.sleep(0.3)
    
    test_title = "테스트 글 제목 - 자동화 테스트"
    pyperclip.copy(test_title)
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(1)
    print(f"   제목 입력: {test_title}")
    
    print("\n=== 6. 본문 입력 ===")
    content_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-text"))
    )
    content_element.click()
    time.sleep(0.5)
    
    text_paragraph = driver.find_element(By.CSS_SELECTOR, ".se-section-text .se-text-paragraph")
    text_paragraph.click()
    time.sleep(0.3)
    
    test_content = "이것은 자동화 테스트 본문입니다.\n\n테스트 중입니다."
    pyperclip.copy(test_content)
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(1)
    print("   본문 입력 완료")
    
    print("\n=== 7. 발행 버튼 클릭 (iframe 내부) ===")
    try:
        help_close = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
        help_close.click()
        print("   도움말 패널 닫기 완료")
        time.sleep(0.5)
    except:
        pass
    
    print("   발행 버튼 찾는 중...")
    publish_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".publish_btn__m9KHH"))
    )
    print(f"   발행 버튼 발견: {publish_button.text}")
    driver.execute_script("arguments[0].click();", publish_button)
    print("   발행 버튼 클릭 완료 (JS click)")
    time.sleep(3)
    
    print("\n=== 8. 발행 설정 레이어 확인 ===")
    print("   현재 HTML에서 발행 관련 요소 찾기...")
    
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        html = body.get_attribute('innerHTML')
        
        if 'publish_layer' in html or 'layer_publish' in html or 'confirm' in html.lower():
            print("   발행 레이어 감지됨!")
            
            import re
            layer_patterns = re.findall(r'class="[^"]*(?:publish|layer|confirm|btn)[^"]*"', html[:5000])
            for pattern in layer_patterns[:20]:
                print(f"     {pattern}")
        
        print("\n   HTML 일부 (처음 4000자):")
        print(html[:4000])
    except Exception as e:
        print(f"   HTML 가져오기 실패: {e}")
    
    print("\n=== 9. 발행 확인 버튼 클릭 시도 ===")
    confirm_selectors = [
        "button.confirm_btn__WEaBq",
        "button.publish_layer_btn__O4Vmk",
        ".publish_layer__d1wPv button",
        "button[data-click-area*='publish']",
        ".btn_confirm__OWmr0",
        "button.btn_ok__fFYRx",
    ]
    
    for selector in confirm_selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"   발견: {selector} -> text='{btn.text}'")
            btn.click()
            print(f"   클릭 완료!")
            break
        except:
            print(f"   없음: {selector}")
    
    time.sleep(5)
    print("\n발행 완료 여부 확인하세요. 10초 후 종료...")
    time.sleep(10)
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()
    input("Enter를 눌러 종료...")
finally:
    driver.quit()
