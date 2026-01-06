import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, redirect, session

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = "super_secret_key"   # ✅ REQUIRED for session

# ✅ CHAT ROUTE (FIXED)
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message")

    if not user_msg:
        return jsonify({"reply": "Error. Try again."})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot."},
            {"role": "user", "content": user_msg}
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth")
def auth():
    return render_template("auth.html")

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json

    google_token = data.get("google_token")
    captcha_token = data.get("captcha_token")

    if not google_token or not captcha_token:
        return jsonify({"success": False})

    session["user"] = "logged_in"
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)