import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/6ihfwcdmwx" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Permissions Bypass (FORCE FLAGS)
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
    
    # Wait object initialize kiya (Max 20 seconds wait karega)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)

        # STEP 1: COOKIES / ACCEPT / ALLOW BUTTON HANDLING (Bypass)
        print("Bypassing initial dialogs/cookies...")
        try:
            driver.execute_script("""
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                    }
                });
            """)
        except Exception:
            pass # Agar koi button nahi mila toh code crash nahi hoga

        # STEP 2: NAME ENTRY (FAIZ IN ENGLISH)
        print("Finding Display Name input field...")
        
        # Name field ka wait karega aur select karega (Screenshot ke hisab se)
        name_input = wait.until(
            EC.presence_of_element_with_locator((By.CSS_SELECTOR, "input[name='name'], input[id*='name'], input[placeholder*='name'], input[type='text']"))
        )
        
        # Click aur Clear karne ke baad text type karna (English mein 'Faiz')
        name_input.click()
        name_input.clear()
        name_input.send_keys("Faiz")
        print("Name 'Faiz' entered successfully.")
        
        time.sleep(2) # Stabilize karne ke liye chhota sa pause

        # STEP 3: CLICK ENTER STUDIO BUTTON
        print("Finding 'Enter studio' button...")
        enter_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enter studio')]"))
        )
        
        # Click command send karna
        enter_button.click()
        print("Clicked 'Enter studio' successfully.")
        
        print("Waiting for Studio to load...")
        time.sleep(25) # Studio properly load hone ke liye wait

        # STEP 4: REPETITIVE AUTO-ADD TO STAGE
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
                    addBtn.click();
                }
            }, 5000);
        """)

        # FFmpeg Section
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
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
