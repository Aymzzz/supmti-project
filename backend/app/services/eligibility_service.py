"""
Eligibility service – checks if a student is eligible for specific programs.
Uses rule-based logic for immediate, accurate results.
"""

from typing import Dict, List, Optional
import json
import os


# Default eligibility rules (will be loaded from data/ in production)
DEFAULT_RULES = {
    "programs": {
        "genie_informatique": {
            "name": "Génie Informatique",
            "name_en": "Computer Engineering",
            "name_darija": "هندسة المعلوميات",
            "eligible_diplomas": ["Bac Sciences Mathématiques", "Bac Sciences Physiques", "Bac Sciences de la Vie et de la Terre", "BTS Informatique", "DUT Informatique", "DEUG Sciences"],
            "min_note": 12.0,
            "specialties": ["mathématiques", "physique", "informatique"],
            "description": "Formation en développement logiciel, réseaux, et systèmes d'information.",
        },
        "genie_civil": {
            "name": "Génie Civil",
            "name_en": "Civil Engineering",
            "name_darija": "الهندسة المدنية",
            "eligible_diplomas": ["Bac Sciences Mathématiques", "Bac Sciences Physiques", "BTS Génie Civil", "DUT Génie Civil"],
            "min_note": 12.0,
            "specialties": ["mathématiques", "physique"],
            "description": "Formation en construction, structures, et gestion de projets BTP.",
        },
        "genie_electrique": {
            "name": "Génie Électrique",
            "name_en": "Electrical Engineering",
            "name_darija": "الهندسة الكهربائية",
            "eligible_diplomas": ["Bac Sciences Mathématiques", "Bac Sciences Physiques", "BTS Électrotechnique", "DUT Génie Électrique"],
            "min_note": 12.0,
            "specialties": ["mathématiques", "physique", "électronique"],
            "description": "Formation en systèmes électriques, électronique, et automatique.",
        },
        "management": {
            "name": "Management & Gestion",
            "name_en": "Management & Business",
            "name_darija": "التدبير والتسيير",
            "eligible_diplomas": ["Bac Sciences Économiques", "Bac Sciences Mathématiques", "Bac Lettres", "BTS Comptabilité", "DUT Gestion"],
            "min_note": 11.0,
            "specialties": ["économie", "gestion", "comptabilité"],
            "description": "Formation en gestion d'entreprise, marketing, et finance.",
        },
    }
}


class EligibilityService:
    """Rule-based eligibility checker for school programs."""

    def __init__(self):
        self.rules = DEFAULT_RULES
        self._load_rules_from_file()

    def _load_rules_from_file(self):
        """Try to load rules from the data directory."""
        rules_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "data", "admissions", "eligibility_rules.json"
        )
        if os.path.exists(rules_path):
            try:
                with open(rules_path, "r", encoding="utf-8") as f:
                    loaded_rules = json.load(f)
                    if loaded_rules.get("programs"):
                        self.rules = loaded_rules
                        print("✅ Loaded eligibility rules from file")
            except Exception as e:
                print(f"⚠️ Could not load rules file: {e}, using defaults")

    def check_eligibility(
        self,
        diploma: str,
        note: Optional[float] = None,
        specialty: Optional[str] = None,
    ) -> Dict:
        """
        Check which programs a student is eligible for.

        Args:
            diploma: Student's diploma type (e.g., "Bac Sciences Mathématiques")
            note: Student's grade/note (optional)
            specialty: Student's specialty interest (optional)

        Returns:
            Dict with eligible programs, alternatives, and recommendations
        """
        eligible = []
        conditional = []
        not_eligible = []

        for prog_id, prog in self.rules["programs"].items():
            result = self._check_program(prog_id, prog, diploma, note, specialty)
            if result["status"] == "eligible":
                eligible.append(result)
            elif result["status"] == "conditional":
                conditional.append(result)
            else:
                not_eligible.append(result)

        # Sort eligible by relevance score
        eligible.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        return {
            "eligible": eligible,
            "conditional": conditional,
            "not_eligible": not_eligible,
            "summary": self._generate_summary(eligible, conditional, diploma),
        }

    def _check_program(
        self,
        prog_id: str,
        program: Dict,
        diploma: str,
        note: Optional[float],
        specialty: Optional[str],
    ) -> Dict:
        """Check eligibility for a single program."""
        result = {
            "program_id": prog_id,
            "program_name": program["name"],
            "program_name_en": program.get("name_en", ""),
            "program_name_darija": program.get("name_darija", ""),
            "description": program.get("description", ""),
            "status": "not_eligible",
            "reasons": [],
            "relevance": 0,
        }

        # Check diploma match
        diploma_lower = diploma.lower().strip()
        diploma_match = any(
            d.lower() in diploma_lower or diploma_lower in d.lower()
            for d in program["eligible_diplomas"]
        )

        if diploma_match:
            result["relevance"] += 50
            result["reasons"].append(f"Diplôme '{diploma}' accepté")
        else:
            result["reasons"].append(
                f"Diplôme '{diploma}' non reconnu pour cette filière. "
                f"Diplômes acceptés: {', '.join(program['eligible_diplomas'])}"
            )
            result["status"] = "not_eligible"
            return result

        # Check note
        min_note = program.get("min_note", 0)
        if note is not None:
            if note >= min_note:
                result["relevance"] += 30
                result["reasons"].append(
                    f"Note {note}/20 ≥ minimum requis ({min_note}/20)"
                )
            else:
                result["status"] = "conditional"
                result["reasons"].append(
                    f"Note {note}/20 < minimum requis ({min_note}/20). "
                    f"Admission sous condition."
                )
                return result
        else:
            result["reasons"].append(
                f"Note minimale requise: {min_note}/20"
            )

        # Check specialty match (bonus)
        if specialty:
            specialty_lower = specialty.lower()
            if any(s in specialty_lower for s in program.get("specialties", [])):
                result["relevance"] += 20
                result["reasons"].append("Spécialité correspond à la filière")

        result["status"] = "eligible"
        return result

    def _generate_summary(
        self,
        eligible: List[Dict],
        conditional: List[Dict],
        diploma: str,
    ) -> str:
        """Generate a human-readable summary."""
        if eligible:
            names = ", ".join(p["program_name"] for p in eligible)
            return (
                f"Avec votre diplôme '{diploma}', vous êtes éligible à: {names}. "
                f"{'Il y a aussi ' + str(len(conditional)) + ' filière(s) sous condition.' if conditional else ''}"
            )
        elif conditional:
            names = ", ".join(p["program_name"] for p in conditional)
            return (
                f"Avec votre diplôme '{diploma}', vous pourriez être admis sous condition à: {names}."
            )
        else:
            return (
                f"Malheureusement, votre diplôme '{diploma}' ne correspond directement à aucune de nos filières. "
                f"Contactez-nous pour étudier votre dossier individuellement."
            )

    def get_all_programs(self) -> List[Dict]:
        """Return all available programs with their details."""
        return [
            {
                "id": prog_id,
                **{k: v for k, v in prog.items() if k != "eligible_diplomas"},
                "eligible_diplomas": prog["eligible_diplomas"],
            }
            for prog_id, prog in self.rules["programs"].items()
        ]


# Global instance
eligibility_service = EligibilityService()
