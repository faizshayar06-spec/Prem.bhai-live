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
        print("Bot Started. Jalwa loading...")
        driver.get(GUEST_URL)
        time.sleep(10)

        # STEP 1: COOKIES HATAO (Java Logic)
        print("Step 1: Cookies saaf kar raha hoon...")
        driver.execute_script("""
            let cookieBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Accept all cookies') || el.textContent.includes('Accept')
            );
            if(cookieBtn) cookieBtn.click();
        """)
        time.sleep(5)

        # STEP 2: NAAM LIKHO (Human Typing Simulation)
        print("Step 2: Naam 'Faiz' likh raha hoon...")
        try:
            # Sahi field ko target karna
            name_field = driver.find_element(By.NAME, "displayName")
            name_field.click()
            time.sleep(1)
            
            for char in "Faiz":
                name_field.send_keys(char)
                time.sleep(0.5) # Slow typing taaki error na aaye
            
            print("Naam likh diya.")
        except Exception as e:
            print("Selenium fail, JS se naam bhar raha hoon...")
            driver.execute_script("document.querySelector('input').value = 'Faiz';")
            driver.execute_script("document.querySelector('input').dispatchEvent(new Event('input', { bubbles: true }));")

        time.sleep(3)

        # STEP 3: ENTER STUDIO (Final Hit)
        print("Step 3: Studio mein entry maar raha hoon...")
        driver.execute_script("""
            let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Enter studio')
            );
            if(enterBtn) enterBtn.click();
        """)
        
        print("Waiting for Studio load...")
        time.sleep(25) 

        # STEP 4: AUTO-ADD TO STAGE
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

        # FFmpeg Signal
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
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
