from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
import os
import asyncio

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

app_flask = Flask(__name__)

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    link_pagamento = f"https://SEU_LINK_MP?ref={user_id}"

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

# ===== WEBHOOK MERCADO PAGO =====
@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        import requests

        headers = {
            "Authorization": f"Bearer {os.getenv('MP_ACCESS_TOKEN')}"
        }

        response = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers=headers
        )

        payment = response.json()

        if payment["status"] == "approved":
            user_id = int(payment["external_reference"])

            asyncio.run(liberar_usuario(user_id))

    return "ok", 200

# ===== LIBERAR USUÁRIO =====
async def liberar_usuario(user_id):

    invite = await bot_app.bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1,
        expire_date=int(__import__("time").time()) + 300
    )

    await bot_app.bot.send_message(
        chat_id=user_id,
        text=f"✅ Pagamento aprovado!\n\nAcesse o VIP:\n{invite.invite_link}"
    )

# ===== INICIAR =====
bot_app.add_handler(CommandHandler("start", start))

async def main():
    await bot_app.initialize()
    await bot_app.start()

    from threading import Thread
    Thread(target=lambda: app_flask.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))).start()

    await bot_app.updater.start_polling()

import asyncio
asyncio.run(main())