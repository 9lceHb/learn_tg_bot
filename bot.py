import enum
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
from datetime import datetime


logging.basicConfig(filename='bot.log', level=logging.INFO)


def talk_to_me(update, context):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text(user_text)


def wordcount(update, context):
    print('Вызван /wordcount')
    user_text = update.message.text
    word_count = len(user_text.split(' ')[1:])
    answer = f'Количество слов в тексте: {word_count}'
    update.message.reply_text(answer)
    


def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, я бот повторятель!')


def next_full_moon(update, context):
    print('Вызван /next_full_moon')
    moon_date = ephem.next_full_moon(datetime.now())

    text_for_user = f'Следкющее полнолуние будет {moon_date}'
    update.message.reply_text(text_for_user)

games = {}
def city_play(update, context):

    user = update.message.chat.id
    if games.get(user) is None:
        games[update.message.chat.id] = list(city_list)
    user_city = update.message.text.split(' ')[1].lower()
    if user_city in games[user]:
        user_city_index = games[user].index(user_city)
        last_letter = user_city[-1]
        for index, city in enumerate(games[user]):
            if city[0] == last_letter:
                bot_city = games[user][index]
                text_for_user = f'{bot_city.capitalize()}, ваш ход'
                games[user].pop(index)
                games[user].pop(user_city_index)
                break
            else:
                text_for_user = 'Вы победили, я больше не знаю города :('
    else:
        text_for_user = 'Я не знаю такого города :('
    #print(city_list)
    update.message.reply_text(text_for_user)
    

city_list = ('москва', 'екатеринбург', 'санкт-Петербург', 'армавир', 'рига', 'архангельск', 'калининград', 'дубна', 'георгиевск')


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('cities', city_play))
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()
    


if __name__ == '__main__':
    main()
