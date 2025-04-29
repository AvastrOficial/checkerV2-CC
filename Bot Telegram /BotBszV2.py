import asyncio
from aiohttp import ClientSession
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

results = {
    "live": [],
    "die": [],
    "unknown": []
}

# Solicita el token del bot
TOKEN = input("Introduce el TOKEN del bot de Telegram: ")

# Función que genera el mensaje detallado en formato HTML
def generar_mensaje(data: dict, tarjeta: str = 'N/A') -> str:
    card = data.get('card', {})
    country = card.get('country', {})
    location = country.get('location', {})

    return f"""<i class="fas fa-credit-card"></i> {card.get('card', tarjeta)}
<i class="fas fa-chart-bar"></i> <b>Status:</b> {data.get('status', 'N/A')} ({data.get('code', '-')})
<i class="fas fa-comments"></i> <b>Mensaje:</b> {data.get('message', 'Sin mensaje')}
<i class="fas fa-building"></i> <b>Banco:</b> {card.get('bank', 'Desconocido')}
<i class="fas fa-briefcase"></i> <b>Tipo:</b> {card.get('type', '?')} - {card.get('category', '?')}
<i class="fas fa-tag"></i> <b>Marca:</b> {card.get('brand', 'N/A')}
<i class="fas fa-globe"></i> <b>País:</b> {country.get('name', 'N/A')} ({country.get('code', '-')}) {country.get('emoji', '')}
<i class="fas fa-money-bill-wave"></i> <b>Moneda:</b> {country.get('currency', 'N/A')}
<i class="fas fa-map-marker-alt"></i> <b>Geo:</b> Lat: {location.get('latitude', '?')}, Lng: {location.get('longitude', '?')}
<i class="fas fa-check-circle"></i> Verificado con el bot <b>BSZCheker</b>"""

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Envíame una lista de tarjetas separadas por línea (formato xxxx|xxxx|xxxx) para validarlas."
    )

# Manejador de validación de tarjetas
async def validate_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip()
    lines = [l.strip() for l in text.split('\n') if '|' in l]

    if not lines:
        await update.message.reply_text("❌ No se encontraron tarjetas válidas.")
        return

    live_count = die_count = unknown_count = 0
    await update.message.reply_text("🔍 Validando tarjetas...\n")

    async with ClientSession() as session:
        for tarjeta in lines:
            try:
                async with session.post(
                    "https://api.chkr.cc/",
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    data=f"data={tarjeta}&charge=false"
                ) as res:
                    data = await res.json()
                    card_info = data.get("card", {}).get("card", tarjeta)
                    code = data.get("code")
                    status = data.get("status", "N/A")

                    if code == 0:
                        results["die"].append(card_info)
                        die_count += 1
                    elif code == 2:
                        results["unknown"].append(card_info)
                        unknown_count += 1
                    else:
                        results["live"].append(card_info)
                        live_count += 1

                    mensaje = generar_mensaje(data, tarjeta)
                    await update.message.reply_text(mensaje, parse_mode='HTML')

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

# Inicializa el bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, validate_cards))
    print("✅ Bot ejecutándose...")
    app.run_polling()

if __name__ == "__main__":
    main()
