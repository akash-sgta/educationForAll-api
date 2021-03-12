from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

import re
import json
import os
from overrides import overrides

# --------------------------------------------------------------------------

from auth_prime.models import User_Credential
from auth_prime.models import User_Profile
from auth_prime.models import Admin_Privilege
from auth_prime.models import Admin_Credential
from auth_prime.models import Admin_Cred_Admin_Prev_Int
from auth_prime.models import User_Token_Table
from auth_prime.models import Api_Token_Table
from auth_prime.models import Image

from auth_prime.serializer import User_Credential_Serializer
from auth_prime.serializer import User_Profile_Serializer
from auth_prime.serializer import Admin_Privilege_Serializer
from auth_prime.serializer import Admin_Credential_Serializer

from auth_prime.authorize import Authorize
from auth_prime.authorize import Cookie

from auth_prime.important_modules import API_Prime

# --------------------------------------------------------------------------

# -------------------------------API_SPACE-------------------------------------

class User_Credential_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()

    def signup(self, incoming_data):
        # print(self.data_returned)
        self.data_returned['action'] += "-SIGNUP"
        self.clear()
        try:
            incoming_data = incoming_data["data"]
            # print(incoming_data)
            incoming_data = incoming_data["data"]
            user_credential_de_serialized = User_Credential_Serializer(data = incoming_data)
                                    
        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                                    
        else:
            user_credential_de_serialized.initial_data['user_email'] = user_credential_de_serialized.initial_data['user_email'].lower()
            user_credential_ref = User_Credential.objects.filter(user_email = user_credential_de_serialized.initial_data['user_email'])
            if(len(user_credential_ref) > 0):
                return JsonResponse(self.CUSTOM_FALSE(104, "NonReusableValue-Email already registered"), safe=True)
                                            
            else:
                try:
                    self.user_email = user_credential_de_serialized.initial_data['user_email']
                    self.user_password = user_credential_de_serialized.initial_data['user_password']

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(407, f"Formatting-{str(ex)}"), safe=True)
                                            
                else:
                    data = self.create_password_hashed()
                    if(data[0] == False):
                        return JsonResponse(self.AMBIGUOUS_404(data[1]), safe=True)

                    else:
                        user_credential_de_serialized.initial_data['user_password'] = data[1] # successfully hashed password
                        if(user_credential_de_serialized.is_valid()):
                            user_credential_de_serialized.save()
                            data = self.sanction_authorization()
                            if(data[0] == False):
                                return JsonResponse(self.AMBIGUOUS_404(data[1]), safe=True)
                                                            
                            else:
                                self.data_returned = self.TRUE_CALL(data = {'hash' : data[1], "user" : user_credential_de_serialized.data['user_credential_id']})

                        else:
                            return JsonResponse(self.CUSTOM_FALSE(405, f"Serializing-{user_credential_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    def signin(self, incoming_data):
        self.data_returned['action'] += "-SIGNIN"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            incoming_data = incoming_data['data']
            self.user_email = incoming_data['user_email'].lower()
            self.user_password = incoming_data['user_password']
        
        except Exception as ex:
            return JsonResponse(self.CUSTOM_FALSE(407, f"Formatting-{str(ex)}"), safe=True)
                            
        else:
            data = self.sanction_authorization()
            if(data[0] == False):
                return JsonResponse(self.AMBIGUOUS_404(data[1]), safe=True)

            else:
                self.data_returned = self.TRUE_CALL({'hash' : data[1]})

            return JsonResponse(self.data_returned, safe=True)

    def signout(self, incoming_data):
        self.data_returned['action'] += "-SIGNOUT"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
                            
        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                            
        else:
            if('user_id' not in incoming_data.keys()): # user logging out self
                data = self.check_authorization("user")

                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not User"), safe=True)

                else:
                    token_table_ref = User_Token_Table.objects.filter(user_credential_id = int(data[1]))
                    token_table_ref = token_table_ref[0]
                    token_table_ref.delete()

                    self.data_returned = self.TRUE_CALL()
                    
            else: # admin + alpha deleting all or selected logins
                data = self.check_authorization("admin", "alpha")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(111, data[1]), safe=True)
                                    
                else:
                    try:
                        user_ids = tuple(set(incoming_data['user_id']))
                                                
                    except Exception as ex:
                        return JsonResponse(self.MISSING_KEY(ex), safe=True)
                                                
                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()

                        if(0 in user_ids):
                            user_token_ref_all = User_Token_Table.objects.all().exclude(user_credential_id = int(data[1])) # force logout everyone except self
                            if(len(user_token_ref_all) < 1):
                                self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-User Token tray empty")
                                                        
                            else:
                                user_token_ref_all.delete()
                                self.data_returned['data'][0] = self.TRUE_CALL()
                                            
                        else:                                            
                            for id in user_ids:
                                try:
                                    token_table_ref = User_Token_Table.objects.filter(user_credential_id = int(id))
                                                            
                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"Data Type-{str(ex)}")
                                                            
                                else:
                                    if(len(token_table_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")

                                    else:
                                        token_table_ref = token_table_ref[0]
                                        token_table_ref.delete()
                                        self.data_returned['data'][id] = self.TRUE_CALL()
                    
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
                            
        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                            
        else:
            if('user_id' not in incoming_data.keys()): # self fetch
                data = self.check_authorization("user")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, "Hash-Not USER"), safe=True)

                else:
                    user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                    self.data_returned = self.TRUE_CALL(User_Credential_Serializer(user_credential_ref, many=False).data)
                    # initially not handed to user for security purposes
                    del(self.data_returned['data']['user_password'])
                    del(self.data_returned['data']["user_security_question"])
                    del(self.data_returned['data']["user_security_answer"])
                    
            else: # fetching as an admin+alpha
                self.data_returned['data'] = dict()
                temp = dict()
                data = self.check_authorization("admin", "alpha")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(113, f"Hash-{data[1]}"), safe=True)

                else:
                    user_ids = tuple(set(incoming_data['user_id']))
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-At least one id required"), safe=True)
                                                
                    else:
                        if(0 in user_ids): # 0 -> fetch all
                            user_credential_ref = User_Credential.objects.all().order_by("-user_credential_id")
                            if(len(user_credential_ref) < 1):
                                self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-User Credential tray empty")
                                return JsonResponse(self.data_returned, safe=True)
                                            
                            else:
                                user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=True).data
                                for user in user_credential_serialized:
                                    key = int(user['user_credential_id'])
                                    temp[key] = user
                                    # not provided to admin as well, security reasons
                                    del(temp[key]['user_password'])
                                    del(temp[key]["user_security_question"])
                                    del(temp[key]["user_security_answer"])

                                self.data_returned = self.TRUE_CALL(temp.copy())
                                temp.clear()
                                        
                        else: # fetch using using ids
                            for id in user_ids:
                                try:
                                    user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                            
                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"Formatting-{str(ex)}")
                                                            
                                else:
                                    if(len(user_credential_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")

                                    else:
                                        user_credential_ref = user_credential_ref[0]
                                        user_credential_serialized = User_Credential_Serializer(user_credential_ref, many=False).data
                                        self.data_returned['data'][id] = self.TRUE_CALL(user_credential_serialized)
                                        # not provided to admin as well, security reasons
                                        del(self.data_returned['data'][id]['data']['user_password'])
                                        del(self.data_returned['data'][id]['data']["user_security_question"])
                                        del(self.data_returned['data'][id]['data']["user_security_answer"])

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def edit(self, incoming_data):
        self.data_returned['action'] += "-EDIT"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
                            
        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                            
        else:
            data = self.check_authorization("user") # only self change applicable for now
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, f"Hash-{data[1]}"), safe=True)

            else:
                user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))            
                user_credential_de_serialized = User_Credential_Serializer(user_credential_ref,
                                                                            data = incoming_data['data'])
                        
                if("user_email" in user_credential_de_serialized.initial_data.keys()):
                    email_temp = user_credential_de_serialized.initial_data['user_email'].lower()
                    user_credential_ref_temp = User_Credential.objects.filter(user_email = email_temp)
                    if(len(user_credential_ref_temp) > 0):
                        user_credential_ref_temp = user_credential_ref_temp[0]
                        if(user_credential_ref_temp.user_credential_id != user_credential_ref.user_credential_id):
                            return JsonResponse(self.CUSTOM_FALSE(104, "Non Reusable-Email reused"), safe=True)
                                
                        else:
                            pass
                            
                    else:
                        pass

                # email_temp = user_credential_ref.user_email.lower()
                user_credential_de_serialized.initial_data['user_email'] = email_temp
                # necessary fields for serializer but can not be given permission to user
                user_credential_de_serialized.initial_data['user_password'] = user_credential_ref.user_password
                # user_credential_de_serialized.initial_data['user_security_question'] = user_credential_ref.user_security_question
                # user_credential_de_serialized.initial_data['user_security_answer'] = user_credential_ref.user_security_answer
                if(user_credential_de_serialized.is_valid()):
                    user_credential_de_serialized.save()
                    self.data_returned = self.TRUE_CALL({"user" : user_credential_de_serialized.data['user_credential_id']})
                
                else:
                    return JsonResponse(self.CUSTOM_FALSE(405, f"Serializer-{user_credential_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
                            
        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                            
        else:
            if('user_id' in incoming_data.keys()): # prime admin deleting others
                self.data_returned['data'] = dict()
                data = self.check_authorization("admin", "alpha")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(111, data[1]), safe=True)
                                    
                else:
                    user_ids = tuple(set(incoming_data['user_id']))
                    if(0 in user_ids): # 0 -> delete all
                        user_credential_ref_all = User_Credential.objects.all().exclude(user_credential_id = int(data[1]))
                        if(len(user_credential_ref_all) < 1):
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-USER CREDENTIAL not found")
                            return JsonResponse(self.data_returned, safe=True)
                                        
                        else:
                            user_credential_ref_all.delete()
                            self.data_returned['data'][0] = self.TRUE_CALL()
                                    
                    else: # individual id deletes
                        for id in user_ids:
                            try:
                                if(int(id) == int(data[1])):
                                    self.data_returned['data'][id] = self.AMBIGUOUS_404("Empty-USER CREDENTIAL not found")

                                else:
                                    try:
                                        user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                    
                                    except Exception as ex:
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"Data Type-{str(ex)}")
                                                    
                                    else:
                                        if(len(user_credential_ref) < 1):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")
                                                        
                                        else:
                                            user_credential_ref = user_credential_ref[0]
                                            user_credential_ref.delete()
                                            self.data_returned['data'][id] = self.TRUE_CALL()
                                            
                            except Exception as ex:
                                self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                                                        
            else: # user self delete
                data = self.check_authorization("user")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, f"Hash-{data[1]}"), safe=True)

                else:
                    user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                    if(user_credential_ref.user_profile_id not in (None, "")):
                        user_credential_ref.user_profile_id.delete()

                    user_credential_ref.delete()
                    self.data_returned = self.TRUE_CALL()
            
            return JsonResponse(self.data_returned, safe=True)

    @overrides
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
                        if(child_method == "SIGNUP"):
                            return self.signup(incoming_data)
                        
                        elif(child_method in ("SIGNIN", "LOGIN")):
                            return self.signin(incoming_data)
                        
                        elif(child_method in ("SIGNOUT", "LOGOUT")):
                            return self.signout(incoming_data)
                        
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

