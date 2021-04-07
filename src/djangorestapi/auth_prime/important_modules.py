from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser

from auth_prime.models import (
        Api_Token_Table,
        User_Token_Table,
        Admin_Credential,
        Admin_Privilege,
        Admin_Cred_Admin_Prev_Int

    )

from hashlib import sha256
import string
import random

# --------------------------------------------------------

def am_I_Authorized(request, key):
    
    if(key.lower() == 'api'):
        try:
            headers = request.headers
            if('Authorization' in headers):
                token = headers['Authorization'].split()[1]
                api_token_ref = Api_Token_Table.objects.filter(user_key_private = token)
                if(len(api_token_ref) < 1):
                    return (False, "API_KEY_UNAUTHORIZED")
                else:
                    api_token_ref = api_token_ref[0]
                    return (True, api_token_ref.pk)
            else:
                return (False, "HTTP_Header_Mismatch - Authorization")
        except Exception as ex:
            print("EX : ", ex)
            return (False, "HTTP_Header_Mismatch - Authorization")
    
    elif(key.lower() == 'user'):
        try:
            headers = request.headers
            if('uauth' in headers):
                token = headers['uauth'].split()[1]
                user_token_ref = User_Token_Table.objects.filter(token_hash = token)
                if(len(user_token_ref) < 1):
                    return (False, "USER_HASH_UNAUTHORIZED")
                else:
                    user_token_ref = user_token_ref[0]
                    return (True, user_token_ref.user_credential_id.user_credential_id)
            else:
                return (False, "HTTP_Header_Mismatch - uauth")
        except Exception as ex:
            print("EX : ", ex)
            return (False, "HTTP_Header_Mismatch - uauth")
    
    elif(key.lower() == 'admin'): # todo
        try:
            headers = request.headers
            if('uauth' in headers):
                token = headers['uauth'].split()[1]
                user_token_ref = User_Token_Table.objects.filter(token_hash = token)
                if(len(user_token_ref) < 1):
                    return 0
                else:
                    user_token_ref = user_token_ref[0]
                    admin_cred_ref = Admin_Credential.objects.filter(
                                        user_credential_id = user_token_ref.user_credential_id.user_credential_id
                                    )
                    if(len(admin_cred_ref) < 1):
                        return 0
                    else:
                        if(admin_cred_ref[0].prime == False):
                            return 2
                        else:
                            return 3 # for now, later check admin level
            else:
                return 0
                
        except Exception as ex:
            print("EX : ", ex)
            return 0

def do_I_Have_Privilege(request, key):

    try:
        headers = request.headers
        if('uauth' in headers):
            token = headers['uauth'].split()[1]
            user_token_ref = User_Token_Table.objects.filter(token_hash = token)
            if(len(user_token_ref) < 1):
                return False
            else:
                user_token_ref = user_token_ref[0]
                admin_cred_ref = Admin_Credential.objects.filter(
                                    user_credential_id = user_token_ref.user_credential_id.user_credential_id
                                )
                if(len(admin_cred_ref) < 1):
                        return False
                else:
                    privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name = key.upper())
                    if(len(privilege_ref) < 1):
                        return False
                    else:
                        many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(
                                            admin_credential_id = admin_cred_ref[0].admin_credential_id,
                                            admin_privilege_id = privilege_ref[0].admin_privilege_id
                                        )
                        if(len(many_to_many_ref) < 1):
                            return False
                        else:
                            return True
        else:
            return False
    except Exception as ex:
        print("EX : ", ex)
        return False

def create_password_hashed(password):
    sha256_ref = sha256()
    sha256_ref.update(f"ooga{password}booga".encode('utf-8'))
    return str(sha256_ref.digest())

def random_generator(length=64):
    password_characters = string.ascii_letters + string.digits
    password = list()
    for x in range(length):
        password.append(random.choice(password_characters))
        
    return "".join(password)

def create_token(user_cred_ref):
    user_token_ref = User_Token_Table.objects.filter(user_credential_id = user_cred_ref.user_credential_id)
    if(len(user_token_ref) < 1):
        user_token_ref = User_Token_Table(
            user_credential_id = user_cred_ref,
            token_hash = random_generator()
        )
        user_token_ref.save()
    else:
        user_token_ref = user_token_ref[0]
    return user_token_ref.token_hash

# --------------------------------------------------------

def logger(api_key, message):
    import logging
    logging.basicConfig(filename="api_access.log", filemode="w", format='%(asctime)s | %(message)s')
    logging.warning(f"{api_key} -> {message}")
