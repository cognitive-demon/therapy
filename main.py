import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# システムプロンプトを変数に格納
# もしファイルになければ、デフォルトの文言を使う
system_prompt = os.getenv("SYSTEM_PROMPT", "あなたは親切なアシスタントです。")

def generate_response(user_input):
    """
    AIにシステムプロンプトとユーザー入力を渡して回答を得るシミュレーション
    """
    # 実際のAPI（OpenAIやGoogle Geminiなど）を呼ぶ際のイメージ
    print(f"--- [送信されるシステム指示] ---\n{system_prompt}\n")
    print(f"--- [ユーザーの質問] ---\n{user_input}\n")
    
    # ここで本来は API呼び出しを行います
    # response = client.chat.completions.create(messages=[
    #     {"role": "system", "content": system_prompt},
    #     {"role": "user", "content": user_input}
    # ])
    
    return "（ここにAIからの回答が表示されます）"

# 実行テスト
if __name__ == "__main__":
    user_msg = "今日の調子はどうですか？"
    result = generate_response(user_msg)
    print(result)