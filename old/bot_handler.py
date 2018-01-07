import requests
import datetime

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)

    def get_updates(self, offset = None, timeout = 30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + method, data = params)
        result = response.json()['result']
        return result

    def send_message(self, chat_id, text, keyboard_markup = None):
        method = 'sendMessage'
        params = {'chat_id': chat_id, 'text': text}
        if keyboard_markup is not None:
            print(keyboard_markup)
            params['reply_markup'] = keyboard_markup
        result = requests.post(self.api_url + method, data = params)
        return result

    def send_photo(self, chat_id, photo):
        method = 'sendPhoto'
        params = {'chat_id': chat_id, 'photo': photo}
        result = requests.post(self.api_url + method, data = params)
        return result

    def send_video(self, chat_id, video):
        method = 'sendVideo'
        params = {'chat_id': chat_id, 'video': video}
        result = requests.post(self.api_url + method, data = params)
        return result

    def get_last_update(self):
        updates = self.get_updates()

        if (len(updates) > 0):
            last_update = updates[-1]
        else:
            last_update = None

        return last_update
