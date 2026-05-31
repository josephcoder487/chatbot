import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_response(user_input):

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        print(e)

        return f"AI Error: {str(e)}"

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