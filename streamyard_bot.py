import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
# 1. Apna StreamYard Guest Invite Link yahan dalein
GUEST_URL = "https://streamyard.com/3r8zzr4cbk" 
# 2. YouTube Stream Key (GitHub Secrets se aayegi)
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Permissions aur Automation Bypass
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(12)

        # STEP 1: COOKIES & PERMISSIONS (Smart Bypass)
        driver.execute_script("""
            function bypassInitial() {
                let btns = Array.from(document.querySelectorAll('button'));
                btns.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    // Sirf setup buttons ko click karega
                    if(txt === 'accept' || txt === 'continue' || txt === 'allow mic/cam access' || txt === 'got it') {
                        btn.click();
                        console.log('Bypassed: ' + txt);
                    }
                });
            }
            bypassInitial();
            setTimeout(bypassInitial, 4000);
        """)
        time.sleep(10)

        # STEP 2: NAME ENTRY & CONTROLLED ENTRY (Error Fix)
        driver.execute_script("""
            let nameInput = document.querySelector('input[name="displayName"]') || 
                           document.querySelector('input[placeholder*="name"]') || 
                           document.querySelector('input');

            if(nameInput) {
                // Naam likhna aur browser ko batana ki typing hui hai
                nameInput.value = 'فیض'; 
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Name Filled');

                // Naam likhne ke 2 second baad hi Enter click hoga
                setTimeout(() => {
                    let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                        el.textContent.includes('Enter studio') || el.textContent.includes('Check')
                    );
                    if(enterBtn && nameInput.value !== "") {
                        enterBtn.click();
                        console.log('Entering Studio...');
                    }
                }, 2000);
            }
        """)
        
        print("Finalizing Studio Entry...")
        time.sleep(25) # Studio load hone ka wait

        # STEP 3: AUTO-ADD TO STAGE (Background Loop)
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                let removeBtn = btns.find(b => b.innerText.includes('Remove'));
                // Agar 'Add to stage' dikh raha hai aur 'Remove' nahi, tabhi click karo
                if (addBtn && !removeBtn) {
                    addBtn.click();
                    console.log('Added to stage');
                }
            }, 5000);
        """)

        # STEP 4: FFmpeg Streaming
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
        print("Bot is LIVE. Run time: 5h 55m.")
        
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
