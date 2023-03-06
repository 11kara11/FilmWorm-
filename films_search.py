import json

from config import TOKEN_api_kinopoisk
import requests


class Films():
    def __init__(self):
        self.URL = 'https://api.kinopoisk.dev/v1'
        self.TITLE = '/movie?name=Человек паук нет пути домой&type=movie'
        self.TOKEN = '&token=' + TOKEN_api_kinopoisk

    def get_film_information(self, name='', type_industry='movie'):
        try:
            self.TITLE = f'/movie?name={name}&type={type_industry}'
            r = requests.get(self.URL + self.TITLE + self.TOKEN)
            with open('test.json', 'wb') as file:
                file.write(r.content)
            with open('test.json', 'r', encoding='utf-8') as file:
                text_json = json.load(file)
                full_name = text_json['docs'][0]['name']
                description = text_json['docs'][0]['description']
                year = text_json['docs'][0]['year']
                poster_link = text_json['docs'][0]['poster']['url']
                poster = requests.get(poster_link)
                with open('img.png', 'wb') as photo:
                    photo.write(poster.content)

                rating = text_json['docs'][0]['rating']['kp']
                print(full_name, '\n', description, '\n', year, '\n', poster, '\n', rating)
        except Exception:
            return (False, False, False, False, False)
        return (full_name, description, year, poster, rating)

        #print(r.json())

#Films().get_film_information()
