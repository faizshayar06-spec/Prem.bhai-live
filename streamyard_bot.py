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
        print("Bot Started. Jalwa dikhane ka time...")
        driver.get(GUEST_URL)
        time.sleep(12)

        # STEP 1: COOKIES & INITIAL BYPASS
        driver.execute_script("""
            let btns = Array.from(document.querySelectorAll('button'));
            btns.forEach(btn => {
                let txt = btn.innerText.toLowerCase();
                if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow')) {
                    btn.click();
                }
            });
        """)
        time.sleep(8)

        # STEP 2: FORCEFUL NAME ENTRY (Faiz)
        print("Step 2: Naam likh raha hoon forcefully...")
        driver.execute_script("""
            let input = document.querySelector('input[name="displayName"]') || document.querySelector('input');
            if(input) {
                input.focus();
                input.value = 'Faiz';
                // Events trigger karna taaki StreamYard ko pata chale naam likha gaya hai
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)
        time.sleep(3)

        # STEP 3: COORDINATE GAME (The Real Hit)
        print("Step 3: Coordinates nikal kar Enter Studio par click kar raha hoon...")
        driver.execute_script("""
            let btn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Enter studio')
            );
            if(btn) {
                btn.disabled = false; // Agar button disable ho toh enable karo
                let rect = btn.getBoundingClientRect();
                let x = rect.left + rect.width / 2;
                let y = rect.top + rect.height / 2;
                
                // Mouse coordinates par forceful click
                let clickEvent = new MouseEvent('click', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': x,
                    'clientY': y
                });
                btn.dispatchEvent(clickEvent);
                console.log('Force Clicked at: ' + x + ',' + y);
            }
        """)
        
        # Backup: Selenium wala Enter key
        try:
            name_field = driver.find_element(By.TAG_NAME, "input")
            name_field.send_keys(Keys.ENTER)
            print("Backup Enter Key Pressed.")
        except:
            pass

        print("Waiting for Studio load...")
        time.sleep(25) 

        # STEP 4: AUTO-ADD TO STAGE
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
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
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
