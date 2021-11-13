from bot_project_new import settings
import clarifai_grpc.channel
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
import requests
import json
import os
from DbFolder.db_file import DBase

# clarifai модель определяет объект на фото
model_object = 'aaa03c23b3724a16a56b629203edc62c'
# clarifai модель определяет контент для взрослых
model_safe = 'e9576d86d2004ed1a38ba0cf39ecb4b1'

dbase = DBase()

def make_photo_path(id_photo, photo, path, update, context):
    tg_id = update.effective_user.id
    user_photo = context.bot.getFile(photo.file_id)
    if path == 'downloads':
        os.makedirs('downloads', exist_ok=True)
        file_path = os.path.join('downloads', f'{id_photo}_{photo.file_id}.jpg')
        user_photo.download(file_path)
        return file_path
    elif path == 'images':
        os.makedirs(f'images/{tg_id}', exist_ok=True)
        new_file_path = os.path.join('images', f'{tg_id}', f'{tg_id}_{id_photo}_{user_photo.file_id}.jpg')
        return new_file_path


# Функция проверяет что на картинке человек и нет контента для взрослых
def is_human_and_sfw(file_name):
    try:
        with open(file_name, "rb") as f:
            file_bytes = f.read()
        stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_json_channel())
        # This is how you authenticate.
        metadata = ((
            'authorization',
            f'Key {settings.CLARIFAI_API_KEY}'),)
        request_safe = service_pb2.PostModelOutputsRequest(
            model_id=model_safe,
            inputs=[resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes)))])
        request_people = service_pb2.PostModelOutputsRequest(
            model_id=model_object,
            inputs=[resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes)))])
        response_safe = stub.PostModelOutputs(request_safe, metadata=metadata)
        response_people = stub.PostModelOutputs(request_people, metadata=metadata)
        if (response_safe.outputs[0].status.code == 10000 and response_people.outputs[0].status.code == 10000):
            for concept in response_people.outputs[0].data.concepts:
                if (concept.name == "man" and concept.value >= 0.7) or \
                        (concept.name == "woman" and concept.value >= 0.7):
                    for concept in response_safe.outputs[0].data.concepts:
                        if concept.name == "sfw" and concept.value >= 0.7:
                            return True
        return False
    except (ValueError,
            requests.RequestException,
            clarifai_grpc.channel.errors.ApiError):
        print('except')
        return True


# Скачиваем базу округов, районов и метро, добавляем сокращенные наименования
def make_location_file():
    url = 'https://apidata.mos.ru/v1/datasets/1488/rows'
    params = {'api_key': settings.MOS_API}
    response = requests.get(url, params=params).json()
    for i, cell in enumerate(response):
        word_list = cell['Cells']['AdmArea'].replace('-', ' ').split(' ')
        admArea_cut = ''
        for word in word_list:
            admArea_cut += word[0].capitalize()
        response[i]['Cells']['admArea_cut'] = admArea_cut
    with open('locations.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)


# Преобразуем пользовательскую локацию в структурированный формат
def update_user_location(user_location):
    with open('locations.json', encoding='utf-8') as f:
        response = json.load(f)
    user_location = user_location.lower()
    location_list = user_location.split(',')
    for i, location in enumerate(location_list):
        location_list[i] = location.strip()
        if len(location_list[i]) == 3:
            location_list[i] = location_list[i].upper()
        else:
            location_list[i] = location_list[i].capitalize()
    user_location = {}
    user_location['AdmArea'] = []
    user_location['District'] = []
    user_location['Station'] = []
    user_location['Line'] = []
    for location in location_list:
        marker = 0
        for cell in response:
            if location == cell['Cells']['AdmArea']:
                user_location['AdmArea'].append(location)
                marker = 1
                break
            if location == cell['Cells']['admArea_cut']:
                location_name = cell['Cells']['AdmArea']
                user_location['AdmArea'].append(location_name)
                marker = 1
                break
            if location == cell['Cells']['District']:
                user_location['District'].append(location)
                marker = 1
                break
            if location == cell['Cells']['Station']:
                user_location['Station'].append(location)
                marker = 1
                break
            if location == cell['Cells']['Line']:
                user_location['Line'].append(location)
                marker = 1
                break
        if marker == 0:
            return False
    return user_location


def make_station_numbers_set(user_location):
    numbers = []
    with open('locations.json', encoding='utf-8') as f:
        response = json.load(f)
    for subject in user_location.keys():
        for location in user_location[subject]:
            station_numbers = take_numbers(location, subject, response)
            numbers += station_numbers
    numbers = set(numbers)
    numbers = list(numbers)
    return numbers


def take_numbers(location, subject, response):
    station_numbers = []
    for station in response:
        if station['Cells'][subject] == location:
            station_numbers.append(station['global_id'])
    return station_numbers


def send_user_photo(update, context, user_photo):
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(user_photo, 'rb'))

def send_user_info(user):
    text = f'''
    Имя: {user['cv']['name']}
    Возраст: {user['cv']['age']}
    Опыт: {user['cv']['expirience']}
    Комментарий: {user['cv']['komment']}
    Место жительства: {user['cv']['location']['Station']}
    '''
    return text


def print_location(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['cv']['location'].get('AdmArea'):
        AdmArea_text = f"    <b>Округ:</b> {', '.join(user['cv']['location']['AdmArea'])}\n"
    else:
        AdmArea_text = ''
    if user['cv']['location'].get('District'):
        District_text = f"    <b>Район:</b> {', '.join(user['cv']['location']['District'])}\n"
    else:
        District_text = ''
    if user['cv']['location'].get('Station'):
        Station_text = f"    <b>Станция:</b> {', '.join(user['cv']['location']['Station'])}\n"
    else:
        Station_text = ''
    if user['cv']['location'].get('Line'):
        Line_text = f"    <b>Линия:</b> {', '.join(user['cv']['location']['Line'])}\n"
    else:
        Line_text = ''
    text = AdmArea_text + District_text + Station_text + Line_text
    return text

def firsttime_user(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if user['first_time']:
        return True
    else:
        return False


def get_sepcialisation(tg_id):
    user = dbase.db_client.users.find_one({'tg_id': tg_id})
    if len(user['cv']['specialisation']) == 0:
        specialisation = 'Специализация не выбрана'
    else:
        specialisation = ', '.join(user['cv']['specialisation'])
    return specialisation


if __name__ == '__main__':
    # make_location_file()
    files = os.listdir(path='images/125929447')
    for file in files:
        if '_0_' in file:
            file_name = file
    print(is_human_and_sfw(f'images/125929447/{file_name}'))
