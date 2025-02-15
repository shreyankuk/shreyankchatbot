from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "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"  # Replace with actual API key
MODEL_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

conversation_history = []
selected_model = "qwen/qwen-vl-plus:free"

def format_response(response):
    """Formats the AI's response to be more readable and structured."""
    lines = response.split("\n")
    structured_response = []

    for line in lines:
        if line.strip():
            if ":" in line:
                structured_response.append(f"<b>{line.strip()}</b>")  # Using HTML <b> tag for bold text
            else:
                structured_response.append(f"- {line.strip()}\n")  # Added spacing between bullet points

    return "<br><br>".join(structured_response)  # Double <br> for clear spacing

def chat_with_ai(user_input, model):
    """Send a message to OpenRouter API and get a structured response."""
    global conversation_history

    conversation_history.append({"role": "user", "content": user_input})

    # Custom responses
    if "who created you" in user_input.lower() or "who developed you" in user_input.lower():
        bot_response = "I was developed by <b>Shreyank U K</b>, from <b>Karnataka, India</b>."
        conversation_history.append({"role": "assistant", "content": bot_response})
        return bot_response

    elif "who is shreyank u k" in user_input.lower() or "who is shreyank" in user_input.lower() or "who is he" in user_input.lower():
        bot_response = (
            "<p><b>Shreyank U K</b> is a dedicated medical student pursuing his MBBS, with a strong passion for technology and finance.</p>"
        )
        conversation_history.append({"role": "assistant", "content": bot_response})
        return bot_response

    # Query AI model
    payload = {
        "model": model,
        "messages": conversation_history,
        "max_tokens": 2000
    }

    response = requests.post(MODEL_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        raw_response = response.json()["choices"][0]["message"]["content"]
        structured_response = format_response(raw_response)
        conversation_history.append({"role": "assistant", "content": structured_response})
        return structured_response
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", conversation_history=conversation_history, selected_model=selected_model)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Message cannot be empty"}), 400

    bot_response = chat_with_ai(user_input, selected_model)
    return jsonify({"user": user_input, "bot": bot_response})

@app.route("/set_model/<model_name>", methods=["POST"])
def set_model(model_name):
    """Update the selected model based on button click."""
    global selected_model
    model_mapping = {
        "mistral": "mistralai/mistral-7b-instruct:free",
        "deepseek": "deepseek/deepseek-r1-distill-llama-70b:free",
        "qwen": "qwen/qwen-vl-plus:free"
    }

    if model_name in model_mapping:
        selected_model = model_mapping[model_name]
        return jsonify({"status": "success", "selected_model": selected_model})
    else:
        return jsonify({"status": "error", "message": "Invalid model selection"}), 400

@app.route("/clear", methods=["POST"])
def clear_chat():
    """Clear the conversation history."""
    global conversation_history
    conversation_history = []
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
