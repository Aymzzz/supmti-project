"""
Recommendation service – suggests the best program based on student interests.
"""

from typing import Dict, List, Optional


# Interest-to-program mapping weights
INTEREST_WEIGHTS = {
    "programming": {"genie_informatique": 10, "genie_electrique": 3},
    "informatique": {"genie_informatique": 10, "genie_electrique": 3},
    "développement": {"genie_informatique": 10},
    "web": {"genie_informatique": 8},
    "mobile": {"genie_informatique": 8},
    "ai": {"genie_informatique": 9},
    "intelligence artificielle": {"genie_informatique": 9},
    "data science": {"genie_informatique": 9},
    "machine learning": {"genie_informatique": 9},
    "cybersécurité": {"genie_informatique": 7},
    "réseaux": {"genie_informatique": 7, "genie_electrique": 4},
    "construction": {"genie_civil": 10},
    "bâtiment": {"genie_civil": 10},
    "btp": {"genie_civil": 10},
    "architecture": {"genie_civil": 8},
    "structures": {"genie_civil": 9},
    "électricité": {"genie_electrique": 10},
    "électronique": {"genie_electrique": 10},
    "automatique": {"genie_electrique": 8},
    "robotique": {"genie_electrique": 8, "genie_informatique": 5},
    "énergie": {"genie_electrique": 7},
    "business": {"management": 10},
    "gestion": {"management": 10},
    "marketing": {"management": 9},
    "finance": {"management": 9},
    "comptabilité": {"management": 8},
    "entrepreneuriat": {"management": 9},
    "commerce": {"management": 8},
    "management": {"management": 10},
    "mathématiques": {"genie_informatique": 5, "genie_civil": 5, "genie_electrique": 5},
    "physique": {"genie_civil": 6, "genie_electrique": 6},
}


class RecommendationService:
    """Recommends programs based on student interests and profile."""

    def recommend(
        self,
        interests: List[str],
        diploma: Optional[str] = None,
        note: Optional[float] = None,
    ) -> Dict:
        """
        Generate program recommendations based on interests.

        Args:
            interests: List of student interest keywords
            diploma: Optional diploma for eligibility cross-check
            note: Optional grade

        Returns:
            Dict with ranked recommendations and compatibility scores
        """
        scores = {}

        for interest in interests:
            interest_lower = interest.lower().strip()
            for keyword, weights in INTEREST_WEIGHTS.items():
                if keyword in interest_lower or interest_lower in keyword:
                    for program_id, weight in weights.items():
                        scores[program_id] = scores.get(program_id, 0) + weight

        # Normalize scores to percentages
        max_score = max(scores.values(), default=1)
        recommendations = []

        for program_id, score in sorted(
            scores.items(), key=lambda x: x[1], reverse=True
        ):
            compatibility = min(round((score / max_score) * 100), 100)
            recommendations.append({
                "program_id": program_id,
                "compatibility_score": compatibility,
                "raw_score": score,
                "matched_interests": [
                    interest for interest in interests
                    if any(
                        kw in interest.lower() or interest.lower() in kw
                        for kw, weights in INTEREST_WEIGHTS.items()
                        if program_id in weights
                    )
                ],
            })

        return {
            "recommendations": recommendations,
            "top_pick": recommendations[0] if recommendations else None,
            "message": self._generate_message(recommendations, interests),
        }

    def _generate_message(
        self,
        recommendations: List[Dict],
        interests: List[str],
    ) -> str:
        """Generate a human-readable recommendation message."""
        if not recommendations:
            return (
                "Je n'ai pas pu trouver de correspondance exacte avec vos intérêts. "
                "Pourriez-vous me donner plus de détails sur ce qui vous passionne ?"
            )

        top = recommendations[0]
        return (
            f"Basé sur vos intérêts ({', '.join(interests)}), "
            f"je vous recommande la filière avec un score de compatibilité "
            f"de {top['compatibility_score']}%."
        )


# Global instance
recommendation_service = RecommendationService()
