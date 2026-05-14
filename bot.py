import os
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
 
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8756035313:AAFHmoHpNiywGxohtAbdMtWmxRga2KxoYVo")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "AIzaSyBIUbJ30esfzJVQp6-SsKFDsj9LxEyTvhY")
 
NOMBRE, CATEGORIA, PRECIO, CARACTERISTICAS = range(4)
 
CATEGORIAS = [
    ["Ropa y calzado", "Electrónica"],
    ["Hogar y muebles", "Deportes"],
    ["Juguetes", "Herramientas"],
    ["Belleza", "Alimentos"],
    ["Otro"]
]
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Bienvenido a *VendeMás*!\n\n"
        "Generá descripciones irresistibles para tus productos de Mercado Libre en segundos con IA. 🚀\n\n"
        "Tocá /generar para empezar.",
        parse_mode="Markdown"
    )
 
async def generar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ ¿Cuál es el *nombre del producto*?", parse_mode="Markdown")
    return NOMBRE
 
async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nombre"] = update.message.text
    markup = ReplyKeyboardMarkup(CATEGORIAS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("📦 ¿Cuál es la *categoría*?", reply_markup=markup, parse_mode="Markdown")
    return CATEGORIA
 
async def recibir_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["categoria"] = update.message.text
    await update.message.reply_text("Cual es el precio en ARS? (o escribi 'saltar')", reply_markup=ReplyKeyboardRemove())
    return PRECIO
 
async def recibir_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["precio"] = update.message.text
    await update.message.reply_text("📝 Describí las *características principales* del producto:", parse_mode="Markdown")
    return CARACTERISTICAS
 
async def recibir_caracteristicas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["caracteristicas"] = update.message.text
    
    nombre = context.user_data.get("nombre", "")
    categoria = context.user_data.get("categoria", "")
    precio = context.user_data.get("precio", "")
    caracteristicas = context.user_data.get("caracteristicas", "")
 
    await update.message.reply_text("⏳ Generando tu descripción...")
 
    prompt = f"""Sos un experto en ventas online en Argentina y Mercado Libre. Generá una descripción de producto atractiva, clara y optimizada para vender.
 
Producto: {nombre}
Categoría: {categoria}
Precio: ${precio} ARS
Características: {caracteristicas}
 
La descripción debe:
- Empezar con un título llamativo en mayúsculas
- Tener 3-4 párrafos cortos y persuasivos
- Resaltar los beneficios principales
- Incluir características con guiones
- Terminar con un llamado a la acción
- Usar tono cercano y argentino
 
Respondé SOLO con la descripción."""
 
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        data = response.json()
        texto = data["candidates"][0]["content"]["parts"][0]["text"]
        
        await update.message.reply_text(
            f"✅ *Descripción lista:*\n\n{texto}\n\n"
            "¿Querés generar otra? Tocá /generar",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ Hubo un error. Intentá de nuevo con /generar"
        )
 
    return ConversationHandler.END
 
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelado. Tocá /generar cuando quieras.")
    return ConversationHandler.END
 
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
 
    conv = ConversationHandler(
        entry_points=[CommandHandler("generar", generar)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_categoria)],
            PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_precio)],
            CARACTERISTICAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_caracteristicas)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
 
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
 
    print("Bot corriendo...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
 
if __name__ == "__main__":
    main()
 
