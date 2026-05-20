import os
import time
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/jktgf2iug5" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def popup_handler(driver):
    """Background loop jo popup ko handle karega"""
    while True:
        try:
            # "Stay in the studio" button ko dhoondo
            stay_btn = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'stay in the studio')]")
            if stay_btn:
                stay_btn[0].click()
                print("🎯 Popup detected and clicked 'Stay in the studio'!")
        except:
            pass
        time.sleep(30) # Har 30 second mein check karega

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080") 
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
    wait = WebDriverWait(driver, 25) 
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)

        # Popup handler thread start
        threading.Thread(target=popup_handler, args=(driver,), daemon=True).start()

        driver.execute_script("""
            function clickAnything() {
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                    }
                });
            }
            setInterval(clickAnything, 2000); 
        """)
        time.sleep(8)
        
        input_xpath = "//input[not(@type='hidden')]"
        name_input = wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
        name_input.send_keys("Faiz")
        time.sleep(2) 

        enter_button_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter studio')]"
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, enter_button_xpath)))
        enter_button.click()

        time.sleep(12) 

        # Coordinate click logic (jo aapka tha)
        driver.execute_script("""
            function clickByCoordinates() {
                let largestArea = 0; let stage = null;
                document.querySelectorAll('div').forEach(el => {
                    let r = el.getBoundingClientRect();
                    let area = r.width * r.height;
                    if (r.width >= 600 && r.width <= 1600 && r.height >= 400 && area > largestArea) {
                        largestArea = area; stage = el;
                    }
                });
                if (stage) {
                    let r = stage.getBoundingClientRect();
                    let clickX = r.right - 30;
                    let clickY = r.bottom - 30;
                    let targetEl = document.elementFromPoint(clickX, clickY);
                    if (targetEl) {
                        targetEl.dispatchEvent(new MouseEvent('click', {bubbles: true, clientX: clickX, clientY: clickY}));
                    }
                }
            }
            clickByCoordinates();
        """)
        
        time.sleep(5) 

        print("Starting FFmpeg rendering...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
