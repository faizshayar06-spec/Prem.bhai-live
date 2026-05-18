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
        time.sleep(5)

        # STEP-BY-STEP SEQUENTIAL MASTER JAVASCRIPT CONTROLLER
        print("Deploying Strict Step-by-Step State Machine...")
        driver.execute_script("""
            let currentStep = 1; 
            console.log('Sequential State Engine Active.');

            let masterSequence = setInterval(() => {
                let buttons = Array.from(document.querySelectorAll('button'));
                
                // OPTIONAL FAIL-SAFE: Baar-baar cookies check karna agar beech me aaye toh
                let cookieBtn = buttons.find(b => {
                    let t = b.innerText.toLowerCase();
                    return t.includes('accept all') || t.includes('accept cookies') || t.includes('all cookies');
                });
                if (cookieBtn) {
                    cookieBtn.click();
                    console.log('Cookies cleared in background.');
                }

                // STEP 1: CLICK "ALLOW MIC/CAM ACCESS" BUTTON (Screenshot stage)
                if (currentStep === 1) {
                    let allowBtn = buttons.find(b => {
                        let t = b.innerText.toLowerCase();
                        return t.includes('allow mic/cam access') || t.includes('allow mic') || t.includes('allow access') || t.includes('continue');
                    });
                    
                    if (allowBtn) {
                        allowBtn.click();
                        console.log('Step 1 Complete: Clicked Allow mic/cam access button!');
                        currentStep = 2; // Agle step par shift ho jao
                    }
                }

                // STEP 2: WAIT FOR NAME FIELD TO RENDER & FILL NAME (Aapka untouched 100% working login trigger)
                if (currentStep === 2) {
                    let nameInput = document.getElementById('name') || 
                                    document.querySelector('input[placeholder*="name"]') || 
                                    document.querySelector('input');
                    if (nameInput) {
                        nameInput.focus();
                        nameInput.value = 'Faiz'; 
                        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                        nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Step 2 Complete: Name successfully filled with Faiz without dropping state.');
                        currentStep = 3; // Click phase par move karo
                    }
                }

                // STEP 3: SAFELY TRIGGER ENTER STUDIO BUTTON AFTER VALIDATION
                if (currentStep === 3) {
                    setTimeout(() => {
                        let enterBtn = buttons.find(el => 
                            el.textContent.includes('Enter studio') || 
                            el.textContent.includes('Enter') ||
                            el.getAttribute('type') === 'submit'
                        );
                        
                        if (enterBtn) {
                            enterBtn.focus();
                            enterBtn.click();
                            console.log('Step 3 Complete: Force Clicked Enter Studio button clean!');
                            clearInterval(masterSequence); // Poora logic successfully run ho gaya, loop destroy karo!
                        }
                    }, 2000); // 2 second ka gap naam stable karne ke liye
                    currentStep = 4;
                }

            }, 1500); // Har 1.5 second me logic array evaluate hoga step-by-step
        """)
        
        print("Sequential controller is processing the steps... Redirecting to studio lobby.")
        time.sleep(35) # Live room aur workspace fully render hone tak ka wait time

        # NOTE: AAPKE KEHNE PAR 'ADD TO STAGE' LOOP POORI TARAH YAHA SE DETACHED HAI.

        # FFmpeg Section
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Pipeline streaming active. Monitor YouTube Dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
