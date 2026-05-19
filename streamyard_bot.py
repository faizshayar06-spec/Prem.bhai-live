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
GUEST_URL = "https://streamyard.com/nuch7yxfcu" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Screen size fix karni zaroori hai taaki coordinates exactly kaam karein
    chrome_options.add_argument("--window-size=1920,1080") 
    
    # Permissions Bypass
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
    wait = WebDriverWait(driver, 25) 
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)

        # STEP 1: FORCE CLICK POPUPS
        driver.execute_script("""
            function clickAnything() {
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                    }
                });
            }
            setInterval(clickAnything, 2000); 
        """)
        time.sleep(8)
        
        # STEP 2: ENTER NAME & STUDIO (Ye perfectly kaam kar raha tha)
        print("Waiting for visible Name input field...")
        input_xpath = "//input[not(@type='hidden')]"
        name_input = wait.until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
        name_input = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
        
        try:
            name_input.clear()
        except:
            pass 
        
        print("Typing name as a real human...")
        name_input.send_keys("Faiz")
        time.sleep(2) 

        print("Hunting for the 'Enter studio' button...")
        enter_button_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter studio')]"
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, enter_button_xpath)))
        enter_button.click()
        print("Successfully bypassed and entered the Studio! 🥀")

        # Studio load hone ka extra time (taaki video player poora aa jaye)
        time.sleep(12) 

        # STEP 3: THE ULTIMATE COORDINATE CLICK 🎯
        print("Executing exact coordinate click on the bottom-right corner... 🖥️")
        driver.execute_script("""
            function clickByCoordinates() {
                // 1. Screen par sabse bada div (Main Stage area) dhoondo
                let largestArea = 0;
                let stage = null;
                document.querySelectorAll('div').forEach(el => {
                    let r = el.getBoundingClientRect();
                    let area = r.width * r.height;
                    // Stage usually lamba chouda hota hai (approx 600px se 1600px ke beech)
                    if (r.width >= 600 && r.width <= 1600 && r.height >= 400 && area > largestArea) {
                        largestArea = area;
                        stage = el;
                    }
                });

                if (stage) {
                    let r = stage.getBoundingClientRect();
                    
                    // 2. Mouse ko stage ke beecho-beech move karo taaki controls 'Wake Up' ho jayein
                    let centerX = r.left + (r.width / 2);
                    let centerY = r.top + (r.height / 2);
                    stage.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: centerX, clientY: centerY}));
                    
                    // Saath mein ek Double Click bhi maar do (kuch players double click pe full screen hote hain)
                    stage.dispatchEvent(new MouseEvent('dblclick', {bubbles: true, clientX: centerX, clientY: centerY}));

                    // 3. 1 second wait karo (Controls aane ke liye) aur theek Bottom-Right corner pe click maar do
                    setTimeout(() => {
                        let clickX = r.right - 30; // Right side se 30 pixels andar
                        let clickY = r.bottom - 30; // Niche se 30 pixels upar
                        
                        let targetEl = document.elementFromPoint(clickX, clickY);
                        if (targetEl) {
                            // Pura mouse click sequence force karna (Sirf click nahi, dabana aur uthana dono)
                            targetEl.dispatchEvent(new MouseEvent('mouseover', {bubbles: true, clientX: clickX, clientY: clickY}));
                            targetEl.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, clientX: clickX, clientY: clickY}));
                            targetEl.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, clientX: clickX, clientY: clickY}));
                            targetEl.dispatchEvent(new MouseEvent('click', {bubbles: true, clientX: clickX, clientY: clickY}));
                            console.log("🎯 BOOM! Coordinate clicked exactly at:", clickX, clickY);
                        }
                    }, 1500); // 1.5 second ka delay wake up ke baad
                }
            }
            clickByCoordinates();
        """)
        
        # Maximize hone ka waqt
        time.sleep(5) 

        # FFmpeg Setup
        print("Starting FFmpeg rendering...")
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
    
