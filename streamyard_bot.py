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
    
    # Permissions Bypass
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🌐 Opening StreamYard...")
        driver.get(GUEST_URL)
        time.sleep(12) 

        print("🚀 Step: Clicking Continue and Entering Name...")
        driver.execute_script("""
            function solveStreamyard() {
                // 1. Continue Button ko click karna (Jo screenshot mein dikh raha hai)
                let btns = Array.from(document.querySelectorAll('button'));
                let continueBtn = btns.find(b => b.innerText.includes('Continue'));
                if(continueBtn) {
                    continueBtn.click();
                    console.log('✅ Continue Clicked');
                }

                // 2. 4 second wait karna taaki naam wala box aa jaye
                setTimeout(() => {
                    let nameField = document.querySelector('input[name="displayName"], input#display-name');
                    if(nameField) {
                        nameField.value = 'Faiz-Live';
                        nameField.dispatchEvent(new Event('input', { bubbles: true }));
                        console.log('✅ Name Entered');
                    }

                    // 3. Last Step: Enter Studio button dabana
                    setTimeout(() => {
                        let finalBtns = Array.from(document.querySelectorAll('button'));
                        let enterBtn = finalBtns.find(b => 
                            b.innerText.toLowerCase().includes('enter') || 
                            b.innerText.toLowerCase().includes('studio')
                        );
                        if(enterBtn) {
                            enterBtn.click();
                            console.log('✅ Studio Entered!');
                        }
                    }, 2500);
                }, 4000);
            }
            solveStreamyard();
        """)
        
        time.sleep(20) 
        print("🎬 Entry sequence finished. Starting FFmpeg...")

        # Stage Bot Loop
        driver.execute_script("""
            setInterval(() => {
                let addBtn = Array.from(document.querySelectorAll('button')).find(b => 
                    b.innerText.toLowerCase().includes('add to stage')
                );
                if (addBtn) addBtn.click();
            }, 10000);
        """)

        # FFmpeg Stream
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
        driver.save_screenshot("after_continue.png")
        driver.quit()

if __name__ == "__main__":
    start_stream()
    
