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

        # SEQUENCE 1: Cookies / Continue / Accept All
        print("Step 1: Handling Popups...")
        driver.execute_script("""
            let btns = Array.from(document.querySelectorAll('button'));
            let target = btns.find(el => 
                el.textContent.includes('Accept') || 
                el.textContent.includes('Continue') || 
                el.textContent.includes('Got it')
            );
            if(target) target.click();
        """)
        time.sleep(5)

        # SEQUENCE 2: Allow Mic/Cam Access (Blue Button)
        print("Step 2: Clicking Allow...")
        driver.execute_script("""
            let allowBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Allow mic/cam') || el.textContent.includes('Allow')
            );
            if(allowBtn) allowBtn.click();
        """)
        time.sleep(8)

        # SEQUENCE 3: English Name Entry (Faiz)
        print("Step 3: Typing Name (Faiz)...")
        try:
            # Display name field ko target karke pehle clear karna
            name_field = driver.find_element(By.NAME, "displayName")
            name_field.click()
            time.sleep(1)
            
            # Ek-ek akshar type karna taaki error na aaye
            bot_name = "Faiz"
            for char in bot_name:
                name_field.send_keys(char)
                time.sleep(0.4)
            
            print("Name Typed. Waiting 2 seconds before Enter...")
            time.sleep(2)
            name_field.send_keys(Keys.ENTER)
        except:
            print("Field not found, using JS Force Fill...")
            driver.execute_script("""
                let input = document.querySelector('input[name="displayName"]') || document.querySelector('input');
                if(input) {
                    input.value = 'Faiz';
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """)
            time.sleep(2)
            driver.execute_script("""
                let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                    el.textContent.includes('Enter studio')
                );
                if(enterBtn) enterBtn.click();
            """)
        
        print("Waiting for Studio load...")
        time.sleep(25) 

        # SEQUENCE 4: Auto-Add to Stage
        print("Step 4: Active in Studio.")
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
    
