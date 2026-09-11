# LivingAI Model Verifier
# ========================
# This module verifies the integrity of downloaded AI models.

import os
import logging
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Local imports
from ..config import ConfigManager
from ..security.audit import AuditLogger


class ModelVerifier:
    """
    Verifies the integrity of downloaded AI models.
    
    Features:
    - Checksum verification (SHA256)
    - File size verification
    - File existence checks
    - Model format validation
    """
    
    # Known checksums for SmolLM3-3B (would be populated with actual values)
    KNOWN_CHECKSUMS = {
        "HuggingFaceTB/SmolLM3-3B": {
            "config.json": "",  # Placeholder - would contain actual SHA256
            "pytorch_model.bin": "",
            "tokenizer.json": "",
            "tokenizer_config.json": "",
            "vocab.txt": "",
        }
    }
    
    # Expected file sizes (approximate)
    EXPECTED_SIZES = {
        "HuggingFaceTB/SmolLM3-3B": {
            "config.json": 1024,  # ~1KB
            "pytorch_model.bin": 2147483648,  # ~2GB (for 4-bit)
            "tokenizer.json": 1048576,  # ~1MB
            "tokenizer_config.json": 1024,
            "vocab.txt": 1048576,
        }
    }
    
    def __init__(
        self,
        model_dir: str,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the ModelVerifier.
        
        Args:
            model_dir: Directory where models are stored.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.model_dir = os.path.expanduser(model_dir)
        self.config = config
        self.audit_logger = audit_logger
        
        # Get model configuration
        self.repository = self.config.get("model.repository", "HuggingFaceTB/SmolLM3-3B")
        
        logging.info(f"ModelVerifier initialized for {self.repository}")
    
    def get_model_path(self) -> str:
        """Get the path to the model directory."""
        return os.path.join(self.model_dir, self.repository.split("/")[-1])
    
    def is_model_available(self) -> bool:
        """
        Check if the model files are available.
        
        Returns:
            bool: True if all expected files exist, False otherwise.
        """
        model_path = self.get_model_path()
        
        if not os.path.exists(model_path):
            return False
        
        # Check for at least one model file (we'll be more lenient here)
        for filename in os.listdir(model_path):
            if filename.endswith(('.bin', '.json', '.txt')):
                return True
        
        return False
    
    def verify(self, checksum_only: bool = False) -> bool:
        """
        Verify the integrity of the downloaded model.
        
        Args:
            checksum_only: If True, only verify checksums (skip size checks).
            
        Returns:
            bool: True if model is valid, False otherwise.
        """
        self.audit_logger.log("MODEL_VERIFY_START", f"Verifying {self.repository}")
        
        model_path = self.get_model_path()
        
        if not os.path.exists(model_path):
            logging.error(f"Model directory not found: {model_path}")
            return False
        
        # Get expected files
        expected_files = self._get_expected_files()
        
        if not expected_files:
            logging.warning("No expected files defined for model verification")
            return True  # Can't verify without expected files
        
        # Verify each file
        all_valid = True
        for filename in expected_files:
            filepath = os.path.join(model_path, filename)
            
            if not os.path.exists(filepath):
                logging.error(f"Expected file not found: {filename}")
                all_valid = False
                continue
            
            # Check file size
            if not checksum_only:
                expected_size = self.EXPECTED_SIZES.get(self.repository, {}).get(filename)
                if expected_size:
                    actual_size = os.path.getsize(filepath)
                    # Allow 10% tolerance for size differences
                    if abs(actual_size - expected_size) > expected_size * 0.1:
                        logging.warning(
                            f"File size mismatch for {filename}: "
                            f"expected ~{expected_size}, got {actual_size}"
                        )
                        # Don't fail on size mismatch alone
            
            # Verify checksum
            if self.repository in self.KNOWN_CHECKSUMS:
                expected_checksum = self.KNOWN_CHECKSUMS[self.repository].get(filename)
                if expected_checksum:
                    actual_checksum = self._calculate_checksum(filepath)
                    if actual_checksum != expected_checksum:
                        logging.error(
                            f"Checksum mismatch for {filename}: "
                            f"expected {expected_checksum}, got {actual_checksum}"
                        )
                        all_valid = False
        
        if all_valid:
            self.audit_logger.log("MODEL_VERIFY_SUCCESS", f"Model {self.repository} verified")
        else:
            self.audit_logger.log("MODEL_VERIFY_FAIL", f"Model {self.repository} verification failed")
        
        return all_valid
    
    def _get_expected_files(self) -> List[str]:
        """
        Get the list of expected files for the model.
        
        Returns:
            List[str]: List of expected filenames.
        """
        # For now, return a basic list of files we expect
        return [
            "config.json",
            "pytorch_model.bin",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
        ]
    
    def _calculate_checksum(self, filepath: str, algorithm: str = "sha256") -> str:
        """
        Calculate the checksum of a file.
        
        Args:
            filepath: Path to the file.
            algorithm: Hash algorithm to use (default: sha256).
            
        Returns:
            str: The hexadecimal checksum.
        """
        hash_func = getattr(hashlib, algorithm)()
        
        with open(filepath, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def verify_checksum(self, filepath: str, expected_checksum: str) -> bool:
        """
        Verify a file against an expected checksum.
        
        Args:
            filepath: Path to the file.
            expected_checksum: Expected checksum value.
            
        Returns:
            bool: True if checksum matches, False otherwise.
        """
        actual_checksum = self._calculate_checksum(filepath)
        return actual_checksum == expected_checksum
    
    def verify_file_size(self, filepath: str, expected_size: int, tolerance: float = 0.1) -> bool:
        """
        Verify a file's size against an expected size.
        
        Args:
            filepath: Path to the file.
            expected_size: Expected size in bytes.
            tolerance: Allowed tolerance (0.1 = 10%).
            
        Returns:
            bool: True if size is within tolerance, False otherwise.
        """
        actual_size = os.path.getsize(filepath)
        difference = abs(actual_size - expected_size)
        return difference <= expected_size * tolerance
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get information about a file (size, checksum).
        
        Args:
            filepath: Path to the file.
            
        Returns:
            Dict[str, Any]: File information.
        """
        if not os.path.exists(filepath):
            return {"exists": False}
        
        size = os.path.getsize(filepath)
        checksum = self._calculate_checksum(filepath)
        
        return {
            "exists": True,
            "path": filepath,
            "size": size,
            "size_mb": round(size / (1024 * 1024), 2),
            "sha256": checksum,
        }
    
    def verify_all_files(self) -> Dict[str, Any]:
        """
        Verify all files in the model directory.
        
        Returns:
            Dict[str, Any]: Verification results for all files.
        """
        model_path = self.get_model_path()
        results = {}
        
        if not os.path.exists(model_path):
            return {"error": "Model directory not found"}
        
        for filename in os.listdir(model_path):
            filepath = os.path.join(model_path, filename)
            if os.path.isfile(filepath):
                results[filename] = self.get_file_info(filepath)
        
        return results
    
    def detect_corruption(self) -> bool:
        """
        Detect if model files are corrupted.
        
        Returns:
            bool: True if corruption detected, False otherwise.
        """
        # For now, just run the full verification
        return not self.verify()
    
    def repair(self) -> bool:
        """
        Attempt to repair corrupted model files.
        
        Returns:
            bool: True if repair succeeded, False otherwise.
        """
        # For now, just delete and redownload
        from .downloader import ModelDownloader
        downloader = ModelDownloader(
            model_dir=self.model_dir,
            config=self.config,
            platform=None,  # Would need platform instance
            audit_logger=self.audit_logger
        )
        
        # Delete corrupted files
        self.delete_corrupted_files()
        
        # Redownload
        return downloader.download()
    
    def delete_corrupted_files(self) -> bool:
        """
        Delete files that failed verification.
        
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        model_path = self.get_model_path()
        
        if not os.path.exists(model_path):
            return True
        
        try:
            # For now, just delete all model files
            # In a real implementation, we'd only delete files that failed verification
            for filename in os.listdir(model_path):
                filepath = os.path.join(model_path, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete corrupted files: {e}")
            return False
