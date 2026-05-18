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

        # SINGLE POWERFUL JAVASCRIPT MASTER LOOP TO CONTROL EVERYTHING
        print("Starting JavaScript Master Engine...")
        driver.execute_script("""
            let nameFilled = false;
            let studioEntered = false;

            let masterInterval = setInterval(() => {
                // 1. Check karo kya Display Name ka input box screen par aa gaya hai?
                let nameInput = document.getElementById('name') || 
                                document.querySelector('input[placeholder*="name"]') || 
                                document.querySelector('input[type="text"]');
                
                if (nameInput) {
                    // Agar name box mil gaya aur abhi tak naam nahi bhara hai
                    if (!nameFilled) {
                        nameInput.focus();
                        
                        // React State compatibility trigger ke saath naam fill karna
                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(nameInput, 'Faiz');
                        
                        // React ko batane ke liye input events fire karna
                        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                        nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        console.log('Name field forcefully filled with Faiz via React setter.');
                        nameFilled = true;

                        // Naam fill hone ke thik 2 seconds baad Enter Studio click hoga
                        setTimeout(() => {
                            let buttons = Array.from(document.querySelectorAll('button'));
                            let enterBtn = buttons.find(el => 
                                el.textContent.includes('Enter studio') || 
                                el.textContent.includes('Enter') ||
                                el.getAttribute('type') === 'submit'
                            );
                            
                            if (enterBtn && !studioEntered) {
                                enterBtn.click();
                                console.log('Successfully Force Clicked Enter Studio!');
                                studioEntered = true;
                                clearInterval(masterInterval); // Kaam khatam, loop close!
                            }
                        }, 2000);
                    }
                } else {
                    // 2. Jab tak naam wala box nahi dikhta, tab tak saare popups (Cookie/Continue) clear karo
                    let buttons = Array.from(document.querySelectorAll('button'));
                    buttons.forEach(btn => {
                        let txt = btn.innerText.toLowerCase();
                        if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                            btn.click();
                            console.log('Cleared popup/overlay: ' + txt);
                        }
                    });
                }
            }, 1500); // Har 1.5 second mein loop lagatar poore page ko check karega
        """)
        
        print("Master workflow is running... Waiting for studio entry.")
        time.sleep(35) # Lobby se main studio ke andar aane tak ka wait time

        # STEP 3: REPETITIVE AUTO-ADD TO STAGE (Studio ke andar)
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
        print("Bot is streaming successfully. Check YouTube dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
