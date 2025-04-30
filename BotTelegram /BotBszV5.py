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
    while len(tarjetas) < cantidad:
        # Rellenar la parte de BIN con dígitos donde haya 'x'
        tarjeta_num = ''.join(
            str(random.randint(0,9)) if c.lower() == 'x' else c
            for c in bin_base
        )
        tarjetas.add(f"{tarjeta_num}|{mes}|{ano}|{cvv}")
    return tarjetas

# ————— Comando /start: muestra menú —————
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

# ————— Callback de los botones del menú —————
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "checker":
        # Indicar uso del comando /chk
        await query.edit_message_text("🔍 Envía tus tarjetas con /chk o pega la lista aquí (xxxx|xx|xxxx|xxx).")
        return

    if choice == "info":
        # Mostrar info del bot
        await query.edit_message_text(
            "🤖 BSZCheckerBot\n"
            "• Verifica tarjetas con /chk\n"
            "• Genera BINs con opción Generador\n"
            "🔗 https://chekerv2bsz.foroactivo.com"
        )
        return

    if choice == "generador":
        # Entrar a la conversación del generador
        await query.edit_message_text("🧾 Por favor escribe el BIN (usa X para aleatorio), e.g.: 4147202656xxxxxx")
        return BIN

# ————— Conversación: paso 1 → MES —————
async def ask_mes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_temp[update.effective_user.id] = {"bin": update.message.text}
    await update.message.reply_text("📅 Ahora escribe el MES (01–12 o 'random'):")
    return MES

# ————— Conversación: paso 2 → AÑO —————
async def ask_ano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_temp[update.effective_user.id]["mes"] = update.message.text
    await update.message.reply_text("📆 Escribe el AÑO (e.g.: 2026 o 'random'):")
    return ANO

# ————— Conversación: paso 3 → CVV —————
async def ask_cvv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_temp[update.effective_user.id]["ano"] = update.message.text
    await update.message.reply_text("🔐 CVV (3 dígitos o 'random'):")
    return CVV

# ————— Conversación: paso 4 → CANTIDAD —————
async def ask_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_temp[update.effective_user.id]["cvv"] = update.message.text
    await update.message.reply_text("🔢 ¿Cuántas tarjetas deseas generar?")
    return CANTIDAD

# ————— Conversación: paso final → Generar y mostrar —————
async def generar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_data_temp.get(uid, {})
    bin_base = data["bin"]
    mes     = data["mes"]
    ano     = data["ano"]
    cvv     = data["cvv"]
    cantidad= int(update.message.text)

    # Funciones auxiliares para random
    rnd_mes = lambda: f"{random.randint(1,12):02d}"
    rnd_ano = lambda: str(random.randint(2025,2030))
    rnd_cvv = lambda: f"{random.randint(0,999):03d}"

    tarjetas = generar_tarjeta(
        bin_base,
        rnd_mes() if mes.lower()=="random" else mes,
        rnd_ano() if ano.lower()=="random" else ano,
        rnd_cvv() if cvv.lower()=="random" else cvv,
        cantidad
    )

    # Mostrar hasta 40 líneas por mensaje
    lista = list(tarjetas)
    for i in range(0, len(lista), 40):
        chunk = "\n".join(lista[i:i+40])
        await update.message.reply_text(f"🎉 Generadas:\n\n{chunk}")

    user_data_temp.pop(uid, None)
    return ConversationHandler.END

# ————— Conversación: cancelar —————
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Generador cancelado.")
    return ConversationHandler.END

# ————— Función auxiliar para mensaje HTML del Checker —————
def generar_mensaje(data: dict, tarjeta: str) -> str:
    card    = data.get("card", {})
    country = card.get("country", {})
    loc     = country.get("location", {})
    code    = data.get("code", -1)
    status  = data.get("status", "N/A")

    if code == 0:   emoji = "🔴"
    elif code == 2: emoji = "🟡"
    else:           emoji = "🟢"

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

# ————— Comando /chk → Checker de tarjetas —————
async def chk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    bot_user = (await context.bot.get_me()).username

    # Quitar mención si es grupo
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
                    resp = await res.text()
                    data = json.loads(resp)
            except Exception:
                unk += 1
                await update.message.reply_text(f"⚠️ Error con {tarjeta}")
                continue

            code = data.get("code", -1)
            if code == 0:   die += 1
            elif code == 2: unk += 1
            else:           live += 1

            await update.message.reply_text(
                generar_mensaje(data, tarjeta),
                parse_mode="HTML"
            )
            await asyncio.sleep(1)

    total = live + die + unk
    await update.message.reply_text(
        f"✅ LIVE: {live}\n❌ DIE: {die}\n❓ UNKNOWN: {unk}\n📊 TOTAL: {total}"
    )

# ————— Comando /info —————
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Este bot verifica tarjetas y genera BINs:\n"
        "• /chk – valida tarjetas\n"
        "• Usa el menú /start para más opciones"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Conversación del generador
    generador_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu_callback, pattern="^generador$")],
        states={
            BIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mes)],
            MES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ano)],
            ANO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_cvv)],
            CVV: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_cantidad)],
            CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, generar)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=True,
    )

    # Handlers básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chk", chk))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(generador_conv)
    app.add_handler(CallbackQueryHandler(menu_callback))  # menú para checker/info
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chk))

    print("✅ Bot ejecutándose...")
    app.run_polling()

if __name__ == "__main__":
    main()
