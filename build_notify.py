import platform
import os


def notify_user(message="Build completed!"):
    try:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"[CI] Notification: {message}")
            return
        
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"Notification failed: {e}")
