from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

# тут будем писать наш код :)
async def hello(update, context):
    if dialog.mode=='gpt':
        await gpt_dialog(update, context)
    elif dialog.mode=='date':
        await date_dialog(update, context)
    elif dialog.mode=='message':
        await message_dialog(update, context)
    else:        
        await send_photo(update, context, "avatar_main")
        await send_text(update, context, f'Привет, {update.message.from_user.first_name}!')
        await send_text(update, context, f"Ты написал: \"{update.message.text}\"")
        await send_text_buttons(update, context, "Выберите режим работы", {  # Текст перед кнопкой
            "btn_start": " Старт ", # Текст и команда кнопки "Старт"
            "btn_stop": " Стоп "  # Текст и команда кнопки "Стоп"
        })

async def hello_button(update, context):
    query = update.callback_query.data   #код кнопки
    await update.callback_query.answer() #помечаем что обработали нажатие на кнопку
    await send_html(update, context, f"Вы нажали на кнопку {query}")

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
    my_message = await send_text(update, context, 'ChatGPT is processing your request...')
    answer = await chatgpt.send_question(load_prompt('gpt'), text)
    await my_message.edit_text(answer)

async def date(update, context):
    dialog.mode='date'
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, load_message("date"), {  # Текст перед кнопкой
        "date_grande": "Ариана Гранде",
        "date_robbie": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди",                
    })

async def date_dialog(update, context):
    text=update.message.text
    my_message=await send_text(update,context,'Ваш собеседник печатает...')
    answer=await chatgpt.add_message(text)
    await my_message.edit_text(answer)


async def date_button(update, context):
    query = update.callback_query.data   #код кнопки
    await update.callback_query.answer() #помечаем что обработали нажатие на кнопку
    await send_photo(update, context, query)
    await send_text(update, context, 'Кутой выбор!!!')
    chatgpt.set_prompt(load_prompt(query))

async def message(update, context):
    dialog.mode='message'
    dialog.list.clear()
    await send_photo(update, context, 'message')
    await send_text_buttons(update, context, load_message('message'),{
        'message_next':'Следующее сообщение',
        'message_date':'Пригласить на свидание'
    })    

async def message_dialog(update, context):
    dialog.list.append(update.message.text)

async def message_button(update, context):
    query = update.callback_query.data   #код кнопки
    await update.callback_query.answer() #помечаем что обработали нажатие на кнопку
    prompt = load_prompt(query)
    msg_history = '\n\n'.join(dialog.list)
    my_message = await send_text(update, context, 'ChatGPT is processing your request...')
    answer = await chatgpt.send_question(prompt, msg_history)
    await my_message.edit_text(answer)


dialog=Dialog()
dialog.mode=''
dialog.list=list()

chatgpt=ChatGptService(load_gpt_token())
tlg_token=load_telegram_token()
app = ApplicationBuilder().token(load_telegram_token()).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern='^date_.*'))
app.add_handler(CallbackQueryHandler(message_button, pattern='^message_.*'))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()