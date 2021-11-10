from pymongo import MongoClient
from bot_project import settings

client = MongoClient(settings.MONGO_LINK)
db = client[settings.MONGO_DB]


# Создание пользователя в базе users, подтягивание информации из TG.
def get_or_create_user(db, effective_user, chat_id):
    user = db.users.find_one({'tg_id': effective_user.id})
    if not user:
        user = {
            'tg_id': effective_user.id,
            'first_name': effective_user.first_name,
            'last_name': effective_user.last_name,
            'username': effective_user.username,
            'chat_id': chat_id,
            'anketa': {}
        }
        db.users.insert_one(user)
    return user


# Добавление или обновление в базе информации из анкеты
def save_anketa(db, user_id, anketa_key, anketa_value):
    user = db.users.find_one({'tg_id': user_id})
    db.users.update_one(
        {'_id': user['_id']},
        {'$set': {f'anketa.{anketa_key}': anketa_value}}
    )