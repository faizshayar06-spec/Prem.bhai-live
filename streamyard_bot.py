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
    wait = WebDriverWait(driver, 20) # 20 seconds max wait time
    
    try:
        print("Opening StreamYard...")
        driver.get(GUEST_URL)

        # STEP 1: FORCE CLICK POPUPS (Cookies, Continue, Allow)
        driver.execute_script("""
            function clickAnything() {
                let buttons = Array.from(document.querySelectorAll('button'));
                buttons.forEach(btn => {
                    let txt = btn.innerText.toLowerCase();
                    if(txt.includes('accept') || txt.includes('continue') || txt.includes('allow') || txt.includes('got it')) {
                        btn.click();
                        console.log('Bypassed: ' + txt);
                    }
                });
            }
            setInterval(clickAnything, 2000); // Har 2 sec me check karega
        """)
        
        # STEP 2: ADVANCED TECHNIQUE FOR NAME & ENTER STUDIO
        print("Waiting for Name input field...")
        time.sleep(5) # 5 seconds diya taaki page puri tarah load ho jaye
        
        # Find input 
        try:
            name_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        except:
            name_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input")))
        
        # JS ke through clear karenge (Invalid Element State bypass)
        driver.execute_script("arguments[0].scrollIntoView(true);", name_input)
        driver.execute_script("arguments[0].focus();", name_input)
        driver.execute_script("arguments[0].value = '';", name_input)
        time.sleep(1)
        
        # Native typing
        print("Typing name as a real human...")
        name_input.send_keys("Faiz")
        
        # React ko input register karwane ke liye JS event trigger
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", name_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", name_input)
        time.sleep(3) 

        # Hunting the "Enter Studio" button robustly
        print("Hunting for the 'Enter studio' button...")
        enter_button_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter studio')]"
        enter_button = wait.until(EC.presence_of_element_located((By.XPATH, enter_button_xpath)))
        
        # Click using Javascript to force click even if slightly overlapped
        driver.execute_script("arguments[0].click();", enter_button)
        print("Successfully bypassed and entered the Studio! 🥀")

        # Wait to load into the studio completely
        time.sleep(5)

        # STEP 3: REPETITIVE AUTO-ADD TO STAGE
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
    
