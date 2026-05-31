import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from groq import Groq

load_dotenv()

app = Flask(__name__)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def get_response(user_input):

    try:

        chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": user_input
        }
    ],
    model="llama-3.1-8b-instant"
)

        return chat_completion.choices[0].message.content

    except Exception as e:

        return str(e)

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