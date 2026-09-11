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
    """
    
    def __init__(
        self,
        skills_dir: str,
        config: ConfigManager,
        audit_logger: AuditLogger
    ):
        self.skills_dir = os.path.expanduser(skills_dir)
        self.config = config
        self.audit_logger = audit_logger
        
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
        
        os.makedirs(self.skills_dir, exist_ok=True)
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._load_skills()
        
        logging.info(f"SkillManager initialized at {self.skills_dir}")
    
    def list_skills(self) -> List[Dict[str, Any]]:
        return self.list()

    def create_skill(self, name: str) -> bool:
        return self.create(name, description=f"Skill {name}", code="result = 'Success'")

    def _load_skills(self) -> None:
        """Load all skills from disk and register built-in skills."""
        self._skills = {}
        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            if os.path.isdir(skill_path):
                skill = self._load_skill(skill_name, skill_path)
                if skill:
                    self._skills[skill_name] = skill

        try:
            from .builtin import get_builtin_skills
            for b_skill in get_builtin_skills():
                b_name = b_skill["name"]
                if b_name not in self._skills:
                    self._skills[b_name] = b_skill
                    self._save_skill(b_name, b_skill)
        except Exception as e:
            logging.warning(f"Failed to load built-in skills: {e}")

    def _load_skill(self, skill_name: str, skill_path: str) -> Optional[Dict[str, Any]]:
        try:
            skill_json_path = os.path.join(skill_path, "skill.json")
            if not os.path.exists(skill_json_path):
                return None
            
            with open(skill_json_path, 'r') as f:
                skill_data = json.load(f)
            
            instructions_path = os.path.join(skill_path, "instructions.md")
            if os.path.exists(instructions_path):
                with open(instructions_path, 'r') as f:
                    skill_data["instructions"] = f.read()
            
            validation_path = os.path.join(skill_path, "validation.json")
            if os.path.exists(validation_path):
                with open(validation_path, 'r') as f:
                    skill_data["validation"] = json.load(f)
            
            examples_path = os.path.join(skill_path, "examples.json")
            if os.path.exists(examples_path):
                with open(examples_path, 'r') as f:
                    skill_data["examples"] = json.load(f)
            
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
        try:
            skill_path = os.path.join(self.skills_dir, skill_name)
            os.makedirs(skill_path, exist_ok=True)
            
            skill_json_path = os.path.join(skill_path, "skill.json")
            with open(skill_json_path, 'w') as f:
                json.dump(skill_data, f, indent=2)
            
            if "instructions" in skill_data:
                instructions_path = os.path.join(skill_path, "instructions.md")
                with open(instructions_path, 'w') as f:
                    f.write(skill_data["instructions"])
            
            if "validation" in skill_data:
                validation_path = os.path.join(skill_path, "validation.json")
                with open(validation_path, 'w') as f:
                    json.dump(skill_data["validation"], f, indent=2)
            
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
        if not self._is_valid_skill_name(name):
            return False
        
        if name in self._skills:
            return False
        
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
        
        if not self.validator.validate(skill_data):
            return False
        
        if not self._save_skill(name, skill_data):
            return False
        
        self._skills[name] = skill_data
        self.audit_logger.log("SKILL_CREATE", f"Created skill {name}")
        return True
    
    def _is_valid_skill_name(self, name: str) -> bool:
        if not name or len(name) > 50:
            return False
        invalid_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        return not any(char in name for char in invalid_chars)
    
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self._skills.get(name)
    
    def list(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": skill.get("description", ""),
                "enabled": skill.get("enabled", True),
                "created_at": skill.get("created_at", 0),
            }
            for name, skill in self._skills.items()
        ]
    
    def update(self, name: str, updates: Dict[str, Any]) -> bool:
        if name not in self._skills:
            return False
        skill = self._skills[name]
        skill.update(updates)
        skill["updated_at"] = time.time()
        if not self.validator.validate(skill):
            return False
        if not self._save_skill(name, skill):
            return False
        self.audit_logger.log("SKILL_UPDATE", f"Updated skill {name}")
        return True
    
    def delete(self, name: str) -> bool:
        if name not in self._skills:
            return False
        skill_path = os.path.join(self.skills_dir, name)
        try:
            import shutil
            shutil.rmtree(skill_path)
        except Exception as e:
            logging.error(f"Failed to delete skill directory {skill_path}: {e}")
            return False
        del self._skills[name]
        self.audit_logger.log("SKILL_DELETE", f"Deleted skill {name}")
        return True
    
    def enable(self, name: str) -> bool:
        return self.update(name, {"enabled": True})
    
    def disable(self, name: str) -> bool:
        return self.update(name, {"enabled": False})
    
    def test(self, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._skills:
            return {"error": f"Skill {name} not found"}
        skill = self._skills[name]
        if not skill.get("enabled", True):
            return {"error": f"Skill {name} is disabled"}
        code = skill.get("code", "")
        if not code:
            return {"error": f"Skill {name} has no code"}
        try:
            return self.executor.execute(name=name, code=code, input_data=input_data, permissions=skill)
        except Exception as e:
            return {"error": str(e)}
    
    def run(self, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.test(name, input_data)
    
    def get_skill_count(self) -> int:
        return len(self._skills)
    
    def get_enabled_skills(self) -> List[str]:
        return [name for name, skill in self._skills.items() if skill.get("enabled", True)]
    
    def get_disabled_skills(self) -> List[str]:
        return [name for name, skill in self._skills.items() if not skill.get("enabled", True)]
    
    def reload(self) -> None:
        self._load_skills()
        self.audit_logger.log("SKILL_RELOAD", "Reloaded all skills")
    
    def doctor(self) -> Dict[str, Any]:
        return {
            "skills_dir": self.skills_dir,
            "skills_dir_exists": os.path.exists(self.skills_dir),
            "total_skills": len(self._skills),
            "enabled_skills": len(self.get_enabled_skills()),
            "disabled_skills": len(self.get_disabled_skills()),
        }
