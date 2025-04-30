from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = input("Introduce el token del bot de Telegram: ")

# Teclados
keyboard_enfermedades = [["Diabetes", "Enfermedades Renales"], ["Hipertensión", "Otros"]]
keyboard_problemas = [["Insomnio", "Mareo"], ["Visión borrosa", "Dolor de cabeza"], ["Baja glucosa", "Dolor de articulaciones", "Deshidratación"]]

# Variables para mantener el estado
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Sí", "No"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("¿Tienes una enfermedad crónica o degenerativa?", reply_markup=markup)

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    # Manejar el flujo de enfermedades
    if text == "Sí":
        markup = ReplyKeyboardMarkup(keyboard_enfermedades, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Selecciona tu enfermedad:", reply_markup=markup)
        user_state[user_id] = {"step": "enfermedad"}

    elif text == "No":
        await update.message.reply_text("Gracias por tu respuesta. ¡Cuídate!")
        if user_id in user_state:
            del user_state[user_id]

    elif user_id in user_state and user_state[user_id]["step"] == "enfermedad":
        # Cuando seleccionan una enfermedad
        if text in ["Diabetes", "Enfermedades Renales", "Hipertensión"]:
            user_state[user_id]["enfermedad"] = text
            markup = ReplyKeyboardMarkup(keyboard_problemas, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("¿Qué síntoma tienes?", reply_markup=markup)
            user_state[user_id]["step"] = "sintoma"
        elif text == "Otros":
            markup = ReplyKeyboardMarkup(keyboard_problemas, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("¿Qué síntoma tienes?", reply_markup=markup)
            user_state[user_id]["step"] = "sintoma"

    elif user_id in user_state and user_state[user_id]["step"] == "sintoma":
        # Cuando seleccionan un síntoma
        sintomas = {
            "Insomnio": (
                "Medicamentos sugeridos para Insomnio:\n"
                "- Melatonina 3mg (1 hora antes de dormir)\n"
                "- Difenhidramina (uso ocasional)\n"
                "- Valeriana (alternativa natural)\n\n"
                "Compra aquí: https://www.farmalisto.com.mx/insomnio"
            ),
            "Mareo": (
                "Medicamentos sugeridos para Mareo:\n"
                "- Dimenhidrinato 50mg (cada 8h si es necesario)\n"
                "- Meclizina (ideal para vértigo leve)\n\n"
                "Compra aquí: https://www.farmalisto.com.mx/mareo"
            ),
            "Visión borrosa": (
                "Recomendación:\n"
                "- Acude a un oftalmólogo para diagnóstico\n"
                "- Evita automedicación sin receta\n\n"
                "Consulta opciones: https://www.farmalisto.com.mx"
            ),
            "Dolor de cabeza": (
                "Medicamentos sugeridos:\n"
                "- Paracetamol 500mg (cada 6h si el dolor persiste)\n"
                "- Ibuprofeno (si hay inflamación o tensión muscular)\n\n"
                "Compra aquí: https://www.farmalisto.com.mx/dolor-de-cabeza"
            ),
            "Baja glucosa": (
                "Sugerencia:\n"
                "- Toma jugo de naranja o come caramelos\n"
                "- Glucosa en tabletas (si disponible)\n\n"
                "Compra aquí: https://www.farmalisto.com.mx/glucosa"
            ),
            "Dolor de articulaciones": (
                "Medicamentos sugeridos:\n"
                "- Ibuprofeno 400mg (cada 8h)\n"
                "- Naproxeno (alternativa si persiste)\n"
                "- Gel antiinflamatorio (uso local)\n\n"
                "Compra aquí: https://www.farmalisto.com.mx/articulaciones"
            ),
            "Deshidratación": (
                "Recomendaciones:\n"
                "- Beber suero oral o agua con electrolitos\n"
                "- Vida Suero Oral (cada 6h)\n\n"
                "Compra aquí: https://www.farmalisto.com.mx/suero-oral"
            )
        }

        if text in sintomas:
            await update.message.reply_text(sintomas[text])
            del user_state[user_id]  # Reseteamos el estado después de proporcionar la sugerencia

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))
    print("Bot iniciado.")
    app.run_polling()

if __name__ == "__main__":
    main()
