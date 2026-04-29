import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/3r8zzr4cbk" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(12)

        # STEP 1: INITIAL POPUPS BYPASS
        driver.execute_script("""
            let btns = Array.from(document.querySelectorAll('button'));
            btns.forEach(btn => {
                let txt = btn.innerText.toLowerCase();
                if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow')) {
                    btn.click();
                }
            });
        """)
        time.sleep(8)

        # STEP 2: HUMAN-LIKE NAME ENTRY (Error Fix)
        print("Entering name...")
        try:
            # Sahi input box dhoondna
            name_field = driver.find_element(By.CSS_SELECTOR, 'input[name="displayName"]') or \
                         driver.find_element(By.TAG_NAME, 'input')
            
            name_field.click() # Pehle click karo
            time.sleep(1)
            
            # Ek-ek karke type karna (Simulation)
            bot_name = "فیض"
            for char in bot_name:
                name_field.send_keys(char)
                time.sleep(0.2)
            
            name_field.send_keys(Keys.ENTER) # Keyboard wala Enter button
            print("Name entered and Enter key pressed.")

        except Exception as e:
            print(f"Name Entry Field not found by Selenium, trying JS backup...")
            driver.execute_script("document.querySelector('input').value = 'فیض';")
            driver.execute_script("document.querySelector('input').dispatchEvent(new Event('input', { bubbles: true }));")

        # STEP 3: STUDIO ENTRY BUTTON (Backup Click)
        time.sleep(3)
        driver.execute_script("""
            let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Enter studio')
            );
            if(enterBtn) enterBtn.click();
        """)
        
        print("Entering Studio...")
        time.sleep(25) 

        # STEP 4: AUTO-ADD TO STAGE LOOP
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                let removeBtn = btns.find(b => b.innerText.includes('Remove'));
                if (addBtn && !removeBtn) {
                    addBtn.click();
                }
            }, 5000);
        """)

        # FFmpeg
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
        print(f"Main Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
