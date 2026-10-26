"""
CareerCompass AI — Local Rule-Based Career Assistant Chatbot
Answers career-guidance queries using local dataset facts, student profile context, and deterministic reasoning.
"""

import re
from typing import Dict, List, Any, Optional
from career_engine import CareerEngine

class CareerAssistantChatbot:
    def __init__(self, engine: Optional[CareerEngine] = None):
        self.engine = engine or CareerEngine()

    def _find_mentioned_career(self, text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()
        # Direct name or ID search
        for c in self.engine.careers:
            if c["id"].lower() in text_lower or c["name"].lower() in text_lower:
                return c

        # Aliases
        alias_map = {
            "ml": "ml_engineer",
            "machine learning": "ml_engineer",
            "ai": "ai_engineer",
            "artificial intelligence": "ai_engineer",
            "software engineer": "software_dev",
            "software development": "software_dev",
            "swe": "software_dev",
            "frontend": "web_dev",
            "web dev": "web_dev",
            "web developer": "web_dev",
            "full stack": "web_dev",
            "data analysis": "data_analyst",
            "data analytics": "data_analyst",
            "ux": "ui_ux_designer",
            "ui": "ui_ux_designer",
            "ui/ux": "ui_ux_designer",
            "cyber": "cybersecurity_analyst",
            "security": "cybersecurity_analyst",
            "infosec": "cybersecurity_analyst",
            "devops": "devops_engineer",
            "cloud": "cloud_engineer",
            "sre": "devops_engineer",
            "qa": "qa_tester",
            "tester": "qa_tester",
            "testing": "qa_tester",
            "mobile": "mobile_dev",
            "ios": "mobile_dev",
            "android": "mobile_dev",
            "database": "db_admin",
            "dba": "db_admin",
            "sql": "db_admin",
            "iot": "iot_dev",
            "robot": "robotics_engineer",
            "robotics": "robotics_engineer",
            "nlp": "nlp_engineer",
            "computer vision": "cv_engineer",
            "cv": "cv_engineer",
            "blockchain": "blockchain_dev",
            "crypto": "blockchain_dev",
            "web3": "blockchain_dev",
            "product management": "product_manager",
            "pm": "product_manager",
            "tech writer": "technical_writer",
            "documentation": "technical_writer",
            "research": "research_assistant",
            "digital marketing": "digital_marketing_analyst",
            "it support": "it_support",
            "sysadmin": "it_support",
            "network": "network_engineer"
        }

        for alias, cid in alias_map.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                return self.engine.get_career_by_id(cid)

        return None

    def respond(self, message: str, profile_context: Optional[Dict[str, Any]] = None, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Processes message and returns a helpful, grounded response with suggested follow-up prompts.
        """
        text = message.strip()
        text_lower = text.lower()
        profile = profile_context or {}
        user_skills = profile.get("existing_skills", profile.get("skills", [])) or []
        hours_per_day = float(profile.get("available_hours_per_day", 2.0) or 2.0)

        # 1. Comparison query: "compare X and Y"
        if "compare" in text_lower:
            careers_found = []
            for c in self.engine.careers:
                if c["name"].lower() in text_lower or c["id"].lower() in text_lower:
                    if c not in careers_found:
                        careers_found.append(c)

            # Check aliases if not enough found
            if len(careers_found) < 2:
                tokens = re.findall(r"\b[a-zA-Z0-9_\-\/]+\b", text_lower)
                for t in tokens:
                    c = self._find_mentioned_career(t)
                    if c and c not in careers_found:
                        careers_found.append(c)
                    if len(careers_found) == 3:
                        break

            if len(careers_found) >= 2:
                c1, c2 = careers_found[0], careers_found[1]
                shared_skills = set(c1["all_skills"]).intersection(set(c2["all_skills"]))
                diff_c1 = set(c1["all_skills"]) - set(c2["all_skills"])
                diff_c2 = set(c2["all_skills"]) - set(c1["all_skills"])

                response_text = (
                    f"**Comparing {c1['name']} vs. {c2['name']}**\n\n"
                    f"• **Category & Focus:**\n"
                    f"  - **{c1['name']}:** {c1['category']} ({c1['work_focus']} focus, {c1['work_style']} work). {c1['description']}\n"
                    f"  - **{c2['name']}:** {c2['category']} ({c2['work_focus']} focus, {c2['work_style']} work). {c2['description']}\n\n"
                    f"• **Shared Core Skills:** {', '.join(list(shared_skills)[:4]) if shared_skills else 'General computing and problem-solving'}\n"
                    f"• **Unique to {c1['name']}:** {', '.join(list(diff_c1)[:4]) if diff_c1 else 'Standard domain skills'}\n"
                    f"• **Unique to {c2['name']}:** {', '.join(list(diff_c2)[:4]) if diff_c2 else 'Standard domain skills'}\n\n"
                    f"• **Primary Tools:**\n"
                    f"  - {c1['name']}: {', '.join(c1['tools_technologies'][:3])}\n"
                    f"  - {c2['name']}: {', '.join(c2['tools_technologies'][:3])}\n\n"
                    f"• **Learning Timeline:** ~{c1['roadmap_weeks']} weeks for {c1['name']} vs. ~{c2['roadmap_weeks']} weeks for {c2['name']} at standard pace."
                )
                return {
                    "reply": response_text,
                    "intent": "compare_careers",
                    "suggested_questions": [
                        f"What should I learn first for {c1['name']}?",
                        f"What skills am I missing for {c2['name']}?",
                        "Create a weekly learning plan based on my time."
                    ]
                }
            else:
                return {
                    "reply": "I can compare any 2 careers in our dataset of 25 paths. For example, try asking: 'Compare Data Analyst and Data Scientist' or 'Compare Software Developer and DevOps Engineer'.",
                    "intent": "clarify_compare",
                    "suggested_questions": [
                        "Compare Data Analyst and Data Scientist",
                        "Compare Software Developer and DevOps Engineer",
                        "Compare UI/UX Designer and Web Developer"
                    ]
                }

        # 2. "Which career matches my interests/profile?"
        if any(p in text_lower for p in ["match my interest", "suit me", "which career", "recommend a career", "what career should i", "best career for me"]):
            if profile and (profile.get("interests") or profile.get("existing_skills")):
                rec = self.engine.recommend(profile)
                top = rec["top_recommendations"]
                lines = [f"Based on your profile, here are your top 3 career matches:"]
                for i, r in enumerate(top, 1):
                    lines.append(f"{i}. **{r['name']}** (Match Score: **{r['match_score']}%**)\n   • Reason: {r['why_recommended']}\n   • Key skills needed: {', '.join(r['required_skills'][:3])}")
                lines.append("\nYou can view the full breakdown in the **Career Recommendations** tab or ask me about learning steps for any of these.")
                return {
                    "reply": "\n".join(lines),
                    "intent": "recommend_from_profile",
                    "suggested_questions": [
                        f"What should I learn first to become a {top[0]['name']}?",
                        f"What skills am I missing for {top[0]['name']}?",
                        "Create a weekly learning plan based on my time."
                    ]
                }
            else:
                return {
                    "reply": (
                        "To give you an accurate, personalized match, please fill out your profile in the **Student Profile** tab (interests, subjects, skills, and activities).\n\n"
                        "Or if you have an idea in mind, tell me what you enjoy! For example: *'I enjoy Python, problem-solving, and analyzing data'*, and I will suggest matching roles."
                    ),
                    "intent": "prompt_profile_input",
                    "suggested_questions": [
                        "I like coding and building web applications",
                        "I enjoy mathematics, statistics, and solving puzzles",
                        "I prefer visual design and user interfaces"
                    ]
                }

        # 3. "What should I learn first / roadmap / how to start"
        if any(p in text_lower for p in ["learn first", "how to start", "where to start", "start learning", "first step"]):
            career = self._find_mentioned_career(text)
            if not career and profile.get("target_career_id"):
                career = self.engine.get_career_by_id(profile["target_career_id"])

            if career:
                reqs = career["required_skills"]
                tools = career["tools_technologies"]
                return {
                    "reply": (
                        f"**Starting Steps for {career['name']}:**\n\n"
                        f"1. **Core Language / Skill to Learn First:** Focus on **{reqs[0] if reqs else 'fundamental programming'}**.\n"
                        f"2. **Foundational Concepts:** Review {career.get('prerequisites', 'core fundamentals')} and master basic problem solving.\n"
                        f"3. **Primary Working Environment:** Install **{tools[0] if tools else 'VS Code and Git'}**.\n"
                        f"4. **First Starter Milestone:** Complete the starter project: *'{career['beginner_projects'][0] if career['beginner_projects'] else 'basic domain calculator'}'*.\n\n"
                        f"Check out the full 6-stage roadmap in the **Learning Roadmap** tab to track your checklist!"
                    ),
                    "intent": "learn_first",
                    "suggested_questions": [
                        f"What skills am I missing for {career['name']}?",
                        f"Suggest beginner projects for {career['name']}",
                        "How can I prepare for an internship?"
                    ]
                }
            else:
                return {
                    "reply": "Which career path would you like a starting guide for? We have 25 paths including Software Developer, Data Analyst, Machine Learning Engineer, Cloud Engineer, Cybersecurity Analyst, and UI/UX Designer.",
                    "intent": "clarify_career",
                    "suggested_questions": [
                        "What should I learn first to become a Data Analyst?",
                        "What should I learn first to become a Software Developer?",
                        "What should I learn first for Cybersecurity?"
                    ]
                }

        # 4. "What skills am I missing / skill gap"
        if any(p in text_lower for p in ["missing", "skill gap", "skills do i need", "skills am i missing", "what do i lack"]):
            career = self._find_mentioned_career(text)
            if not career and profile.get("target_career_id"):
                career = self.engine.get_career_by_id(profile["target_career_id"])

            if career:
                gap = self.engine.analyze_skill_gap(career["id"], user_skills)
                possessed = gap["possessed_skills"]
                missing = gap["missing_skills"]
                readiness = gap["skill_readiness_percentage"]

                lines = [
                    f"**Skill Gap Analysis for {career['name']}**\n",
                    f"• **Current Skill Readiness:** **{readiness}%**",
                    f"• **Skills You Already Have:** {', '.join(possessed) if possessed else 'None recorded yet in your profile.'}",
                    f"• **Skills to Learn / Missing:** {', '.join(missing[:5]) if missing else 'You have recorded all key skills!'}\n",
                    f"• **Highest Priority Skill:** **{gap['priority_skills_to_learn'][0]['skill'] if gap['priority_skills_to_learn'] else 'Hands-on projects'}**.",
                    f"• **Recommended Action:** {gap['suggested_practice_activities'][0] if gap['suggested_practice_activities'] else 'Build a practice project.'}"
                ]
                return {
                    "reply": "\n".join(lines),
                    "intent": "skill_gap",
                    "suggested_questions": [
                        f"What should I learn first to become a {career['name']}?",
                        f"Suggest a beginner project for {career['name']}",
                        "Create a weekly learning plan based on my available time."
                    ]
                }
            else:
                return {
                    "reply": "Which career would you like to analyze your skill gap for? (e.g. 'What skills am I missing for Data Analyst?' or 'What skills do I need for Cloud Engineer?')",
                    "intent": "clarify_gap_career",
                    "suggested_questions": [
                        "What skills am I missing for a Software Developer role?",
                        "What skills am I missing for Data Analyst?",
                        "What skills do I need for Machine Learning?"
                    ]
                }

        # 5. Beginner project suggestion
        if any(p in text_lower for p in ["project", "build", "portfolio project", "starter project"]):
            career = self._find_mentioned_career(text)
            if career:
                projects = career.get("beginner_projects", [])
                lines = [f"**Beginner Projects for {career['name']}:**\n"]
                for i, p in enumerate(projects, 1):
                    lines.append(f"{i}. **{p}**")
                lines.append(f"\n**Tools to use:** {', '.join(career.get('tools_technologies', [])[:4])}")
                lines.append("Tip: Build project #1 first, document it in a clean README on GitHub, and include a screenshot or demo.")
                return {
                    "reply": "\n".join(lines),
                    "intent": "project_ideas",
                    "suggested_questions": [
                        f"What should I learn first to become a {career['name']}?",
                        "How can I prepare for an internship?",
                        "Create a weekly learning plan based on my time."
                    ]
                }
            else:
                return {
                    "reply": "Tell me which field you would like project ideas for! For example: AI, Web Development, Data Science, Cybersecurity, or Robotics.",
                    "intent": "clarify_project_field",
                    "suggested_questions": [
                        "Suggest a beginner project for AI",
                        "Suggest a beginner project for Web Development",
                        "Suggest a beginner project for Cybersecurity"
                    ]
                }

        # 6. Internship and career preparation
        if any(p in text_lower for p in ["internship", "interview", "get hired", "job ready", "resume"]):
            return {
                "reply": (
                    "**How to Prepare for an Internship as a Student:**\n\n"
                    "1. **Build 2 Concrete Showcase Projects:** Generic tutorial clones won't stand out. Build projects that solve a real problem, write automated unit tests, and host a live demo or clear video walkthrough.\n"
                    "2. **Clean GitHub Presence:** Ensure your repositories have a clear README, installation steps, and well-organized code.\n"
                    "3. **Skill-Aligned Resume:** List specific technical skills and quantify outcomes on projects (e.g., *'Built REST API handling 5 endpoints with SQLite persistence and 85% test coverage'*).\n"
                    "4. **Master Fundamentals:** Be ready to explain your project architecture, edge-case decisions, and data structures in a conversational technical interview.\n"
                    "5. **Early Outreach:** Apply to smaller startups, university research labs, and open-source programs (like Google Summer of Code) alongside formal internships."
                ),
                "intent": "internship_guidance",
                "suggested_questions": [
                    "What should I learn first to become a Software Developer?",
                    "Suggest a beginner project for AI",
                    "Create a weekly learning plan based on my available time."
                ]
            }

        # 7. Weekly learning plan based on time
        if any(p in text_lower for p in ["weekly learning plan", "learning plan", "study schedule", "schedule", "available time"]):
            hrs = hours_per_day
            weekly_hrs = round(hrs * 7, 1)
            return {
                "reply": (
                    f"**Personalized Weekly Learning Plan ({hrs} hrs/day = ~{weekly_hrs} hrs/week):**\n\n"
                    f"• **Monday & Tuesday (Theory & Concept Mastery — {round(hrs*2, 1)} hrs total):**\n"
                    f"  Read core documentation, study algorithmic concepts or syntax, and take concise reference notes.\n\n"
                    f"• **Wednesday & Thursday (Hands-On Coding & Exercises — {round(hrs*2, 1)} hrs total):**\n"
                    f"  Solve 4-6 deliberate practice exercises focusing on your current missing skills.\n\n"
                    f"• **Friday (Tooling & Integration — {hrs} hrs total):**\n"
                    f"  Work with Git, configure your environment, or test API endpoints.\n\n"
                    f"• **Saturday (Mini-Project Building — {round(hrs*1.5, 1)} hrs):**\n"
                    f"  Synthesize what you learned by building a tangible component of your milestone project.\n\n"
                    f"• **Sunday (Review & Rest — {round(hrs*0.5, 1)} hrs):**\n"
                    f"  Review errors, commit clean code to GitHub, and mark off completed items in your **Learning Roadmap** checklist."
                ),
                "intent": "weekly_plan",
                "suggested_questions": [
                    "Which career best matches my interests?",
                    "How can I prepare for an internship?",
                    "What should I learn first to become a Data Analyst?"
                ]
            }

        # 8. Single career details query
        career = self._find_mentioned_career(text)
        if career:
            return {
                "reply": (
                    f"**{career['name']} Overview:**\n\n"
                    f"{career['description']}\n\n"
                    f"• **Category:** {career['category']}\n"
                    f"• **Key Responsibilities:** {'; '.join(career['responsibilities'][:3])}\n"
                    f"• **Required Skills:** {', '.join(career['required_skills'])}\n"
                    f"• **Standard Tools:** {', '.join(career['tools_technologies'])}\n"
                    f"• **Typical Roadmap Duration:** ~{career['roadmap_weeks']} weeks (adaptable based on your hours)\n"
                    f"• **Starter Project:** {career['beginner_projects'][0]}"
                ),
                "intent": "career_overview",
                "suggested_questions": [
                    f"What should I learn first to become a {career['name']}?",
                    f"What skills am I missing for {career['name']}?",
                    f"Suggest beginner projects for {career['name']}"
                ]
            }

        # Default fallback with helpful direction
        return {
            "reply": (
                "I am your local rule-based CareerCompass AI assistant. I can answer questions using our 25-career dataset, compare career options, explain missing skills, and build study plans.\n\n"
                "Try asking me:\n"
                "• *'Which career best matches my interests?'*\n"
                "• *'What should I learn first to become a Data Analyst?'*\n"
                "• *'Compare Data Science and Machine Learning'*\n"
                "• *'What skills am I missing for a Software Developer role?'*\n"
                "• *'Suggest a beginner project for AI'*\n"
                "• *'Create a weekly learning plan based on my available time'*"
            ),
            "intent": "general_guidance",
            "suggested_questions": [
                "Which career best matches my interests?",
                "What should I learn first to become a Data Analyst?",
                "Compare Data Science and Machine Learning",
                "Suggest a beginner project for AI"
            ]
        }
