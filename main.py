import os
import re
import requests
import urllib.parse
from google import genai
# ==========================================
# 
# ==========================================
LINE_CHANNEL_ACCESS_TOKEN = "f1854ad486840f4cbe6d715bc2f71356"
GEMINI_API_KEY = "AQ.Ab8RN6L7-ZpYKp65CjD4SEO6f_lkFECqggp3ixX_7EhJvEkrWg"
# XからLivePocketのリンクを含むツイートを検索する処理
def search_x_livepocket():
   search_query = '(トレカorポケカorワンピースor遊戯王） "t.livepocket.jp"'
   encoded_query = urllib.parse.quote(search_query)
   rss_url = f"https://nitter.net/search/rss?f=tweet
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
# Gemini APIによる中部地方判定
def analyze_with_ai(tweet_text):
   prompt = f"""
   以下のツイートテキストを分析し、トレーディングカードゲーム（ポケモンカード、ワンピースカード、遊戯王、その他トレカ全般）の抽選予約情報であるか確認してください。
   特に【中部地方（新潟県、富山県、石川県、福井県、山梨県、長野県、岐阜県、静岡県、愛知県）】のイベントであるかを判定してください。
   対象テキスト:
   {tweet_text}
   回答フォーマット:
   もし中部地方のイベントであれば以下のフォーマットのみを出力してください。
   中部地方でない場合は「該当なし」とだけ出力してください。
   【対象】はい
   【県名】〇〇県
   【店舗名】〇〇店
   """
   try:
       client = genai.Client(api_key=GEMINI_API_KEY)
       response = client.models.generate_content(
           model='gemini-2.5-flash',
           contents=prompt,
       )
       return response.text.strip()
   except Exception as e:
       print(f"AI判定エラー: {e}")
       return "該当なし"
# LINE通知送信処理
def send_line_notification(message):
   url = "https://api.line.me/v2/bot/message/broadcast"
   headers = {
       "Content-Type": "application/json",
       "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
   }
   payload = {
       "messages": [{"type": "text", "text": message}]
   }
   requests.post(url, headers=headers, json=payload)
# メイン処理
def main():
   print("Xの投稿を検索中...")
   tweets = search_x_livepocket()
   for tweet in tweets:
       ai_result = analyze_with_ai(tweet)
       if "【対象】はい" in ai_result:
           urls = re.findall(r'https?://t\.livepocket\.jp/e/[a-zA-Z0-9_-]+', tweet)
           target_url = urls[0] if urls else "URL自動判定失敗"
           notification_text = f"🔥【トレカ抽選情報（中部地方）】🔥\n\n{ai_result}\n\n▼応募URL\n{target_url}"
           send_line_notification(notification_text)
           print("中部地方の情報を発見！LINEに送信しました。")
if __name__ == "__main__":
   main()
コンテキスト メニューあり
