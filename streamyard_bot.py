import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
    # Headless band kiya hai taaki Xvfb screen capture ho sake
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🌐 Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(20) # Thoda extra time load hone ke liye

        # --- IS CODE SE ENTER HOGA ---
        print("⌨️ Injecting Login Script...")
        driver.execute_script("""
            // 1. Name bharna
            let input = document.querySelector('input[name="displayName"], input#display-name');
            if(input) {
                input.value = 'Faiz-Live';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // 2. 3 second baad 'Enter Studio' button dhoond kar click karna
            setTimeout(() => {
                let buttons = Array.from(document.querySelectorAll('button'));
                let target = buttons.find(b => b.innerText.toLowerCase().includes('enter'));
                if(target) {
                    target.click();
                    console.log('Clicked Enter Studio');
                }
            }, 3000);
        """)
        
        time.sleep(15) # Wait for studio to load
        print("✅ Inside Studio. Starting FFmpeg capture...")

        # Stage pe add karne ka loop
        driver.execute_script("""
            setInterval(() => {
                let addBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Add to stage'));
                if (addBtn) addBtn.click();
            }, 10000);
        """)

        # FFmpeg with display fix
        ffmpeg_cmd = (
            f"ffmpeg -f x11grab -video_size 1920x1080 -framerate 30 -i :99.0 "
            f"-f pulse -i default -c:v libx264 -preset ultrafast -pix_fmt yuv420p "
            f"-maxrate 3000k -bufsize 6000k -g 60 -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
        )
        
        process = subprocess.Popen(ffmpeg_cmd, shell=True)
        time.sleep(21500) # Pure 6 Ghante
        process.terminate()

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
