from datetime import datetime

import vk_api

from config import access_token


class VkTools:

    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'sex': info['sex'] if 'sex' in info else None,
                     'city': info['city']['id'] if 'city' in info else None,
                     'relation': info['relation'] if 'relation' in info else None
                     }
        return user_info

    def get_city_id(self, city):
        res = self.api.method('database.getCities', {'q': city})
        return res['items'][0]['id']

    def search_users(self, params, offset=0):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5

        users = self.api.method('users.search',
                                {'count': 1000,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'has_photo': 1,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                 }
                                )

        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] is False:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(access_token)
    # params = bot.get_profile_info(12344567)
    # users = bot.serch_users(params)
    # print(users)
    # print(bot.get_photos(users[2]['id']))
