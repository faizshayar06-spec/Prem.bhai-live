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
    
    # Permissions Bypass (Camera, Mic aur Autoplay force allow karne ke liye)
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
        
        # Green room page load hone ke liye wait karein
        time.sleep(12)

        # STEP 1: COOKIES YA INITIAL POPUPS KO AUTOMATIC HANDLE KARNA
        driver.execute_script("""
            function clearPopups() {
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('cookie') || txt.includes('got it')) {
                        btn.click();
                        console.log('Cleared popup: ' + txt);
                    }
                });
            }
            clearPopups();
        """)
        time.sleep(3)

        # STEP 2: NAME ENTRY AUR ENTER STUDIO (Urdu to English Fallback Ke Saath)
        print("Entering name with fallback mechanism...")
        driver.execute_script("""
            function fillNameAndEnter() {
                let nameInput = document.getElementById('name') || 
                                document.querySelector('input[name="name"]') || 
                                document.querySelector('input[placeholder*="Display name"]') ||
                                document.querySelector('input[type="text"]');
                
                if (nameInput) {
                    nameInput.focus();
                    
                    // 1. Pehle Urdu naam try karte hain
                    nameInput.value = 'فیض';
                    nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                    nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('Tried filling Urdu name.');

                    // 2. 1.5 second baad check karenge agar characters support nahi hue ya invalid raha
                    setTimeout(() => {
                        // Agar input khali reh gaya ya form ne block kiya, toh English standard try karo
                        if (!nameInput.value || nameInput.value.trim() === "" || nameInput.classList.contains('invalid')) {
                            console.log('Urdu script not fully supported or blocked. Switching to English...');
                            nameInput.value = ''; 
                            nameInput.value = 'Faiz'; 
                            nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                            nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        }

                        // 3. Final submission (Naam fill hone ke baad strict Enter action)
                        setTimeout(() => {
                            let buttons = Array.from(document.querySelectorAll('button'));
                            let enterBtn = buttons.find(el => 
                                el.textContent.includes('Enter studio') || 
                                el.textContent.includes('Enter') ||
                                el.getAttribute('type') === 'submit'
                            );
                            
                            if (enterBtn) {
                                enterBtn.click();
                                console.log('Enter Studio button clicked.');
                            } else {
                                console.log('Button click failed, trying form submit fallback.');
                                let form = nameInput.closest('form');
                                if(form) form.submit();
                            }
                        }, 1000);

                    }, 1500);
                } else {
                    console.log('Name input field not found.');
                }
            }
            fillNameAndEnter();
        """)
        
        print("Waiting for studio environment to load fully...")
        time.sleep(25) # Studio ke andar enter hone ka safe buffer wait

        # STEP 3: AUTOMATIC ADD TO STAGE IF HOST HASN'T ADDED YET
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
                    addBtn.click();
                    console.log('Clicked Add to Stage button inside studio.');
                }
            }, 5000);
        """)

        # FFmpeg Screen Capture & RTMP Streaming Section
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        print("Bot automation successfully executed. Checking stream status...")
        
        # Stream running duration (approx 6 hours)
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
