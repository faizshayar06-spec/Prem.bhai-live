import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/3r8zzr4cbk" # Apna asli link yahan dalein
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(12) # Cookies popup aane ka wait

        # FIX: COOKIES ACCEPT LOGIC
        driver.execute_script("""
            let cookieBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Accept all cookies') || 
                el.textContent.includes('Accept') || 
                el.textContent.includes('Got it')
            );
            if(cookieBtn) {
                cookieBtn.click();
                console.log('Cookies Accepted!');
            }
        """)
        time.sleep(3)

        # NAME ENTRY & ENTER
        driver.execute_script("""
            let nameInput = document.querySelector('input[placeholder*="name"]') || document.querySelector('input');
            if(nameInput) {
                nameInput.value = 'فیض'; 
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            setTimeout(() => {
                let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                    el.textContent.includes('Enter') || el.textContent.includes('Check')
                );
                if(enterBtn) enterBtn.click();
            }, 2000);
        """)
        
        print("Studio loading...")
        time.sleep(20)

        # AUTO-ADD TO STAGE
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

        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p', '-g', '60',
            '-c:a', 'aac', '-b:a', '128k', '-ar', '44100',
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
    
