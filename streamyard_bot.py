import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/6ihfwcdmwx" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Permissions Bypass (FORCE FLAGS)
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1, 
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1
    })

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(10)

        # STEP 1: COOKIES & CONTINUE BYPASS (Is loop ko control me lene ke liye window variable banaya hai)
        driver.execute_script("""
            window.bypassManager = setInterval(function() {
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                        console.log('Bypassed loop event: ' + txt);
                    }
                });
            }, 2500);
        """)
        
        # Safe wait jab tak naam wale page par na pahunche
        time.sleep(12)

        # STEP 2: NAME ENTRY ONLY (Aapka original 100% working code - UNTOUCHED)
        print("Filling English name in the input field...")
        driver.execute_script("""
            let nameInput = document.getElementById('name') || 
                            document.querySelector('input[placeholder*="name"]') || 
                            document.querySelector('input');
            if(nameInput) {
                nameInput.focus();
                nameInput.value = 'Faiz'; 
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Name field locked and filled with Faiz.');
            }
        """)
        
        # NAAM LIKHNE KE THIK BAAD - PURANI JAVASCRIPT KO ROKNA
        print("Stopping previous background JavaScript loops to freeze the name state...")
        driver.execute_script("""
            if (window.bypassManager) {
                clearInterval(window.bypassManager);
                console.log('Background bypass loop successfully stopped!');
            }
        """)
        
        # Ab state freeze ho chuki hai, 3 second ka wait taaki form button blue ho jaye
        time.sleep(3) 

        # STEP 3: MANUALLY FORM ENTER CLICK (Bina JS interference ke safe submission)
        print("Executing clean Enter Studio execution...")
        driver.execute_script("""
            let buttons = Array.from(document.querySelectorAll('button'));
            let enterBtn = buttons.find(el => 
                el.textContent.includes('Enter studio') || 
                el.textContent.includes('Enter') ||
                el.getAttribute('type') === 'submit'
            );
            
            if(enterBtn) {
                enterBtn.click();
                console.log('Studio entered cleanly.');
            } else {
                // Agar button direct click kaam na kare toh native HTML submit trigger karo
                let nameInput = document.getElementById('name') || document.querySelector('input');
                if(nameInput) {
                    let form = nameInput.closest('form');
                    if(form) form.submit();
                }
            }
        """)
        
        print("Successfully sent enter command. Syncing with studio lobby...")
        time.sleep(25) 

        # STEP 4: REPETITIVE AUTO-ADD TO STAGE (Studio ke andar)
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
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Bot is doing its job. Check YouTube dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
