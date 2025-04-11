import requests
import time
import telebot

BOT_TOKEN = "7752015986:AAFPDHq9v8CpA59HU4NUwNNcrj1fqtJHc_M"
CHAT_ID = "6361936855"
API_KEY = "bf2d8b96c85fbee2719733dedcefd8f18e36efa0"

SENT_LINKS_FILE = "sent_links.txt"

bot = telebot.TeleBot(BOT_TOKEN)

def load_sent_links():
    try:
        with open(SENT_LINKS_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def save_sent_link(link):
    with open(SENT_LINKS_FILE, "a") as f:
        f.write(link + "\n")

def get_news():
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
        "auth_token": API_KEY,
        "kind": "news",
        "regions": "en",
        "public": "true",
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for post in data.get("results", []):
        title = post.get("title")
        url = post.get("url")
        coins = post.get("currencies", [])
        tags = post.get("tags", [])
        sentiment = post.get("vote", {}).get("positive") or post.get("vote", {}).get("negative")

        is_important = "important" in tags or "breaking" in tags
        if title and url and sentiment and coins:
            results.append({
                "title": title,
                "url": url,
                "sentiment": sentiment,
                "coins": coins,
                "is_important": is_important
            })
    return results

def determine_strength(coin_symbol):
    strong_coins = {"BTC", "ETH", "BNB", "SOL", "AVAX", "MATIC", "ADA", "DOT", "LTC"}
    return "sağlam" if coin_symbol in strong_coins else "zayıf"

def format_message(post):
    sentiment = post["sentiment"]
    sentiment_text = "Pozitif" if sentiment else "Negatif"
    direction = "📈 Pump ihtimali" if sentiment else "📉 Dump ihtimali"

    coin = post["coins"][0].get("code", "???")
    coin_strength = determine_strength(coin)

    msg = f"""
[{sentiment_text} Haber] {coin} ({coin_strength})
{direction}
📰 {post['title']}
🔗 Kaynak: {post['url']}
"""
    return msg.strip()

def main_loop():
    print("Bot çalışmaya başladı...")
    sent_links = load_sent_links()

    while True:
        try:
            news_list = get_news()
            for post in news_list:
                if post["url"] not in sent_links:
                    msg = format_message(post)
                    bot.send_message(CHAT_ID, msg, parse_mode="HTML")
                    save_sent_link(post["url"])
        except Exception as e:
            print(f"Hata oluştu: {e}")

        time.sleep(60)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Koince Bot aktif ✅ Büyük haberleri burada paylaşacağım.")

# Bu satır polling başlatmaz ama aşağıdakiyle başlatabilirsin:
# bot.polling()

if __name__ == "__main__":
    main_loop()
