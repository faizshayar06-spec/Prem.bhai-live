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
GUEST_URL = "https://streamyard.com/tfaqht4h6b" 
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

        # STEP 3: THE SMART DOM CLICK 🎯 (UPDATED)
        print("Locating and clicking the maximize button... 🖥️")
        driver.execute_script("""
            function clickMaximize() {
                // Attempt 1: Agar aria-label se direct button mil jaye
                let ariaBtns = document.querySelectorAll('[aria-label*="ullscreen"], [aria-label*="aximize"], [title*="ullscreen"]');
                if (ariaBtns.length > 0) {
                    ariaBtns[0].click();
                    return;
                }

                // Attempt 2: Smart Detection - Stage find karke bottom-right icon ko target karna
                let largestArea = 0;
                let stage = null;
                document.querySelectorAll('div').forEach(el => {
                    let r = el.getBoundingClientRect();
                    let area = r.width * r.height;
                    // Stage size logic
                    if (r.width >= 600 && r.height >= 400 && area > largestArea) {
                        largestArea = area;
                        stage = el;
                    }
                });

                if (stage) {
                    let r = stage.getBoundingClientRect();
                    let centerX = r.left + (r.width / 2);
                    let centerY = r.top + (r.height / 2);
                    
                    // Mouse move karke controls ko show/wake up karna
                    stage.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: centerX, clientY: centerY}));
                    
                    setTimeout(() => {
                        // Stage ke andar ke saare buttons aur SVGs nikaalo
                        let elements = stage.querySelectorAll('button, svg');
                        let targetBtn = null;
                        let maxRight = 0;
                        
                        elements.forEach(el => {
                            let elRect = el.getBoundingClientRect();
                            // Condition: Element stage ke bottom half mein hona chahiye
                            if (elRect.top > r.top + (r.height / 2)) {
                                // Sabse Right side wala element dhundo (jo maximize hota hai)
                                if (elRect.right > maxRight) {
                                    maxRight = elRect.right;
                                    targetBtn = el;
                                }
                            }
                        });

                        if (targetBtn) {
                            // Agar direct SVG mila, toh uske parent button pe click karo
                            let clickable = targetBtn.closest('button') || targetBtn;
                            clickable.click();
                            console.log("🎯 Maximize button detected and clicked!");
                        }
                    }, 1500); // 1.5 second wait taaki controls screen par aa jayein
                }
            }
            clickMaximize();
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
    
