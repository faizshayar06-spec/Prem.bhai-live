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

        # STEP 1: FORCE CLICK EVERYTHING (Cookies, Continue, Allow bypass karne ke liye JavaScript)
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
            // 3 baar check karega intervals mein taaki welcome screens clear ho jayein
            clickAnything();
            setTimeout(clickAnything, 3000);
            setTimeout(clickAnything, 6000);
        """)
        time.sleep(10)

        # STEP 2: NAME ENTRY AND AUTOMATIC ENTER STUDIO CLICK (With Safe Delay)
        print("Filling English name in the input field and queueing enter studio...")
        driver.execute_script("""
            let nameInput = document.getElementById('name') || 
                            document.querySelector('input[placeholder*="name"]') || 
                            document.querySelector('input');
            if(nameInput) {
                nameInput.focus();
                nameInput.value = 'Faiz'; // Aapka sahi chalne wala English naam
                nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Name field locked and filled with Faiz.');

                // NAAM LIKHNE KE THIK 5 SECONDS BAAD ENTER STUDIO PAR AUTOMATIC CLICK HOGA
                setTimeout(() => {
                    let buttons = Array.from(document.querySelectorAll('button'));
                    let enterBtn = buttons.find(el => 
                        el.textContent.includes('Enter studio') || 
                        el.textContent.includes('Enter') ||
                        el.getAttribute('type') === 'submit'
                    );
                    
                    if (enterBtn) {
                        enterBtn.click();
                        console.log('Successfully clicked Enter Studio button.');
                    } else {
                        // Agar button nahi milta toh form submit fallback trigger hoga
                        let form = nameInput.closest('form');
                        if(form) form.submit();
                    }
                }, 5000); // 5000ms = 5 seconds ka safe wait time nominal entry ke liye
            }
        """)
        
        print("Waiting for studio environment to load fully...")
        time.sleep(25) # Studio ke andar enter hone ka wait

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
    
