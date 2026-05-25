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
from selenium.webdriver.common.keys import Keys # Naya import (shortcuts ke liye)
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/x7hedy7jfq" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Screen size fix
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

        # STEP 3: THE WAITING GAME (Aapka Timer Idea) ⏱️
        print("\n=======================================================")
        print("🚨 BOT STUDIO MEIN AA GAYA HAI! 🚨")
        print("Aapke paas 40 SECONDS hain bot ko 'STAGE' par lene ke liye.")
        print("=======================================================\n")
        
        # 40 seconds ka countdown console mein dikhega
        for i in range(40, 0, -1):
            if i % 10 == 0 or i <= 5:
                print(f"⏳ Waiting... {i} seconds left to add bot to stage.")
            time.sleep(1)
            
        print("\nTimer over! Ab bot maximize karne ki koshish kar raha hai... 🖥️")

        # STEP 4: THE ULTIMATE TRIPLE-THREAT MAXIMIZE 🎯
        try:
            actions = ActionChains(driver)
            
            # Video element (Main Stage) dhoondhna
            video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            
            # Tarika 1: Double Click (Aksar web players double-click se fullscreen ho jate hain)
            print("Attempt 1: Double clicking the video...")
            actions.move_to_element(video_element).double_click().perform()
            time.sleep(1)
            
            # Tarika 2: Keyboard Shortcut ('f' dabana)
            print("Attempt 2: Sending 'f' key for fullscreen...")
            video_element.send_keys("f")
            time.sleep(1)

            # Tarika 3: Aggressive JS Search
            print("Attempt 3: JavaScript se Fullscreen button dhoondh kar click karna...")
            driver.execute_script("""
                let btns = document.querySelectorAll('button');
                for(let btn of btns){
                    let aria = btn.getAttribute('aria-label') || '';
                    let title = btn.getAttribute('title') || '';
                    if(aria.toLowerCase().includes('fullscreen') || 
                       title.toLowerCase().includes('fullscreen') || 
                       aria.toLowerCase().includes('maximize')) {
                        btn.click();
                        console.log('🎯 JS Clicked the Fullscreen button!');
                    }
                }
            """)
            print("✅ Maximize commands bhej diye gaye hain!")
                
        except Exception as e:
            print("Maximize block me thodi dikkat aayi:", e)

        # Maximize hone ka final settlement time
        time.sleep(5) 

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
    
