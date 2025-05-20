from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

# тут будем писать наш код :)
async def hello(update, context):
    if dialog.mode=='gpt':
        await gpt_dialog(update, context)
    else:
        await send_photo(update, context, "avatar_main")
        await send_text(update, context, "Привет!")
        await send_text(update, context, f"Ты написал: \"{update.message.text}\"")
        await send_text_buttons(update, context, "Выберите режим работы", {  # Текст перед кнопкой
            "btn_start": " Старт ", # Текст и команда кнопки "Старт"
            "btn_stop": " Стоп "  # Текст и команда кнопки "Стоп"
        })

async def hello_button(update, context):
    query = update.callback_query.data   #код кнопки
    await update.callback_query.answer() #помечаем что обработали нажатие на кнопку
    await send_html(update, context, "Вы нажали на кнопку " + query)

async def start(update, context):
    dialog.mode='main'
    await send_photo(update, context, "main")
    await send_text(update, context, load_message("main"))
    await show_main_menu(update, context, {
        'start':'главное меню бота',
        'profile':'генерация Tinder-профля 😎',
        'opener':'сообщение для знакомства 🥰',
        'message':'переписка от вашего имени 😈',
        'date':'переписка со звездами 🔥',
        '/gpt':'задать вопрос чату GPT 🧠'
    })

async def gpt(update, context):
    dialog.mode='gpt'
    await send_photo(update, context, "gpt")
    await send_text(update, context, load_message("gpt"))

async def gpt_dialog(update, context):
    text=update.message.text
    answer=await chatgpt.send_question(load_prompt('gpt'), text)
    await send_text(update, context, answer)

dialog=Dialog()
dialog.mode=None

chatgpt=ChatGptService(load_gpt_token())

app = ApplicationBuilder().token(load_telegram_token()).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()