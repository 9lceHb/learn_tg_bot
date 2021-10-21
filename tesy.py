import bot_project.settings
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2


# clarifai модель определяет объект на фото
model_object = 'aaa03c23b3724a16a56b629203edc62c'


# Функция проверяет что на картинке человек и нет контента для взрослых
def is_human_and_sfw(file_name):
    with open(file_name, "rb") as f:
        file_bytes = f.read()
    stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
    # This is how you authenticate.
    metadata = ((
        'authorization',
        f'Key {bot_project.settings.CLARIFAI_API_KEY}'),)

    request_people = service_pb2.PostModelOutputsRequest(
        model_id=model_object,
        inputs=[
            resources_pb2.Input(data=resources_pb2.Data(
                image=resources_pb2.Image(base64=file_bytes)
                ))
        ])

    response_people = stub.PostModelOutputs(request_people, metadata=metadata)
    if response_people.outputs[0].status.code == 10000:

        for concept in response_people.outputs[0].data.concepts:
            if concept.name == "people" and concept.value >= 0.7:
                return True
    return False


print(is_human_and_sfw('downloads/pi.jpg'))