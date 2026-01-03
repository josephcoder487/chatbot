import os
import secrets
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI

# -------------------- SETUP --------------------

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # REQUIRED for session


# -------------------- SESSION HELPERS --------------------

def init_session():
    if "summary" not in session:
        session["summary"] = ""


def update_summary(old_summary, new_question):
    prompt = f"""
Existing summary:
{old_summary}

New user question:
{new_question}

Update the summary in one short sentence.
"""
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content


# -------------------- ROUTES --------------------

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


@app.route("/chat", methods=["POST"])
def chat():
    try:
        init_session()

        data = request.json
        user_msg = data.get("message", "")

        if not user_msg:
            return jsonify({"reply": "Empty message"}), 400

        # update rolling summary
        session["summary"] = update_summary(session["summary"], user_msg)

        system_prompt = f"Conversation summary:\n{session['summary']}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("CHAT ERROR:", e)   # 👈 THIS WILL SHOW REAL ERROR
        return jsonify({"reply": "Server error"}), 500

# -------------------- RUN --------------------

if __name__ == "__main__":
    app.run(debug=True)
