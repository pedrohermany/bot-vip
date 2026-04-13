from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
import os
import asyncio
import time
import logging

# ===== LOG =====
logging.basicConfig(level=logging.INFO)

# ===== CONFIG (via Railway Variables) =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
CAKTO_LINK = os.getenv("CAKTO_LINK")  # ex: https://pay.cakto.com/abc123

# ===== APPs =====
app_flask = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # link com ref para identificar quem pagou
    link_pagamento = f"{CAKTO_LINK}?ref={user_id}"

    keyboard = [
        [InlineKeyboardButton("💳 Comprar acesso", url=link_pagamento)]
    ]

    await update.message.reply_text(
        "🔥 Conteúdo VIP exclusivo\n\n"
        "💎 Acesso imediato\n"
        "🔞 Sem censura\n\n"
        "Clique abaixo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== WEBHOOK (Cakto / genérico) =====
@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook recebido:", data)

    # tenta extrair o user_id de vários formatos comuns
    user_id = None

    # formato 1
    if isinstance(data, dict):
        if "ref" in data:
            user_id = data["ref"]

        # formato 2 (mais comum em gateways)
        elif "data" in data and isinstance(data["data"], dict):
            user_id = data["data"].get("ref") or data["data"].get("external_reference")

        # formato 3
        elif "external_reference" in data:
            user_id = data["external_reference"]

    if user_id:
        try:
            user_id = int(user_id)
            asyncio.run(liberar_usuario(user_id))
        except Exception as e:
            print("Erro ao liberar usuário:", e)

    return "ok", 200

# ===== LIBERAR USUÁRIO =====
async def liberar_usuario(user_id):
    invite = await bot_app.bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1,
        expire_date=int(time.time()) + 300  # expira em 5 min
    )

    await bot_app.bot.send_message(
        chat_id=user_id,
        text=f"✅ Pagamento aprovado!\n\nAcesse o VIP:\n{invite.invite_link}"
    )

# ===== MAIN =====
async def main():
    await bot_app.initialize()
    await bot_app.start()

    from threading import Thread
    Thread(
        target=lambda: app_flask.run(
            host="0.0.0.0",
            port=int(os.getenv("PORT", 3000))
        )
    ).start()

    print("Bot rodando...")

    await asyncio.Event().wait()

# ===== HANDLERS =====
bot_app.add_handler(CommandHandler("start", start))

# ===== RUN =====
asyncio.run(main())