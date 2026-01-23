from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from openpyxl import load_workbook
from dotenv import load_dotenv
from datetime import datetime
import pyperclip
import platform
import time
import os
import glob

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
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# WebDriver 초기화
driver = webdriver.Chrome(options=chrome_options)

def find_blog_excel_file():
    """
    현재 디렉토리에서 blog+날짜.xlsx 파일을 찾습니다.
    
    Returns:
        str: 파일 경로
    """
    current_dir = os.getcwd()
    # blog로 시작하고 .xlsx로 끝나는 파일 찾기
    pattern = os.path.join(current_dir, "blog*.xlsx")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError("blog+날짜.xlsx 파일을 찾을 수 없습니다.")
    
    # 가장 최근 파일 반환 (여러 개 있을 경우)
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def naver_login():
    """네이버 로그인 처리"""
    print("네이버 로그인 페이지 접속 중...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)
    
    # 아이디 입력
    print("아이디 입력 중...")
    id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id"))
    )
    id_input.click()
    time.sleep(0.5)
    
    pyperclip.copy(NAVER_ID)
    id_input.send_keys(PASTE_KEY, 'v')
    time.sleep(0.5)
    
    # 비밀번호 입력
    print("비밀번호 입력 중...")
    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    time.sleep(0.5)
    
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
    print("로그인 완료!\n")

def write_blog_post(title, content):
    """블로그 글쓰기 페이지에 제목과 본문을 입력하고 저장"""
    # 블로그 글쓰기 페이지로 이동
    print("블로그 글쓰기 페이지로 이동 중...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(2)
    
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
    print(f"제목 입력 중: {title}")
    title_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
    )
    title_element.click()
    time.sleep(0.5)
    
    # 기존 내용 삭제 후 새 제목 입력
    title_element.send_keys(PASTE_KEY, 'a')  # 전체 선택
    time.sleep(0.2)
    
    # ActionChains를 사용하여 0.03초 간격으로 한 글자씩 타이핑
    actions = ActionChains(driver)
    for char in str(title):
        actions.send_keys(char).pause(0.03)
    actions.perform()
    print(f"  - 제목 입력 완료")
    time.sleep(0.5)
    
    # 4. 본문 입력
    print("본문 입력 중...")
    content_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-text"))
    )
    content_element.click()
    time.sleep(0.5)
    
    # 기존 내용 삭제
    content_element.send_keys(PASTE_KEY, 'a')
    time.sleep(0.2)
    
    # 본문을 줄 단위로 입력 (엔터 포함, 0.03초 간격)
    content_str = str(content) if content else ""
    actions = ActionChains(driver)
    content_lines = content_str.split('\n')
    
    for i, line in enumerate(content_lines):
        # 각 줄의 텍스트 입력
        for char in line:
            actions.send_keys(char).pause(0.03)
        # 마지막 줄이 아니면 엔터 입력
        if i < len(content_lines) - 1:
            actions.send_keys(Keys.RETURN).pause(0.03)
    
    actions.perform()
    print(f"  - 본문 입력 완료 ({len(content_lines)}줄)")
    time.sleep(1)
    
    # 5. 저장 버튼 클릭
    print("저장 버튼 클릭 중...")
    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".save_btn__bzc5B"))
    )
    save_button.click()
    print("  - 저장 버튼 클릭 완료")
    time.sleep(3)  # 저장 완료 대기
    
    # iframe에서 나오기
    driver.switch_to.default_content()
    print("글 업로드 완료!\n")

def main():
    """메인 함수: 엑셀 파일 읽기 및 블로그 업로드"""
    try:
        # blog+날짜.xlsx 파일 찾기
        excel_file = find_blog_excel_file()
        print(f"엑셀 파일 열기: {excel_file}")
        wb = load_workbook(excel_file)
        ws = wb.active
        
        # 2행부터 마지막 행까지 데이터 읽기
        max_row = ws.max_row
        blog_posts = []
        
        for row in range(2, max_row + 1):  # 2행부터 시작 (1행은 헤더)
            title = ws[f'A{row}'].value
            content = ws[f'B{row}'].value
            
            if title and content:  # 제목과 본문이 모두 있는 경우만 추가
                blog_posts.append((row, title, content))
        
        if not blog_posts:
            print("처리할 블로그 글이 없습니다.")
            wb.close()
            return
        
        print(f"총 {len(blog_posts)}개의 블로그 글을 업로드합니다.\n")
        
        # 네이버 로그인 (한 번만)
        naver_login()
        
        # 각 블로그 글 업로드
        for row, title, content in blog_posts:
            try:
                print(f"[{row}행] 블로그 글 업로드 시작")
                print(f"  제목: {title}")
                
                write_blog_post(title, content)
                
                print(f"[{row}행] 업로드 완료\n")
                print("-" * 50 + "\n")
                
            except Exception as e:
                print(f"[{row}행] 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                print("-" * 50 + "\n")
                # iframe에서 나오기 (오류 발생 시)
                try:
                    driver.switch_to.default_content()
                except:
                    pass
                continue
        
        wb.close()
        print("모든 블로그 글 업로드 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 브라우저 닫기 (필요시 주석 처리)
        # driver.quit()
        pass

if __name__ == "__main__":
    main()
