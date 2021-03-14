from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser

def logger(api_key, message):
    import logging
    logging.basicConfig(filename="api_access.log", filemode="w", format='%(asctime)s | %(message)s')
    logging.warning(f"{api_key} -> {message}")

class Json_Forward(object):

    def __init__(self):
        super().__init__()
    
    # true call return
    def TRUE_CALL(self, data=None, message=None):
        if(data != None):
            if(message != None):
                return {"return" : True, "code" : 100, "data" : data, "message" : message}
            else:
                return {"return" : True, "code" : 100, "data" : data}
        elif(message != None):
            return {"return" : True, "code" : 100, "message" : message}
        else:
            return {"return" : True, "code" : 100}

    # invalid GET method
    def GET_INVALID(self, data=None):
        return {"return" : False, "code" : 403, "message" : 'ERROR-Invalid-GET Not supported'}

    # JSONParser error
    def JSON_PARSER_ERROR(self, data):
        return {"return" : False, "code" : 401, "message" : f"ERROR-Parsing-{str(data)}"}

    # missing KEY
    def MISSING_KEY(self, data):
        return {"return" : False, "code" : 402, "message" : f"ERROR-Key-{str(data)}"}

    # invalid API
    def API_RELATED(self, data):
        return {"return" : False, "code" : 115, "message" : f"ERROR-Key-{str(data)}"}

    # error ambiguous 404
    def AMBIGUOUS_404(self, data):
        return {"return" : False, "code" : 404, "message" : f"ERROR-Ambiguous-{str(data)}"}

    # invalid action
    def INVALID_ACTION(self, data):
        if(str(data).upper() == 'PARENT'):
            return {"return" : False, "code" : 403, "message" : "ERROR-Action-Child action invalid"}
        elif(str(data).upper() == 'CHILD'):
            return {"return" : False, "code" : 403, "message" : "ERROR-Action-Parent action invalid"}
        else:
            return {"return" : False, "code" : 403, "message" : f"ERROR-Action-{str(data).upper()} action invalid"}

    # custom error reference
    def CUSTOM_FALSE(self, code=None, message=None):
        if(code != None and message != None):
            return {"return" : False, "code" : code, "message" : f"ERROR-{message}"}
        else:
            return {"return" : False, "code" : None, "message" : "Custom_False:Admin"}

class API_Prime(Json_Forward):

    def __init__(self):
        super().__init__()
        self.__request = None
        self.__data_returned = dict()
        self.json_response = JsonResponse({"return" : False, "message" : "Action not permitted"}, safe=True)
    
    @property
    def request(self):
        return self.__request
    @request.setter
    def request(self, data):
        self.__request = data
    
    @property
    def data_returned(self):
        return self.__data_returned
    @data_returned.setter
    def data_returned(self, data):
        self.__data_returned = data
    
    def method_get(self):
        return JsonResponse(self.GET_INVALID(), safe=True)
    
    def create(self, *args, **kwargs):
        return self.json_response
    
    def read(self, *args, **kwargs):
        return self.json_response
    
    def edit(self, *args, **kwargs):
        return self.json_response
    
    def delete(self, *args, **kwargs):
        return self.json_response
    
    def method_post(self):
        try:
            user_data = JSONParser().parse(self.request)

        except Exception as ex:
            return JsonResponse(self.JSON_PARSER_ERROR(ex), safe=True)
                
        else:
            try:
                incoming_api = user_data["api"]
                incoming_data = user_data["data"]
                # print(incoming_data)

            except Exception as ex:
                return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
            else:
                self.api = incoming_api
                data = self.check_authorization(api_check=True)
                if(data[0] == False):
                    return JsonResponse(self.API_RELATED(data[1]), safe=True)

                else:
                    try:
                        child_method = incoming_data["action"].upper()
                        if(child_method == "CREATE"):
                            return self.create(incoming_data)
                        
                        elif(child_method == 'READ'):
                            return self.read(incoming_data)
                        
                        elif(child_method == 'EDIT'):
                            return self.edit(incoming_data)
                        
                        elif(child_method == 'DELETE'):
                            return self.delete(incoming_data)

                        else:
                            return JsonResponse(self.INVALID_ACTION('child'), safe=True)
                    
                    except Exception as ex:
                        return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)

    @csrf_exempt
    def run(self, request = None):
        if(request == None):
            raise Exception('[request] not passed as argument')
 
        else:
            self.request = request
            parent_method = self.request.method.upper()
            self.data_returned['action'] = parent_method
            if(parent_method == 'GET'):
                return self.method_get()

            elif(parent_method == 'POST'):
                return self.method_post()

            else:
                return JsonResponse(self.INVALID_ACTION('parent'), safe=True)

    def __str__(self):
        return super().__str__()
