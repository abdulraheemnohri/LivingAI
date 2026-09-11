# LivingAI Skill Manager
# ======================
# This module manages skills for the LivingAI system.

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

# Local imports
from .validator import SkillValidator
from .sandbox import SkillSandbox
from .executor import SkillExecutor
from ..config import ConfigManager
from ..security.audit import AuditLogger


class SkillManager:
    """
    Manages skills for the LivingAI system.
    
    Responsibilities:
    - CRUD operations for skills
    - Skill validation
    - Skill execution
    - Skill testing
    - Skill import/export
    """
    
    def __init__(
        self,
        skills_dir: str,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        """
        Initialize the SkillManager.
        
        Args:
            skills_dir: Directory to store skills.
            config: Configuration manager.
            audit_logger: Audit logger for tracking actions.
        """
        self.skills_dir = os.path.expanduser(skills_dir)
        self.config = config
        self.audit_logger = audit_logger
        
        # Initialize components
        self.validator = SkillValidator(
            config=self.config,
            audit_logger=self.audit_logger
        )
        self.sandbox = SkillSandbox(
            config=self.config,
            audit_logger=self.audit_logger
        )
        self.executor = SkillExecutor(
            sandbox=self.sandbox,
            config=self.config,
            audit_logger=self.audit_logger
        )
        
        # Create skills directory if it doesn't exist
        os.makedirs(self.skills_dir, exist_ok=True)
        
        # Skill state
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._load_skills()
        
        logging.info(f"SkillManager initialized at {self.skills_dir}")
    
    def _load_skills(self) -> None:
        """Load all skills from the skills directory."""
        self._skills = {}
        
        # Scan skills directory
        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            
            if os.path.isdir(skill_path):
                skill = self._load_skill(skill_name, skill_path)
                if skill:
                    self._skills[skill_name] = skill
    
    def _load_skill(self, skill_name: str, skill_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a single skill from its directory.
        
        Args:
            skill_name: Name of the skill.
            skill_path: Path to the skill directory.
            
        Returns:
            Optional[Dict[str, Any]]: Loaded skill, or None if failed.
        """
        try:
            # Load skill.json
            skill_json_path = os.path.join(skill_path, "skill.json")
            if not os.path.exists(skill_json_path):
                return None
            
            with open(skill_json_path, 'r') as f:
                skill_data = json.load(f)
            
            # Load instructions.md if it exists
            instructions_path = os.path.join(skill_path, "instructions.md")
            if os.path.exists(instructions_path):
                with open(instructions_path, 'r') as f:
                    skill_data["instructions"] = f.read()
            
            # Load validation.json if it exists
            validation_path = os.path.join(skill_path, "validation.json")
            if os.path.exists(validation_path):
                with open(validation_path, 'r') as f:
                    skill_data["validation"] = json.load(f)
            
            # Load examples.json if it exists
            examples_path = os.path.join(skill_path, "examples.json")
            if os.path.exists(examples_path):
                with open(examples_path, 'r') as f:
                    skill_data["examples"] = json.load(f)
            
            # Set default values
            skill_data.setdefault("enabled", True)
            skill_data.setdefault("sandboxed", True)
            skill_data.setdefault("allow_network", False)
            skill_data.setdefault("allow_filesystem", False)
            skill_data.setdefault("allow_shell", False)
            
            return skill_data
            
        except Exception as e:
            logging.error(f"Failed to load skill {skill_name}: {e}")
            return None
    
    def _save_skill(self, skill_name: str, skill_data: Dict[str, Any]) -> bool:
        """
        Save a skill to its directory.
        
        Args:
            skill_name: Name of the skill.
            skill_data: Skill data to save.
            
        Returns:
            bool: True if save succeeded, False otherwise.
        """
        try:
            skill_path = os.path.join(self.skills_dir, skill_name)
            os.makedirs(skill_path, exist_ok=True)
            
            # Save skill.json
            skill_json_path = os.path.join(skill_path, "skill.json")
            with open(skill_json_path, 'w') as f:
                json.dump(skill_data, f, indent=2)
            
            # Save instructions.md if present
            if "instructions" in skill_data:
                instructions_path = os.path.join(skill_path, "instructions.md")
                with open(instructions_path, 'w') as f:
                    f.write(skill_data["instructions"])
            
            # Save validation.json if present
            if "validation" in skill_data:
                validation_path = os.path.join(skill_path, "validation.json")
                with open(validation_path, 'w') as f:
                    json.dump(skill_data["validation"], f, indent=2)
            
            # Save examples.json if present
            if "examples" in skill_data:
                examples_path = os.path.join(skill_path, "examples.json")
                with open(examples_path, 'w') as f:
                    json.dump(skill_data["examples"], f, indent=2)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to save skill {skill_name}: {e}")
            return False
    
    def create(
        self,
        name: str,
        description: str = "",
        instructions: str = "",
        code: str = "",
        validation: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Create a new skill.
        
        Args:
            name: Name of the skill.
            description: Description of the skill.
            instructions: Instructions for the skill.
            code: Code for the skill.
            validation: Validation rules for the skill.
            examples: Example inputs/outputs for the skill.
            
        Returns:
            bool: True if creation succeeded, False otherwise.
        """
        # Validate skill name
        if not self._is_valid_skill_name(name):
            logging.error(f"Invalid skill name: {name}")
            return False
        
        # Check if skill already exists
        if name in self._skills:
            logging.error(f"Skill {name} already exists")
            return False
        
        # Create skill data
        skill_data = {
            "name": name,
            "description": description,
            "instructions": instructions,
            "code": code,
            "validation": validation or {},
            "examples": examples or [],
            "enabled": True,
            "sandboxed": True,
            "allow_network": False,
            "allow_filesystem": False,
            "allow_shell": False,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        
        # Validate the skill
        if not self.validator.validate(skill_data):
            logging.error(f"Skill {name} failed validation")
            return False
        
        # Save the skill
        if not self._save_skill(name, skill_data):
            return False
        
        # Add to loaded skills
        self._skills[name] = skill_data
        
        self.audit_logger.log(
            "SKILL_CREATE",
            f"Created skill {name}"
        )
        
        return True
    
    def _is_valid_skill_name(self, name: str) -> bool:
        """
        Check if a skill name is valid.
        
        Args:
            name: Skill name to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Basic validation
        if not name:
            return False
        
        # Check for invalid characters
        invalid_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        if any(char in name for char in invalid_chars):
            return False
        
        # Check if name is too long
        if len(name) > 50:
            return False
        
        return True
    
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a skill by name.
        
        Args:
            name: Name of the skill.
            
        Returns:
            Optional[Dict[str, Any]]: The skill, or None if not found.
        """
        return self._skills.get(name)
    
    def list(self) -> List[Dict[str, Any]]:
        """
        List all skills.
        
        Returns:
            List[Dict[str, Any]]: List of all skills.
        """
        return [
            {
                "name": name,
                "description": skill.get("description", ""),
                "enabled": skill.get("enabled", True),
                "created_at": skill.get("created_at", 0),
            }
            for name, skill in self._skills.items()
        ]
    
    def update(
        self,
        name: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a skill.
        
        Args:
            name: Name of the skill to update.
            updates: Dictionary of updates to apply.
            
        Returns:
            bool: True if update succeeded, False otherwise.
        """
        if name not in self._skills:
            return False
        
        # Get current skill
        skill = self._skills[name]
        
        # Apply updates
        skill.update(updates)
        skill["updated_at"] = time.time()
        
        # Validate the updated skill
        if not self.validator.validate(skill):
            logging.error(f"Updated skill {name} failed validation")
            return False
        
        # Save the skill
        if not self._save_skill(name, skill):
            return False
        
        self.audit_logger.log(
            "SKILL_UPDATE",
            f"Updated skill {name}"
        )
        
        return True
    
    def delete(self, name: str) -> bool:
        """
        Delete a skill.
        
        Args:
            name: Name of the skill to delete.
            
        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        if name not in self._skills:
            return False
        
        # Delete skill directory
        skill_path = os.path.join(self.skills_dir, name)
        try:
            import shutil
            shutil.rmtree(skill_path)
        except Exception as e:
            logging.error(f"Failed to delete skill directory {skill_path}: {e}")
            return False
        
        # Remove from loaded skills
        del self._skills[name]
        
        self.audit_logger.log(
            "SKILL_DELETE",
            f"Deleted skill {name}"
        )
        
        return True
    
    def enable(self, name: str) -> bool:
        """
        Enable a skill.
        
        Args:
            name: Name of the skill to enable.
            
        Returns:
            bool: True if enable succeeded, False otherwise.
        """
        return self.update(name, {"enabled": True})
    
    def disable(self, name: str) -> bool:
        """
        Disable a skill.
        
        Args:
            name: Name of the skill to disable.
            
        Returns:
            bool: True if disable succeeded, False otherwise.
        """
        return self.update(name, {"enabled": False})
    
    def test(self, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test a skill with input data.
        
        Args:
            name: Name of the skill to test.
            input_data: Input data for the test.
            
        Returns:
            Dict[str, Any]: Test results.
        """
        if name not in self._skills:
            return {"error": f"Skill {name} not found"}
        
        skill = self._skills[name]
        
        if not skill.get("enabled", True):
            return {"error": f"Skill {name} is disabled"}
        
        # Get the skill code
        code = skill.get("code", "")
        if not code:
            return {"error": f"Skill {name} has no code"}
        
        # Execute in sandbox
        try:
            result = self.executor.execute(
                name=name,
                code=code,
                input_data=input_data,
                permissions=skill
            )
            
            self.audit_logger.log(
                "SKILL_TEST",
                f"Tested skill {name}"
            )
            
            return result
            
        except Exception as e:
            self.audit_logger.log(
                "SKILL_TEST_FAIL",
                f"Test failed for skill {name}: {str(e)}"
            )
            return {"error": str(e)}
    
    def run(
        self,
        name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a skill with input data.
        
        Args:
            name: Name of the skill to run.
            input_data: Input data for the skill.
            
        Returns:
            Dict[str, Any]: Execution results.
        """
        if name not in self._skills:
            return {"error": f"Skill {name} not found"}
        
        skill = self._skills[name]
        
        if not skill.get("enabled", True):
            return {"error": f"Skill {name} is disabled"}
        
        # Get the skill code
        code = skill.get("code", "")
        if not code:
            return {"error": f"Skill {name} has no code"}
        
        # Execute in sandbox
        try:
            result = self.executor.execute(
                name=name,
                code=code,
                input_data=input_data,
                permissions=skill
            )
            
            self.audit_logger.log(
                "SKILL_RUN",
                f"Ran skill {name}"
            )
            
            return result
            
        except Exception as e:
            self.audit_logger.log(
                "SKILL_RUN_FAIL",
                f"Run failed for skill {name}: {str(e)}"
            )
            return {"error": str(e)}
    
    def export_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Export a skill as a dictionary.
        
        Args:
            name: Name of the skill to export.
            
        Returns:
            Optional[Dict[str, Any]]: Exported skill, or None if not found.
        """
        if name not in self._skills:
            return None
        
        return self._skills[name].copy()
    
    def import_skill(self, skill_data: Dict[str, Any]) -> bool:
        """
        Import a skill from a dictionary.
        
        Args:
            skill_data: Skill data to import.
            
        Returns:
            bool: True if import succeeded, False otherwise.
        """
        name = skill_data.get("name")
        if not name:
            return False
        
        # Check if skill already exists
        if name in self._skills:
            return False
        
        # Validate the skill
        if not self.validator.validate(skill_data):
            return False
        
        # Save the skill
        if not self._save_skill(name, skill_data):
            return False
        
        # Add to loaded skills
        self._skills[name] = skill_data
        
        self.audit_logger.log(
            "SKILL_IMPORT",
            f"Imported skill {name}"
        )
        
        return True
    
    def get_skill_count(self) -> int:
        """
        Get the total number of skills.
        
        Returns:
            int: Number of skills.
        """
        return len(self._skills)
    
    def get_enabled_skills(self) -> List[str]:
        """
        Get a list of enabled skill names.
        
        Returns:
            List[str]: List of enabled skill names.
        """
        return [name for name, skill in self._skills.items() if skill.get("enabled", True)]
    
    def get_disabled_skills(self) -> List[str]:
        """
        Get a list of disabled skill names.
        
        Returns:
            List[str]: List of disabled skill names.
        """
        return [name for name, skill in self._skills.items() if not skill.get("enabled", True)]
    
    def reload(self) -> None:
        """Reload all skills from disk."""
        self._load_skills()
        self.audit_logger.log("SKILL_RELOAD", "Reloaded all skills")
    
    def doctor(self) -> Dict[str, Any]:
        """
        Run skill system diagnostics.
        
        Returns:
            Dict[str, Any]: Diagnostic results.
        """
        return {
            "skills_dir": self.skills_dir,
            "skills_dir_exists": os.path.exists(self.skills_dir),
            "total_skills": len(self._skills),
            "enabled_skills": len(self.get_enabled_skills()),
            "disabled_skills": len(self.get_disabled_skills()),
        }
