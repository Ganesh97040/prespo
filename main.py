import flet as ft
import yfinance as yf, requests, time, threading, json, os
from datetime import datetime
import pytz
IST = pytz.timezone("Asia/Kolkata")
TOKEN = "9262697085:AAGFPdkGsrWiRmAZFPLkTi_RAg3RQ7_0ZaM"
CHAT_ID = "1492850487"
FILE = "portfolio.json"
running = False
def load():
    if not os.path.exists(FILE): return [{"stock":"JPL.NS","buy":1119,"qty":12,"target":1550,"sl":1350}]
    return json.load(open(FILE))
def save(d): json.dump(d, open(FILE,"w"), indent=2)
def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":msg}, timeout=10)
    except: pass
def agent_loop():
    global running
    while running:
        for p in load():
            try:
                df = yf.Ticker(p['stock']).history(period="1d", interval="1m")
                if df.empty: continue
                live = float(df.iloc[-1]['Close'])
                high_5 = float(df.tail(5)['High'].max())
                low_5 = float(df.tail(5)['Low'].min())
                support = float(df.tail(20)['Low'].min())
                profit = (live - p['buy']) * p['qty']
                t = datetime.now(IST).strftime("%H:%M")
                alert = ""
                if live >= p['target']: alert = "\n🚀 TARGET HIT!"
                if live <= p['sl']: alert = "\n🚨 STOPLOSS HIT!"
                msg = f"📊 {p['stock']} - {t}\n\n💰 Live: ₹{live:.2f}\n📈 High: ₹{high_5:.2f}\n📉 Low: ₹{low_5:.2f}\n🛡️ Support: ₹{support:.2f}\n🎯 Target: ₹{p['target']} | 🛑 SL: ₹{p['sl']}\n💵 Profit: ₹{profit:.0f}{alert}"
                send(msg)
            except Exception as e: print(e)
        for _ in range(600):
            if not running: return
            time.sleep(1)
def main(page: ft.Page):
    page.title = "Naa Agent App"; page.scroll = "auto"
    stock_in = ft.TextField(label="Stock (Ex: JPL.NS)", value="JPL.NS")
    buy_in = ft.TextField(label="Buy Price", value="1119", keyboard_type="number")
    qty_in = ft.TextField(label="Quantity", value="12", keyboard_type="number")
    target_in = ft.TextField(label="Target", value="1550", keyboard_type="number")
    sl_in = ft.TextField(label="Stoploss", value="1350", keyboard_type="number")
    status = ft.Text("Agent: Stopped", color="red", weight="bold")
    list_col = ft.Column()
    def refresh():
        list_col.controls.clear()
        for i, p in enumerate(load()):
            def delete(e, idx=i):
                d = load(); d.pop(idx); save(d); refresh()
            list_col.controls.append(ft.Card(content=ft.Container(content=ft.Row([ft.Text(f"{p['stock']} | Buy ₹{p['buy']} x {p['qty']}\nTarget ₹{p['target']} | SL ₹{p['sl']}", size=14), ft.IconButton(icon="delete", on_click=delete)]), padding=10)))
        page.update()
    def add_click(e):
        d = load(); d.append({"stock": stock_in.value.upper().strip(), "buy": float(buy_in.value), "qty": int(qty_in.value), "target": float(target_in.value), "sl": float(sl_in.value)}); save(d); refresh()
    def start_click(e):
        global running
        if not running:
            running = True; status.value = "Agent: Running - Every 10 Mins"; status.color = "green"
            threading.Thread(target=agent_loop, daemon=True).start(); send("✅ Agent Start Ayindhi! Phone App nunchi."); page.update()
    def stop_click(e):
        global running; running = False; status.value = "Agent: Stopped"; status.color = "red"; page.update()
    page.add(ft.Text("📊 Naa Agent Control App", size=22, weight="bold"), status, stock_in, buy_in, qty_in, target_in, sl_in, ft.ElevatedButton("✅ ADD STOCK", on_click=add_click, bgcolor="blue", color="white"), ft.Row([ft.ElevatedButton("▶️ START AGENT", on_click=start_click, bgcolor="green", color="white"), ft.ElevatedButton("⏹️ STOP", on_click=stop_click, bgcolor="red", color="white")]), ft.Divider(), ft.Text("💼 Naa Portfolio", size=18, weight="bold"), list_col)
    refresh()
ft.app(target=main)
