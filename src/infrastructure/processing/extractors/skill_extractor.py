import json
import re
from pathlib import Path

class SkillExtractor:
    def __init__(self, description: str):
        mapping_path = Path(__file__).parent / "data" / "skill_mapping.json"
        with open(mapping_path, encoding="utf-8") as file:
            self.skill_mapping = json.load(file)
        self.skill_patterns = self._build_patterns()
        self.description = description

    def _build_patterns(self):
        patterns = {}
        self._build_patterns_recursive(self.skill_mapping, patterns)
        return patterns

    def _build_patterns_recursive(self, nodes, patterns):
        for skill_name, node in nodes.items():

            aliases = node.get("aliases", [])

            escaped_aliases = [
                re.escape(alias.lower())
                for alias in aliases
            ]

            patterns[skill_name] = re.compile(
                r"(?<!\w)(?:"
                + "|".join(escaped_aliases)
                + r")(?!\w)",
                re.IGNORECASE
            )

            children = node.get("children", {})

            self._build_patterns_recursive(
                children,
                patterns
            )

    def extract_skills(self):
        self.description = (
            self.description.lower()
            .replace("("," ").replace(")", " ")
            .replace("["," ").replace("]", " ")
        )
        found_skills = set()
        for canonical_skill, pattern in self.skill_patterns.items():
            if pattern.search(self.description):
                found_skills.add(canonical_skill)
        return self._remove_parent_skills(found_skills)
    
    def _remove_parent_skills(self, skills = None):
        skills = set(skills)
        for skill_name, skill_data in self.skill_mapping.items():
            self._remove_recursive(skill_name, skill_data, skills)
        return sorted(skills)
    
    def _remove_recursive(self, node_name, node, skills):
        children = node.get("children", {})
        descendants_present = False

        for child_name, child_node in children.items():
            if child_name in skills:
                descendants_present = True

            descendants_present |= self._remove_recursive(
                child_name,
                child_node,
                skills
            )

        if node_name in skills and descendants_present:
            skills.remove(node_name)

        return node_name in skills or descendants_present