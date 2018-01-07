import requests
from time import sleep

url = "https://api.telegram.org/bot545921711:AAE5LHkyP8DglJisg-aqQEZPvgACE_h-HBw"

def get_updates_json(request):
    params = {'timeout': 100, 'offset': None}
    response = requests.get(request + "getUpdates", data = params)
    return response.json()

def get_last_update(data):
    result = data['result']
    last_update_index = len(result) - 1
    return result[last_update_index]

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def send_message(chat_id, text):
    params = {'chat_id': chat_id, 'text': text}
    requests.post(url + "sendMessage", data = params)

def main():
    update_id = get_last_update(get_updates_json(url))['update_id']
    while True:
        update_id_tmp = get_last_update(get_updates_json(url))['update_id']
        if update_id == update_id_tmp:
            chat_id = get_chat_id(get_last_update(get_updates_json(url)))
            send_message(chat_id, "Message from python")
            update_id += 1
        sleep(1)

if __name__ == "__main__":
    main()

#chat_id = get_chat_id(get_last_update(get_updates_json(url)))
#send_message(chat_id, "Message from python")
