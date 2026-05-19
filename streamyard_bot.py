import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/6ihfwcdmwx" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080") 
    
    # Permissions Bypass
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1, 
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1
    })

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 30) 
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        driver.maximize_window() 

        # STEP 1: FORCE CLICK POPUPS (Python Method)
        print("Handling popups...")
        time.sleep(5)
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for btn in buttons:
            try:
                txt = btn.text.lower()
                if any(x in txt for x in ['accept', 'continue', 'allow', 'got it']):
                    btn.click()
            except:
                pass
        
        # STEP 2: ENTER NAME & STUDIO
        print("Waiting for name input...")
        name_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[not(@type='hidden')]")))
        name_input.clear()
        name_input.send_keys("Faiz")
        time.sleep(2) 

        print("Clicking Enter Studio...")
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter studio')]")))
        enter_button.click()
        
        print("Waiting for Studio to settle (15s)...")
        time.sleep(15) 

        # STEP 3: ABSOLUTE COORDINATE CLICK (1345, 715)
        print("Targeting Maximize button (1345, 715)...")
        targetX, targetY = 1345, 715
        body = driver.find_element(By.TAG_NAME, "body")
        
        # Wake up controls
        ActionChains(driver).move_to_element_with_offset(body, targetX, targetY).perform()
        time.sleep(1)
        # Click
        ActionChains(driver).move_to_element_with_offset(body, targetX, targetY).click().perform()
        print("Maximize click successful.")
        
        time.sleep(5) 

        # FFmpeg
        print("Starting FFmpeg...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Bot is running. Stream active.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
