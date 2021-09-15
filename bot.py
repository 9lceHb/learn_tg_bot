import enum
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
from datetime import datetime
import re
import operator


logging.basicConfig(filename='bot.log', level=logging.INFO)


def talk_to_me(update, context):
    user_text = update.message.text
    print(user_text)
    update.message.reply_text(user_text)


def check_for_words(user_text_list):
    cheked_words = {'real_words': [], 'not_words': []}
    for word in user_text_list:
        if re.search('[a-zA-Zа-яА-Я]', word):
            cheked_words['real_words'].append(word)
        else:
            cheked_words['not_words'].append(word)
    return cheked_words

def wordcount(update, context):
    print('Вызван /wordcount')
    user_text = update.message.text
    user_text_list = user_text.split(' ')[1:]
    start_word_count =len(user_text_list)
    cheked_words = check_for_words(user_text_list) # функция возвращает словарь из списков слов и 'не слов'.
    word_count = len(cheked_words['real_words'])
    if word_count == start_word_count: # если все, что напечатал пользователь - слова
        answer = f"Количество слов в тексте: {word_count}"
    else:
        answer = f"Количество слов в тексте: {word_count}. \
Кажется в тексте есть не слова, например: {cheked_words['not_words'][0]}!"
    update.message.reply_text(answer)


def make_operation(oper, num_list, oper_list):
    index = oper_list.index(oper)
    num_list[index] = oper(num_list[index], num_list[index+1])
    del num_list[index+1]
    del oper_list[index]


def pyton_operators(items):
    list_oper = []
    for oper in items:
        if oper == '+':
            list_oper.append(operator.add)
        elif oper == '-':
            list_oper.append(operator.sub)
        elif oper == '*':
            list_oper.append(operator.mul)
        else:
            list_oper.append(operator.truediv)
    return list_oper


def calc(update, context):
    print('Вызван /calc')
    user_text = ''.join(update.message.text.split(' ')[1:])
    print(user_text)
    operators_list = ['*', '/', '+', '-']
    user_numbers = []
    user_operators = []
    num = ''
    for index, symbol in enumerate(user_text):
        if symbol in operators_list:
            user_operators.append(symbol)
            user_numbers.append(float(num))
            num = ''
        else:
            num += symbol
    user_numbers.append(float(num))
    user_operators = pyton_operators(user_operators)
    print(user_numbers)
    print(user_operators)
    for oper in tuple(user_operators):
        if oper is operator.mul:
            make_operation(operator.mul, user_numbers, user_operators)
        if oper is operator.truediv:
            make_operation(operator.truediv, user_numbers, user_operators)
    for oper in tuple(user_operators):
        if oper is operator.add:
            make_operation(operator.add, user_numbers, user_operators)
        if oper is operator.sub:
            make_operation(operator.sub, user_numbers, user_operators)
    update.message.reply_text(f'Ответ:{round(user_numbers[0], 2)}')
    

def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, я бот повторятель!')


def next_full_moon(update, context):
    print('Вызван /next_full_moon')
    moon_date = ephem.next_full_moon(datetime.now())

    text_for_user = f'Следующее полнолуние будет {moon_date}'
    update.message.reply_text(text_for_user)


city_list = ('москва', 'екатеринбург', 'санкт-Петербург', 'армавир', 'рига', 'архангельск', 'калининград', 'дубна', 'георгиевск')
games = {}


def city_play(update, context):

    user = update.message.chat.id
    if games.get(user) is None: # Создание списка городов для нового пользователя.
        games[update.message.chat.id] = list(city_list)
    user_city = update.message.text.split(' ')[1].lower()
    if user_city in games[user]: # Проверка наличия пользовательского города в списке.
        user_city_index = games[user].index(user_city)
        last_letter = user_city[-1]
        for index, city in enumerate(games[user]):
            if city[0] == last_letter: # Поиск города в списке(на последнюю букву)
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
    

def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('cities', city_play))
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('wordcount', wordcount))
    dp.add_handler(CommandHandler('calc', calc))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Бот стартовал')
    mybot.start_polling()
    mybot.idle()
    


if __name__ == '__main__':
    main()
