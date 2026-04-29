import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/3r8zzr4cbk" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    # Agar server pe ho toh screen setup zaroori hai
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    actions = ActionChains(driver)
    
    try:
        print("Bot Restarted...")
        driver.get(GUEST_URL)
        time.sleep(12)

        # STEP 1 & 2: Cookies aur Continue (JS handles this well)
        driver.execute_script("""
            let btns = Array.from(document.querySelectorAll('button'));
            let cb = btns.find(el => el.innerText.includes('Accept') || el.innerText.includes('Continue'));
            if(cb) cb.click();
        """)
        time.sleep(10)

        # STEP 4: COORDINATE BASED CLICK & TYPE
        print("Step 4: Finding Name field position and typing...")
        
        try:
            # Name field dhoondo
            name_field = driver.find_element(By.CSS_SELECTOR, 'input[name="displayName"]')
            
            # ActionChains se element ke center pe move karo aur click karo
            # Ye JS injection se zyada "Human-like" hai
            actions.move_to_element(name_field).click().perform()
            time.sleep(1)
            
            # Type name character by character
            for char in "Faiz":
                actions.send_keys(char).perform()
                time.sleep(0.2)
            
            time.sleep(1)
            actions.send_keys(Keys.ENTER).perform()
            print("Name Entered via ActionChains.")
            
        except Exception as e:
            print(f"ActionChains failed: {e}. Trying absolute coordinates backup...")
            # Backup: Agar aap display 0 ya 99 par hain, toh input field 
            # StreamYard mein lagbhag screen ke center mein hoti hai.
            # coordinates: x=960, y=600 (approx for 1080p)
            actions.move_by_offset(960, 550).click().perform() 
            time.sleep(1)
            actions.send_keys("Faiz").send_keys(Keys.ENTER).perform()

        print("Entering Studio...")
        time.sleep(20) 

        # STEP 5: AUTO-ADD TO STAGE (Running in background)
        driver.execute_script("""
            window.stageInterval = setInterval(() => {
                let addBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Add to stage'));
                if (addBtn) addBtn.click();
            }, 5000);
        """)

        # FFmpeg process...
        # ... (rest of your ffmpeg code)

    except Exception as e:
        print(f"Main Error: {e}")
    finally:
        # driver.quit() # Testing ke waqt band mat karo check karne ke liye
        pass

if __name__ == "__main__":
    start_stream()
