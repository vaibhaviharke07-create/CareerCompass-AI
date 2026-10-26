"""
CareerCompass AI — Career Recommendation & Skill-Gap Analysis Engine
Accurate, explainable, and transparent career guidance for students.
"""

import os
import csv
import math
from typing import Dict, List, Any, Optional

# Default weights for scoring formula (sums to 1.0)
DEFAULT_WEIGHTS = {
    "interests": 0.30,
    "skills": 0.30,
    "subjects": 0.20,
    "activities": 0.15,
    "preferences": 0.05,
}

# Standard 6-Stage Roadmap Template Generator
def build_roadmap_stages(career: Dict[str, Any], hours_per_day: float = 2.0) -> List[Dict[str, Any]]:
    tools = career.get("tools_technologies", [])
    req_skills = career.get("required_skills", [])
    useful_skills = career.get("useful_skills", [])
    projects = career.get("beginner_projects", [])
    base_weeks = int(career.get("roadmap_weeks", 20))
    
    # Adjust duration based on study hours (standard baseline: 2 hours/day)
    time_factor = 2.0 / max(0.5, float(hours_per_day))
    adj_weeks = max(8, int(round(base_weeks * time_factor)))
    
    w1 = max(2, int(round(adj_weeks * 0.15)))
    w2 = max(3, int(round(adj_weeks * 0.25)))
    w3 = max(2, int(round(adj_weeks * 0.20)))
    w4 = max(2, int(round(adj_weeks * 0.15)))
    w5 = max(2, int(round(adj_weeks * 0.15)))
    w6 = max(1, adj_weeks - (w1 + w2 + w3 + w4 + w5))
    if w6 < 1:
        w6 = 1

    return [
        {
            "stage_id": 1,
            "title": "Stage 1: Foundations",
            "estimated_weeks": w1,
            "objectives": "Understand core theoretical foundations, principles, and terminology.",
            "topics": [
                f"Introduction to {career.get('name')}",
                f"Prerequisites: {career.get('prerequisites', 'Basic computing and analytical logic')}",
                "Fundamental terminology and domain workflows",
                "Ethics and industry standards"
            ],
            "practice_tasks": [
                "Read overview documentation and complete beginner syntax exercises",
                "Set up local development or working environment",
                "Write your first 'Hello World' or foundational script"
            ],
            "milestone_project": "Environment setup guide and foundational concepts summary notes.",
            "completed": False
        },
        {
            "stage_id": 2,
            "title": "Stage 2: Core Technical Skills",
            "estimated_weeks": w2,
            "objectives": "Master primary technical concepts, languages, and methodologies.",
            "topics": [
                f"Core skill: {req_skills[0] if len(req_skills) > 0 else 'Problem-solving'}",
                f"Secondary skill: {req_skills[1] if len(req_skills) > 1 else 'Logical thinking'}",
                f"Specialized domain methods: {req_skills[2] if len(req_skills) > 2 else 'Data structures'}",
                "Algorithmic problem-solving and clean patterns"
            ],
            "practice_tasks": [
                "Complete 15-20 targeted coding or analysis exercises",
                "Implement 3 modular functions solving real domain calculations",
                "Document edge cases and error handling"
            ],
            "milestone_project": projects[0] if len(projects) > 0 else "Foundational domain exercise application.",
            "completed": False
        },
        {
            "stage_id": 3,
            "title": "Stage 3: Tools & Technologies",
            "estimated_weeks": w3,
            "objectives": "Gain hands-on proficiency with industry-standard developer and workflow tools.",
            "topics": [
                f"Primary tooling: {tools[0] if len(tools) > 0 else 'Git'}",
                f"Ecosystem tool: {tools[1] if len(tools) > 1 else 'VS Code'}",
                f"Testing & CI/CD tools: {tools[2] if len(tools) > 2 else 'Postman'}",
                "Version control workflows (Git commits, branches, pull requests)"
            ],
            "practice_tasks": [
                "Configure a GitHub repository with a descriptive README and LICENSE",
                "Integrate external libraries and package managers",
                "Automate recurring commands with scripts or workflows"
            ],
            "milestone_project": "Configured repository featuring modular scripts, unit tests, and structured config.",
            "completed": False
        },
        {
            "stage_id": 4,
            "title": "Stage 4: Small Practice Projects",
            "estimated_weeks": w4,
            "objectives": "Synthesize learned skills by building focused, end-to-end applications.",
            "topics": [
                "End-to-end application lifecycle",
                "Input validation, data persistence, and error feedback",
                "User interface or CLI ergonomics",
                "Automated testing and verification"
            ],
            "practice_tasks": [
                "Build application logic from scratch without following a verbatim tutorial",
                "Implement automated tests covering main positive and negative cases",
                "Collect feedback from a peer or mentor"
            ],
            "milestone_project": projects[1] if len(projects) > 1 else (projects[0] if len(projects) > 0 else "Practice project."),
            "completed": False
        },
        {
            "stage_id": 5,
            "title": "Stage 5: Capstone Portfolio Project",
            "estimated_weeks": w5,
            "objectives": "Build a comprehensive showcase project demonstrating production readiness.",
            "topics": [
                "System architecture design and modularity",
                "Clean documentation, architecture diagrams, and live demonstration",
                "Performance profiling and security considerations",
                "Public deployment or executable packaging"
            ],
            "practice_tasks": [
                "Draft a 1-page Project Specification before writing code",
                "Build features iteratively with disciplined Git commit history",
                "Deploy live demo or package downloadable executable with setup script",
                "Record a 3-minute video walkthrough explaining architectural decisions"
            ],
            "milestone_project": projects[2] if len(projects) > 2 else "Comprehensive capstone portfolio application.",
            "completed": False
        },
        {
            "stage_id": 6,
            "title": "Stage 6: Internship & Career Preparation",
            "estimated_weeks": w6,
            "objectives": "Prepare professional artifacts, interview readiness, and network outreach.",
            "topics": [
                f"Target roles: {', '.join(career.get('entry_level_roles', ['Junior Associate']))}",
                "Crafting an ATS-friendly, skill-aligned resume",
                "Technical interview questions and system walkthroughs",
                "Contributing to open source and community projects"
            ],
            "practice_tasks": [
                "Refactor resume highlighting projects, measurable outcomes, and exact skills",
                "Conduct 2 mock technical interviews with peers",
                "Apply to 5 entry-level internships or junior positions with tailored cover notes"
            ],
            "milestone_project": "Polished developer portfolio website and interview-ready GitHub repository.",
            "completed": False
        }
    ]