class User_Profile_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()

    @overrides
    def create(self, incoming_data):
        self.data_returned['action'] += "-CREATE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-Not USER"), safe=True)

            else:
                user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                if(user_credential_ref.user_profile_id in (None, "")):
                    try:
                        user_profile_de_serialized = User_Profile_Serializer(data = incoming_data['data'])

                    except Exception as ex:
                        return JsonResponse(self.JSON_PARSER_ERROR(ex), safe=True)
                                        
                    else:
                        if(("prime" in user_profile_de_serialized.initial_data.keys()) and (user_profile_de_serialized.initial_data["prime"] == True)): # if student then roll number required
                            if(("user_roll_number" in user_profile_de_serialized.initial_data.keys()) and (user_profile_de_serialized.initial_data["user_roll_number"] in (None, ""))):
                                return JsonResponse(self.MISSING_KEY("Student profile required roll number"), safe=True)
                        
                        if(user_profile_de_serialized.is_valid()):
                            user_profile_de_serialized.save()
                            user_profile_ref = User_Profile.objects.get(user_profile_id = user_profile_de_serialized.data['user_profile_id'])
                            user_credential_ref.user_profile_id = user_profile_ref
                            user_credential_ref.save()
                            self.data_returned = self.TRUE_CALL({"user" : user_credential_ref.user_credential_id, "profile" : user_profile_ref.user_profile_id})

                        else:
                            return JsonResponse(self.CUSTOM_FALSE(405, f"Serialize-{user_profile_de_serialized.errors}"), safe=True)
                    
                else:
                    return JsonResponse(self.CUSTOM_FALSE(105, "Create-Profile exists"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                        
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                    
            else:
                self_user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                if('user_id' in incoming_data.keys()): # user fetching other user_profiles
                    self.data_returned['data'] = dict()
                    temp = dict()
                    user_ids = tuple(set(incoming_data['user_id']))
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                            
                    else:
                        if(0 in user_ids): # all at once
                            user_profile_ref = User_Profile.objects.all()
                            if(len(user_profile_ref) < 1):
                                self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Already empty tray of USER PROFILES")
                                return JsonResponse(self.data_returned, safe=True)
                                                        
                            else:
                                user_profile_serialized = User_Profile_Serializer(user_profile_ref, many=True).data
                                self.data_returned['data'][0] = dict()
                                for user in user_profile_serialized:
                                    key = int(user['user_profile_id'])
                                    if(user['user_profile_pic'] in (None, "")):
                                        user['user_profile_pic'] = None
                                    else:
                                        user['user_profile_pic'] = Image.objects.get(image_id = int(user['user_profile_pic'])).image_url
                                    self.data_returned['data'][0][key] = user
                                                        
                        else: # individual id_profile fetch
                            for id in user_ids:
                                try:
                                    user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                                            
                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                else:
                                    if(len(user_credential_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")
                                                                
                                    else:
                                        user_credential_ref = user_credential_ref[0]
                                        if(user_credential_ref.user_profile_id in (None, "")):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(106, "NotFound-USER PROFILE")

                                        else:
                                            user_profile_serialized = User_Profile_Serializer(user_credential_ref.user_profile_id, many=False).data
                                            if(user_profile_serialized['user_profile_pic'] in (None, "")):
                                                user_profile_serialized['user_profile_pic'] = None
                                            else:
                                                user_profile_serialized['user_profile_pic'] = Image.objects.get(image_id = int(user_profile_serialized['user_profile_pic'])).image_url

                                            self.data_returned['data'][id] = self.TRUE_CALL(data = user_profile_serialized)
                                        
                else: # self fetch profile
                    if(self_user_credential_ref.user_profile_id == None):
                        return JsonResponse(self.CUSTOM_FALSE(106, "NotFound-USER PROFILE"), safe=True)
                                            
                    else:
                        self_user_profile_ref = User_Profile.objects.get(user_profile_id = int(self_user_credential_ref.user_profile_id.user_profile_id))
                        print(self_user_profile_ref)
                        user_profile_serialized = User_Profile_Serializer(self_user_profile_ref, many=False).data
                        if(user_profile_serialized['user_profile_pic'] in (None, "")):
                            user_profile_serialized['user_profile_pic'] = None
                        else:
                            user_profile_serialized['user_profile_pic'] = Image.objects.get(image_id = int(user_profile_serialized['user_profile_pic'])).image_url
                        self.data_returned = self.TRUE_CALL(data = {"user" : self_user_credential_ref.user_credential_id, "profile" : user_profile_serialized})

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def edit(self, incoming_data):
        self.data_returned['action'] += "-EDIT"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            incoming_data = incoming_data['data']

        except Exception as ex:
            return JsonResponse(self.CUSTOM_FALSE(402, f"Parsing-{str(ex)}"), safe=True)
                        
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

            else:
                self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id
                if(self_user_profile_ref == None):
                    return JsonResponse(self.CUSTOM_FALSE(106, "NotFound-USER PROFILE"), safe=True)
                                        
                else:
                    try:
                        user_profile_de_serialized = User_Profile_Serializer(self_user_profile_ref, data = incoming_data)

                    except Exception as ex:
                        return JsonResponse(self.CUSTOM_FALSE(405, f"Serialize-{str(ex)}"), safe=True)

                    else:
                        if(("prime" in user_profile_de_serialized.initial_data.keys()) and (user_profile_de_serialized.initial_data["prime"] == True)): # if student then roll number required
                            if(("user_roll_number" in user_profile_de_serialized.initial_data.keys()) and (user_profile_de_serialized.initial_data["user_roll_number"] in (None, ""))):
                                return JsonResponse(self.MISSING_KEY("Key-Student profile required roll number"), safe=True)
                            
                        user_profile_de_serialized.initial_data["user_profile_id"] = self_user_profile_ref.user_profile_id
                        if(user_profile_de_serialized.is_valid()):
                            user_profile_de_serialized.save()
                            if(user_profile_de_serialized.data['user_profile_pic'] in (None, "")):
                                message = "SUCCESS-Edit-PROFILE without IMAGE"
                            else:
                                message = "SUCCESS-Edit-PROFILE with IMAGE"
                            self.data_returned = self.TRUE_CALL(message = message)

                        else:
                            return JsonResponse(self.CUSTOM_FALSE(405, f"Serialize-{user_profile_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):

        def delete_image(data):
            try:
                image = data
                fs = FileSystemStorage('uploads/image')
                if(fs.exists(image.image_name)):
                    fs.delete(image.image_name)
                image.delete()
            
            except:
                return False
            
            else:
                return True

        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.JSON_PARSER_ERROR(ex), safe=True)
                        
        else:
            data = self.check_authorization("user") # redundant, but code already became large, will see to it later
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-Not USER"), safe=True)
                                    
            else:
                if('user_id' in incoming_data.keys()): # admin deleting other users(-1) profile
                    self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id
                    data = self.check_authorization("admin", "alpha")
                    if(data[0] == False):
                        return JsonResponse(self.CUSTOM_FALSE(113, f"Hash-{data[1]}"), safe=True)

                    else:
                        user_ids = tuple(set(incoming_data['user_id']))
                        if(len(user_ids) < 1):
                            return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                                        
                        else:
                            self.data_returned['data'] = dict()
                            temp = dict()
                            if(0 in user_ids): # all at once

                                if(self_user_profile_ref not in (None, "")):
                                    user_profile_ref_all = User_Profile.objects.all().exclude(user_profile_id = int(self_user_profile_ref.user_profile_id))
                                else:
                                    user_profile_ref_all = User_Profile.objects.all()

                                if(len(user_profile_ref_all) < 1):
                                    self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Profile Tray")
                                    return JsonResponse(self.data_returned, safe=True)
                                                                
                                else:
                                    for user in user_profile_ref_all:
                                        if(user.user_profile_pic in (None, "")):
                                            pass
                                        else:
                                            if(delete_image(user.user_profile_pic)):
                                                pass
                                        user.delete()
                                    self.data_returned['data'][0] = self.TRUE_CALL()

                            else: # individual id_profile delete
                                for id in user_ids:
                                    try:
                                        user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))

                                    except Exception as ex:
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                                                    
                                    else:
                                        if(len(user_credential_ref) < 1):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")
                                                                        
                                        else:
                                            user_credential_ref = user_credential_ref[0]
                                            if(user_credential_ref.user_profile_id in (None, "")):
                                                self.data_returned['data'][id] = self.CUSTOM_FALSE(106, "NotFound-PROFILE does not exist")
                                                                            
                                            else:
                                                if(self_user_profile_ref == user_credential_ref.user_profile_id):
                                                    message = "SUCCESS-Delete-self profile"

                                                else:
                                                    message = None
                                                
                                                if(user_credential_ref.user_profile_id.user_profile_pic in (None, "")):
                                                    pass
                                                else:
                                                    if(delete_image(user_credential_ref.user_profile_id.user_profile_pic)):
                                                        pass
                                                
                                                user_credential_ref.user_profile_id.delete()

                                                if(message == None):
                                                    self.data_returned['data'][id] = self.TRUE_CALL()
                                                else:
                                                    self.data_returned['data'][id] = self.TRUE_CALL(message = message)

                else: # self deleting profile
                    self_user_profile_ref = User_Credential.objects.get(user_credential_id = int(data[1])).user_profile_id
                    if(self_user_profile_ref == None):
                        print("here1")
                        return JsonResponse(self.CUSTOM_FALSE(106, "NotFound-PROFILE does not exist"), safe=True)

                    else:
                        print("here2")
                        if(self_user_profile_ref.user_profile_pic in (None, "")):
                            pass
                        else:
                            if(delete_image(self_user_profile_ref.user_profile_pic)):
                                pass
                        self_user_profile_ref.delete()
                        self.data_returned = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Image_Api(API_Prime):

    def __init__(self):
        super().__init__()

    @overrides
    def create(self):
        self.data_returned['action'] += "-CREATE"
        # self.clear()
        if('auth' not in self.request.POST.keys()):
            return False, "Value-No api auth token found"
        
        else:
            auth = self.request.POST.get('auth')
            api_token_ref = Api_Token_Table.objects.filter(user_key_private = auth)
            if(len(api_token_ref) < 1):
                return False, "Api-Not Registered"
            
            else:
                api_token_ref = api_token_ref[0]
                if(len(self.request.FILES) < 1):
                    return False, "Value-No files found"
                else:
                    image_file = self.request.FILES['image']
                    if(str(image_file.content_type).startswith("image")):
                        if(image_file.size < 5000000):
                            if not os.path.exists('uploads/images'):
                                os.makedirs('uploads/images')

                            fs = FileSystemStorage('uploads/images')
                            file_name = fs.save(image_file.name, image_file)
                            file_url = fs.url(file_name)
                            image_ref = Image(image_url = file_url, image_name = file_name)
                            image_ref.save()
                            return True, image_ref.image_id

                        else:
                            return False, "Size-Image size should be less than 5mb"
                    else:
                        return False, "Format-POST file should be Image"

    @overrides
    def delete(self):
        self.data_returned['action'] += "-DELETE"
        # self.clear()
        if('auth' not in self.request.POST.keys()):
            return False, "Value-No api auth token found"
        
        else:
            auth = self.request.POST.get('auth')
            api_token_ref = Api_Token_Table.objects.filter(user_key_private = auth)
            if(len(api_token_ref) < 1):
                return False, "Api-Not Registered"
            
            else:
                api_token_ref = api_token_ref[0]
                if('image_id' not in self.request.POST.keys()):
                    return False, "image_id key required"
        
                else:
                    try:
                        id = int(self.request.POST.get('image_id'))
                    
                    except Exception as ex:
                        return False, f"DataType-{str(ex)}"
            
                    else:
                        image_ref = Image.objects.filter(image_id = id)
                        if(len(image_ref) < 1):
                            return False, f"-Invalid-image id"
                
                        else:
                            image_ref = image_ref[0]
                            fs = FileSystemStorage('uploads/images')
                            if(fs.exists(image_ref.image_name)):
                                fs.delete(image_ref.image_name)
                                image_ref.delete()

                                return True, None
                            
                            else:
                                return False, "Invalid-Image name"

    @overrides
    def method_post(self):
        try:
            action = self.request.POST.get('action')
        
        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
        
        else:
            child_method = action.upper()
            if(child_method == 'CREATE'):
                returned, message = self.create()
                if(returned == True):
                    self.data_returned = self.TRUE_CALL(data = {"image" : message})

                else:
                    return JsonResponse(self.AMBIGUOUS_404(message), safe=True)
        
            elif(child_method == 'DELETE'):
                returned, message = self.delete()
                if(returned == True):
                    self.data_returned = self.TRUE_CALL()

                else:
                    return JsonResponse(self.AMBIGUOUS_404(message), safe=True)

            else:
                return JsonResponse(self.INVALID_ACTION('child'), safe=True)

            return JsonResponse(self.data_returned, safe=True)

class Admin_Credential_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()

    @overrides
    def create(self, incoming_data):
        self.data_returned['action'] += "-CREATE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("admin", "prime") #only prime admins can grant admin access
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(110, "Hash-not have ADMIN PRIME"), safe=True)
                                
            else:
                if('user_id' in incoming_data.keys()): # only this method of admin inclusion accepted
                    self.data_returned['data'] = dict()
                    temp = dict()
                    for id in incoming_data['user_id']:
                        try:
                            if(int(data[1]) == int(id)):
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(112, "Operation-USER already ADMIN")
                                        
                            else:
                                user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                if(len(user_credential_ref) < 1):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")

                                else:
                                    try:
                                        user_credential_ref = user_credential_ref[0]
                                        admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(user_credential_ref.user_credential_id))

                                    except Exception as ex:
                                        self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                                    
                                    else:
                                        if(len(admin_credential_ref) > 0):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(112, "Operation-USER already ADMIN")
                                        
                                        else:
                                            admin_credential_ref_new = Admin_Credential(user_credential_id = user_credential_ref)
                                            admin_credential_ref_new.save()
                                            self.data_returned['data'][id] = self.TRUE_CALL(data = {"user" : user_credential_ref.user_credential_id, "admin" : admin_credential_ref_new.data['admin_credential_id']})

                        except Exception as ex:
                            self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                            
                else:
                    return JsonResponse(self.MISSING_KEY("user_id field required"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            if('user_id' in incoming_data.keys()): # admin prime fetching others admin details
                data = self.check_authorization("admin", "prime") #only prime admins can fetch admin access from others
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(110, "Hash-not ADMIN PRIME"), safe=True)

                else:
                    user_ids = tuple(incoming_data['user_id'])
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                        
                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()
                        if(0 in user_ids):
                            admin_credential_ref_all = Admin_Credential.objects.all()
                            if(len(admin_credential_ref_all) < 1):
                                self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-ADMIN Tray is empty")
                                return JsonResponse(self.data_returned, safe=True)
                                                
                            else:
                                self.data_returned['data'][0] = list()
                                admin_credential_all_serialized = Admin_Credential_Serializer(admin_credential_ref_all, many=True).data
                                for admin in admin_credential_all_serialized:
                                    # if(admin['user_credential_id'] == int(data[1])):
                                    #     key = "self"
                                    # else:
                                    #     key = admin['user_credential_id']                                            
                                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin['admin_credential_id'])
                                    if(len(many_to_many_ref) < 1):
                                        privileges = None
                                    else:
                                        privileges = list()
                                        for mtmr in many_to_many_ref:
                                            privileges.append(mtmr.admin_privilege_id.admin_privilege_id)
                                    self.data_returned['data'][0].append({"admin" : admin, "privilege" : privileges})
                                self.data_returned['data'][0] = self.TRUE_CALL(data = self.data_returned['data'][0])
                                            
                        else:
                            temp = dict()
                            for id in user_ids: # self fetch allowed this way SECURITY CHECK
                                try:
                                    user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))

                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, "DataType-{str(ex)}")
                                
                                else:
                                    if(len(user_credential_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")

                                    else:
                                        try:
                                            user_credential_ref = user_credential_ref[0]
                                            admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(user_credential_ref.user_credential_id))
                                
                                        except Exception as ex:
                                            self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                                                    
                                        else:
                                            if(len(admin_credential_ref) < 1):
                                                self.data_returned['data'][id] = self.CUSTOM_FALSE(113, "Invalid-USER not ADMIN")

                                            else:
                                                admin_credential_ref = admin_credential_ref[0]
                                                admin_credential_serialized = Admin_Credential_Serializer(admin_credential_ref, many=False).data
                                                many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_serialized['admin_credential_id'])
                                                if(len(many_to_many_ref) < 1):
                                                    privileges = None
                                                else:
                                                    privileges = list()
                                                    for mtmr in many_to_many_ref:
                                                        privileges.append(mtmr.admin_privilege_id.admin_privilege_id)
                                                self.data_returned['data'][id] = self.TRUE_CALL(data = {"admin" : admin_credential_serialized, "privilege" : privileges})
                                    
            else: # self fetch
                data = self.check_authorization("admin")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(114, "Hash-not ADMIN"), safe=True)

                else:
                    temp = dict()
                    admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                    admin_credential_serialized = Admin_Credential_Serializer(admin_credential_ref, many=False).data
                    many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_serialized['admin_credential_id'])
                    if(len(many_to_many_ref) < 1):
                        privileges = None
                    else:
                        privileges = list()
                        for mtmr in many_to_many_ref:
                            privileges.append(mtmr.admin_privilege_id.admin_privilege_id)
                    self.data_returned = self.TRUE_CALL(data = {"admin" : admin_credential_serialized, "privilege" : privileges})

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def edit(self, incoming_data):
        self.data_returned['action'] += "-EDIT"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("admin", "prime") #admins can change other admins and self change is permitted
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(110, "Hash-not ADMIN PRIME"), safe=True)

            else:
                if("updates" in incoming_data.keys()): # admin prime change others, ONLY THIS METHOD ALLOWED
                    if(len(incoming_data['updates']) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one update required"), safe=True)
                                        
                    else:
                        self_admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                        self.data_returned['data'] = dict()
                        temp = dict()
                        updates = tuple(incoming_data['updates'])
                        for update in updates:
                            try:
                                admin_credential_ref = Admin_Credential.objects.filter(admin_credential_id = int(update['admin_id']))
                                key = f"{update['admin_id']}_{update['privilege_id']}"

                            except Exception as ex:
                                self.data_returned['data'][key] = self.AMBIGUOUS_404(ex)
                                                
                            else:
                                if(len(admin_credential_ref) < 1):
                                    self.data_returned['data'][key] = self.CUSTOM_FALSE(111, "Invalid-ADMIN CRED id")
                                                    
                                else:
                                    admin_credential_ref = admin_credential_ref[0]
                                    try:
                                        if(int(update['privilege_id']) < 0): # [2,-2]
                                            flag = False # delete pair
                                            update['privilege_id'] = int(update['privilege_id'])*(-1)
                                        else:
                                            flag = True # create pair
                                        admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(update['privilege_id']))
                                                    
                                    except Exception as ex:
                                        self.data_returned['data'][key] = self.AMBIGUOUS_404(ex)

                                    else:
                                        if(len(admin_privilege_ref) < 1):
                                            self.data_returned['data'][key] = self.CUSTOM_FALSE(116, "Invalid-ADMIN PRIV id")

                                        else:
                                            admin_privilege_ref = admin_privilege_ref[0]
                                            many_to_many_ref = Admin_Cred_Admin_Prev_Int.objects.filter(admin_credential_id = admin_credential_ref.admin_credential_id, 
                                                                                                        admin_privilege_id = admin_privilege_ref.admin_privilege_id)
                                            if(flag == True):
                                                if(len(many_to_many_ref) > 0):
                                                    self.data_returned['data'][key] = self.CUSTOM_FALSE(115, "Pair-Exists ADMIN CRED<=>ADMIN PRIV pair")

                                                else:
                                                    many_to_many_new = Admin_Cred_Admin_Prev_Int(admin_credential_id = admin_credential_ref,
                                                                                                    admin_privilege_id = admin_privilege_ref)
                                                    many_to_many_new.save()
                                                    self.data_returned['data'][key] = self.TRUE_CALL(message = "SUCCESS-Pair-Generated ADMIN CRED<=>ADMIN PRIV pair")

                                            else:
                                                if(len(many_to_many_ref) < 1):
                                                    self.data_returned['data'][key] = self.CUSTOM_FALSE(115, "Pair-Not Exists ADMIN CRED<=>ADMIN PRIV pair")

                                                else:
                                                    many_to_many_ref = many_to_many_ref[0]
                                                    many_to_many_ref.delete()
                                                    self.data_returned['data'][key] = self.TRUE_CALL(message = "SUCCESS-Pair-Removed ADMIN CRED<=>ADMIN PRIV pair")

                else:
                    return JsonResponse(self.MISSING_KEY("updates required"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            if('user_id' in incoming_data.keys()): # admin prime revoking others access
                data = self.check_authorization("admin", "prime") #only prime admins can revoke admin access from others
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(110, "Hash-not ADMIN PRIME"), safe=True)
                                    
                else:
                    user_ids = tuple(set(incoming_data['user_id']))
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                        
                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()
                        if(0 in user_ids):
                            admin_credential_ref_all = Admin_Credential.objects.all().exclude(user_credential_id = int(data[1]))
                            if(len(admin_credential_ref_all) < 1):
                                data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-ADMIN Tray is empty")
                                return JsonResponse(self.data_returned, safe=True)
                                                
                            else:
                                admin_credential_ref_all.delete()
                                temp['data'][0] = self.TRUE_CALL(message="SUCCESS-Empty-ADMIN(-1) Tray cleared")

                        else:
                            for id in user_ids: # self delete not allowed this way SECURITY CHECK
                                try:
                                    if(int(data[1]) == int(id)):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Operation-Self delete not allowed")

                                    else:
                                        user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                        if(len(user_credential_ref) < 1):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "INVALID-USER ID")

                                        else:
                                            try:
                                                user_credential_ref = user_credential_ref[0]
                                                admin_credential_ref = Admin_Credential.objects.filter(user_credential_id = int(user_credential_ref.user_credential_id))
                                
                                            except Exception as ex:
                                                self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                                                    
                                            else:
                                                if(len(admin_credential_ref) < 1):
                                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(113, "INVALID-ADMIN ID")

                                                else:
                                                    admin_credential_ref = admin_credential_ref[0]
                                                    admin_credential_ref.delete()
                                                    self.data_returned['data'][id] = self.TRUE_CALL()

                                except Exception as ex:
                                    self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                                    
            else: # self delete
                data = self.check_authorization("admin")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(114, "Hash-not ADMIN"), safe=True)
                                    
                else:
                    admin_credential_ref = Admin_Credential.objects.get(user_credential_id = int(data[1]))
                    admin_credential_ref.delete()
                    self.data_returned = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Admin_Privilege_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()

    @overrides
    def create(self, incoming_data):
        self.data_returned['action'] += "-CREATE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            incoming_data = incoming_data['data']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("admin", "prime") #only prime admins can create admin priv
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(110, "Hash-not ADMIN PRIME"), safe=True)

            else:
                try:
                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = incoming_data["admin_privilege_name"].upper())

                except Exception as ex:
                    return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)

                else:
                    if(len(admin_privilege_ref) > 0):
                        return JsonResponse(self.CUSTOM_FALSE(117, "Create-Admin Privilege exists"), safe=True)

                    else:
                        admin_privilege_de_serialized = Admin_Privilege_Serializer(data=incoming_data)
                        if(admin_privilege_de_serialized.is_valid()):
                            admin_privilege_de_serialized.save()
                            self.data_returned = self.TRUE_CALL(data = {"privilege" : admin_privilege_de_serialized.data['admin_privilege_id']})

                        else:
                            return JsonResponse(self.CUSTOM_FALSE(405, f"Serialize-{admin_privilege_de_serialized.errors}"), safe=True)
                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            privilege_ids = tuple(set(incoming_data['privilege_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("admin") #only prime admins can see privileges
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(111, "Hash-not ADMIN"), safe=True)

            else:
                if(len(privilege_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    if(0 in privilege_ids):
                        admin_privilege_ref = Admin_Privilege.objects.all()
                        if(len(admin_privilege_ref) < 1):
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Atleast one id required")
                            return JsonResponse(self.data_returned, safe=True)
                                            
                        else:
                            admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=True).data
                            self.data_returned['data'][0][id] = self.TRUE_CALL(data = admin_privilege_serialized)
                                        
                    else:
                        for id in privilege_ids:
                            try:
                                admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(id))
                                                
                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(408, "DataType-{str(ex)}")

                            else:
                                if(len(admin_privilege_ref) < 1):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-PRIVILEGE id")
                            
                                else:
                                    admin_privilege_ref = admin_privilege_ref[0]
                                    admin_privilege_serialized = Admin_Privilege_Serializer(admin_privilege_ref, many=False).data
                                    self.data_returned['data'][id] = self.TRUE_CALL(data = admin_privilege_serialized)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def edit(self, incoming_data):
        self.data_returned['action'] += "-EDIT"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            incoming_data = incoming_data['data']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("admin", "prime") #admins can change other admins and self change is permitted
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(110, 'Hash-not ADMIN PRIME'), safe=True)

            else:
                try:
                    admin_privilege_ref_self = Admin_Privilege.objects.filter(admin_privilege_id = incoming_data['admin_privilege_id'])
                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_name__contains = incoming_data["admin_privilege_name"].upper())
                                    
                except Exception as ex:
                    return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)

                else:
                    if(len(admin_privilege_ref_self) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(111, "Invalid-ADMIN PRIVILEGE id"), safe=True)
                                        
                    else:
                        admin_privilege_ref_self = admin_privilege_ref_self[0]
                        if(len(admin_privilege_ref) > 0):
                            admin_privilege_ref = admin_privilege_ref[0]
                            if(admin_privilege_ref_self.admin_privilege_id != admin_privilege_ref_self.admin_privilege_id):
                                return JsonResponse(self.CUSTOM_FALSE(117, "Create-Admin Privilege Name exists"), safe=True)
                                                
                            else:
                                pass
                                                    
                        else:
                            pass
                                    
                        admin_privilege_de_serialized = Admin_Privilege_Serializer(admin_privilege_ref_self, data=incoming_data)
                        if(admin_privilege_de_serialized.is_valid()):
                            admin_privilege_de_serialized.save()
                            self.data_returned = self.TRUE_CALL(data = {"privilege" : admin_privilege_de_serialized.data['admin_privilege_id']})
                                            
                        else:
                            return JsonResponse(self.CUSTOM_FALSE(403, f"Serialize-{admin_privilege_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            privilege_ids = tuple(set(incoming_data['privilege_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("admin", "prime") #only prime admins can grant admin access
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(110, "Hash-not ADMIN PRIME"), safe=True)

            else:
                try:
                    if(len(privilege_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-At least one id required"), safe=True)
                                        
                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()
                        if(0 in privilege_ids):
                            self.data_returned['data'][0] = self.AMBIGUOUS_404("[0] => universal deletion not applicable")
                            return JsonResponse(self.data_returned, safe=True)
                                            
                        else:
                            for id in privilege_ids:
                                try:
                                    admin_privilege_ref = Admin_Privilege.objects.filter(admin_privilege_id = int(id))
                                                    
                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                                    
                                else:
                                    if(len(admin_privilege_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "INVALID-Admin Privilege id")
                                                        
                                    else:
                                        admin_privilege_ref = admin_privilege_ref[0]
                                        admin_privilege_ref.delete()
                                        self.data_returned['data'][id] = self.TRUE_CALL()

                except Exception as ex:
                    return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)
                                    
                else:
                    return JsonResponse(self.data_returned, safe=True)

# -------------------------------------------------

image_endpoint = Image_Api()
user_credential = User_Credential_Api()
user_profile = User_Profile_Api()
admin_credential = Admin_Credential_Api()
admin_privilege = Admin_Privilege_Api()

# -------------------------------------------------

# ------------------------------VIEW_SPACE-------------------------------------

pinned = [

    '<span style="color: yellow;">[25-02-2021]</span> All methods migrated to POST -> check postman export for clarity',
    '<span style="color: yellow;">[23-02-2021]</span> FETCH method have been changed to REQUEST method',

]

def api_token_web(request, word=None):
    auth = Authorize()
    cookie = Cookie()
    data_returned = dict()

    data_returned['site_name'] = 'API'

    if(request.method == 'GET'):
        if(word != None):
            if(word.upper() == 'signin'.upper()):
                type = 'signin'.upper()
            else:
                auth.clear()
                type = 'logged'.upper()
        else:
            type = 'signup'.upper()
        
        data = cookie.check_authentication_info(request)
        if(data[0] == True):
            type = 'logged'.upper()
            api_ref = Api_Token_Table.objects.get(pk = data[1])
            data_returned['user'] = api_ref
            data_returned['type'] = 'logged'.upper()
            data_returned['pinned'] = pinned
            return render(request, 'auth_prime/api.html', data_returned)
            # return cookie.set_authentication_info(request=request, file_path='auth_prime/api.html', data=data_returned, pk=api_ref.pk)
        
        data_returned['type'] = type

        return render(request, 'auth_prime/api.html', data_returned)
    
    elif(request.method == 'POST'):
        temp = dict(request.POST)
        if(temp['form_type'][0] == 'signup'):
            keys = ('user_f_name', 'user_l_name', 'user_email', 'user_password', 'api_endpoint')
            
            auth.clear()
            try:
                auth.user_password = f"{temp[keys[3]][0]}"
                data = auth.create_password_hashed()
            except Exception as ex:
                messages.add_message(request, messages.INFO, str(ex))
                data_returned['type'] = 'signup'.upper()
                return render(request, 'auth_prime/api.html', data_returned)
            else:
                if(data[0] == False):
                    print("------------------------------------------------------------------")
                    print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL : HASHING ERROR.")
                else:
                    try:
                        api_new = Api_Token_Table(user_name = f"{temp[keys[0]][0]} {temp[keys[1]][0]}",
                                                  user_email = f"{temp[keys[2]][0].lower()}",
                                                  user_password = f"{data[1]}",
                                                  user_key_private = auth.random_generator(),
                                                  api_endpoint = temp[keys[4]][0])
                        api_new.save()
                    except Exception as ex:
                        print("------------------------------------------------------------------")
                        print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL")
                        print(f"[x] Exception : {str(ex)}")
                    else:
                        print("------------------------------------------------------------------")
                        print(f"[.] API TOKEN GENERATION : SUCCESSFUL")
                        return redirect('API_TOKEN', word='signin')
        
        elif(temp['form_type'][0] == 'signin'):
            keys = ['user_email', 'user_password']

            auth.clear()
            try:
                auth.user_password = f"{temp[keys[1]][0]}"
                data = auth.create_password_hashed()
            except Exception as ex:
                messages.add_message(request, messages.INFO, str(ex))
                data_returned['type'] = 'signin'.upper()
                return render(request, 'auth_prime/api.html', data_returned)
            else:
                if(data[0] == False):
                    print("------------------------------------------------------------------")
                    print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL : HASHING ERROR.")
                else:
                    try:
                        api_ref = Api_Token_Table.objects.filter(user_email = f"{temp[keys[0]][0].lower()}",
                                                                 user_password = data[1])
                        if(len(api_ref) < 1):
                            messages.add_message(request, messages.INFO, "Wrong Credentials ! Try again !")
                            data_returned['type'] = 'signin'.upper()
                            return render(request, 'auth_prime/api.html', data_returned)
                        else:
                            api_ref = api_ref[0]
                            data_returned['user'] = api_ref
                            data_returned['type'] = 'logged'.upper()
                            data_returned['pinned'] = pinned
                            return cookie.set_authentication_info(request=request, file_path='auth_prime/api.html', data=data_returned, pk=api_ref.pk)
                    except Exception as ex:
                        print(f"[x] API KEY LOGIN : {str(ex)}")
            
            return render(request, 'auth_prime/api.html', data_returned)
        
        elif(temp['form_type'][0] == 'signout'):

            data_returned['type'] = 'signin'.upper()
            return cookie.revoke_authentication_info(request, 'auth_prime/api.html', data_returned)
        
        else:
            return redirect('AUTH_TOKEN')

        