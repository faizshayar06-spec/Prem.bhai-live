import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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

        # STEP 1: FORCE CLICK EVERYTHING (Timers are saved to window object)
        driver.execute_script("""
            function clickAnything() {
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                        console.log('Bypassed: ' + txt);
                    }
                });
            }
            clickAnything();
            window.t1 = setTimeout(clickAnything, 3000);
            window.t2 = setTimeout(clickAnything, 6000);
        """)
        time.sleep(10)

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
        
        # STEP 2.1: PURANE JAVA WORKFLOW KO POORI TARAH STOP KARNA
        print("Killing previous background timeouts to secure name field state...")
        driver.execute_script("""
            clearTimeout(window.t1);
            clearTimeout(window.t2);
            console.log('All initial background scripts destroyed successfully.');
        """)
        
        time.sleep(2) # State freeze karne ke liye chhota buffer wait

        # STEP 2.2: FORCEFULLY CLICK ENTER STUDIO VIA NATIVE KEYSTROKE OR BUTTON ACTION
        print("Executing clean manual Enter Studio action via JavaScript...")
        driver.execute_script("""
            let nameInput = document.getElementById('name') || document.querySelector('input');
            let buttons = Array.from(document.querySelectorAll('button'));
            let enterBtn = buttons.find(el => 
                el.textContent.includes('Enter studio') || 
                el.textContent.includes('Enter') ||
                el.getAttribute('type') === 'submit'
            );
            
            if (enterBtn) {
                enterBtn.click();
                console.log('Enter Studio button force clicked.');
            } else if (nameInput) {
                // Agar button target na ho paye, toh active element par form submit push karo
                let form = nameInput.closest('form');
                if(form) form.submit();
            }
        """)
        
        print("Bypass operation done. Transitioning to inside the studio...")
        time.sleep(25) # Studio properly load hone tak ka wait

        # STEP 3: REPETITIVE AUTO-ADD TO STAGE (Studio ke andar jane ke baad kaam karega)
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
    