class CareerEngine:
    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            # Look in standard paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            candidate = os.path.join(base_dir, "data", "careers.csv")
            if os.path.exists(candidate):
                csv_path = candidate
            else:
                csv_path = "data/careers.csv"
        self.csv_path = csv_path
        self.careers: List[Dict[str, Any]] = []
        self.load_dataset()

    def load_dataset(self) -> None:
        """Loads careers dataset from CSV with reliable parsing."""
        if not os.path.exists(self.csv_path):
            self.careers = []
            return

        careers = []
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                career = {
                    "id": row.get("id", "").strip(),
                    "name": row.get("name", "").strip(),
                    "category": row.get("category", "").strip(),
                    "description": row.get("description", "").strip(),
                    "responsibilities": [r.strip() for r in row.get("responsibilities", "").split(";") if r.strip()],
                    "interests": [i.strip() for i in row.get("interests", "").split(";") if i.strip()],
                    "subjects": [s.strip() for s in row.get("subjects", "").split(";") if s.strip()],
                    "required_skills": [sk.strip() for sk in row.get("required_skills", "").split(";") if sk.strip()],
                    "useful_skills": [sk.strip() for sk in row.get("useful_skills", "").split(";") if sk.strip()],
                    "tools_technologies": [t.strip() for t in row.get("tools_technologies", "").split(";") if t.strip()],
                    "beginner_projects": [p.strip() for p in row.get("beginner_projects", "").split(";") if p.strip()],
                    "entry_level_roles": [r.strip() for r in row.get("entry_level_roles", "").split(";") if r.strip()],
                    "prerequisites": row.get("prerequisites", "").strip(),
                    "work_style": row.get("work_style", "Team-based").strip(),
                    "work_focus": row.get("work_focus", "Analytical").strip(),
                    "roadmap_weeks": int(row.get("roadmap_weeks", 20)) if row.get("roadmap_weeks", "").isdigit() else 20,
                }
                # Combined skills list for lookup
                career["all_skills"] = list(dict.fromkeys(career["required_skills"] + career["useful_skills"]))
                careers.append(career)
        self.careers = careers

    def get_all_careers(self) -> List[Dict[str, Any]]:
        return self.careers

    def get_career_by_id(self, career_id: str) -> Optional[Dict[str, Any]]:
        for c in self.careers:
            if c["id"].lower() == career_id.lower():
                return c
        return None

    def _normalize_string_set(self, items: List[str]) -> set:
        return {str(x).strip().lower() for x in items if str(x).strip()}

    def _calculate_overlap_score(self, user_items: List[str], career_items: List[str]) -> float:
        """Calculates normalized Jaccard-like overlap score between 0.0 and 1.0."""
        user_set = self._normalize_string_set(user_items)
        career_set = self._normalize_string_set(career_items)
        if not career_set:
            return 0.5 if not user_set else 0.0
        if not user_set:
            return 0.0
        overlap = user_set.intersection(career_set)
        # Recall-weighted overlap: how well user attributes satisfy the career requirements
        return len(overlap) / len(career_set)

    def recommend(self, profile: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculates normalized, explainable career recommendations.
        Returns sorted recommendations with score breakdowns and explanations.
        """
        if weights is None:
            weights = DEFAULT_WEIGHTS

        user_interests = profile.get("interests", []) or []
        user_subjects = profile.get("favourite_subjects", profile.get("subjects", [])) or []
        user_skills = profile.get("existing_skills", profile.get("skills", [])) or []
        user_activities = profile.get("activities", []) or []
        preferred_category = (profile.get("preferred_category") or "").strip().lower()
        work_focus_pref = (profile.get("work_focus") or "").strip().lower()
        hours_per_day = float(profile.get("available_hours_per_day", 2.0) or 2.0)

        results = []
        is_partial_profile = (len(user_interests) == 0 and len(user_skills) == 0 and len(user_subjects) == 0)

        for career in self.careers:
            # 1. Interests Score
            s_interests = self._calculate_overlap_score(user_interests, career["interests"])

            # 2. Subjects Score
            s_subjects = self._calculate_overlap_score(user_subjects, career["subjects"])

            # 3. Skills Score: required skills weighted 2x compared to useful skills
            req_set = self._normalize_string_set(career["required_skills"])
            useful_set = self._normalize_string_set(career["useful_skills"])
            user_skill_set = self._normalize_string_set(user_skills)

            req_overlap = len(user_skill_set.intersection(req_set))
            useful_overlap = len(user_skill_set.intersection(useful_set))

            total_points = (len(req_set) * 2) + len(useful_set)
            earned_points = (req_overlap * 2) + useful_overlap
            s_skills = (earned_points / total_points) if total_points > 0 else 0.0

            # 4. Activities Score
            # Map activities loosely to career domain
            career_text = (
                career["name"] + " " +
                career["category"] + " " +
                " ".join(career["responsibilities"]) + " " +
                " ".join(career["beginner_projects"])
            ).lower()
            
            matched_activities = 0
            for act in user_activities:
                act_words = [w for w in act.lower().split() if len(w) > 3]
                if any(w in career_text for w in act_words):
                    matched_activities += 1
            s_activities = (matched_activities / max(1, len(user_activities))) if user_activities else 0.0

            # 5. Preferences Score
            pref_score = 0.5 # Neutral baseline
            if preferred_category and preferred_category != "all":
                if preferred_category in career["category"].lower():
                    pref_score += 0.3
                else:
                    pref_score -= 0.2
            if work_focus_pref and work_focus_pref != "any":
                if work_focus_pref in career["work_focus"].lower():
                    pref_score += 0.2
                else:
                    pref_score -= 0.1
            s_pref = max(0.0, min(1.0, pref_score))

            # Composite weighted match calculation
            w_total = sum(weights.values())
            raw_score = (
                (weights["interests"] * s_interests) +
                (weights["skills"] * s_skills) +
                (weights["subjects"] * s_subjects) +
                (weights["activities"] * s_activities) +
                (weights["preferences"] * s_pref)
            ) / (w_total if w_total > 0 else 1.0)

            # Boost slightly for baseline if partial profile
            match_percentage = round(raw_score * 100, 1)

            # Matched specific attributes
            matched_interests = [i for i in career["interests"] if i.lower() in self._normalize_string_set(user_interests)]
            matched_subjects = [s for s in career["subjects"] if s.lower() in self._normalize_string_set(user_subjects)]
            matched_skills = [sk for sk in career["all_skills"] if sk.lower() in self._normalize_string_set(user_skills)]

            # Generate honest reason why
            why_reasons = []
            if matched_interests:
                why_reasons.append(f"Directly connects with your interest in {', '.join(matched_interests[:2])}.")
            if matched_skills:
                why_reasons.append(f"Leverages your existing background in {', '.join(matched_skills[:2])}.")
            if matched_subjects:
                why_reasons.append(f"Builds on your coursework in {', '.join(matched_subjects[:2])}.")
            if not why_reasons:
                why_reasons.append(f"Provides a strong entry into {career['category']} based on your selected preferences.")

            # Identify areas needing exploration
            missing_req = [sk for sk in career["required_skills"] if sk.lower() not in self._normalize_string_set(user_skills)]
            explore_areas = []
            if missing_req:
                explore_areas.append(f"Strengthen key foundations in {', '.join(missing_req[:2])}.")
            explore_areas.append(f"Build small starter projects such as '{career['beginner_projects'][0]}'.")

            results.append({
                "career_id": career["id"],
                "name": career["name"],
                "category": career["category"],
                "description": career["description"],
                "match_score": match_percentage,
                "score_breakdown": {
                    "interests": round(s_interests * 100, 1),
                    "skills": round(s_skills * 100, 1),
                    "subjects": round(s_subjects * 100, 1),
                    "activities": round(s_activities * 100, 1),
                    "preferences": round(s_pref * 100, 1),
                },
                "matched_attributes": {
                    "interests": matched_interests,
                    "subjects": matched_subjects,
                    "skills": matched_skills,
                },
                "why_recommended": " ".join(why_reasons),
                "areas_to_explore": explore_areas,
                "work_style": career["work_style"],
                "work_focus": career["work_focus"],
                "roadmap_weeks": career["roadmap_weeks"],
                "entry_level_roles": career["entry_level_roles"],
                "required_skills": career["required_skills"],
                "useful_skills": career["useful_skills"],
                "tools_technologies": career["tools_technologies"],
                "beginner_projects": career["beginner_projects"],
            })

        # Rank strictly by match_score descending
        results.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "top_recommendations": results[:3],
            "all_recommendations": results,
            "total_analyzed": len(results),
            "is_partial_profile": is_partial_profile,
            "disclaimer": "Scores reflect calculated profile-match similarity based on your selected interests and skills. They do not predict guaranteed job outcomes or employment likelihood."
        }

    def analyze_skill_gap(self, career_id: str, user_skills: List[str]) -> Dict[str, Any]:
        """
        Calculates skill gap analysis for a chosen career against user skills.
        """
        career = self.get_career_by_id(career_id)
        if not career:
            return {"error": f"Career with ID '{career_id}' not found."}

        user_skills_normalized = self._normalize_string_set(user_skills)
        
        req_skills = career["required_skills"]
        useful_skills = career["useful_skills"]
        all_career_skills = list(dict.fromkeys(req_skills + useful_skills))

        possessed_skills = [s for s in all_career_skills if s.lower() in user_skills_normalized]
        missing_skills = [s for s in all_career_skills if s.lower() not in user_skills_normalized]

        total_count = len(all_career_skills)
        possessed_count = len(possessed_skills)
        readiness_pct = round((possessed_count / total_count * 100), 1) if total_count > 0 else 0.0

        # Prioritize missing skills: missing required skills first
        priority_skills = []
        for s in req_skills:
            if s.lower() not in user_skills_normalized:
                priority_skills.append({"skill": s, "type": "Required", "priority": "High"})
        for s in useful_skills:
            if s.lower() not in user_skills_normalized:
                priority_skills.append({"skill": s, "type": "Useful", "priority": "Medium"})

        # Practice activities tailored to missing skills
        suggested_practices = []
        for p_item in priority_skills[:3]:
            suggested_practices.append(f"Practice exercises and build mini-modules targeting {p_item['skill']}.")

        return {
            "career_id": career["id"],
            "career_name": career["name"],
            "category": career["category"],
            "total_skills_count": total_count,
            "possessed_skills_count": possessed_count,
            "missing_skills_count": len(missing_skills),
            "skill_readiness_percentage": readiness_pct,
            "possessed_skills": possessed_skills,
            "missing_skills": missing_skills,
            "priority_skills_to_learn": priority_skills,
            "suggested_practice_activities": suggested_practices,
            "suggested_beginner_projects": career["beginner_projects"],
            "tools_to_learn": career["tools_technologies"][:4],
            "disclaimer": "Selecting a skill indicates your exposure or study, not certified mastery. Practical project application is advised to solidify knowledge."
        }

    def compare_careers(self, career_ids: List[str], user_skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compares 2 to 3 careers side-by-side using real dataset values.
        """
        if not career_ids or len(career_ids) < 2:
            return {"error": "Please provide at least 2 career IDs to compare."}

        selected_careers = []
        for cid in career_ids[:3]:
            c = self.get_career_by_id(cid)
            if c:
                selected_careers.append(c)

        if len(selected_careers) < 2:
            return {"error": "Could not find at least two valid careers to compare."}

        user_skills = user_skills or []
        user_skills_set = self._normalize_string_set(user_skills)

        comparison_items = []
        for c in selected_careers:
            all_skills = c["all_skills"]
            possessed = [s for s in all_skills if s.lower() in user_skills_set]
            missing = [s for s in all_skills if s.lower() not in user_skills_set]
            readiness = round((len(possessed) / len(all_skills) * 100), 1) if all_skills else 0.0

            comparison_items.append({
                "career_id": c["id"],
                "name": c["name"],
                "category": c["category"],
                "description": c["description"],
                "skill_readiness": readiness,
                "possessed_skills": possessed,
                "missing_skills": missing,
                "required_skills": c["required_skills"],
                "useful_skills": c["useful_skills"],
                "tools": c["tools_technologies"],
                "beginner_projects": c["beginner_projects"],
                "work_style": c["work_style"],
                "work_focus": c["work_focus"],
                "estimated_roadmap_weeks": c["roadmap_weeks"],
                "entry_level_roles": c["entry_level_roles"]
            })

        return {
            "comparison": comparison_items,
            "total_compared": len(comparison_items)
        }

    def get_roadmap(self, career_id: str, hours_per_day: float = 2.0) -> Dict[str, Any]:
        """Generates dynamic 6-stage roadmap for a career."""
        career = self.get_career_by_id(career_id)
        if not career:
            return {"error": f"Career '{career_id}' not found."}

        stages = build_roadmap_stages(career, hours_per_day)
        total_weeks = sum(s["estimated_weeks"] for s in stages)

        return {
            "career_id": career["id"],
            "career_name": career["name"],
            "category": career["category"],
            "hours_per_day": hours_per_day,
            "total_estimated_weeks": total_weeks,
            "stages": stages,
            "prerequisites": career.get("prerequisites", "Foundational study and interest"),
            "disclaimer": "Durations are estimates based on your available study time. Individual learning paces vary."
        }
