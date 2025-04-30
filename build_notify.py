import platform
import os
import pyttsx3

def notify_user(message="Build completed!"):
    try:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"[CI] Notification: {message}")
            return
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"Notification failed: {e}")
