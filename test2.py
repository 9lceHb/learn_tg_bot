from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
import bot_project.settings
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
# This is how you authenticate.
metadata = (('authorization', f'Key {bot_project.settings.CLARIFAI_API_KEY}'),)

request = service_pb2.PostModelOutputsRequest(
    # This is the model ID of a publicly available General model. You may use any other public or custom model ID.
    model_id='aaa03c23b3724a16a56b629203edc62c',
    inputs=[
      resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(url='https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Redhead_Cat_%28%D0%A0%D1%8B%D0%B6%D0%B8%D0%B9_%D0%9A%D0%BE%D1%82%29.jpg/1280px-Redhead_Cat_%28%D0%A0%D1%8B%D0%B6%D0%B8%D0%B9_%D0%9A%D0%BE%D1%82%29.jpg')))
    ])
response = stub.PostModelOutputs(request, metadata=metadata)

if response.status.code != status_code_pb2.SUCCESS:
    print("There was an error with your request!")
    print("\tCode: {}".format(response.outputs[0].status.code))
    print("\tDescription: {}".format(response.outputs[0].status.description))
    print("\tDetails: {}".format(response.outputs[0].status.details))
    raise Exception("Request failed, status code: " + str(response.status.code))

for concept in response.outputs[0].data.concepts:
    print('%12s: %.2f' % (concept.name, concept.value))

