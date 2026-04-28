import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

GUEST_URL = "https://streamyard.com/3r8zzr4cbk" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    # Headless mode kabhi-kabhi black screen deta hai, 
    # isliye virtual display (Xvfb) ke saath headless rehne dein.
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Loading StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(10) # Content load hone ka zyada wait

        # Entry logic
        driver.execute_script("""
            let input = document.querySelector('input');
            if(input) {
                input.value = 'Live_Bot';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
            setTimeout(() => {
                let btn = Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Enter'));
                if(btn) btn.click();
            }, 3000);
        """)
        
        print("Studio mein enter ho rahe hain...")
        time.sleep(20) # Studio aur Stage load hone ka extra time

        # Auto-Add to Stage
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                let removeBtn = btns.find(b => b.innerText.includes('Remove'));
                if (addBtn && !removeBtn) { addBtn.click(); }
            }, 5000);
        """)

        # FFmpeg with 'drawtext' for testing (agar black screen aaye toh text dikhega)
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-s', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '3000k',
            '-pix_fmt', 'yuv420p', # Compatibility ke liye
            '-c:a', 'aac', '-b:a', '128k',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Streaming active...")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
