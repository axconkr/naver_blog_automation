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
    print("네이버 로그인 페이지 접속 중...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(3)
    
    print("아이디 입력 중...")
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
        print("  클립보드 방식 실패, JavaScript 방식 시도...")
        driver.execute_script(f"arguments[0].value = '{NAVER_ID}';", id_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", id_input)
        time.sleep(0.5)
    
    print("비밀번호 입력 중...")
    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    time.sleep(0.5)
    pyperclip.copy(NAVER_PW)
    pw_input.send_keys(PASTE_KEY, 'v')
    time.sleep(1)
    
    current_pw = pw_input.get_attribute('value')
    if not current_pw:
        print("  클립보드 방식 실패, JavaScript 방식 시도...")
        driver.execute_script(f"arguments[0].value = '{NAVER_PW}';", pw_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", pw_input)
        time.sleep(0.5)
    
    print("로그인 버튼 클릭 중...")
    login_button = driver.find_element(By.ID, "log.login")
    login_button.click()
    
    print("로그인 처리 중... (3초 대기)")
    time.sleep(3)
    
    current_url = driver.current_url
    if "nidlogin" not in current_url:
        print("로그인 성공!\n")
    else:
        print("로그인 실패 - 수동 확인 필요\n")

def select_category(category_name):
    """발행 레이어에서 카테고리 선택"""
    if not category_name:
        return
    
    print(f"  카테고리 선택 중: {category_name}")
    try:
        cat_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".selectbox_button__jb1Dt"))
        )
        driver.execute_script("arguments[0].click();", cat_button)
        time.sleep(1)
        
        cat_labels = driver.find_elements(By.CSS_SELECTOR, ".option_list_layer__YX1Tq label.radio_label__mB6ia")
        for label in cat_labels:
            label_text = label.text.strip()
            if category_name in label_text or label_text in category_name:
                driver.execute_script("arguments[0].click();", label)
                print(f"    - 카테고리 '{label_text}' 선택 완료")
                time.sleep(0.5)
                return
        
        print(f"    - 카테고리 '{category_name}'를 찾을 수 없음")
        driver.execute_script("arguments[0].click();", cat_button)
    except Exception as e:
        print(f"    - 카테고리 선택 실패: {e}")


def set_schedule_time(schedule_time_str):
    """예약 발행 시간 설정 (형식: YYYY-MM-DD HH:MM)"""
    if not schedule_time_str:
        return
    
    print(f"  예약 발행 설정 중: {schedule_time_str}")
    try:
        from selenium.webdriver.support.ui import Select
        
        parts = schedule_time_str.strip().split()
        if len(parts) != 2:
            print(f"    - 잘못된 형식 (YYYY-MM-DD HH:MM 필요)")
            return
        
        date_part, time_part = parts
        hour, minute = time_part.split(":")
        
        minute_rounded = str((int(minute) // 10) * 10).zfill(2)
        
        reserve_radio = driver.find_element(By.CSS_SELECTOR, "input#radio_time2[value='pre']")
        driver.execute_script("arguments[0].click();", reserve_radio)
        time.sleep(1)
        
        date_input = driver.find_element(By.CSS_SELECTOR, "input.input_date__QmA0s")
        driver.execute_script("arguments[0].click();", date_input)
        time.sleep(1)
        
        try:
            year, month, day = date_part.split("-")
            day_buttons = driver.find_elements(By.CSS_SELECTOR, ".react-datepicker__day:not(.react-datepicker__day--outside-month)")
            for btn in day_buttons:
                if btn.text.strip() == str(int(day)):
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"    - 날짜 {day}일 선택")
                    break
            time.sleep(0.5)
        except:
            print(f"    - 날짜 선택 실패, 기본 날짜 사용")
        
        hour_select = Select(driver.find_element(By.CSS_SELECTOR, "select.hour_option__J_heO"))
        hour_select.select_by_value(hour.zfill(2))
        print(f"    - 시간 {hour}시 선택")
        
        minute_select = Select(driver.find_element(By.CSS_SELECTOR, "select.minute_option__Vb3xB"))
        minute_select.select_by_value(minute_rounded)
        print(f"    - 분 {minute_rounded}분 선택")
        
        time.sleep(0.5)
        print(f"    - 예약 발행 설정 완료")
    except Exception as e:
        print(f"    - 예약 발행 설정 실패: {e}")


def write_blog_post(title, content, category=None, schedule_time=None):
    """블로그 글쓰기 페이지에 제목과 본문을 입력하고 발행"""
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
    
    # 3. 제목 입력 (클립보드 붙여넣기 방식)
    print(f"제목 입력 중: {title}")
    title_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
    )
    title_element.click()
    time.sleep(0.5)
    
    title_paragraph = driver.find_element(By.CSS_SELECTOR, ".se-section-documentTitle .se-text-paragraph")
    title_paragraph.click()
    time.sleep(0.3)
    
    pyperclip.copy(str(title))
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(0.5)
    print(f"  - 제목 입력 완료")
    
    # 4. 본문 입력 (클립보드 붙여넣기 방식)
    print("본문 입력 중...")
    content_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-text"))
    )
    content_element.click()
    time.sleep(0.5)
    
    text_paragraph = driver.find_element(By.CSS_SELECTOR, ".se-section-text .se-text-paragraph")
    text_paragraph.click()
    time.sleep(0.3)
    
    content_str = str(content) if content else ""
    pyperclip.copy(content_str)
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(1)
    print(f"  - 본문 입력 완료")
    time.sleep(1)
    
    # 5. 발행 버튼 클릭 전 도움말 패널 닫기
    print("발행 버튼 클릭 중...")
    try:
        help_close = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
        help_close.click()
        print("  - 도움말 패널 닫기 완료")
        time.sleep(0.5)
    except:
        pass
    
    publish_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".publish_btn__m9KHH"))
    )
    driver.execute_script("arguments[0].click();", publish_button)
    print("  - 발행 버튼 클릭 완료")
    time.sleep(2)
    
    # 6. 발행 설정 (카테고리, 예약 발행)
    print("발행 설정 중...")
    time.sleep(1)
    
    select_category(category)
    set_schedule_time(schedule_time)
    
    # 7. 발행 확인 버튼 클릭
    print("발행 확인 버튼 클릭 중...")
    try:
        confirm_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.confirm_btn__WEaBq"))
        )
        driver.execute_script("arguments[0].click();", confirm_button)
        print("  - 발행 확인 버튼 클릭 완료")
    except Exception as e:
        print(f"  - 발행 확인 버튼 처리 실패: {e}")
    
    time.sleep(3)
    print("글 발행 완료!\n")

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
        
        for row in range(2, max_row + 1):
            title = ws[f'A{row}'].value
            content = ws[f'B{row}'].value
            category = ws[f'C{row}'].value
            schedule_time = ws[f'D{row}'].value
            
            if title and content:
                blog_posts.append((row, title, content, category, schedule_time))
        
        if not blog_posts:
            print("처리할 블로그 글이 없습니다.")
            wb.close()
            return
        
        print(f"총 {len(blog_posts)}개의 블로그 글을 업로드합니다.\n")
        
        # 네이버 로그인 (한 번만)
        naver_login()
        
        for row, title, content, category, schedule_time in blog_posts:
            try:
                print(f"[{row}행] 블로그 글 업로드 시작")
                print(f"  제목: {title}")
                if category:
                    print(f"  카테고리: {category}")
                if schedule_time:
                    print(f"  예약 발행: {schedule_time}")
                
                write_blog_post(title, content, category, schedule_time)
                
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
