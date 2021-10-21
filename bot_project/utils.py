import bot_project.settings
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
import requests
import json

# clarifai модель определяет объект на фото
model_object = 'aaa03c23b3724a16a56b629203edc62c'
# clarifai модель определяет контент для взрослых
model_safe = 'e9576d86d2004ed1a38ba0cf39ecb4b1'


# Функция проверяет что на картинке человек и нет контента для взрослых
def is_human_and_sfw(file_name):
    with open(file_name, "rb") as f:
        file_bytes = f.read()
    stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
    # This is how you authenticate.
    metadata = ((
        'authorization',
        f'Key {bot_project.settings.CLARIFAI_API_KEY}'),)
    request_safe = service_pb2.PostModelOutputsRequest(
        model_id=model_safe,
        inputs=[
            resources_pb2.Input(data=resources_pb2.Data(
                image=resources_pb2.Image(base64=file_bytes)
                ))
        ])
    request_people = service_pb2.PostModelOutputsRequest(
        model_id=model_object,
        inputs=[
            resources_pb2.Input(data=resources_pb2.Data(
                image=resources_pb2.Image(base64=file_bytes)
                ))
        ])
    response_safe = stub.PostModelOutputs(request_safe, metadata=metadata)
    response_people = stub.PostModelOutputs(request_people, metadata=metadata)
    if (response_safe.outputs[0].status.code == 10000
            and response_people.outputs[0].status.code == 10000):

        for concept in response_people.outputs[0].data.concepts:
            if concept.name == "people" and concept.value >= 0.7:
                for concept in response_safe.outputs[0].data.concepts:
                    if concept.name == "sfw" and concept.value >= 0.7:
                        return True
    return False


# Скачиваем базу округов, районов и метро, добавляем сокращенные наименования
def make_location_file():
    url = 'https://apidata.mos.ru/v1/datasets/1488/rows'
    params = {'api_key': bot_project.settings.MOS_API}
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


if __name__ == '__main__':
    # make_location_file()
    print(is_human_and_sfw('downloads/pi.jpg'))
