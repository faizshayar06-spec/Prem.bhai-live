import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/6ihfwcdmwx" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless=new")  # GitHub Actions ke liye headless mode secure rahega
    
    # Permissions & Automation Bypass
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1, 
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1
    })

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # GitHub Actions par thoda extra wait time (30 seconds max) secure rahega
    wait = WebDriverWait(driver, 30)
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)
        
        # --- STEP 1: COOKIES & INITIAL ALLOW BUTTONS ---
        print("Checking for Initial Prompts / Cookies...")
        time.sleep(8) # Elements ko background me load hone ka time diya
        driver.execute_script("""
            let setupButtons = Array.from(document.querySelectorAll('button, [role="button"]'));
            let targetBtn = setupButtons.find(b => {
                let t = b.innerText.toLowerCase();
                return t.includes('accept') || t.includes('got it') || t.includes('cookies') || t.includes('allow');
            });
            if (targetBtn) {
                targetBtn.click();
                console.log('Initial overlay handled');
            }
        """)
        
        # --- STEP 2: NAME ENTRY (FAIL-PROOF) ---
        print("Locating Display Name Field...")
        
        # Change: Yahan presence_of_element_located ki jagah element_to_be_clickable use kiya hai
        name_input = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "input[name='displayName'], input[placeholder*='name'], input[type='text']"
        )))
        
        # Element screen par click aur focal center me aaye, uske liye extra sleep aur click trigger
        time.sleep(3)
        name_input.click() 
        name_input.clear()
        
        print("Entering Name: فیض")
        # Direct fallback pure JS input taaki 'not interactable' error completely bypass ho jaye
        driver.execute_script("""
            let inputField = arguments[0];
            inputField.focus();
            inputField.value = 'فیض';
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
            inputField.dispatchEvent(new Event('change', { bubbles: true }));
        """, name_input)
        
        time.sleep(3) # Input dynamic register hone ka delay

        # --- STEP 3: CLICK ENTER STUDIO ---
        print("Locating Enter Studio Button...")
        driver.execute_script("""
            let entryButtons = Array.from(document.querySelectorAll('button'));
            let enterStudioBtn = entryButtons.find(el => 
                el.textContent.includes('Enter studio') || 
                el.textContent.includes('Enter Studio') ||
                el.textContent.includes('Check your audio')
            );
            if(enterStudioBtn) {
                enterStudioBtn.click();
                console.log('Clicked Enter Studio');
            } else {
                let secondaryBtn = document.querySelector('button[type="submit"]');
                if(secondaryBtn) secondaryBtn.click();
            }
        """)
        
        print("Waiting for Studio Interface to fully load...")
        time.sleep(25) 

        # --- STEP 4: STAGE PERSISTENCE (LOOP) ---
        print("Starting Loop for 'Add to stage' enforcement...")
        driver.execute_script("""
            window.stageEnforcer = setInterval(() => {
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
                    addBtn.click();
                    console.log('Enforced: Added to stage');
                }
            }, 5000);
        """)

        # --- STEP 5: FFMPEG STREAM TRANSMISSION ---
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '4000k',
            '-pix_fmt', 'yuv420p',
            '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        print("Starting FFmpeg background pipe...")
        process = subprocess.Popen(ffmpeg_cmd)
        print("Streaming active. Monitoring engine uptime...")
        
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Execution Error Encountered: {e}")
    finally:
        print("Closing browser context...")
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
