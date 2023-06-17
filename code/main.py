from markups import MARKUPS
from telegram.ext import Application, CommandHandler

from weather import get_weather, get_coordinates, save_dialog, get_random_joke

import logging

TOKEN = "5800047796:AAGMowIZgmjkBWMXvbI52z8u_ayoX5oQHn4"


async def start(update, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(f"./logs/{update.message.chat_id}.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "[%H:%M:%S]"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    context.user_data["logger"] = logger

    # await save_dialog(update.message.chat_id, update.message.text, "Пользователь")
    context.user_data.get("logger", 0).info("Пользователь:\n" + update.message.text)
    reply = (
        "Приветствую, я бот-помощник, с моей помощью вы можете узнать погоду и многое другое\n\n"
        "Узнать погоду (/weather)\n"
        "Получить случайную шутку (/joke)"
    )
    await update.message.reply_text(
        reply,
        reply_markup=MARKUPS["start"],
    )
    context.user_data.get("logger", 0).info("Бот:\n" + reply)
    # await save_dialog(update.message.chat_id, reply, "Бот")


async def back(update, context):
    context.user_data.get("logger", 0).info("Пользователь:\n" + update.message.text)
    # await save_dialog(update.message.chat_id, update.message.text, "Пользователь")
    await start(update, context)


async def log(update, context):
    chat_id = update.message.chat_id
    message = update.message.text
    user = "Пользователь"
    await save_dialog(chat_id, message, user)


async def city(update, context):
    context.user_data.get("logger", 0).info("Пользователь:\n" + update.message.text)
    # await save_dialog(update.message.chat_id, update.message.text, "Пользователь")
    try:
        lat, lon, city = await get_coordinates("".join(update.message.text.split()[1:]))
        if lat and lon and city:
            context.user_data["lat"] = lat
            context.user_data["lon"] = lon
            context.user_data["city"] = city
            reply = "Город успешно выбран"
            await update.message.reply_text(reply)
            context.user_data.get("logger", 0).info("Бот:\n" + reply)
            # await save_dialog(update.message.chat_id, reply, "Бот")
            await weather(update, context)
    except TypeError:
        reply = "Ошибка, город не найден"
        await update.message.reply_text(reply)
        context.user_data.get("logger", 0).info("Бот:\n" + reply)
        # await save_dialog(update.message.chat_id, reply, "Бот")


async def weather(update, context):
    context.user_data.get("logger", 0).info("Пользователь:\n" + update.message.text)
    # await save_dialog(update.message.chat_id, update.message.text, "Пользователь")
    if context.user_data.get("city", 0):
        if update.message.text in ("/now", "/today", "/4days"):
            reply = f"{''.join(await get_weather(update.message.text, context.user_data['lat'], context.user_data['lon']))}"
            await update.message.reply_text(reply, reply_markup=MARKUPS["weather"])
            context.user_data.get("logger", 0).info("Бот:\n" + reply)
            # await save_dialog(update.message.chat_id, reply, "Бот")
        else:
            reply = (
                f"Выбранный город: {context.user_data['city']}\n"
                "Выберите интересующую вас категорию:\n\n"
                "Погода в данный момент (/now)\n"
                "Прогноз на остаток сегодняшнего дня с интервалом в 3 часа (/today)\n"
                "Прогноз на следующие 4 дня (/4days)\n"
                "Изменить город (/city <название города>)\n"
                "Вернуться назад (/back)"
            )
            await update.message.reply_text(
                reply,
                reply_markup=MARKUPS["weather"],
            )
            context.user_data.get("logger", 0).info("Бот:\n" + reply)
            # await save_dialog(update.message.chat_id, reply, "Бот")
    else:
        reply = (
            "Сначала выберите город при помощи команды /city <название города>,\n"
            "Например, /city Кемерово"
        )
        await update.message.reply_text(reply, reply_markup=MARKUPS["weather"])
        context.user_data.get("logger", 0).info("Бот:\n" + reply)
        # await save_dialog(update.message.chat_id, reply, "Бот")


async def joke(update, context):
    context.user_data.get("logger", 0).info("Пользователь:\n" + update.message.text)
    reply = f"{''.join(await get_random_joke())}"
    await update.message.reply_text(reply)
    context.user_data.get("logger", 0).info("Бот:\n" + reply)
    pass


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handlers(
        [
            CommandHandler("start", start),
            CommandHandler("back", back),
            CommandHandler("weather", weather),
            CommandHandler("send", weather),
            CommandHandler("now", weather),
            CommandHandler("today", weather),
            CommandHandler("4days", weather),
            CommandHandler("city", city),
            CommandHandler("joke", joke),
            # MessageHandler(filters.TEXT, log),
        ]
    )

    application.run_polling()


if __name__ == "__main__":
    main()
