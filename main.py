import os
import time
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import sys

# ログ出力をリアルタイム（バッファリングなし）にする設定
sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

PRODUCT_URL = os.getenv("PRODUCT_URL")
CHECK_INTERVAL = 180
IN_STOCK_KEYWORDS = [k.strip().lower() for k in os.getenv("IN_STOCK_KEYWORDS", "在庫あり,In Stock,Add to Cart,カートに入れる").split(",")]
OUT_OF_STOCK_KEYWORDS = [k.strip().lower() for k in os.getenv("OUT_OF_STOCK_KEYWORDS", "現在お取り扱いできません,一時的に在庫切れ,Currently unavailable,Out of Stock,在庫切れ").split(",")]
 
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")

STATE_FILE = "notified.flag"


def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def check_stock(url: str) -> bool:
	html = fetch_page(url)
	text = BeautifulSoup(html, "html.parser").get_text().lower()

	for out_kw in OUT_OF_STOCK_KEYWORDS:
		if out_kw and out_kw in text:
			return False

	for kw in IN_STOCK_KEYWORDS:
		if kw and kw in text:
			return True

	return False


def send_email(subject: str, body: str) -> None:
	msg = EmailMessage()
	msg["Subject"] = subject
	msg["From"] = FROM_EMAIL
	msg["To"] = TO_EMAIL
	msg.set_content(body)

	with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
		smtp.starttls()
		if SMTP_USER and SMTP_PASSWORD:
			smtp.login(SMTP_USER, SMTP_PASSWORD)
		smtp.send_message(msg)


def load_notified() -> bool:
	return os.path.exists(STATE_FILE)


def save_notified():
	open(STATE_FILE, "w").write("notified")


def clear_notified():
	try:
		os.remove(STATE_FILE)
	except FileNotFoundError:
		pass

def main():
    if not PRODUCT_URL:
        print("PRODUCT_URL が設定されていません。")
        return

    print("監視チェック開始:", PRODUCT_URL)

    try:
        while True:
            was_notified = load_notified()

            try:
                in_stock = check_stock(PRODUCT_URL)
                print(time.strftime("%Y-%m-%d %H:%M:%S"), "在庫:", in_stock)

                if in_stock and not was_notified:
                    subject = "商品が入荷しました"
                    body = f"商品が入荷しました: {PRODUCT_URL}"
                    if SMTP_SERVER and FROM_EMAIL and TO_EMAIL:
                        send_email(subject, body)
                        print("通知メールを送信しました。")
                    save_notified()

                if not in_stock and was_notified:
                    clear_notified()

            except Exception as e:
                print("エラー発生:", e)

            print(f"次回チェックまで {CHECK_INTERVAL} 秒待機します。")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("監視を停止しました。")

if __name__ == "__main__":
    main()