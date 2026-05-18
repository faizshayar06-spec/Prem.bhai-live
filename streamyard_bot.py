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

        # STEP 1 & 2: SINGLE MAIN LOOP (Bypass -> Fill Name -> Wait -> Enter Studio)
        print("Running unified JavaScript workflow loop...")
        driver.execute_script("""
            let nameFilled = false;
            let studioEntered = false;

            let mainWorkflow = setInterval(() => {
                // 1. Sabse pehle check karo kya Display Name box aa gaya hai?
                let nameInput = document.getElementById('name') || 
                                document.querySelector('input[placeholder*="name"]') || 
                                document.querySelector('input[type="text"]');
                
                if (nameInput) {
                    // Agar name input mil gaya aur abhi tak naam nahi likha hai, toh naam likho
                    if (!nameFilled) {
                        nameInput.focus();
                        nameInput.value = 'Faiz';
                        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                        nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Name field filled with Faiz.');
                        nameFilled = true;

                        # Naam likhne ke thik 3 second baad Enter Studio par click hoga
                        setTimeout(() => {
                            let buttons = Array.from(document.querySelectorAll('button'));
                            let enterBtn = buttons.find(el => 
                                el.textContent.includes('Enter studio') || 
                                el.textContent.includes('Enter') ||
                                el.getAttribute('type') === 'submit'
                            );
                            
                            if (enterBtn && !studioEntered) {
                                enterBtn.click();
                                console.log('Successfully clicked Enter Studio!');
                                studioEntered = true;
                                clearInterval(mainWorkflow); // Kaam poora hone par loop band karo
                            }
                        }, 3000);
                    }
                } else {
                    // 2. Agar naam wala box nahi aaya, toh raste ke baaki buttons (Cookies/Continue) clear karo
                    let buttons = Array.from(document.querySelectorAll('button'));
                    buttons.forEach(btn => {
                        let txt = btn.innerText.toLowerCase();
                        if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                            btn.click();
                            console.log('Force Clicked Element: ' + txt);
                        }
                    });
                }
            }, 2000); // Har 2 second mein poori screen scan hogi
        """)
        
        print("Waiting for studio entry to complete...")
        time.sleep(35) # Studio ke andar set hone ka safe wait time

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
    
