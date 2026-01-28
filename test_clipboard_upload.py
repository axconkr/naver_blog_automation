from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from utils import extract_content_sequence
from dotenv import load_dotenv
import subprocess
import pyperclip
import platform
import tempfile
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


def copy_image_to_clipboard(image_path):
    if platform.system() == 'Darwin':
        script = f'''
        use framework "AppKit"
        use scripting additions
        
        set pb to current application's NSPasteboard's generalPasteboard()
        pb's clearContents()
        
        set img to current application's NSImage's alloc()'s initWithContentsOfFile:"{image_path}"
        pb's writeObjects:{{img}}
        
        return "OK"
        '''
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            print(f"    Clipboard error: {result.stderr}")
            return False
        except Exception as e:
            print(f"    Clipboard copy failed: {e}")
            return False
    elif platform.system() == 'Windows':
        script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $image = [System.Drawing.Image]::FromFile("{image_path}")
        [System.Windows.Forms.Clipboard]::SetImage($image)
        '''
        try:
            subprocess.run(['powershell', '-Command', script], check=True, capture_output=True)
            return True
        except:
            return False
    return False


def upload_image_clipboard(image_path):
    if not image_path or not os.path.exists(image_path):
        print(f"    Image not found: {image_path}")
        return False
    
    abs_path = os.path.abspath(image_path)
    print(f"    Uploading via clipboard: {os.path.basename(image_path)}")
    
    try:
        text_area = driver.find_element(By.CSS_SELECTOR, ".se-component-content")
        driver.execute_script("arguments[0].click();", text_area)
        time.sleep(0.3)
        
        if copy_image_to_clipboard(abs_path):
            ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
            time.sleep(3)
            print(f"    Upload complete!")
            return True
        else:
            print(f"    Clipboard copy failed")
            return False
    except Exception as e:
        print(f"    Upload error: {e}")
        return False


def login():
    print("1. Naver login...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(3)
    
    try:
        id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id"))
        )
        id_input.click()
        time.sleep(0.5)
        pyperclip.copy(NAVER_ID or "")
        id_input.send_keys(PASTE_KEY, 'v')
        time.sleep(1)
        
        pw_input = driver.find_element(By.ID, "pw")
        pw_input.click()
        time.sleep(0.5)
        pyperclip.copy(NAVER_PW or "")
        pw_input.send_keys(PASTE_KEY, 'v')
        time.sleep(1)
        
        login_button = driver.find_element(By.ID, "log.login")
        login_button.click()
        time.sleep(4)
    except:
        pass
    
    if "nidlogin" in driver.current_url:
        print("\n   Manual login required")
        input("   Press Enter after login...")
    else:
        print("   Login success!")


def test_clipboard_upload():
    docx_path = "output/test_document_with_images.docx"
    if not os.path.exists(docx_path):
        docx_files = [f for f in os.listdir("output") if f.endswith('.docx')]
        if docx_files:
            docx_path = os.path.join("output", docx_files[0])
        else:
            print("No docx file found in output folder")
            return
    
    temp_dir = tempfile.mkdtemp()
    
    print(f"\n2. Extract content from: {docx_path}")
    sequence = extract_content_sequence(docx_path, temp_dir)
    
    text_count = len([s for s in sequence if s["type"] == "text"])
    image_count = len([s for s in sequence if s["type"] == "image"])
    print(f"   Sequence: {len(sequence)} items ({text_count} text, {image_count} images)")
    
    for i, item in enumerate(sequence):
        if item["type"] == "text":
            print(f"   [{i}] Text: {len(item['content'])} chars")
        else:
            print(f"   [{i}] Image: {os.path.basename(item['path'])}")
    
    print("\n3. Navigate to blog editor...")
    driver.get("https://blog.naver.com/GoBlogWrite.naver")
    time.sleep(5)
    
    print("4. Switch to iframe...")
    main_frame = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "mainFrame"))
    )
    driver.switch_to.frame(main_frame)
    time.sleep(3)
    
    print("5. Close popups...")
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
    
    print("\n6. Input title...")
    title_para = driver.find_element(By.CSS_SELECTOR, ".se-section-documentTitle .se-text-paragraph")
    driver.execute_script("arguments[0].click();", title_para)
    time.sleep(0.5)
    
    pyperclip.copy("Test - Clipboard Image Upload")
    ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
    time.sleep(1)
    
    print("\n7. Input content sequence (text + image pattern)...")
    
    for i, item in enumerate(sequence):
        print(f"\n  [{i+1}/{len(sequence)}]", end=" ")
        
        if item["type"] == "text":
            print(f"Text ({len(item['content'])} chars)")
            text_para = driver.find_element(By.CSS_SELECTOR, ".se-component-content")
            driver.execute_script("arguments[0].click();", text_para)
            time.sleep(0.3)
            
            pyperclip.copy(item["content"])
            ActionChains(driver).key_down(PASTE_KEY).send_keys('v').key_up(PASTE_KEY).perform()
            ActionChains(driver).send_keys(Keys.ENTER, Keys.ENTER).perform()
            time.sleep(0.5)
            
        elif item["type"] == "image":
            print(f"Image ({os.path.basename(item['path'])})")
            upload_image_clipboard(item["path"])
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            time.sleep(1)
    
    print("\n\nTest complete! Check the browser.")
    print("Press Enter to close...")
    input()


try:
    login()
    test_clipboard_upload()
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
finally:
    driver.quit()
