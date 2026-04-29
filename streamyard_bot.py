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
        print("Opening StreamYard... Force Mode ON")
        driver.get(GUEST_URL)
        time.sleep(12)

        # STEP 1: BYPASS INITIAL (In case Cookies or Continue appears)
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

        # STEP 2: FORCEFUL NAME ENTRY (Jalwa logic)
        print("Step 2: Forcefully entering name 'Faiz'...")
        driver.execute_script("""
            let nameField = document.querySelector('input[name="displayName"]') || 
                            document.querySelector('input[placeholder*="name"]') || 
                            document.querySelector('input');
            
            if(nameField) {
                // Focus aur Value forcefully set karna
                nameField.focus();
                nameField.value = 'Faiz';
                
                // StreamYard ko trigger dena ki typing hui hai
                nameField.dispatchEvent(new Event('input', { bubbles: true }));
                nameField.dispatchEvent(new Event('change', { bubbles: true }));
                nameField.dispatchEvent(new Event('blur', { bubbles: true }));
                console.log('Forceful Name Fill Done');
            }
        """)
        time.sleep(3)

        # STEP 3: FORCEFUL ENTER STUDIO CLICK
        print("Step 3: Force-clicking Enter Studio...")
        driver.execute_script("""
            let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                el.textContent.includes('Enter studio')
            );
            if(enterBtn) {
                // Button ko forcefully enable karke click karna
                enterBtn.disabled = false;
                enterBtn.click();
                console.log('Force Entry Clicked');
            }
        """)
        
        # Backup: Agar JS click fail hua toh Selenium se Enter press karna
        try:
            name_field = driver.find_element(By.TAG_NAME, "input")
            name_field.send_keys(Keys.ENTER)
        except:
            pass

        print("Waiting for Studio load...")
        time.sleep(25) 

        # STEP 4: AUTO-ADD TO STAGE (Background loop)
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

        # FFmpeg Start
        ffmpeg_cmd = [
            'ffmpeg', '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p', '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Streaming is active. Check YouTube!")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Main Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
