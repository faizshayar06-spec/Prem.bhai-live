import os
import time
import subprocess
import traceback
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
    wait = WebDriverWait(driver, 20) 
    
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
        
        # STEP 2: NAME & ENTER STUDIO
        print("Waiting for popups to clear before finding input...")
        time.sleep(4) # Thoda time diya taaki popups hat jayein
        
        print("Hunting for Name input field...")
        # element_to_be_clickable use kar rahe hain taaki ready hone par hi click kare
        name_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input")))
        
        # FIX: Normal .clear() hata diya jo error de raha tha. JS se forcefully focus aur type karenge.
        driver.execute_script("arguments[0].focus();", name_input)
        driver.execute_script("arguments[0].value = 'Faiz';", name_input)
        # React ko batane ke liye ki kuch type hua hai, event dispatch karenge
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", name_input)
        
        print("Name 'Faiz' successfully typed via JS...")
        time.sleep(2) 

        print("Hunting for the 'Enter studio' button...")
        enter_button_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter studio')]"
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, enter_button_xpath)))
        enter_button.click()
        print("Successfully bypassed and entered the Studio! 🥀")

        # Studio load hone ka wait
        time.sleep(10)

        # STEP 3: AUTO ADD TO STAGE & MAXIMIZE (F12 METHOD)
        print("Injecting F12/JS based Add to Stage and Maximize script...")
        driver.execute_script("""
            setInterval(() => {
                // 1. Add to stage logic
                let btns = Array.from(document.querySelectorAll('button'));
                let addBtn = btns.find(b => b.innerText.includes('Add to stage'));
                if (addBtn) {
                    addBtn.click();
                    console.log("Clicked: Add to stage");
                }

                // 2. MAXIMIZE BUTTON LOGIC
                let maxBtn = document.querySelector('button[aria-label="Maximize"]') || 
                             document.querySelector('button[aria-label="Full screen"]') ||
                             document.querySelector('button[aria-label="Enter full screen"]');
                
                if (maxBtn) {
                    let ev = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    maxBtn.dispatchEvent(ev);
                    console.log("Successfully Clicked Maximize / Full Screen!");
                }
            }, 5000); 
        """)

        # STEP 4: START STREAMING
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
        print("Bot is LIVE and Streaming for 6 Hours! Check YouTube dashboard.")
        
        time.sleep(21300) 
        
        process.terminate()

    except Exception as e:
        print("Bhai ek Error aayi hai, neeche detail dekho:")
        traceback.print_exc() 
    finally:
        driver.quit()
        print("Script finished and driver closed.")

if __name__ == "__main__":
    start_stream()
    
