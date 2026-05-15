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
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🚀 Script Started: Faiz 6H Version")
        driver.get(GUEST_URL)
        time.sleep(15) # Wait for page load

        # Sabse Fast Tarika: Direct JavaScript se Name bharna aur Button click karna
        print("⌨️ Entering Name and Studio...")
        driver.execute_script("""
            let nameField = document.querySelector('input[name="displayName"], input#display-name');
            if(nameField) {
                nameField.value = 'Faiz-Live';
                nameField.dispatchEvent(new Event('input', { bubbles: true }));
            }
            setTimeout(() => {
                let btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Enter studio'));
                if(btn) btn.click();
            }, 2000);
        """)
        
        time.sleep(10)
        print("✅ Inside Studio (Hopefully). Starting Background Stage Bot...")

        # Stage pe add karne wala bot (Har 10 second check karega)
        driver.execute_script("""
            setInterval(() => {
                let addBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Add to stage'));
                if (addBtn) addBtn.click();
            }, 10000);
        """)

        # FFmpeg Command - 6 Ghante Fixed
        print("🎬 Streaming to YouTube...")
        ffmpeg_cmd = (
            f"ffmpeg -f x11grab -s 1920x1080 -i :99.0+0,0 "
            f"-f pulse -i default -vcodec libx264 -preset veryfast "
            f"-maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 50 "
            f"-acodec aac -b:a 128k -ar 44100 -f flv rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
        )
        
        # Isse 6 ghante (21600 seconds) tak chalao
        process = subprocess.Popen(ffmpeg_cmd, shell=True)
        time.sleep(21500) 
        process.terminate()
        print("🏁 6 Hours Completed.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
