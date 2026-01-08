import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from google import genai


# 1. Load your .env file
load_dotenv()

# 2. Initialize Gemini client
# The Free Tier requires a valid key from https://aistudio.google.com/
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def get_response(user_input):
    """
    Tries the standard 2026 Free Tier models.
    """
    # Order: 2.5 Flash (Fast/Stable) -> 3 Pro (High Intelligence) -> 1.5 Flash (Legacy)
    models_to_try = ["gemini-2.5-flash", "gemini-3-pro-preview", "gemini-1.5-flash"]
    
    for model_id in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=user_input
            )
            return response.text
        except Exception:
            continue # Try the next model if one fails
            
    return "AI Error: I'm having trouble connecting to the Gemini models. Please check your API key."

app = Flask(__name__)
app.secret_key = "super_secret_key"

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

# Auth routes for your templates
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

if __name__ == "__main__":
    app.run(debug=True)