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

        # SINGLE MASTER SEQUENTIAL JAVASCRIPT
        print("Starting Controlled Step-by-Step JavaScript Sequence...")
        driver.execute_script("""
            let currentStep = 1; 
            console.log('Master Step Controller Initialized.');

            let workflowInterval = setInterval(() => {
                let buttons = Array.from(document.querySelectorAll('button'));
                
                // STEP 1: COOKIES ACCEPTANCE (Agar screen par dikhe toh turant bypass karo)
                let cookieBtn = buttons.find(b => {
                    let t = b.innerText.toLowerCase();
                    return t.includes('accept all') || t.includes('accept cookies') || t.includes('all cookies');
                });
                if (cookieBtn) {
                    cookieBtn.click();
                    console.log('Step 1 Complete: Cookies Accepted.');
                }

                // STEP 2: WELCOME / CONTINUE PAGE BYPASS
                if (currentStep === 1) {
                    let continueBtn = buttons.find(b => {
                        let t = b.innerText.toLowerCase();
                        return t.includes('continue') || t.includes('got it') || t.includes('allow access');
                    });
                    if (continueBtn) {
                        continueBtn.click();
                        console.log('Step 2 Complete: Clicked Continue/Welcome Bypass.');
                        currentStep = 2; // Move to next step safely
                    }
                }

                // STEP 3: NAME INPUT FIELD FILLING (Aapka original working logic untouched)
                if (currentStep === 2) {
                    let nameInput = document.getElementById('name') || 
                                    document.querySelector('input[placeholder*="name"]') || 
                                    document.querySelector('input');
                    if (nameInput) {
                        nameInput.focus();
                        nameInput.value = 'Faiz'; 
                        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                        nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Step 3 Complete: Name field securely locked with Faiz.');
                        currentStep = 3; // Move to final click stage
                    }
                }

                // STEP 4: DELIBERATE ENTER STUDIO EXECUTION
                if (currentStep === 3) {
                    // Small internal timeout taaki input framework process ho sake
                    setTimeout(() => {
                        let enterBtn = buttons.find(el => 
                            el.textContent.includes('Enter studio') || 
                            el.textContent.includes('Enter') ||
                            el.getAttribute('type') === 'submit'
                        );
                        
                        if (enterBtn) {
                            enterBtn.focus();
                            enterBtn.click();
                            console.log('Step 4 Complete: Force Clicked Enter Studio!');
                            clearInterval(workflowInterval); // Poora sequence khatam, loop stop!
                        }
                    }, 2000); // 2 second ka gap naam fill hone aur enter dabne ke beech
                    currentStep = 4;
                }

            }, 1500); // Har 1.5 second me system state machine check karega
        """)
        
        print("Sequence is running perfectly in background. Transitioning to studio room...")
        time.sleep(35) # Studio properly load hone tak ka pure wait time

        # NOTE: AAPKE KEHNE PAR 'ADD TO STAGE' LOOP KO COMPLETELY YAHA SE HTA DIYA HAI.

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
        print("Bot stream successfully initialized. Check YouTube dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
