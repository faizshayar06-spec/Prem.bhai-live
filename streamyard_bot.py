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
    # Screen size ko strict 1920x1080 par lock kar rahe hain
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
    wait = WebDriverWait(driver, 25) 
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        driver.maximize_window() # Double safety for 1920x1080 screen size

        # STEP 1: FORCE CLICK POPUPS
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
        
        # STEP 2: ENTER NAME & STUDIO
        print("Waiting for visible Name input field...")
        input_xpath = "//input[not(@type='hidden')]"
        name_input = wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
        name_input = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
        
        try:
            name_input.clear()
        except:
            pass 
        
        print("Typing name as a real human...")
        name_input.send_keys("Faiz")
        time.sleep(2) 

        print("Hunting for the 'Enter studio' button...")
        enter_button_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter studio')]"
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, enter_button_xpath)))
        enter_button.click()
        print("Successfully bypassed and entered the Studio! 🥀")

        # Studio aane ka poora wait (15 seconds taaki player load ho jaye)
        print("Waiting for Studio to settle...")
        time.sleep(15) 

        # STEP 3: ABSOLUTE SCREEN COORDINATE CLICK 🎯
        print("Targeting Maximize button via absolute PC Screen Coordinates (1345, 715)... 🖥️")
        
        # We will target the top-left of the webpage body to calculate exact absolute coordinates
        body_element = driver.find_element(By.TAG_NAME, "body")
        
        # Fixed screen coordinates determined from the 1920x1080 screenshot
        target_x = 1345
        target_y = 715
        
        # 1. Pehle mouse ko wahan move karenge taaki player ke controls 'Wake Up' ho jayein
        print("Moving mouse to wake up player controls...")
        ActionChains(driver).move_to_element_with_offset(body_element, target_x, target_y).perform()
        time.sleep(1) # Controls aane ka delay
        
        # 2. Ab exact point par force click marenge
        print(f"Clicking exactly at X={target_x}, Y={target_y}")
        ActionChains(driver).move_to_element_with_offset(body_element, target_x, target_y).click().perform()
        print("🎯 Boom! Absolute coordinate click completed successfully.")
        
        time.sleep(5) # Maximize animation finish hone do

        # FFmpeg Setup
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
        print("Bot is doing its job. Check YouTube dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
