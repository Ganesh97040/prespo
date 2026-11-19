import flet as ft
import urllib.request
import urllib.parse
import json
import threading

def main(page: ft.Page):
    page.title = "NAA AGENT APP"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    token_box = ft.TextField(label="Telegram Bot Token", password=True)
    chat_box = ft.TextField(label="Telegram Chat ID", value="")
    stock_box = ft.TextField(label="Stock Symbol", value="RELIANCE.NS")
    # IKKADA KOTTHA BOXES - QUANTITY & PRICE
    qty_box = ft.TextField(label="Quantity - Enni Shares?", value="10", keyboard_type=ft.KeyboardType.NUMBER)
    buy_box = ft.TextField(label="Buy Price - Enta ki Konnavu? Rs.", value="2400", keyboard_type=ft.KeyboardType.NUMBER)

    status_text = ft.Text("Ready...", size=16)
    price_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
    profit_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD)

    def get_price(symbol):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
                return data["chart"]["result"][0]["meta"].get("regularMarketPrice")
        except:
            return None

    def send_telegram(token, chat_id, msg):
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": msg}
            data = urllib.parse.urlencode(payload).encode()
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=15) as r:
                return True
        except:
            return False

    def get_chat_id_click(e):
        token = token_box.value.strip()
        if not token:
            status_text.value = "❌ Mundhu Token petti, Bot ki /start pampu!"
            page.update(); return
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            with urllib.request.urlopen(url, timeout=15) as r:
                data = json.loads(r.read().decode())
                results = data.get("result", [])
                if not results:
                    status_text.value = "❌ Bot ki velli /start pampu, malli GET nokku!"
                else:
                    chat_id = results[-1]["message"]["chat"]["id"]
                    chat_box.value = str(chat_id)
                    status_text.value = f"✅ Chat ID: {chat_id}"
        except Exception as ex:
            status_text.value = f"❌ Error: {ex}"
        page.update()

    def start_agent_thread():
        token = token_box.value.strip()
        chat_id = chat_box.value.strip()
        symbol = stock_box.value.strip().upper()
        try:
            qty = float(qty_box.value or 0)
            buy = float(buy_box.value or 0)
        except:
            status_text.value = "❌ Quantity / Price lo numbers mathrame veyyi!"
            page.update(); return
        if not token or not chat_id:
            status_text.value = "❌ Token + Chat ID kavali!"
            page.update(); return
        status_text.value = f"Price testhunna {symbol}..."
        page.update()
        live = get_price(symbol)
        if live is None:
            status_text.value = "❌ Price raledhu. Symbol check cheyyi"
            page.update(); return

        # PROFIT CALCULATION
        total_buy = qty * buy
        total_now = qty * live
        profit = total_now - total_buy
        profit_text_val = f"Profit: Rs.{profit:.2f}" if profit >= 0 else f"Loss: Rs.{profit:.2f}"

        price_text.value = f"💰 {symbol} : Live Rs.{live} | Nuvvu Konnadi Rs.{buy}"
        profit_text.value = f"📊 Qty: {qty} | {profit_text_val}"
        profit_text.color = "green" if profit >= 0 else "red"

        msg = f"🤖 NAA AGENT\nStock: {symbol}\nQty: {qty}\nBuy Price: Rs.{buy}\nLive Price: Rs.{live}\n{profit_text_val}\nTotal Value: Rs.{total_now:.2f}"
        ok = send_telegram(token, chat_id, msg)
        status_text.value = "✅ Telegram lo Message Vellindhi!" if ok else "❌ Telegram ki pampaledhu"
        page.update()

    def start_click(e):
        threading.Thread(target=start_agent_thread, daemon=True).start()

    page.add(
        ft.Text("🤖 NAA AGENT APP", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Real Stock Agent - Live Price to Telegram", size=16),
        token_box,
        chat_box,
        ft.Button("GET CHAT ID", on_click=get_chat_id_click),
        stock_box,
        qty_box,
        buy_box,
        ft.Button("START AGENT - SEND TO TELEGRAM", on_click=start_click),
        price_text,
        profit_text,
        status_text,
    )

ft.run(main)
