import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/6ihfwcdmwx" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
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

        # Studio aane ka pura wait (12 seconds minimum chahiye hi chahiye)
        time.sleep(12) 

        # STEP 3: THE PERFECT MAXIMIZE FIX 🎯
        print("Locating the exact Black Video Stage... 🖥️")
        
        # Pehle try karte hain Mouse Double-Click se (Sabse natural tareeka)
        try:
            video_el = driver.find_element(By.TAG_NAME, "video")
            ActionChains(driver).double_click(video_el).perform()
            print("ActionChains: Double-clicked the video!")
            time.sleep(2)
        except:
            pass

        # Ab specific Javascript Coordinate Logic chalayenge jo sirf Black Box pe kaam karega
        driver.execute_script("""
            function maximizePerfectly() {
                // Exact Video element ya 'Black Box' ko pakdo
                let stage = document.querySelector('video');
                if (!stage) {
                    let divs = Array.from(document.querySelectorAll('div'));
                    stage = divs.find(d => {
                        let r = d.getBoundingClientRect();
                        let bg = window.getComputedStyle(d).backgroundColor;
                        // Sirf wahi dhoondo jo sach me video area jitna ho aur purely BLACK ho
                        return r.width > 400 && r.height > 250 && r.width < 1500 && (bg === 'rgb(0, 0, 0)' || bg === 'rgba(0, 0, 0, 1)');
                    });
                }

                if (stage) {
                    let r = stage.getBoundingClientRect();
                    
                    // Mouse ko us black box ke center me hilao taaki controls jaag jayein
                    let centerX = r.left + (r.width / 2);
                    let centerY = r.top + (r.height / 2);
                    stage.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: centerX, clientY: centerY}));
                    
                    setTimeout(() => {
                        // Click EXACTLY us kaale box ke andar bottom right me. 
                        // Help button isse bahar hoga, isliye wahan click nahi jayega.
                        let clickX = r.right - 25; 
                        let clickY = r.bottom - 25;
                        
                        let target = document.elementFromPoint(clickX, clickY);
                        if (target) {
                            target.click();
                            console.log("🎯 Hit exact stage coordinate:", clickX, clickY);
                        }
                    }, 1000);
                }
            }
            maximizePerfectly();
        """)
        
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
    
