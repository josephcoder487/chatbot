import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Create Flask app FIRST
app = Flask(__name__)
CORS(app)
app.secret_key = "super_secret_key"

# Gemini API setup
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def get_response(user_input):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content(user_input)

        return response.text

    except Exception as e:
        return f"AI Error: {str(e)}"

    for model_id in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=user_input
            )
            return response.text

        except Exception:
            continue

    return "AI Error: Unable to connect to Gemini."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message")

    if not user_msg:
        return jsonify({"reply": "Empty message."})

    reply = get_response(user_msg)

    return jsonify({"reply": reply})

@app.route("/auth")
def auth():
    return render_template("auth.html")

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json

    if not data.get("google_token") or not data.get("captcha_token"):
        return jsonify({"success": False})

    session["user"] = "logged_in"

    return jsonify({"success": True})

# IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)