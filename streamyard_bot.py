import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

        # STEP 1: BACKGROUND POPUP CLEARER (JavaScript background me chalta rahega)
        print("Starting background popup clearer...")
        driver.execute_script("""
            window.popupClearerInterval = setInterval(() => {
                let nameInput = document.getElementById('name') || 
                                document.querySelector('input[placeholder*="name"]') || 
                                document.querySelector('input[type="text"]');
                
                // Agar naam wala box abhi tak nahi aaya, tabhi tak baaki buttons click karo
                if (!nameInput) {
                    let buttons = Array.from(document.querySelectorAll('button'));
                    buttons.forEach(btn => {
                        let txt = btn.innerText.toLowerCase();
                        if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                            btn.click();
                            console.log('Cleared overlay button: ' + txt);
                        }
                    });
                } else {
                    // Jab naam ka box mil jaye, toh popups hatana band kar do taaki input refresh na ho
                    clearInterval(window.popupClearerInterval);
                }
            }, 1500);
        """)

        # STEP 2: NATIVE PYTHON NAME ENTRY (Yeh 100% naam likhega hi likhega)
        print("Waiting for Name Input field via Selenium native locator...")
        
        # Maximize wait time up to 30 seconds jab tak input box real me screen par visible na ho jaye
        wait = WebDriverWait(driver, 30)
        name_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='name'], input#name, input[type='text']")))
        
        print("Name field detected! Typing name using native keys...")
        time.sleep(2) # Stabilize hone ke liye chhota wait
        
        name_field.click() # Element par physically click karo
        name_field.clear() # Agar pehle se kuch kachra likha ho toh clear karo
        name_field.send_keys("Faiz") # Keyboard emulation se 'Faiz' type karo (Yeh kabhi fail nahi hota)
        
        print("Name filled successfully. Waiting 3 seconds for React validation...")
        time.sleep(3)

        # STEP 3: NATIVE ENTER STUDIO CLICK
        print("Locating Enter Studio button...")
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enter studio') or contains(text(), 'Enter') or @type='submit']")))
        
        print("Clicking Enter Studio button natively...")
        enter_button.click()
        
        print("Waiting for studio environment to load fully...")
        time.sleep(30) 

        # STEP 4: REPETITIVE AUTO-ADD TO STAGE (Studio ke andar)
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
        print(f"Error encountered: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
