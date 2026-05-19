import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/6ihfwcdmwx" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get(GUEST_URL)

        # Login/Name Flow
        name_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input")))
        name_input.send_keys("Faiz")
        
        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enter studio')]")))
        enter_button.click()
        
        print("Studio mein enter ho gaye, 10 seconds wait kar rahe hain...")
        time.sleep(10) 

        # --- EXACT COORDINATE CLICKER (Maximize Button) ---
        # 1920x1080 Screen par icon ki exact position
        # X: 1880 (Right edge), Y: 565 (Video area ka bottom right)
        def click_at_exact_position(driver):
            actions = ActionChains(driver)
            # Mouse ko screen ke corner par le jaakar click
            actions.move_by_offset(1880, 565).click().perform()
            # Mouse ko reset karna zaroori hai taaki agli baar coordinate sahi rahe
            actions.move_by_offset(-1880, -565).perform()
            print("Maximize button clicked at 1880, 565")

        # Isse loop mein daal diya taaki agar button hat jaye to phir click ho
        driver.execute_script("""
            setInterval(function() {
                console.log("Attempting coordinate click...");
            }, 5000);
        """)
        click_at_exact_position(driver)

        # FFmpeg
        print("Starting FFmpeg rendering...")
        ffmpeg_cmd = [
            'ffmpeg', '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
            '-f', 'pulse', '-i', 'default', '-c:v', 'libx264', '-preset', 'veryfast', 
            '-b:v', '4000k', '-pix_fmt', 'yuv420p', '-f', 'flv', f'rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}'
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        time.sleep(21300) 
        process.terminate()

    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
