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
        
        # STEP 2: ENTER NAME & STUDIO
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

        # Wait to load into the studio completely
        time.sleep(8)

        # STEP 3: FORCE MAXIMIZE (SUPER AGGRESSIVE)
        print("Maximizing the studio screen (Force Mode)... 🖥️")
        driver.execute_script("""
            function forceMaximize() {
                // 1. Code ke andar chup hue SVG icons ko scan karega
                let elements = document.querySelectorAll('button, div[role="button"], svg');
                for (let el of elements) {
                    let htmlData = el.outerHTML.toLowerCase();
                    // Agar element ke code me inme se kuch bhi mila
                    if (htmlData.includes('fullscreen') || htmlData.includes('maximize') || htmlData.includes('full-screen')) {
                        // SVG mila toh uske parent button ko target karega
                        let target = el.tagName.toLowerCase() === 'svg' ? el.closest('button, div[role="button"]') : el;
                        if (target) {
                            target.click();
                            console.log("Clicked Fullscreen Button!");
                            return true;
                        }
                    }
                }
                
                // 2. Fallback: Agar button click fail hua, toh Browser ka inbuilt fullscreen API trigger karega
                try {
                    let videoContainer = document.querySelector('video') ? document.querySelector('video').closest('div') : document.body;
                    if (videoContainer && videoContainer.requestFullscreen) {
                        videoContainer.requestFullscreen();
                        console.log("Native Fullscreen Triggered!");
                        return true;
                    }
                } catch(e) {}
                
                return false;
            }
            
            // Turant maximize karega, agar slow internet hua toh 4 second baad dobara try karega
            if(!forceMaximize()) {
                setTimeout(forceMaximize, 4000);
            }
        """)
        time.sleep(5) # Maximize hone ka waqt de rahe hain

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
    
