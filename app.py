from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import json
import re
import os

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ Supported & stable Groq model
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.1-70b-versatile"
)

reviews = []  # in-memory storage


# ==============================
# ROUTES
# ==============================
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/analyze', methods=['POST'])
def analyze_pr():
    try:
        review = {
            "id": len(reviews) + 1,
            "pr_title": request.form.get("pr_title"),
            "language": request.form.get("language"),
            "description": request.form.get("description", ""),
            "author": request.form.get("author"),
            "repository": request.form.get("repository"),
            "source_branch": request.form.get("source_branch"),
            "target_branch": request.form.get("target_branch"),
            "git_diff": request.form.get("git_diff"),
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }

        if not review["pr_title"] or not review["git_diff"]:
            return jsonify({"error": "PR title and Git diff required"}), 400

        analysis = perform_llm_analysis(review)
        review["analysis"] = analysis
        review["status"] = analysis["recommendation"]

        reviews.append(review)

        return jsonify({
            "success": True,
            "review_id": review["id"],
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reviews')
def get_reviews():
    return jsonify({"total": len(reviews), "reviews": reviews})


@app.route('/metrics')
def metrics():
    return jsonify({
        "total": len(reviews),
        "approved": sum(r["status"] == "approved" for r in reviews),
        "needs_changes": sum(r["status"] == "needs_changes" for r in reviews),
        "blocked": sum(r["status"] == "blocked" for r in reviews)
    })


# ==============================
# LLM ANALYSIS
# ==============================
def perform_llm_analysis(review):
    llm_response = query_groq_for_review(review["git_diff"], review)

    if not llm_response:
        return generate_empty_review()

    recommendation = determine_recommendation(llm_response)

    return {
        "security_issues": llm_response.get("security_issues", []),
        "quality_issues": llm_response.get("quality_issues", []),
        "positive_notes": llm_response.get("positive_notes", []),
        "summary": llm_response.get("summary", "Code review completed."),
        "recommendation": recommendation
    }


def query_groq_for_review(git_diff, review):
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set")
        return None

    truncated_diff = git_diff[:8000] if len(git_diff) > 8000 else git_diff

    prompt = f"""
Analyze the following git diff and return ONLY valid JSON.

PR TITLE: {review.get("pr_title")}
LANGUAGE: {review.get("language")}
DESCRIPTION: {review.get("description")}
AUTHOR: {review.get("author")}
REPOSITORY: {review.get("repository")}

GIT DIFF:
{truncated_diff}

JSON FORMAT:
{{
  "security_issues": [
    {{
      "severity": "high|medium|low",
      "title": "Issue title",
      "message": "Issue explanation",
      "suggestion": "Exact fix"
    }}
  ],
  "quality_issues": [
    {{
      "severity": "high|medium|low",
      "title": "Issue title",
      "message": "Issue explanation",
      "suggestion": "Exact fix"
    }}
  ],
  "positive_notes": [
    "Good practice 1",
    "Good practice 2"
  ],
  "summary": "Short summary",
  "has_blocking_issues": true|false
}}

Respond with JSON ONLY. No text outside JSON.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You must respond with ONLY valid JSON. No explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 2048
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            json=payload,
            headers=headers,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()
        raw_output = data["choices"][0]["message"]["content"]

        print("\n--- GROQ RAW OUTPUT ---\n", raw_output)

        # 1️⃣ Try direct JSON parse
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        # 2️⃣ Fallback: extract JSON block
        start = raw_output.find("{")
        end = raw_output.rfind("}")

        if start == -1 or end == -1 or end <= start:
            print("ERROR: JSON boundaries not found")
            return None

        json_str = raw_output[start:end + 1]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("FINAL JSON PARSE FAILED:", e)
            return None

    except Exception as e:
        print("Groq API Error:", e)
        return None


def determine_recommendation(llm_response):
    if llm_response.get("has_blocking_issues"):
        return "blocked"

    if any(i.get("severity") == "high" for i in llm_response.get("security_issues", [])):
        return "blocked"

    if any(i.get("severity") == "high" for i in llm_response.get("quality_issues", [])):
        return "needs_changes"

    return "approved"


def generate_empty_review():
    return {
        "security_issues": [],
        "quality_issues": [],
        "positive_notes": [],
        "summary": "Unable to complete analysis. Please check logs and try again.",
        "recommendation": "approved"
    }


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
