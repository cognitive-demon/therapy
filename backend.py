import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_prompt():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "prompt.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        print(f"Prompt loading error: {e}")
    return """あなたは優秀な交流分析カウンセラーです。必ずJSON形式で回答してください。
{
  "game_name": "心理ゲーム名",
  "definition": "定義",
  "position_start": {"self": "I am OK/not OK", "others": "You are OK/not OK", "description": "開始時"},
  "position_end": {"self": "I am OK/not OK", "others": "You are OK/not OK", "description": "結末"},
  "prediction": "破綻の予測",
  "hidden_motive": "無意識の利得",
  "advice": "回避策"
}"""

SYSTEM_PROMPT = get_prompt()

@app.route('/', methods=['GET', 'POST', 'OPTIONS'], strict_slashes=False)
def home():
    if request.method == 'OPTIONS':
        return '', 200
    
    if request.method == 'GET':
        return "CBT Backend is Online (Gemini 2.5 Flash Mode)"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    try:
        data = request.get_json()
        thought = data.get('thought', '入力なし')
        conviction = data.get('conviction', '50')

        full_prompt = f"{SYSTEM_PROMPT}\n\nユーザーの思考: {thought}\nとらわれ度: {conviction}%"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "safetySettings": [
                {"category": "HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
            ],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        response = requests.post(url, params={"key": api_key}, json=payload, timeout=25)
        
        if response.status_code != 200:
            return jsonify({"error": "Gemini API Error", "detail": response.text}), response.status_code

        result = response.json()
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify(json.loads(ai_text))

    except Exception as e:
        return jsonify({"error": "Analysis Error", "detail": str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)