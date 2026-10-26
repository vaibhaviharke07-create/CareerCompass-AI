"""
CareerCompass AI — Flask Web Application & REST API
Clean, beginner-friendly, and production-tested local career guidance system.
"""

import os
import sys
from flask import Flask, request, jsonify, render_template, send_from_directory
from career_engine import CareerEngine
from chatbot import CareerAssistantChatbot
from storage import StorageManager

app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize modules
engine = CareerEngine()
chatbot = CareerAssistantChatbot(engine)
storage = StorageManager()

# --- Page Routes ---

@app.route("/")
def index():
    """Serves the main application single-page interface."""
    return render_template("index.html")

# --- API Endpoints ---

@app.route("/api/health", methods=["GET"])
def health():
    """Application health and dataset integrity check."""
    career_count = len(engine.get_all_careers())
    return jsonify({
        "status": "healthy",
        "app_name": "CareerCompass AI",
        "version": "1.0.0",
        "dataset": {
            "status": "loaded" if career_count > 0 else "empty",
            "total_careers": career_count,
            "path": engine.csv_path
        },
        "storage": {
            "engine": "sqlite3",
            "database_file": storage.db_path
        }
    })

@app.route("/api/careers", methods=["GET"])
def get_careers():
    """Returns the full catalog of distinct career paths."""
    category = request.args.get("category")
    careers = engine.get_all_careers()
    if category and category.lower() != "all":
        careers = [c for c in careers if c.get("category", "").lower() == category.lower()]
    return jsonify({
        "total": len(careers),
        "careers": careers
    })

@app.route("/api/careers/<career_id>", methods=["GET"])
def get_career(career_id):
    """Retrieves a single career by its unique ID."""
    career = engine.get_career_by_id(career_id)
    if not career:
        return jsonify({"error": f"Career with ID '{career_id}' not found."}), 404
    return jsonify(career)

@app.route("/api/recommend", methods=["POST"])
def recommend_careers():
    """Generates explainable career recommendations based on student profile."""
    data = request.get_json(silent=True) or {}
    custom_weights = data.get("weights")
    result = engine.recommend(data, weights=custom_weights)
    return jsonify(result)

@app.route("/api/skill-gap", methods=["POST"])
def skill_gap():
    """Performs dynamic skill-gap analysis for a specific career."""
    data = request.get_json(silent=True) or {}
    career_id = data.get("career_id")
    if not career_id:
        return jsonify({"error": "Missing required 'career_id' field."}), 400

    user_skills = data.get("existing_skills", data.get("skills", []))
    analysis = engine.analyze_skill_gap(career_id, user_skills)
    if "error" in analysis:
        return jsonify(analysis), 404
    return jsonify(analysis)

@app.route("/api/compare", methods=["POST"])
def compare_careers():
    """Compares 2 to 3 careers side by side."""
    data = request.get_json(silent=True) or {}
    career_ids = data.get("career_ids", [])
    if not isinstance(career_ids, list) or len(career_ids) < 2:
        return jsonify({"error": "Please provide a list of at least 2 career IDs under 'career_ids'."}), 400

    user_skills = data.get("existing_skills", data.get("skills", []))
    comparison = engine.compare_careers(career_ids, user_skills)
    if "error" in comparison:
        return jsonify(comparison), 400
    return jsonify(comparison)

@app.route("/api/roadmap", methods=["GET"])
def get_roadmap():
    """Retrieves standard 6-stage roadmap for a career."""
    career_id = request.args.get("career_id")
    if not career_id:
        return jsonify({"error": "Missing query parameter 'career_id'."}), 400

    hours = request.args.get("hours_per_day", 2.0)
    try:
        hours = float(hours)
    except ValueError:
        hours = 2.0

    roadmap = engine.get_roadmap(career_id, hours_per_day=hours)
    if "error" in roadmap:
        return jsonify(roadmap), 404
    return jsonify(roadmap)

@app.route("/api/roadmap/progress", methods=["POST"])
def update_roadmap_progress():
    """Saves completed roadmap stage IDs for a specific student profile and career."""
    data = request.get_json(silent=True) or {}
    profile_id = data.get("profile_id")
    career_id = data.get("career_id")
    completed_stages = data.get("completed_stages", [])

    if not profile_id or not career_id:
        return jsonify({"error": "Fields 'profile_id' and 'career_id' are required."}), 400

    updated = storage.update_roadmap_progress(profile_id, career_id, completed_stages)
    return jsonify(updated)

@app.route("/api/roadmap/progress/<profile_id>/<career_id>", methods=["GET"])
def get_roadmap_progress(profile_id, career_id):
    """Retrieves saved completed stages for a profile and career."""
    completed = storage.get_roadmap_progress(profile_id, career_id)
    return jsonify({
        "profile_id": profile_id,
        "career_id": career_id,
        "completed_stages": completed
    })

@app.route("/api/profiles", methods=["GET"])
def list_profiles():
    """Lists all saved student profiles."""
    profiles = storage.list_profiles()
    return jsonify({"profiles": profiles, "total": len(profiles)})

@app.route("/api/profiles", methods=["POST"])
def save_profile():
    """Saves a student profile and optional recommendations to local storage."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body provided."}), 400

    saved = storage.save_profile(data)
    return jsonify({"success": True, "profile": saved}), 201

@app.route("/api/profiles/<profile_id>", methods=["GET"])
def get_profile(profile_id):
    """Retrieves a single saved profile by ID."""
    p = storage.get_profile(profile_id)
    if not p:
        return jsonify({"error": f"Profile '{profile_id}' not found."}), 404
    return jsonify(p)

@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    """Deletes a saved profile."""
    success = storage.delete_profile(profile_id)
    if not success:
        return jsonify({"error": f"Profile '{profile_id}' not found."}), 404
    return jsonify({"success": True, "message": f"Profile '{profile_id}' successfully deleted."})

@app.route("/api/chat", methods=["POST"])
def chat():
    """Local rule-based career assistant that uses student profile context and career dataset."""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message received."}), 400

    profile_context = data.get("profile_context")
    conversation_history = data.get("history")

    reply_payload = chatbot.respond(
        message=message,
        profile_context=profile_context,
        conversation_history=conversation_history
    )
    return jsonify(reply_payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting CareerCompass AI on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
