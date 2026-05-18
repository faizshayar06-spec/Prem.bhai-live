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

        # NEW MASTER CONTROL: OVERLAY BYPASS & STEP-BY-STEP CONTROLLER
        print("Deploying Strict Step-by-Step State Machine with Permission Override...")
        driver.execute_script("""
            // Force browser API level permissions bypass
            if (navigator.permissions && navigator.permissions.query) {
                navigator.permissions.query = (auth) => {
                    return Promise.resolve({ state: 'granted', onchange: null });
                };
            }

            let currentStep = 1; 
            console.log('Sequential State Engine Active.');

            let masterSequence = setInterval(() => {
                let buttons = Array.from(document.querySelectorAll('button'));
                
                // BACKUP: Cookies clear check
                let cookieBtn = buttons.find(b => {
                    let t = b.innerText.toLowerCase();
                    return t.includes('accept all') || t.includes('accept cookies') || t.includes('all cookies');
                });
                if (cookieBtn) {
                    cookieBtn.click();
                }

                # STEP 1: FORCE OVERRIDE "ALLOW MIC/CAM ACCESS"
                if (currentStep === 1) {
                    let allowBtn = buttons.find(b => {
                        let t = b.innerText.toLowerCase();
                        return t.includes('allow mic/cam') || t.includes('allow mic') || t.includes('allow access') || t.includes('continue');
                    });
                    
                    if (allowBtn) {
                        allowBtn.focus();
                        allowBtn.click();
                        console.log('Step 1: Clicked Allow mic/cam access.');
                    }
                    
                    // Fail-safe: 3 second baad agle step par automatically push karega agar overlay change na ho
                    setTimeout(() => { currentStep = 2; }, 3000);
                }

                # STEP 2: NAME FIELD INJECTION (Aapka untouched working login block)
                if (currentStep === 2) {
                    let nameInput = document.getElementById('name') || 
                                    document.querySelector('input[placeholder*="name"]') || 
                                    document.querySelector('input');
                    if (nameInput) {
                        nameInput.focus();
                        nameInput.value = 'Faiz'; 
                        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                        nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Step 2: Name filled with Faiz securely.');
                        currentStep = 3;
                    }
                }

                # STEP 3: RE-ENABLE BUTTON & FORCE CLICK ENTER STUDIO
                if (currentStep === 3) {
                    setTimeout(() => {
                        let enterBtn = buttons.find(el => 
                            el.textContent.includes('Enter studio') || 
                            el.textContent.includes('Enter') ||
                            el.getAttribute('type') === 'submit'
                        );
                        
                        if (enterBtn) {
                            // Agar button browser restriction ki wajah se disabled lock hai, toh use force unlock karo
                            enterBtn.removeAttribute('disabled');
                            enterBtn.disabled = false;
                            
                            enterBtn.focus();
                            enterBtn.click();
                            console.log('Step 3: Forced unlock and Clicked Enter Studio button!');
                            clearInterval(masterSequence); // Sequence over, stop loop!
                        }
                    }, 2000); // 2 second pause state transition ke liye
                    currentStep = 4;
                }

            }, 1500);
        """)
        
        print("Sequence engine is successfully handling stages. Transitioning to studio workspace...")
        time.sleep(35) # Live room workspace render hone tak ka wait time

        # NOTE: AAPKE KEHNE PAR 'ADD TO STAGE' LOOP COMPLETELY DETACHED HAI

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
        print("Streaming sequence activated inside studio. Track YouTube dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
