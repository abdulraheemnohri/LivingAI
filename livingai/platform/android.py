# LivingAI Android Platform Facilities
import subprocess
import shutil
import logging
import json
from typing import Dict, Any, Optional


class AndroidPlatform:
    """Handles Android system interaction via Termux API or getprop."""

    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        info = {}
        for prop, key in [
            ("ro.product.model", "model"),
            ("ro.product.brand", "brand"),
            ("ro.build.version.release", "android_version"),
            ("ro.product.cpu.abi", "cpu_abi"),
            ("ro.build.version.sdk", "sdk_version"),
        ]:
            try:
                info[key] = subprocess.check_output(["getprop", prop], text=True, stderr=subprocess.DEVNULL).strip()
            except Exception:
                info[key] = "Unknown"
        return info

    @staticmethod
    def toast(message: str) -> bool:
        if shutil.which("termux-toast"):
            try:
                subprocess.run(["termux-toast", message], check=True, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def vibrate(duration_ms: int = 200) -> bool:
        if shutil.which("termux-vibrate"):
            try:
                subprocess.run(["termux-vibrate", "-d", str(duration_ms)], check=True, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def show_notification(title: str, content: str, id_tag: str = "livingai") -> bool:
        if shutil.which("termux-notification"):
            try:
                subprocess.run([
                    "termux-notification",
                    "--title", title,
                    "--content", content,
                    "--id", id_tag
                ], check=True, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def set_clipboard(text: str) -> bool:
        if shutil.which("termux-clipboard-set"):
            try:
                proc = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True)
                proc.communicate(input=text)
                return proc.returncode == 0
            except Exception:
                return False
        return False

    @staticmethod
    def get_clipboard() -> str:
        if shutil.which("termux-clipboard-get"):
            try:
                return subprocess.check_output(["termux-clipboard-get"], text=True, stderr=subprocess.DEVNULL).strip()
            except Exception:
                return ""
        return ""

    @staticmethod
    def get_location() -> Dict[str, Any]:
        if shutil.which("termux-location"):
            try:
                out = subprocess.check_output(["termux-location", "-p", "gps", "-r", "once"], text=True, stderr=subprocess.DEVNULL)
                return json.loads(out)
            except Exception:
                return {"status": "UNAVAILABLE", "reason": "Location permission or service unavailable"}
        return {"status": "UNAVAILABLE", "reason": "termux-location tool not found"}

    @staticmethod
    def take_photo(output_path: str = "/sdcard/livingai_photo.jpg") -> bool:
        if shutil.which("termux-camera-photo"):
            try:
                subprocess.run(["termux-camera-photo", "-c", "0", output_path], check=True, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False
