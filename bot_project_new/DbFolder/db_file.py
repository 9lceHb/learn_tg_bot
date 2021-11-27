from pymongo import MongoClient
import settings


class DBase:

    def __init__(self):
        self.client = MongoClient(settings.MONGO_LINK)
        self.db_client = self.client[settings.MONGO_DB]

    def get_or_create_user(self, effective_user):
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
                'cv': {'show_cv': True, 'specialisation': [], 'first_time': True},
                'filter': {'specialisation': [], 'first_time': True}
            }
            self.db_client.users.insert_one(user)
        return user

    def save_cv(self, user_id, cv_key, cv_value):
        """
        Добавление или обновление в базе информации из анкеты
        """
        user = self.db_client.users.find_one({'tg_id': user_id})

        # TODO: нужно добавить проверку на None у user
        self.db_client.users.update_one(
            {'_id': user['_id']},
            {'$set': {f'cv.{cv_key}': cv_value}}
        )

    def save_filter(self, user_id, filter_key, filter_value):
        """
        Добавление или обновление в базе информации по фильтрам поиска резюме
        """
        user = self.db_client.users.find_one({'tg_id': user_id})

        # TODO: нужно добавить проверку на None у user
        self.db_client.users.update_one(
            {'_id': user['_id']},
            {'$set': {f'filter.{filter_key}': filter_value}}
        )

    def clear_filters(self, user_id):
        user = self.db_client.users.find_one({'tg_id': user_id})
        self.db_client.users.update_one(
            {'_id': user['_id']},
            {'$set': {'filter': {'specialisation': [], 'first_time': True}}}
        )

    def clear_cv(self, user_id):
        user = self.db_client.users.find_one({'tg_id': user_id})
        self.db_client.users.update_one(
            {'_id': user['_id']},
            {'$set': {
                'cv.salary': False,
                'cv.salary_key': False,
                'cv.education': False,
                'cv.education_key': False,
                'cv.experience': False,
                'cv.experience_key': False,
                'cv.schedule': False,
                'cv.specialisation': []
            }}
        )

    def update_specialisation(self, user_id, cv_value, cv_or_filter):
        """
        Добавление или обновление в базе информации из анкеты
        """
        user = self.db_client.users.find_one({'tg_id': user_id})
        user_specialisations = set(user[cv_or_filter]['specialisation'])
        user_specialisations = list(user_specialisations)
        if cv_value in user_specialisations:
            user_specialisations.remove(cv_value)
        else:
            user_specialisations.append(cv_value)
        # TODO: нужно добавить проверку на None у user
        if cv_or_filter == 'cv':
            self.db_client.users.update_one(
                {'_id': user['_id']},
                {'$set': {'cv.specialisation': user_specialisations}}
            )
        elif cv_or_filter == 'filter':
            self.db_client.users.update_one(
                {'_id': user['_id']},
                {'$set': {'filter.specialisation': user_specialisations}}
            )
