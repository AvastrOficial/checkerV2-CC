import asyncio
from aiohttp import ClientSession
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

results = {
    "live": [],
    "die": [],
    "unknown": []
}

# Pide token al inicio
TOKEN = input("Introduce el TOKEN del bot de Telegram: ")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Envíame una lista de tarjetas separadas por línea (formato xxxx|xxxx|xxxx) para validarlas.")

async def validate_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip()
    lines = [l.strip() for l in text.split('\n') if '|' in l]

    if not lines:
        await update.message.reply_text("No se encontraron tarjetas válidas.")
        return

    live_count = die_count = unknown_count = 0
    msg = "🔍 Validando tarjetas...\n\n"
    await update.message.reply_text(msg)

    async with ClientSession() as session:
        for i, tarjeta in enumerate(lines):
            try:
                async with session.post(
                    "https://api.chkr.cc/",
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    data=f"data={tarjeta}&charge=false"
                ) as res:
                    data = await res.json()
                    card_info = data.get("card", {}).get("card", tarjeta)
                    status = data.get("status", "N/A")
                    code = data.get("code")

                    if code == 0:
                        results["die"].append(card_info)
                        die_count += 1
                        estado = "❌ DIE"
                    elif code == 2:
                        results["unknown"].append(card_info)
                        unknown_count += 1
                        estado = "❓ UNKNOWN"
                    else:
                        results["live"].append(card_info)
                        live_count += 1
                        estado = "✅ LIVE"

                    await update.message.reply_text(
                        f"💳 {card_info}\n📊 Status: {estado}\n🔢 Code: {code}\n💬 {data.get('message', 'Sin mensaje')}"
                    )

            except Exception as e:
                results["die"].append(tarjeta)
                die_count += 1
                await update.message.reply_text(f"❌ Error al validar {tarjeta}: {e}")

            await asyncio.sleep(1)  # espera 1s entre cada petición

        total = live_count + die_count + unknown_count
        resumen = f"""
✅ LIVE: {live_count}
❌ DIE: {die_count}
❓ UNKNOWN: {unknown_count}
📊 TOTAL: {total}
🔍 Verificado con el bot BSZChecker
        """
        await update.message.reply_text(resumen)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, validate_cards))
    print("✅ Bot ejecutándose...")
    app.run_polling()

if __name__ == "__main__":
    main()
