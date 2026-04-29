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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Bot Restarted. Step-by-step logic running...")
        driver.get(GUEST_URL)
        time.sleep(12)

        # STEP 1: COOKIES HATAO (Sirf agar 'Accept' button dikhe tabhi)
        print("Step 1: Cookies handle kar raha hoon...")
        driver.execute_script("""
            let cookieBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Accept all cookies') || el.textContent.includes('Accept')
            );
            if(cookieBtn) cookieBtn.click();
        """)
        time.sleep(5)

        # STEP 2: WELCOME CONTINUE (Screenshot wala Blue Button)
        print("Step 2: Clicking Continue...")
        driver.execute_script("""
            let continueBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Continue')
            );
            if(continueBtn) continueBtn.click();
        """)
        time.sleep(8)

        # STEP 3: MIC/CAM ALLOW (Agar page aaye tabhi)
        print("Step 3: Clicking Allow Access...")
        driver.execute_script("""
            let allowBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Allow mic/cam access')
            );
            if(allowBtn) allowBtn.click();
        """)
        time.sleep(10)

        # STEP 4: NAME ENTRY (English Name: Faiz)
        print("Step 4: Typing Name...")
        try:
            name_field = driver.find_element(By.CSS_SELECTOR, 'input[name="displayName"]') or \
                         driver.find_element(By.TAG_NAME, 'input')
            name_field.click()
            time.sleep(1)
            name_field.send_keys("Faiz")
            time.sleep(2)
            name_field.send_keys(Keys.ENTER)
            print("Name Entered via Keys.")
        except:
            # Backup JS for Name
            driver.execute_script("document.querySelector('input').value = 'Faiz';")
            driver.execute_script("document.querySelector('input').dispatchEvent(new Event('input', { bubbles: true }));")
            time.sleep(2)
            driver.execute_script("""
                let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                    el.textContent.includes('Enter studio')
                );
                if(enterBtn) enterBtn.click();
            """)

        print("Entering Studio...")
        time.sleep(25) 

        # STEP 5: AUTO-ADD TO STAGE
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
            'ffmpeg', '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p', '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
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
    
