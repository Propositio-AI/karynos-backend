import json
from shared.utils.file import readJson

def request_deserializer(data: bytes):
    return json.loads(data.decode())

def response_serializer(obj):
    return json.dumps(obj).encode()


def readConfig():
    response = readJson("./shared/lib/gRPC/grpc.json")
    if response["success"]:
        return response["data"]
    raise RuntimeError("\n".join(response["message"]))