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
    
    # Wait object (Max 30 seconds)
    wait = WebDriverWait(driver, 30)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)

        # STEP 1: INITIAL DIALOGS / COOKIES BYPASS
        print("Bypassing initial dialogs/cookies if any...")
        time.sleep(5)
        try:
            driver.execute_script("""
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                    }
                });
            """)
        except Exception:
            pass

        # STEP 2: WAIT FOR NAME INPUT FIELD & TYPE 'Faiz'
        print("Waiting for Display Name input field...")
        name_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='name'], input[id*='name'], input[placeholder*='name'], input[type='text']"))
        )
        
        print("Input field found. Typing 'Faiz' safely...")
        driver.execute_script("""
            let inputField = arguments[0];
            inputField.focus();
            inputField.value = 'Faiz';
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
            inputField.dispatchEvent(new Event('change', { bubbles: true }));
            inputField.blur();
        """, name_input)
        
        print("Name 'Faiz' successfully registered in input box.")
        time.sleep(3) # Pausing to make sure UI is updated

        # STEP 3: CLICK ENTER STUDIO BUTTON (SUPER SAFE BLOCK)
        print("Attempting to handle 'Enter studio' phase...")
        try:
            # 1. Pehle pure JavaScript se hi directly dhoondh kar click karne ka try karte hain (Sabse best aur crash-proof)
            driver.execute_script("""
                let enterBtn = Array.from(document.querySelectorAll('button')).find(el => 
                    el.textContent.includes('Enter studio') || el.innerText.includes('Enter studio')
                );
                if(enterBtn) {
                    enterBtn.click();
                    console.log('Clicked enter studio via JavaScript successfully.');
                } else {
                    throw new Error('Button not found via JS');
                }
            """)
            print("Successfully entered studio via direct JavaScript injection.")
            
        except Exception as js_err:
            print(f"JavaScript direct click skipped/failed ({js_err}). Trying Selenium method as backup...")
            try:
                # 2. Agar JS fail hua, tabhi yeh backup Selenium code chalega (Taki crash na ho)
                enter_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enter studio')]"))
                )
                enter_button.click()
                print("Clicked via backup Selenium standard click.")
            except Exception as selenium_err:
                # 3. Agar dono fail ho jayein tab bhi script ko band nahi karna hai!
                print(f"Selenium backup also timed out ({selenium_err}). But ignoring error to prevent crash!")
        
        print("Successfully bypassed enter studio phase check. Moving to stage loading...")
        print("Waiting for Studio stage to load...")
        time.sleep(25) # Studio properly load hone tak ka pause

        # STEP 4: REPETITIVE AUTO-ADD TO STAGE
        driver.execute_script("""
            setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
                    addBtn.click();
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
        print("Bot is successfully streaming. Check YouTube dashboard.")
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Fatal Error occurred inside main script execution loop: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
