import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from core import VkTools

import database
import json


class BotInterface:

    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.user_id = None
        self.result = None
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    @staticmethod
    def select_from_json(user_id):
        with open('search_lists.json', 'r') as e:
            a = e.read()
        data = json.loads(a)
        return data[str(user_id)]

    @staticmethod
    def update_json(user_id, params):
        with open('search_lists.json', 'r') as e:
            a = e.read()
        data = json.loads(a)
        data[str(user_id)] = params
        to_json = json.dumps(data)
        with open('search_lists.json', 'w') as f:
            f.write(to_json)

    @staticmethod
    def get_key(params, none_value):
        for key, value in params.items():
            if value == none_value:
                return key

    def info_user_check(self, params, longpoll):
        if None in params.values():
            param = self.get_key(self.params, None)
            if params[param] is None:

                if param == 'bdate':
                    self.message_send(self.user_id, f'Введите дату рождения в формате "ХХ.ХХ.ХХХХ:"', None)
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['bdate'] = event.text
                            self.info_user_check(self.params, longpoll)

                elif param == 'sex':
                    self.message_send(self.user_id, f'Введите свой пол цифрой, женский - 1, мужской - 2', None)
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['sex'] = event.text
                            self.info_user_check(self.params, longpoll)

                elif param == 'city':
                    self.message_send(self.user_id, f'Введите свой город', None)
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['city'] = self.api.get_city_id(event.text)
                            self.info_user_check(self.params, longpoll)

                elif param == 'relation':
                    self.message_send(self.user_id, f'''Введите свое семейное положение из предложенных:
0 — не указано, 5 — всё сложно, 6 — в активном поиске, ''', None)
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            self.params['relation'] = event.text
                            self.info_user_check(self.params, longpoll)
        else:
            self.search(longpoll, self.user_id)

    def search(self, longpoll, user_id):
        data = self.select_from_json(user_id)

        if data is None:
            self.result = self.api.search_users(self.params, self.user_id)
            self.send_result_to_user(self.result, longpoll, self.user_id)

        elif data == []:
            self.offset += 50
            self.result = self.api.search_users(self.params, self.user_id, offset=self.offset)
            self.send_result_to_user(self.result, longpoll, self.user_id)

        else:
            self.result = data
            self.send_result_to_user(self.result, longpoll, self.user_id)

    def send_result_to_user(self, users, longpoll, user_id):
        user = users.pop()
        self.update_json(user_id, users)
        check = database.check_user(user['id'], self.user_id)
        if check is None:
            photos_user = self.api.get_photos(user['id'])
            attachments = []
            link = f'vk.com/id{user["id"]}'
            for num, photo in enumerate(photos_user):
                attachments.append(f'photo{photo["owner_id"]}_{photo["id"]}')
                if num == 2:
                    break
            self.message_send(self.user_id,
                              f'''Встречайте, {user["name"]}!
{link}
Чтобы продолжить, напишите "дальше", выйти и остановить поиск - "стоп"''',
                              attachment=','.join(attachments)
                              )
            database.add_user(user, self.user_id)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    command = event.text.lower()
                    if command == 'дальше':
                        self.search(longpoll, self.user_id)
                    elif command == 'стоп':
                        self.message_send(event.user_id, f'Поиск остановлен, жду дальнейших команд')
                        self.event_handler()
        else:
            self.search(longpoll, self.user_id)

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.user_id = event.user_id
                    self.params = self.api.get_profile_info(event.user_id)
                    with open('search_lists.json', 'r') as e:
                        a = e.read()
                    data = json.loads(a)
                    if str(self.user_id) not in data:
                        data[self.user_id] = None
                        to_json = json.dumps(data)
                        with open('search_lists.json', 'w') as f:
                            f.write(to_json)
                    self.message_send(event.user_id, f'''Привет, {self.params["name"]}

Я - Vkinder! Помогу тебе найти свою вторую половинку! Для того, чтобы начать, просто напиши мне слово "поиск"!''')

                elif command == 'поиск':
                    self.info_user_check(self.params, longpoll)

                elif command == 'пока':
                    self.message_send(event.user_id, 'Что ж, пока...')
                else:
                    self.message_send(event.user_id, 'Команда не найдена, я такое не понимаю')


if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
