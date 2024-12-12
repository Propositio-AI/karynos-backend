import uuid

class User:
    def __init__(self):
       self.userID_list = []
       self.request_list = {}

    def open_user(self, userID):
        self.userID_list.append(userID)
        return "success"
    
    def open_request(self, rcv_data):
        userID = rcv_data["id"]
        if userID in self.userID_list:
            request_ID = uuid.uuid1()
            self.request_list[request_ID] = {
                "userID":userID,
                "request_message":rcv_data["message"],
                "execution":"running",
                "data":{
                    "archiDraft":{},
                    "response":[]
                }
            }
            ai_send_data = {
                "type":"message",
                "request_ID":request_ID,
                "data":{
                    "message":rcv_data["message"]
                    }
                }
            return ai_send_data
        else:
            return "error"
        
    def response_save(self, rcv_data):
        request_ID = rcv_data["request_ID"]
        match rcv_data["type"]:
            case "respons":
                self.request_list[request_ID]["data"]["response"].append(rcv_data["data"])
                web_send_data = {
                    "type":"response",
                    "status":"success",
                    "id":self.request_list[request_ID]["userID"],
                    "message":"",
                    "data":rcv_data["data"]
                }
                return web_send_data
            case "archiDraft":
                self.request_list[request_ID]["data"]["archiDraft"] = rcv_data["data"]
                web_send_data = {
                    "type":"archiDraft",
                    "status":"success",
                    "id":self.request_list[request_ID]["userID"],
                    "message":"",
                    "data":rcv_data["data"]
                }
                return web_send_data
            case "endResponse":
                self.request_list[request_ID]["execution"] = "done"
                web_send_data = {
                    "type":"endResponse",
                    "status":"success",
                    "id":self.request_list[request_ID]["userID"],
                    "message":"",
                }
                return web_send_data