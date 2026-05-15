import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
GUEST_URL = "https://streamyard.com/3r8zzr4cbk" 
STREAM_KEY = os.getenv("YT_STREAM_KEY")

def start_stream():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Bypass Mic/Cam and Popups
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🌐 Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(15) 

        # --- FULL BYPASS LOGIC ---
        print("⌨️ Starting Bypass and Entry Process...")
        driver.execute_script("""
            function bypassEverything() {
                // 1. Sabse pehle Cookies 'Accept' karo (Screenshoot mein yehi ruk raha hai)
                let cookieBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.innerText.includes('Accept') || b.innerText.includes('cookies')
                );
                if(cookieBtn) {
                    cookieBtn.click();
                    console.log('✅ Cookies Accepted');
                }

                // 2. 3 second baad naam bharna aur enter studio par click karna
                setTimeout(() => {
                    let nameField = document.querySelector('input[name="displayName"], input#display-name');
                    if(nameField) {
                        nameField.value = 'Faiz-Live';
                        nameField.dispatchEvent(new Event('input', { bubbles: true }));
                        console.log('✅ Name Entered');
                    }

                    setTimeout(() => {
                        let enterBtn = Array.from(document.querySelectorAll('button')).find(b => 
                            b.innerText.toLowerCase().includes('enter') || 
                            b.innerText.toLowerCase().includes('studio')
                        );
                        if(enterBtn) {
                            enterBtn.click();
                            console.log('✅ Clicked Enter');
                        }
                    }, 2000);
                }, 3000);
            }
            bypassEverything();
        """)
        
        time.sleep(20) # Wait for studio to load
        print("🏁 Entry Process Done. Checking for Studio...")

        # Stage pe add karne ka loop
        driver.execute_script("""
            setInterval(() => {
                let addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.innerText.toLowerCase().includes('add to stage')
                );
                if (addBtn) addBtn.click();
            }, 10000);
        """)

        # FFmpeg Start
        ffmpeg_cmd = (
            f"ffmpeg -f x11grab -video_size 1920x1080 -framerate 30 -i :99.0 "
            f"-f pulse -i default -c:v libx264 -preset ultrafast -pix_fmt yuv420p "
            f"-maxrate 3000k -bufsize 6000k -g 60 -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
        )
        
        process = subprocess.Popen(ffmpeg_cmd, shell=True)
        time.sleep(21500) # 6 Hours
        process.terminate()

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.save_screenshot("final_check.png")
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
