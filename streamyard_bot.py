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
    
    # Permissions Bypass (Mic, Camera aur saari automatic popups bypass flags)
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
        print("Opening StreamYard Room...")
        driver.get(GUEST_URL)
        
        # Initial loading time
        time.sleep(8)

        # STEP 1 & 2: FULL FORCE AUTOMATION (Jab tak naam na likha jaye, sab kuch click karo)
        print("Starting Force-Click Loop until Name Box is found...")
        driver.execute_script("""
            let nameFilled = false;

            let forceInterval = setInterval(() => {
                // 1. Sabse pehle dhoondho ki kya Name Input Box screen par aa gaya hai?
                let nameInput = document.getElementById('name') || 
                                document.querySelector('input[name="name"]') || 
                                document.querySelector('input[placeholder*="name"]') ||
                                document.querySelector('input[type="text"]');
                
                if (nameInput && !nameFilled) {
                    console.log('Target Achieved: Name input field found!');
                    nameInput.focus();
                    
                    // Urdu to English Fallback text insertion
                    nameInput.value = 'فیض';
                    nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                    nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Safely check if Urdu script is retained, otherwise fallback to English
                    setTimeout(() => {
                        if (!nameInput.value || nameInput.value.trim() === "") {
                            nameInput.value = 'Faiz';
                            nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                            nameInput.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }, 500);

                    nameFilled = true; // Loop ko pata chal gaya naam likh diya hai
                    
                    // Naam likhne ke thik 1.5 second baad Enter button par final click
                    setTimeout(() => {
                        let finalButtons = Array.from(document.querySelectorAll('button'));
                        let enterBtn = finalButtons.find(el => 
                            el.textContent.includes('Enter studio') || 
                            el.textContent.includes('Enter') ||
                            el.getAttribute('type') === 'submit'
                        );
                        if (enterBtn) {
                            enterBtn.click();
                            console.log('Successfully Entered Studio Room.');
                            clearInterval(forceInterval); // Loop ko stop karo jab kaam poora ho jaye
                        } else {
                            let form = nameInput.closest('form');
                            if(form) {
                                form.submit();
                                clearInterval(forceInterval);
                            }
                        }
                    }, 1500);

                } else if (!nameFilled) {
                    // 2. Agar Name Box abhi tak nahi aaya, toh raaste me jo bhi button dikhe usko click maro (Continue, Allow, etc.)
                    let currentButtons = Array.from(document.querySelectorAll('button'));
                    currentButtons.forEach(btn => {
                        let txt = btn.innerText.toLowerCase();
                        // Har us button ko click karo jo next page par le jaye, mic-cam validation bypass kare ya welcome door khole
                        if(txt.includes('continue') || txt.includes('allow') || txt.includes('accept') || txt.includes('got it')) {
                            btn.click();
                            console.log('Force Clicked Element: ' + txt);
                        }
                    });
                }
            }, 2500); // Har 2.5 second me screen scan aur force-action hoga
        """)
        
        # Studio ke load hone ke liye safe transition wait
        print("Waiting for studio workspace to synchronize...")
        time.sleep(30) 

        # STEP 3: STUDIO KE ANDAR AUTOMATIC ADD TO STAGE
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
                    addBtn.click();
                    console.log('Bot added to stage.');
                }
            }, 5000);
        """)

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
        print("Bot sequence working flawlessly. Check status.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
