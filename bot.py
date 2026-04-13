from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
import os
import asyncio
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8546135640:AAEMwgdxT2gLVD-MY-EyLXnu9vDo30YM-Hk")
GROUP_ID = int(os.environ.get("GROUP_ID", "-1003956517196"))

app_flask = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    link_pagamento = f"https://SEU_LINK_AQUI?ref={user_id}"

    keyboard = [
        [InlineKeyboardButton("💳 Comprar acesso", url=link_pagamento)]
    ]

    await update.message.reply_photo(
        photo=open("imagem.jpeg", "rb"),
        caption="🔥 Conteúdo VIP exclusivo\n\n💎 Acesso imediato\n🔞 Sem censura\n\nClique abaixo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== LIBERAR =====
async def liberar_usuario(user_id):
    invite = await bot_app.bot.create_chat_invite_link(
        chat_id=GROUP_ID,
        member_limit=1,
        expire_date=int(time.time()) + 300
    )

    await bot_app.bot.send_message(
        chat_id=user_id,
        text=f"✅ Pagamento aprovado!\n\nAcesse o VIP:\n{invite.invite_link}"
    )

# ===== WEBHOOK (SIMPLES POR ENQUANTO) =====
@app_flask.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    user_id = int(data.get("user_id", 0))

    if user_id:
        asyncio.run(liberar_usuario(user_id))

    return "ok", 200

# ===== INIT =====
bot_app.add_handler(CommandHandler("start", start))

async def main():
    await bot_app.initialize()
    await bot_app.start()

    from threading import Thread
    Thread(target=lambda: app_flask.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))).start()

    while True:
        await asyncio.sleep(60)

import asyncio
asyncio.run(main())