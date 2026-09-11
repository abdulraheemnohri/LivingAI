# LivingAI Model Manager
# ======================
# This module manages the AI model lifecycle: download, verify, load, unload, etc.

import os
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Local imports
from .downloader import ModelDownloader
from .verifier import ModelVerifier
from .runtime import ModelRuntime
from ..config import ConfigManager
from ..platform.termux import TermuxPlatform
from ..security.audit import AuditLogger


class ModelManager:
    """
    Manages the lifecycle of the AI model (SmolLM3-3B).
    
    Responsibilities:
    - Download the model from HuggingFace
    - Verify model integrity
    - Load/unload the model
    - Provide model status and info
    - Benchmark model performance
    """
    
    def __init__(
        self,
        model_dir: str,
        config: ConfigManager,
        platform: TermuxPlatform,
        audit_logger: AuditLogger
    ):
        """
        Initialize the ModelManager.
        
        Args:
            model_dir: Directory to store models.
            config: Configuration manager.
            platform: Termux platform utilities.
            audit_logger: Audit logger for tracking actions.
        """
        self.model_dir = os.path.expanduser(model_dir)
        self.config = config
        self.platform = platform
        self.audit_logger = audit_logger
        
        # Initialize components
        self.downloader = ModelDownloader(
            model_dir=self.model_dir,
            config=self.config,
            platform=self.platform,
            audit_logger=self.audit_logger
        )
        self.verifier = ModelVerifier(
            model_dir=self.model_dir,
            config=self.config,
            audit_logger=self.audit_logger
        )
        self.runtime = ModelRuntime(
            model_dir=self.model_dir,
            config=self.config,
            platform=self.platform,
            audit_logger=self.audit_logger
        )
        
        # Model state
        self._model_loaded = False
        self._current_model_path: Optional[str] = None
        
        logging.info("ModelManager initialized")
    
    def get_model_dir(self) -> str:
        """Get the model directory path."""
        return self.model_dir
    
    def get_model_path(self) -> Optional[str]:
        """Get the path to the current model."""
        return self._current_model_path
    
    def is_model_loaded(self) -> bool:
        """Check if the model is currently loaded."""
        return self._model_loaded
    
    def download(self, force: bool = False) -> bool:
        """
        Download the AI model.
        
        Args:
            force: If True, redownload even if model exists.
            
        Returns:
            bool: True if download succeeded, False otherwise.
        """
        self.audit_logger.log("MODEL_DOWNLOAD_START", "Starting model download")
        
        # Check if already downloaded
        if not force and self.is_model_available():
            logging.info("Model already available, skipping download")
            self.audit_logger.log("MODEL_DOWNLOAD_SKIP", "Model already available")
            return True
        
        # Download the model
        success = self.downloader.download()
        
        if success:
            self._current_model_path = self.downloader.get_downloaded_path()
            self.audit_logger.log("MODEL_DOWNLOAD_SUCCESS", f"Model downloaded to {self._current_model_path}")
        else:
            self.audit_logger.log("MODEL_DOWNLOAD_FAIL", "Model download failed")
        
        return success
    
    def is_model_available(self) -> bool:
        """
        Check if the model is available locally.
        
        Returns:
            bool: True if model files exist, False otherwise.
        """
        return self.verifier.is_model_available()
    
    def verify(self) -> bool:
        """
        Verify the model's integrity.
        
        Returns:
            bool: True if model is valid, False otherwise.
        """
        self.audit_logger.log("MODEL_VERIFY_START", "Starting model verification")
        
        success = self.verifier.verify()
        
        if success:
            self.audit_logger.log("MODEL_VERIFY_SUCCESS", "Model verification passed")
        else:
            self.audit_logger.log("MODEL_VERIFY_FAIL", "Model verification failed")
        
        return success
    
    def load(self, force: bool = False) -> bool:
        """
        Load the AI model into memory.
        
        Args:
            force: If True, reload even if already loaded.
            
        Returns:
            bool: True if model loaded successfully, False otherwise.
        """
        if self._model_loaded and not force:
            logging.info("Model already loaded, skipping")
            return True
        
        # Check if model is available
        if not self.is_model_available():
            logging.warning("Model not available, attempting download")
            if not self.download():
                logging.error("Failed to download model")
                return False
        
        # Verify model
        if not self.verify():
            logging.error("Model verification failed")
            return False
        
        # Load the model
        self.audit_logger.log("MODEL_LOAD_START", "Starting model load")
        
        success = self.runtime.load()
        
        if success:
            self._model_loaded = True
            self._current_model_path = self.runtime.get_model_path()
            self.audit_logger.log("MODEL_LOAD_SUCCESS", f"Model loaded from {self._current_model_path}")
        else:
            self.audit_logger.log("MODEL_LOAD_FAIL", "Model load failed")
        
        return success
    
    def unload(self) -> bool:
        """
        Unload the AI model from memory.
        
        Returns:
            bool: True if unload succeeded, False otherwise.
        """
        if not self._model_loaded:
            logging.info("Model not loaded, skipping unload")
            return True
        
        self.audit_logger.log("MODEL_UNLOAD_START", "Starting model unload")
        
        success = self.runtime.unload()
        
        if success:
            self._model_loaded = False
            self._current_model_path = None
            self.audit_logger.log("MODEL_UNLOAD_SUCCESS", "Model unloaded")
        else:
            self.audit_logger.log("MODEL_UNLOAD_FAIL", "Model unload failed")
        
        return success
    
    def reload(self) -> bool:
        """
        Reload the AI model.
        
        Returns:
            bool: True if reload succeeded, False otherwise.
        """
        self.unload()
        return self.load(force=True)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the model.
        
        Returns:
            Dict[str, Any]: Model status information.
        """
        return {
            "loaded": self._model_loaded,
            "available": self.is_model_available(),
            "path": self._current_model_path,
            "repository": self.config.get("model.repository", "Unknown"),
            "revision": self.config.get("model.revision", "Unknown"),
            "runtime": self.config.get("model.runtime", "Unknown"),
        }
    
    def info(self) -> Dict[str, Any]:
        """
        Get detailed information about the model.
        
        Returns:
            Dict[str, Any]: Model information.
        """
        info = self.get_status()
        
        if self._model_loaded:
            runtime_info = self.runtime.get_info()
            info.update(runtime_info)
        
        return info
    
    def doctor(self) -> Dict[str, Any]:
        """
        Run model diagnostics.
        
        Returns:
            Dict[str, Any]: Diagnostic results.
        """
        diagnostics = {
            "available": self.is_model_available(),
            "loaded": self._model_loaded,
            "path": self._current_model_path,
        }
        
        # Add verification status
        if self.is_model_available():
            diagnostics["verified"] = self.verify()
        else:
            diagnostics["verified"] = False
        
        # Add runtime compatibility
        diagnostics["runtime_compatible"] = self.runtime.is_compatible()
        
        return diagnostics
    
    def benchmark(self) -> Dict[str, Any]:
        """
        Benchmark model performance.
        
        Returns:
            Dict[str, Any]: Benchmark results.
        """
        if not self._model_loaded:
            if not self.load():
                return {"error": "Failed to load model for benchmark"}
        
        return self.runtime.benchmark()
    
    def generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Generate text using the loaded model.
        
        Args:
            prompt: The input prompt.
            **kwargs: Additional generation parameters.
            
        Returns:
            str: Generated text.
        """
        if not self._model_loaded:
            if not self.load():
                raise RuntimeError("Failed to load model for generation")
        
        return self.runtime.generate(prompt, **kwargs)
    
    def generate_streaming(
        self,
        prompt: str,
        **kwargs
    ) -> Any:
        """
        Generate text with streaming output.
        
        Args:
            prompt: The input prompt.
            **kwargs: Additional generation parameters.
            
        Returns:
            Generator or similar for streaming output.
        """
        if not self._model_loaded:
            if not self.load():
                raise RuntimeError("Failed to load model for generation")
        
        return self.runtime.generate_streaming(prompt, **kwargs)
    
    def status(self) -> None:
        """Print model status to console."""
        from ..ui.terminal import TerminalUI
        ui = TerminalUI()
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("MODEL STATUS")
        print("=" * 50)
        print(f"Repository: {status['repository']}")
        print(f"Revision: {status['revision']}")
        print(f"Runtime: {status['runtime']}")
        print(f"Available: {'Yes' if status['available'] else 'No'}")
        print(f"Loaded: {'Yes' if status['loaded'] else 'No'}")
        if status['path']:
            print(f"Path: {status['path']}")
        print("=" * 50 + "\n")
    
    def delete(self) -> bool:
        """
        Delete the downloaded model.
        
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        self.audit_logger.log("MODEL_DELETE_START", "Starting model deletion")
        
        # Unload first if loaded
        if self._model_loaded:
            self.unload()
        
        # Delete model files
        success = self.downloader.delete()
        
        if success:
            self._current_model_path = None
            self.audit_logger.log("MODEL_DELETE_SUCCESS", "Model deleted")
        else:
            self.audit_logger.log("MODEL_DELETE_FAIL", "Model deletion failed")
        
        return success
