from pymongo import MongoClient
from bot_project import settings


class DBase:

    def __init__(self):
        self.client = MongoClient(settings.MONGO_LINK)
        self.db_client = self.client[settings.MONGO_DB]

    def get_or_create_user(self, effective_user, chat_id):
        """
        Создание пользователя в базе users, подтягивание информации из TG.
        """
        user = self.db_client.users.find_one({'tg_id': effective_user.id})
        if not user:
            user = {
                'tg_id': effective_user.id,
                'first_name': effective_user.first_name,
                'last_name': effective_user.last_name,
                'username': effective_user.username,
                'chat_id': chat_id,
                'anketa': {},
                'filters': {}
            }
            self.db_client.users.insert_one(user)
        return user

    def save_anketa(self, user_id, anketa_key, anketa_value):
        """
        Добавление или обновление в базе информации из анкеты
        """
        user = self.db_client.users.find_one({'tg_id': user_id})

        # TODO: нужно добавить проверку на None у user
        self.db_client.users.update_one(
            {'_id': user['_id']},
            {'$set': {f'anketa.{anketa_key}': anketa_value}}
        )

    def save_filters(self, user_id, filter_key, filter_value):
        """
        Добавление или обновление в базе информации по фильтрам поиска резюме
        """
        user = self.db_client.users.find_one({'tg_id': user_id})

        # TODO: нужно добавить проверку на None у user
        self.db_client.users.update_one(
            {'_id': user['_id']},
            {'$set': {f'filters.{filter_key}': filter_value}}
        )
