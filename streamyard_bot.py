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
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(10)

        # SEQUENCE 1: Cookies / Continue
        print("Step 1: Handling Initial Buttons...")
        driver.execute_script("""
            let btns = Array.from(document.querySelectorAll('button'));
            let initialBtn = btns.find(el => el.textContent.includes('Accept') || el.textContent.includes('Continue'));
            if(initialBtn) initialBtn.click();
        """)
        time.sleep(5)

        # SEQUENCE 2: Allow Mic/Cam Access
        print("Step 2: Clicking Allow Mic/Cam...")
        driver.execute_script("""
            let allowBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Allow mic/cam access')
            );
            if(allowBtn) allowBtn.click();
        """)
        time.sleep(8)

        # SEQUENCE 3: Human-Like Name Entry
        print("Step 3: Entering Name...")
        try:
            # Display name field ko target karna
            name_field = driver.find_element(By.NAME, "displayName")
            name_field.click()
            time.sleep(1)
            
            bot_name = "فیض"
            for char in bot_name:
                name_field.send_keys(char)
                time.sleep(0.3)
            
            print("Name Typed. Pressing Enter...")
            name_field.send_keys(Keys.ENTER)
        except:
            print("Name field issue, using backup click...")
            driver.execute_script("document.querySelector('input').value = 'فیض';")
            time.sleep(2)
            driver.execute_script("""
                let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                    el.textContent.includes('Enter studio')
                );
                if(enterBtn) enterBtn.click();
            """)
        
        time.sleep(20) # Studio load hone ka wait

        # SEQUENCE 4: Auto-Add to Stage (Only after entering studio)
        print("Step 4: Bot is in Studio. Stage loop active.")
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
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
