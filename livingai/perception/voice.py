# LivingAI Voice Perception
import shutil
import subprocess
from typing import Dict, Any


class VoicePerception:
    """Handles speech input via Termux API or Android system facilities."""

    @staticmethod
    def is_voice_available() -> bool:
        return shutil.which("termux-speech-to-text") is not None

    @staticmethod
    def listen() -> Dict[str, Any]:
        if not VoicePerception.is_voice_available():
            return {"status": "UNAVAILABLE", "reason": "termux-speech-to-text not installed", "text": ""}
        try:
            out = subprocess.check_output(["termux-speech-to-text"], text=True, stderr=subprocess.DEVNULL)
            return {"status": "SUCCESS", "text": out.strip()}
        except Exception as e:
            return {"status": "ERROR", "reason": str(e), "text": ""}

    @staticmethod
    def speak(text: str) -> bool:
        if shutil.which("termux-tts-speak"):
            try:
                subprocess.run(["termux-tts-speak", text], check=True, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False
