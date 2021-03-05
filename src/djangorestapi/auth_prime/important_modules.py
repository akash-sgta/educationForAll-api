def logger(api_key, message):
    import logging
    logging.basicConfig(filename="api_access.log", filemode="w", format='%(asctime)s | %(message)s')
    logging.warning(f"{api_key} -> {message}")

# true call return
def TRUE_CALL(data=None, message=None):
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
def GET_INVALID(data=None):
    return {"return" : False, "code" : 403, "message" : 'ERROR-Invalid-GET Not supported'}

# JSONParser error
def JSON_PARSER_ERROR(data):
    return {"return" : False, "code" : 401, "message" : f"ERROR-Parsing-{str(data)}"}

# missing KEY
def MISSING_KEY(data):
    return {"return" : False, "code" : 402, "message" : f"ERROR-Key-{str(data)}"}

# invalid API
def API_RELATED(data):
    return {"return" : False, "code" : 115, "message" : f"ERROR-Key-{str(data)}"}

# error ambiguous 404
def AMBIGUOUS_404(data):
    return {"return" : False, "code" : 404, "message" : f"ERROR-Ambiguous-{str(data)}"}

# invalid action
def INVALID_ACTION(data):
    if(str(data).upper() == 'PARENT'):
        return {"return" : False, "code" : 403, "message" : "ERROR-Action-Child action invalid"}
    elif(str(data).upper() == 'CHILD'):
        return {"return" : False, "code" : 403, "message" : "ERROR-Action-Parent action invalid"}
    else:
        return {"return" : False, "code" : 403, "message" : f"ERROR-Action-{str(data).upper()} action invalid"}

# custom error reference
def CUSTOM_FALSE(code=None, message=None):
    if(code != None and message != None):
        return {"return" : False, "code" : code, "message" : f"ERROR-{message}"}
    else:
        return {"return" : False, "code" : None, "message" : "Custom_False:Admin"}
