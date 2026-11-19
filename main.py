import flet as ft

def main(page: ft.Page):
    page.title = "Naa Agent App"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    token_box = ft.TextField(label="9262697085:AAGFPdkGsrWiRmAZFPLkTi_RAg3RQ7_0ZaM", password=True, hint_text="BotFather Token ikkada pettu")
    stock_box = ft.TextField(label="Stock Symbol", value="RELIANCE.NS", hint_text="Ex: RELIANCE.NS")
    status_text = ft.Text("Ready... App Work Avthundi ✅", color="green", size=16)

    def start_click(e):
        if not token_box.value:
            status_text.value = "❌ Mundhu Token Petti SAVE nokku!"
            status_text.color = "red"
        else:
            status_text.value = f"✅ Agent Started! Stock: {stock_box.value} - Telegram Check Cheyyi!"
            status_text.color = "green"
        page.update()

    def save_click(e):
        status_text.value = "✅ Token Saved! Ippudu START nokku."
        status_text.color = "green"
        page.update()

    page.add(
        ft.Text("🤖 NAA AGENT APP", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ft.Text("Stock Agent Control", size=16, color="grey", text_align=ft.TextAlign.CENTER),
        ft.Divider(),
        token_box,
        ft.ElevatedButton("SAVE TOKEN", on_click=save_click, width=1000, bgcolor="blue", color="white"),
        ft.Divider(),
        stock_box,
        ft.Button("START AGENT", on_click=start_click, width=1000, bgcolor="green", color="white"),
        ft.Divider(),
        status_text,
    )

ft.run(main)
