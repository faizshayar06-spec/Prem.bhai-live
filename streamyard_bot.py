import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    chrome_options.add_argument("--headless=new") 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 40)
    
    try:
        print("🚀 Script Started...")
        driver.get(GUEST_URL)

        # Name Entry
        name_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='displayName'], input#display-name")))
        name_input.send_keys("Faiz-Live")
        name_input.send_keys(Keys.ENTER)

        # Studio Entry
        enter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enter studio')]")))
        enter_btn.click()
        print("✅ Inside Studio.")

        # Auto-Add to Stage
        driver.execute_script("""
            setInterval(() => {
                let addBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Add to stage'));
                if (addBtn) addBtn.click();
            }, 10000);
        """)

        # FFmpeg Stream (Approx 5 hours 50 mins to be safe)
        ffmpeg_cmd = (
            f"ffmpeg -f x11grab -s 1920x1080 -i :99.0+0,0 "
            f"-f pulse -i default -vcodec libx264 -preset veryfast "
            f"-maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 50 "
            f"-acodec aac -b:a 128k -ar 44100 -f flv rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
        )
        
        process = subprocess.Popen(ffmpeg_cmd, shell=True)
        time.sleep(21000) # 5.8 Hours
        process.terminate()

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
