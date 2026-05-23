import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains # <-- NEW IMPORT
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

        # Studio load hone ka extra time
        time.sleep(12) 

        # STEP 3: THE ULTIMATE ACTIONCHAINS MAXIMIZE 🎯
        print("Waking up controls and forcing Maximize... 🖥️")
        try:
            actions = ActionChains(driver)
            
            # 1. Video tag dhoondo (Yahi sabse main element hai)
            video_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            
            # 2. Mouse ko video ke center me le jao taaki UI controls pop-up ho jayein
            actions.move_to_element(video_element).perform()
            time.sleep(2) 
            
            # 3. Pehli koshish: Fullscreen button ko dhund kar click karna
            fs_xpath = "//button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'fullscreen')]"
            try:
                fs_button = driver.find_element(By.XPATH, fs_xpath)
                actions.move_to_element(fs_button).click().perform()
                print("🎯 BOOM! Fullscreen button located and clicked perfectly!")
            except:
                print("Button ka naam nahi mila, brute-force bottom-right corner click apply kar rahe hain...")
                # 4. Dusri koshish: Agar button ka naam change ho gaya hai, to exact bottom-right me click maaro
                v_width = video_element.size['width']
                v_height = video_element.size['height']
                
                # Center point se offset nikalna
                x_offset = int((v_width / 2) - 40)
                y_offset = int((v_height / 2) - 30)
                
                actions.move_to_element_with_offset(video_element, x_offset, y_offset).click().perform()
                print("🎯 Bottom-right coordinate force click done!")
                
        except Exception as e:
            print("Maximize block me error aaya:", e)

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
    
