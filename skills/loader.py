"""
OpenNemesis - Skills Loader
Carga la documentación de skills desde ./skills/*/SKILL.md
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("OpenNemesis.SkillsLoader")

SKILLS_DIR = Path("skills")


def load_skill(skill_dir: Path) -> Optional[Dict[str, str]]:
    """Carga una skill desde su directorio"""
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        logger.warning(f"⚠️ SKILL.md no encontrado en {skill_dir}")
        return None
    
    try:
        content = skill_md.read_text(encoding="utf-8")
        
        name = skill_dir.name
        description = _extract_description(content)
        
        logger.info(f"✓ Skill cargada: {name}")
        
        return {
            "name": name,
            "path": str(skill_dir),
            "description": description,
            "content": content
        }
    except Exception as e:
        logger.error(f"✗ Error cargando skill {skill_dir}: {e}")
        return None


def _extract_description(content: str) -> str:
    """Extrae la descripción de la skill del contenido markdown"""
    lines = content.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if line.startswith("description:"):
            return line.split("description:")[1].strip().rstrip(".")
        if line.startswith("# ") and len(line) > 2:
            return line[2:].strip()
    
    return ""


def load_all_skills() -> Dict[str, Dict[str, str]]:
    """Carga todas las skills disponibles"""
    skills = {}
    
    if not SKILLS_DIR.exists():
        logger.warning(f"⚠️ Directorio skills no encontrado: {SKILLS_DIR}")
        return skills
    
    for entry in SKILLS_DIR.iterdir():
        if entry.is_dir() and not entry.name.startswith(".") and not entry.name.startswith("_"):
            skill = load_skill(entry)
            if skill:
                skills[skill["name"]] = skill
    
    logger.info(f"✓ Total skills cargadas: {len(skills)}")
    return skills


def get_skills_context() -> str:
    """Retorna el contexto de todas las skills para el prompt"""
    skills = load_all_skills()
    
    if not skills:
        return "No hay skills disponibles."
    
    context = "=== SKILLS DISPONIBLES ===\n\n"
    
    for name, skill in skills.items():
        context += f"--- {name.upper()} ---\n"
        context += f"{skill['content']}\n\n"
    
    context += "===========================\n"
    
    return context


def get_skill_names() -> List[str]:
    """Retorna lista de nombres de skills"""
    skills = load_all_skills()
    return list(skills.keys())


_global_skills: Optional[Dict[str, Dict[str, str]]] = None


def get_skills(force_reload: bool = False) -> Dict[str, Dict[str, str]]:
    """Obtiene las skills cargadas (cached)"""
    global _global_skills
    
    if _global_skills is None or force_reload:
        _global_skills = load_all_skills()
    
    return _global_skills


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== Skills Loader Test ===")
    context = get_skills_context()
    print(context[:500] + "..." if len(context) > 500 else context)
