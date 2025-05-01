import asyncio
import json
import random
from aiohttp import ClientSession
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ————— Estados para el Generador —————
BIN, MES, ANO, CVV, CANTIDAD = range(5)

# ————— Datos temporales por usuario —————
user_data_temp = {}

# ————— Diccionario para resultados del Checker —————
results = {
    "live": [],
    "die": [],
    "unknown": [],
}

# ————— Token del bot —————
TOKEN = input("Introduce el TOKEN del bot de Telegram: ")

# ————— Función de generación de tarjetas —————
def generar_tarjeta(bin_base: str, mes: str, ano: str, cvv: str, cantidad: int):
    tarjetas = set()

    rnd_mes = lambda: f"{random.randint(1,12):02d}"
    rnd_ano = lambda: str(random.randint(2025,2030))
    rnd_cvv = lambda: f"{random.randint(0,999):03d}"

    while len(tarjetas) < cantidad:
        tarjeta_num = ''.join(
            str(random.randint(0, 9)) if c.lower() == 'x' else c
            for c in bin_base
        )
        final_mes = rnd_mes() if mes.lower() == "random" else mes
        final_ano = rnd_ano() if ano.lower() == "random" else ano
        final_cvv = rnd_cvv() if cvv.lower() == "random" else cvv

        tarjetas.add(f"{tarjeta_num}|{final_mes}|{final_ano}|{final_cvv}")
    return tarjetas

# ————— Comando /start —————
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1️⃣ Checker", callback_data="checker")],
        [InlineKeyboardButton("2️⃣ Generador", callback_data="generador")],
        [InlineKeyboardButton("3️⃣ Información", callback_data="info")],
    ]
    await update.message.reply_text(
        "👋 ¡Bienvenido! Elige una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ————— Callback de menú —————
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "checker":
        await query.edit_message_text("🔍 Envía tus tarjetas con /chk o pega la lista aquí (xxxx|xx|xxxx|xxx).")
        return

    if choice == "info":
        await query.edit_message_text(
            "🤖 BSZCheckerBot\n"
            "• Verifica tarjetas con /chk\n"
            "• Genera BINs con opción Generador\n"
            "🔗 https://chekerv2bsz.foroactivo.com"
        )
        return

    if choice == "generador":
        await query.edit_message_text("🧾 Por favor escribe el BIN (usa X para aleatorio), e.g.: 4147202656xxxxxx")
        return BIN

# ————— Generador paso a paso —————
async def recibir_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bin'] = update.message.text.strip()
    await update.message.reply_text("📅 Escribe el mes (MM), e.g.: 03 o escribe 'random'")
    return MES

async def recibir_mes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mes'] = update.message.text.strip()
    await update.message.reply_text("📆 Escribe el año (YYYY), e.g.: 2026 o escribe 'random'")
    return ANO

async def recibir_ano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ano'] = update.message.text.strip()
    await update.message.reply_text("🔐 Escribe el CVV (3 dígitos) o escribe 'random'")
    return CVV

async def recibir_cvv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cvv'] = update.message.text.strip()
    await update.message.reply_text("🔢 ¿Cuántas tarjetas deseas generar?")
    return CANTIDAD

async def recibir_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cantidad = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Ingresa un número válido.")
        return CANTIDAD

    bin_input = context.user_data['bin']
    mes = context.user_data['mes']
    ano = context.user_data['ano']
    cvv = context.user_data['cvv']

    tarjetas = generar_tarjeta(bin_input, mes, ano, cvv, cantidad)

    lista = list(tarjetas)
    for i in range(0, len(lista), 40):
        chunk = "\n".join(lista[i:i+40])
        await update.message.reply_text(f"🎉 Generadas:\n\n{chunk}")

    return ConversationHandler.END

# ————— Cancelar conversación —————
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Generador cancelado.")
    return ConversationHandler.END

# ————— Checker de tarjetas —————
def generar_mensaje(data: dict, tarjeta: str) -> str:
    card = data.get("card", {})
    country = card.get("country", {})
    loc = country.get("location", {})
    code = data.get("code", -1)
    status = data.get("status", "N/A")

    emoji = "🟢" if code == 1 else "🟡" if code == 2 else "🔴"

    return (
        f"💳 <b>{card.get('card', tarjeta)}</b>\n"
        f"📊 <b>Status:</b> {emoji} {status} ({code})\n"
        f"🏦 <b>Banco:</b> {card.get('bank','?')}\n"
        f"📌 <b>Tipo:</b> {card.get('type','?')} - {card.get('category','?')}\n"
        f"🏷️ <b>Marca:</b> {card.get('brand','N/A')}\n"
        f"🌎 <b>País:</b> {country.get('name','N/A')} ({country.get('code','-')}) {country.get('emoji','')}\n"
        f"💱 <b>Moneda:</b> {country.get('currency','?')}\n"
        f"📍 <b>Geo:</b> Lat:{loc.get('latitude','?')} Lng:{loc.get('longitude','?')}\n"
        "✅ Verificado con BSZChecker"
    )

async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    bot_user = (await context.bot.get_me()).username

    if update.message.chat.type != "private":
        text = text.replace(f"@{bot_user}", "").strip()

    lines = [l.strip() for l in text.splitlines() if "|" in l]
    if not lines:
        await update.message.reply_text("❌ No encontré tarjetas para validar.")
        return

    live = die = unk = 0
    await update.message.reply_text("🔍 Validando...")

    async with ClientSession() as session:
        for tarjeta in lines:
            try:
                async with session.post(
                    "https://api.chkr.cc/",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0"
                    },
                    data=f"data={tarjeta}&charge=false"
                ) as res:
                    data = json.loads(await res.text())
            except Exception:
                unk += 1
                await update.message.reply_text(f"⚠️ Error con {tarjeta}")
                continue

            code = data.get("code", -1)
            if code == 0: die += 1
            elif code == 2: unk += 1
            else: live += 1

            await update.message.reply_text(
                generar_mensaje(data, tarjeta),
                parse_mode="HTML"
            )
            await asyncio.sleep(1)

    total = live + die + unk
    await update.message.reply_text(
        f"✅ LIVE: {live}\n❌ DIE: {die}\n❓ UNKNOWN: {unk}\n📊 TOTAL: {total}"
    )

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    print("✅ Bot iniciado... Esperando comandos.")

    app = ApplicationBuilder().token(TOKEN).build()

    # Conversación para Generador
    generador_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_callback, pattern="^generador$")],
        states={
            BIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_bin)],
            MES: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mes)],
            ANO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_ano)],
            CVV: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cvv)],
            CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cantidad)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Handlers principales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(generador_handler)
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chk))

    app.run_polling()
