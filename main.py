import flet as ft
import urllib.request
import urllib.parse
import json
import threading
import time
from datetime import datetime

def main(page: ft.Page):
    page.title = "Prespo"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT

    token_box = ft.TextField(label="9262697085:AAGFPdkGsrWiRmAZFPLkTi_RAg3RQ7_0ZaM", password=True, prefix_icon=ft.Icons.LOCK)
    chat_box = ft.TextField(label="1492850487", prefix_icon=ft.Icons.CHAT)
    stock_box = ft.TextField(label="Stock Symbol - Ex: BEL.NS", value="BEL.NS", prefix_icon=ft.Icons.SHOW_CHART)
    qty_box = ft.TextField(label="Quantity", value="10", keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.NUMBERS)
    buy_box = ft.TextField(label="Buy Price Rs.", value="450", keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.CURRENCY_RUPEE)

    status_text = ft.Text("Ready...", size=16)
    list_container = ft.Column([])
    preview = ft.Text("", size=13, selectable=True)

    my_stocks = []
    running = {"on": False}

    def get_data(symbol):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
                meta = data["chart"]["result"][0]["meta"]
                return {"live": meta.get("regularMarketPrice"), "high": meta.get("regularMarketDayHigh"), "low": meta.get("regularMarketDayLow")}
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
            status_text.value = "❌ Token petti, Bot ki /start pampu!"; page.update(); return
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            with urllib.request.urlopen(url, timeout=15) as r:
                data = json.loads(r.read().decode())
                res = data.get("result", [])
                if not res:
                    status_text.value = "❌ Bot ki /start pampu, malli GET nokku!"
                else:
                    chat_box.value = str(res[-1]["message"]["chat"]["id"])
                    status_text.value = "✅ Chat ID Dorikindhi"
        except Exception as ex:
            status_text.value = f"❌ Error: {ex}"
        page.update()

    def refresh_list():
        list_container.controls.clear()
        if not my_stocks:
            list_container.controls.append(ft.Text("📭 Inka Stocks Lev - Kindha ADD cheyyi", color="grey"))
        for s in my_stocks:
            # Small Card for each stock in App
            card = ft.Container(
                content=ft.Row([
                    ft.Text(f"{s['symbol']}", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(f"{s['qty']} Qty @ ₹{s['buy']}", size=14),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#EEF2FF", padding=12, border_radius=10
            )
            list_container.controls.append(card)
        page.update()

    def add_stock_click(e):
        symbol = stock_box.value.strip().upper()
        try:
            qty = float(qty_box.value or 0); buy = float(buy_box.value or 0)
        except:
            status_text.value = "❌ Qty / Price lo numbers veyyi!"; page.update(); return
        if not symbol:
            status_text.value = "❌ Stock Symbol veyyi!"; page.update(); return
        for s in my_stocks:
            if s["symbol"] == symbol:
                s["qty"] = qty; s["buy"] = buy
                status_text.value = f"✅ {symbol} Update Ayindhi!"; refresh_list(); return
        my_stocks.append({"symbol": symbol, "qty": qty, "buy": buy})
        status_text.value = f"✅ {symbol} Add Ayindhi! Total: {len(my_stocks)}"
        stock_box.value = ""; qty_box.value = ""; buy_box.value = ""
        refresh_list()

    def clear_click(e):
        my_stocks.clear(); refresh_list()
        status_text.value = "🗑️ Anni Clear Ayayi"; page.update()

    def build_friendly_dashboard():
        now = datetime.now().strftime("%d %b, %I:%M %p")
        lines = []
        lines.append("📊 MY PORTFOLIO DASHBOARD")
        lines.append(f"🕒 {now}")
        lines.append("━━━━━━━━━━━━━━━━━━")
        total_invest = 0; total_now = 0
        for s in my_stocks:
            d = get_data(s["symbol"])
            if not d or d["live"] is None:
                lines.append(f"⚠️ {s['symbol']} - Price Raledhu")
                lines.append("━━━━━━━━━━━━━━━━━━")
                continue
            live, high, low = d["live"], d["high"], d["low"]
            invest = s["qty"] * s["buy"]
            now_val = s["qty"] * live
            profit = now_val - invest
            pct = ((live - s["buy"]) / s["buy"] * 100) if s["buy"] else 0
            total_invest += invest; total_now += now_val
            short = s["symbol"].replace(".NS", "")
            icon = "🟢" if profit >= 0 else "🔴"
            trend = "📈" if pct >= 0 else "📉"
            profit_label = "✅ Profit" if profit >= 0 else "❌ Loss"
            lines.append(f"{icon} {short}")
            lines.append(f"💰 Live: ₹{live:,.2f}  |  {trend} {pct:+.2f}%")
            lines.append(f"🔺 High: ₹{high:,.2f}  |  🔻 Low: ₹{low:,.2f}")
            lines.append(f"🎯 Buy: ₹{s['buy']:,.2f} x {s['qty']:g} Qty")
            lines.append(f"💼 Invested: ₹{invest:,.0f}  |  📦 Value: ₹{now_val:,.0f}")
            lines.append(f"{profit_label}: ₹{abs(profit):,.0f}")
            lines.append("━━━━━━━━━━━━━━━━━━")
        total_profit = total_now - total_invest
        total_icon = "🟢" if total_profit >= 0 else "🔴"
        lines.append("🏆 TOTAL SUMMARY")
        lines.append(f"💰 Total Invested: ₹{total_invest:,.0f}")
        lines.append(f"📦 Total Value: ₹{total_now:,.0f}")
        if total_profit >= 0:
            lines.append(f"✅ Total Profit: ₹{total_profit:,.0f}")
        else:
            lines.append(f"❌ Total Loss: ₹{abs(total_profit):,.0f}")
        lines.append(f"{total_icon} Stocks: {len(my_stocks)}")
        return "\n".join(lines)

    def send_once():
        if not my_stocks:
            status_text.value = "❌ Mundhu stock ADD cheyyi!"; page.update(); return
        status_text.value = "Dashboard testhunna..."; page.update()
        dash = build_friendly_dashboard()
        preview.value = dash
        ok = send_telegram(token_box.value.strip(), chat_box.value.strip(), dash)
        status_text.value = "✅ Dashboard Telegram ki Vellindhi!" if ok else "❌ Telegram ki pampaledhu"
        page.update()

    def auto_loop():
        while running["on"]:
            if my_stocks:
                dash = build_friendly_dashboard()
                preview.value = dash
                send_telegram(token_box.value.strip(), chat_box.value.strip(), dash)
                status_text.value = "✅ Auto Dashboard Vellindhi! Next in 5 mins..."
                page.update()
            for i in range(300):
                if not running["on"]: break
                time.sleep(1)

    def start_auto(e):
        if running["on"]: return
        if not my_stocks:
            status_text.value = "❌ Mundhu stocks ADD cheyyi!"; page.update(); return
        running["on"] = True
        status_text.value = "▶️ Auto Started! Prathi 5 mins ki Dashboard vasthundi..."
        page.update()
        threading.Thread(target=auto_loop, daemon=True).start()

    def stop_auto(e):
        running["on"] = False
        status_text.value = "⏹️ Auto Aapesaavu"; page.update()

    page.add(
        ft.Text("🤖 NAA AGENT APP", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Premium Dashboard Agent", size=16, color="grey"),
        token_box,
        chat_box,
        ft.Button("GET CHAT ID", on_click=get_chat_id_click, width=400),
        ft.Divider(),
        ft.Text("➕ Add Stock", size=18, weight=ft.FontWeight.BOLD),
        stock_box, qty_box, buy_box,
        ft.Row([ft.Button("➕ ADD STOCK", on_click=add_stock_click, bgcolor="#2563EB", color="white"),
                ft.Button("🗑️ CLEAR", on_click=clear_click)]),
        ft.Text("📋 Nee Stocks:", size=16, weight=ft.FontWeight.BOLD),
        list_container,
        ft.Divider(),
        ft.Button("📊 SEND DASHBOARD NOW", on_click=lambda e: threading.Thread(target=send_once, daemon=True).start(), bgcolor="#16A34A", color="white", width=400),
        ft.Row([ft.Button("▶️ START AUTO 5 MINS", on_click=start_auto, bgcolor="#9333EA", color="white"),
                ft.Button("⏹️ STOP", on_click=stop_auto)]),
        preview,
        status_text,
    )
    refresh_list()

ft.run(main)
