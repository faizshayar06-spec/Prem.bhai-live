import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
GUEST_URL = "https://streamyard.com/3r8zzr4cbk" # Apna link yahan dalein
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

    # Fixed Driver Initialization
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(5)

        driver.execute_script("""
            let input = document.querySelector('input');
            if(input) {
                input.value = 'Live_Bot';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
            setTimeout(() => {
                let btn = Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Enter'));
                if(btn) btn.click();
            }, 2000);
        """)
        
        time.sleep(15)

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
        print("Bot logic active.")

        # FFmpeg Command
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-s', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '3500k',
            '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Streaming... will run for 5h 55m.")
        time.sleep(21300) # 5 hours 55 minutes
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
