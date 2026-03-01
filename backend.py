import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# フロントエンド（index.html）からのクロスドメインリクエストを許可
CORS(app)

def get_prompt():
    """
    prompt.txt からシステムプロンプトを読み込みます。
    悪魔の言葉と天使の言葉を出力するよう定義されたプロンプトを期待しています。
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "prompt.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        print(f"Prompt loading error: {e}")
    # フォールバック用の最小限のプロンプト
    return "あなたはCBTカウンセラーです。devil_voiceとangel_voiceを含むJSON形式で回答してください。"

SYSTEM_PROMPT = get_prompt()

@app.route('/', methods=['GET', 'POST', 'OPTIONS'], strict_slashes=False)
def home():
    if request.method == 'OPTIONS':
        return '', 200
    
    if request.method == 'GET':
        return "CBT Backend is Online (Gemini 2.5 Flash Mode)"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "API Key is not set"}), 500
    
    # 指定された最新モデル名を使用
    url = "[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent)"

    try:
        data = request.get_json()
        thought = data.get('thought', '入力なし')

        # Gemini APIへのペイロード構築
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{SYSTEM_PROMPT}\n\nユーザーの思考: {thought}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.8,
                "topK": 40
            }
        }

        response = requests.post(
            url, 
            params={"key": api_key}, 
            json=payload, 
            timeout=25
        )
        
        if response.status_code != 200:
            return jsonify({
                "error": "Gemini API Error", 
                "detail": response.text
            }), response.status_code

        result = response.json()
        ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # AIがMarkdown（```json ... ```）を付けて出力した場合に備えてクレンジング
        clean_json = ai_text.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.split("\n", 1)[-1]  # 最初の ```json を除去
            if clean_json.endswith("```"):
                clean_json = clean_json.rsplit("```", 1)[0]  # 最後の ``` を除去
        
        clean_json = clean_json.strip()

        # 安全にJSONとしてパースしてフロントエンドに返す
        return jsonify(json.loads(clean_json))

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render等のホスティング環境のポート設定に対応
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)