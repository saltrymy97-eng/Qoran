from flask import Flask, request, jsonify
from services import ask_ai, smart_classify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Quran University API is running!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"reply": "يرجى كتابة سؤال."})
    category = smart_classify(question)
    reply = ask_ai(question, category)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
