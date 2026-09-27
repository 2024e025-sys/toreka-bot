import os
import re
import requests
import urllib.parse
from google import genai

# ==========================================
# 設定情報（ご自身の鍵を貼ってください）
# ==========================================
LINE_CHANNEL_ACCESS_TOKEN = "f1854ad486840f4cbe6d715bc2f71356"
GEMINI_API_KEY = "AQ.Ab8RN6L7-ZpYKp65CjD4SEO6f_lkFECqggp3ixX_7EhJvEkrWg"

# XからLivePocketのリンクを含むツイートを検索する処理（トレカ全般）
def search_x_livepocket():
    search_query = '(トレカ OR ポケカ OR ワンピース OR 遊戯王 OR デュエマ) "t.livepocket.jp"'
    encoded_query = urllib.parse.quote(search_query)
    rss_url = f"https://nitter.poast.org/search/rss?f=tweets&q={encoded_query}"
    tweets = []
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            items = re.findall(r'<description>(.*?)</description>', response.text, re.DOTALL)
            for item in items[:10]:
                clean_text = re.sub(r'<[^>]+>', '', item)
                if "t.livepocket.jp" in clean_text:
                    tweets.append(clean_text)
    except Exception as e:
        print(f"X検索エラー: {e}")
    return tweets

# Gemini APIによる中部地方・トレカ判定
def analyze_with_ai(tweet_text):
    prompt = f"""
以下のツイートテキストを分析し、トレーディングカードゲーム（ポケモンカード、ワンピースカード、遊戯王、デュエルマスターズ、その他トレカ全般）の抽選予約情報であるか確認してください。
特に【中部地方（新潟県、富山県、石川県、福井県、山梨県、長野県、岐阜県、静岡県、愛知県）】のイベントであるかを判定してください。

対象テキスト:
{tweet_text}

回答フォーマット:
もし中部地方のトレカイベントであれば以下のフォーマットのみを出力してください。
該当しない場合や判断できない場合は「対象外」とだけ出力してください。

【タイトル/店舗名】
【カード種別】
【場所/県】
【詳細・URL】
"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini APIエラー: {e}")
        return "対象外"

# LINE通知処理
def send_line_notification(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": f"🔔 【中部地区】トレカ抽選情報！\n\n{message}"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"LINE送信結果: {response.status_code}")

def main():
    print("トレカ抽選情報の監視を開始します...")
    tweets = search_x_livepocket()
    print(f"取得したツイート数: {len(tweets)}")
    
    for tweet in tweets:
        result = analyze_with_ai(tweet)
        if "対象外" not in result:
            print("中部地方のトレカ抽選情報を発見！LINEへ通知します。")
            send_line_notification(result)
        else:
            print("中部地方以外のイベントまたは対象外のためスキップしました。")

if __name__ == "__main__":
    main()
