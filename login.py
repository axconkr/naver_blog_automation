from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import pyperclip
import platform
import time
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# 네이버 계정 정보 (.env 파일에서 읽어오기)
NAVER_ID = os.getenv("NAVER_ID")
NAVER_PW = os.getenv("NAVER_PW")

# 계정 정보 확인
if not NAVER_ID or not NAVER_PW:
    raise ValueError(".env 파일에서 NAVER_ID 또는 NAVER_PW를 찾을 수 없습니다.")

# OS에 따른 붙여넣기 키 설정 (Mac: Command, Windows/Linux: Control)
PASTE_KEY = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL

# Chrome 옵션 설정
chrome_options = Options()
# 필요시 headless 모드 해제 (브라우저 창을 보려면 주석 처리)
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# WebDriver 초기화
driver = webdriver.Chrome(options=chrome_options)

try:
    # 네이버 로그인 페이지 접속
    print("네이버 로그인 페이지 접속 중...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)  # 페이지 로딩 대기
    
    # 아이디 입력 필드 찾기 및 클릭
    print("아이디 입력 중...")
    id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id"))
    )
    id_input.click()
    time.sleep(0.5)
    
    # 클립보드에 아이디 복사 후 붙여넣기
    pyperclip.copy(NAVER_ID)
    id_input.send_keys(PASTE_KEY, 'v')
    time.sleep(0.5)
    
    # 비밀번호 입력 필드 찾기 및 클릭
    print("비밀번호 입력 중...")
    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    time.sleep(0.5)
    
    # 클립보드에 비밀번호 복사 후 붙여넣기
    pyperclip.copy(NAVER_PW)
    pw_input.send_keys(PASTE_KEY, 'v')
    time.sleep(0.5)
    
    # 로그인 버튼 클릭
    print("로그인 버튼 클릭 중...")
    login_button = driver.find_element(By.ID, "log.login")
    login_button.click()
    
    # 로그인 후 2초 대기
    print("로그인 처리 중... (2초 대기)")
    time.sleep(2)
    
    # 블로그 글쓰기 페이지로 이동
    print("블로그 글쓰기 페이지로 이동 중...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(2)
    
    print("로그인 완료 및 블로그 글쓰기 페이지 접속 완료!")
    
    # ===== 글쓰기 페이지 입력 및 제어 로직 =====
    
    # 1. iframe 전환 (#mainFrame)
    print("iframe으로 전환 중...")
    main_frame = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mainFrame"))
    )
    driver.switch_to.frame(main_frame)
    time.sleep(1)
    
    # 2. 팝업 닫기 처리
    print("팝업 닫기 처리 중...")
    
    # .se-popup-button-cancel 요소가 있으면 클릭
    try:
        cancel_button = driver.find_element(By.CSS_SELECTOR, ".se-popup-button-cancel")
        cancel_button.click()
        print("  - 팝업 취소 버튼 클릭 완료")
        time.sleep(0.5)
    except:
        print("  - 팝업 취소 버튼 없음 (무시)")
    
    # .se-help-panel-close-button 요소가 있으면 클릭
    try:
        close_button = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
        close_button.click()
        print("  - 도움말 패널 닫기 버튼 클릭 완료")
        time.sleep(0.5)
    except:
        print("  - 도움말 패널 닫기 버튼 없음 (무시)")
    
    # 3. 제목 입력
    print("제목 입력 중...")
    title_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
    )
    title_element.click()
    time.sleep(0.5)
    
    # ActionChains를 사용하여 0.03초 간격으로 한 글자씩 타이핑
    title_text = "제목 테스트"
    actions = ActionChains(driver)
    for char in title_text:
        actions.send_keys(char).pause(0.03)
    actions.perform()
    print(f"  - 제목 입력 완료: {title_text}")
    time.sleep(0.5)
    
    # 4. 본문 입력
    print("본문 입력 중...")
    content_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-text"))
    )
    content_element.click()
    time.sleep(0.5)
    
    # 5줄 입력 (엔터 포함, 0.03초 간격)
    content_text = "18기 블로그글쓰기 스터디입니다."
    actions = ActionChains(driver)
    
    for i in range(5):
        # 각 줄의 텍스트 입력
        for char in content_text:
            actions.send_keys(char).pause(0.03)
        # 마지막 줄이 아니면 엔터 입력
        if i < 4:
            actions.send_keys(Keys.RETURN).pause(0.03)
    
    actions.perform()
    print(f"  - 본문 입력 완료: {content_text} (5줄)")
    time.sleep(1)
    
    # 5. 저장 버튼 클릭
    print("저장 버튼 클릭 중...")
    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".save_btn__bzc5B"))
    )
    save_button.click()
    print("  - 저장 버튼 클릭 완료")
    time.sleep(2)
    
    print("글쓰기 완료!")
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
    driver.quit()

# 브라우저를 열어둘지 닫을지 결정
# 자동으로 닫으려면 아래 주석을 해제하세요
# driver.quit()
