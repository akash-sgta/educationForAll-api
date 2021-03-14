from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from datetime import datetime
from overrides import overrides

# ------------------------------------------------------------

from user_personal.models import Diary
from user_personal.models import Submission
from user_personal.models import Notification
from user_personal.models import User_Notification_Int
from user_personal.models import Enroll

from user_personal.serializer import Diary_Serializer
from user_personal.serializer import Submission_Serializer
from user_personal.serializer import Notification_Serializer
from user_personal.serializer import User_Notification_Int_Serializer
from user_personal.serializer import Enroll_Serializer

from auth_prime.models import User_Credential

from content_delivery.models import Post
from content_delivery.models import Coordinator

from auth_prime.important_modules import API_Prime

from auth_prime.authorize import Authorize

# ------------------------------------------------------------

class Diary_Api(API_Prime, Authorize):
    
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
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                diary_de_serialized = Diary_Serializer(data = incoming_data)
                diary_de_serialized.initial_data['user_credential_id'] = int(data[1])
                diary_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                if(diary_de_serialized.is_valid()):
                    diary_de_serialized.save()
                    self.data_returned = self.TRUE_CALL(data = {"diary" : diary_de_serialized.data['diary_id'], "post" : diary_de_serialized.data['diary_id']})
                                        
                else:
                    return JsonResponse(self.CUSTOM_FALSE(404, f"Serialise-{diary_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            datas = tuple(incoming_data['data'])

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            keys = ('post_id', 'user')
            for check in datas:
                if('post_id' in check.keys()):
                    if('user_id' in check.keys()):
                        if(check['user_id'].upper() == 'ALL'):
                            action = 1 # all diaries of post
                        elif(check['user_id'].upper() == 'SELF'):
                            action = 2 # one user diaries of post+user
                        else:
                            action = 4
                    else:
                        action = 4
                elif('diary_id' in check.keys()):
                    action = 3 # specific diaries
                else:
                    action = 4 # invalid
                                    
                if(action == 4): # invalid
                    key = "-".join(list(check.keys()))
                    self.data_returned['data'][key] = self.MISSING_KEY('Follow API contract')
                                    
                elif(action == 3): # specific diaries
                    key = "diary"
                    data = self.check_authorization('user')
                                        
                    if(data[0] == False):
                        self.data_returned['data'][key] = self.CUSTOM_FALSE(666, "Hash-not USER")
                                        
                    else:
                        try:
                            diary_ids = tuple(set(check['diary_id']))
                                            
                        except Exception as ex:
                            self.data_returned['data'][key] = self.AMBIGUOUS_404(ex)
                                            
                        else:
                            for id in diary_ids:
                                try:
                                    diary_ref = Diary.objects.filter(diary_id = int(id))
                                                
                                except Exception as ex:
                                    self.data_returned['data'][key][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                else:
                                    if(len(diary_ref) < 1):
                                        self.data_returned['data'][key][id] = self.CUSTOM_FALSE(404, "Invalid-Diary ID")
                                                    
                                    else:
                                        diary_ref = diary_ref[0]
                                        if(diary_ref.user_credential_id != int(data[1])):
                                            self.data_returned['data'][key][id] = self.CUSTOM_FALSE(404, "Invalid-Diary Does not belong to USER")

                                        else:
                                            diary_serialized = Diary_Serializer(diary_ref, many=False).data
                                            self.data_returned['data'][key][id] = self.TRUE_CALL(data = diary_serialized)
                                    
                elif(action == 1): # all diaries of post
                    key = "-".join('POST', check['post_id'], "ALL")
                    data = auth.check_authorization('admin', 'alpha')
                    if(data[1] == False):
                        self.data_returned['data'][key] = self.CUSTOM_FALSE(666, "Hash-not ADMIN_ALPHA")
                                        
                    else:
                        try:
                            diary_ref_post = Diary.objects.filter(post_id = int(check[keys[1]])).order_by("-diary_id")
                                            
                        except Exception as ex:
                            self.data_returned['data'][key] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                                            
                        else:
                            if(len(diary_ref_post) < 1):
                                self.data_returned['data'][key] = self.CUSTOM_FALSE(151, f"Empty-Post_Diary Tray empty")
                                                
                            else:
                                diary_ref_post_serialized = Diary_Serializer(diary_ref_post, many=True).data
                                self.data_returned['data'][key] = self.TRUE_CALL(data = diary_ref_post_serialized)
                                    
                else: # one user diaries of post+user
                    key = "-".join('POST', check['post_id'], "SELF")
                    data = auth.check_authorization('user')
                    if(data[1] == False):
                        self.data_returned['data'][key] = self.CUSTOM_FALSE(666, "Hash-not USER")
                                        
                    else:
                        try:
                            diary_ref_user = Diary.objects.filter(user_id = int(data[1]), post_id = int(check['post_id'])).order_by("-diary_id")
                                            
                        except Exception as ex:
                            self.data_returned['data'][key] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                                            
                        else:
                            if(len(diary_ref_user) < 1):
                                self.data_returned['data'][key] = self.CUSTOM_FALSE(151, f"Empty-Post_Diary Tray empty")
                                                
                            else:
                                diary_ref_user_serialized = Diary_Serializer(diary_ref_user, many=True).data
                                self.data_returned['data'][key] = self.TRUE_CALL(data = diary_ref_post_serialized)


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
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, 'Hash-not USER'), safe=True)
                                
            else:
                try:
                    diary_ref = Diary.objects.filter(lecture_id = int(incoming_data['diary_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)
                                    
                else:
                    if(len(diary_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Diary Id"), safe=True)
                                        
                    else:
                        diary_ref = diary_ref[0]
                        if(diary_ref.user_credential_id.user_credential_id != int(data[1])):
                            return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Diary does not belong to USER"), safe=True)
                                            
                        else:
                            diary_de_serialized = Diary_Serializer(diary_ref, data = incoming_data)
                            if(diary_de_serialized.is_valid()):
                                diary_de_serialized.save()
                                self.data_returned = self.TRUE_CALL(data = {"diary" : diary_de_serialized.data['diary_id'], "post" : diary_de_serialized.data['diary_id']})
                                        
                            else:
                                return JsonResponse(self.JSON_PARSER_ERROR(f"{diary_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            diary_ids = tuple(set(incoming_data['diary_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data_a = self.check_authorization("admin", "alpha")
            data_u = self.check_authorization("user")
            for id in diary_ids:
                try:
                    diary_ref = Diary.objects.filter(lecture_id = int(id))
                                        
                except Exception as ex:
                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                else:
                    if(len(diary_ref) < 1):
                        self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Diary Id")
                                        
                    else:
                        if(data_u[0] == False):
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Hash-not USER")
                                            
                        else:
                            diary_ref = diary_ref[0]
                            if(diary_ref.user_credential_id != int(data_u[1])):
                                if(data_a[0] == False):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Diary does not belong to USER")
                                                
                                else: # deleted other as admin
                                    diary_ref.delete()
                                    self.data_returned['data'][id] = self.TRUE_CALL(message = "As ADMIN")
                                                
                            else: # deleted self as user
                                diary_ref.delete()
                                self.data_returned['data'][id] = self.TRUE_CALL(message = "As USER")

            return JsonResponse(self.data_returned, safe=True)

class Submission_Api(API_Prime, Authorize):
    
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
            data = self.check_authorization("user") # user -> student
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                submission_de_serialized = Submission_Serializer(data = incoming_data)
                submission_de_serialized.initial_data['user_credential_id'] = int(data[1])
                submission_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                if(submission_de_serialized.is_valid()):
                    submission_de_serialized.save()
                    self.data_returned = self.TRUE_CALL(data = {"submission" : submission_de_serialized.data['submission_id'], "assignment" : submission_de_serialized.data['assignment_id']})
                                        
                else:
                    return JsonResponse(self.CUSTOM_FALSE(404, f"Serialise-{submission_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            submission_ids = tuple(set(incoming_data['submission_id']))
            assignment_ids = tuple(set(incoming_data['assignment_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data_u = self.check_authorization("user")
            if(data_u[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                if(len(submission_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    if(len(assignment_ids) < 1):
                        flag = (False, False)
                    else:
                        flag = (True, True)

                    self.data_returned['data'] = dict()
                    temp = dict()
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data_u[1]))
                    if(len(coordinator_ref) < 1):
                        cor_flag = False
                    
                    else:
                        coordinator_ref = coordinator_ref[0]
                        cor_flag = True

                    for id in submission_ids:
                        try:
                            submission_ref = Submission.objects.filter(submission_id = int(id))
                                            
                        except Exception as ex:
                            self.data_returned['data']['sumbission'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                        else:
                            if(len(submission_ref) < 1):
                                self.data_returned['data']['sumbission'][id] = self.CUSTOM_FALSE(404, "Invalid-Submission ID")
                                                
                            else:
                                submission_ref = submission_ref[0]
                                if(submission_ref.user_credential_id != int(data_u[1])): # coordinator checking submission
                                    if(cor_flag == False):
                                        self.data_returned['data']['sumbission'][id] = self.CUSTOM_FALSE(666, "User not Coordinator")
                                        flag[1] = False
                                                        
                                    else:
                                        submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                        self.data_returned['data']['sumbission'][id] = self.TRUE_CALL(data = submission_serialized)
                                                    
                                else: # self checking submissions
                                    submission_serialized = Submission_Serializer(submission_ref, many=False).data
                                    self.data_returned['data']['sumbission'][id] = self.TRUE_CALL(data = submission_serialized)

                    if(flag[0] == False):
                        pass
                    else:
                        if(flag[1] == False):
                            self.data_returned['data']['assignment'] = self.CUSTOM_FALSE(666, "USER not COORDINATOR")
                        else:
                            for id in assignment_ids:
                                try:
                                    post_ref = Submission.objects.filter(assignment_id = int(id))
                                            
                                except Exception as ex:
                                    self.data_returned['data']['assignment'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                                else:
                                    if(len(post_ref) < 1):
                                        self.data_returned['data']['assignment'][id] = self.CUSTOM_FALSE(408, "Invalid-Assignment id")
                                                        
                                    else:
                                        post_ref = post_ref[0]
                                        assignment_id = post_ref.assignment_id.assignment_id
                                        submission_ref = Submission.objects.filter(assignment_id = assignment_id)
                                        if(len(submission_ref) < 1):
                                            self.data_returned['data']['assignment'][id] = self.CUSTOM_FALSE(151, "Empty-Assignment<=>Submission Empty")
                                                            
                                        else:
                                            submission_serialized = Submission_Serializer(submission_ref, many=True).data
                                            self.data_returned['data']['assignment'][id] = self.TRUE_CALL(data = submission_serialized)

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
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                try:
                    submission_ref = Submission.objects.filter(submission_id = int(incoming_data['submission_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, "DataType-{str(ex)}"), safe=True)
                                    
                else:
                    if(len(submission_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Submission Id"), safe=True)
                                        
                    else:
                        submission_ref = submission_ref[0]
                        if(submission_ref.user_credential_id != int(data[1])):
                            return JsonResponse(self.CUSTOM_FALSE(404, 'Invalid-Submission does not belong to USER'), safe=True)
                                            
                        else:
                            submission_de_serialized = Submission_Serializer(submission_ref, data = incoming_data)
                            if(submission_de_serialized.is_valid()):
                                submission_de_serialized.save()
                                self.data_returned = self.TRUE_CALL(data = {"submission" : submission_de_serialized.data['submission_id'], "assignment" : submission_de_serialized.data['assignment_id']})
                                        
                            else:
                                return JsonResponse(self.JSON_PARSER_ERROR(f"{submission_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            submission_ids = tuple(set(incoming_data['submission_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data_u = self.check_authorization("user")
            if(data_u[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                if(len(submission_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data_u[1]))
                    if(len(coordinator_ref) < 1):
                        cor_flag = False
                    else:
                        coordinator_ref = coordinator_ref[0]
                        cor_flag = True

                    for id in submission_ids:
                        try:
                            submission_ref = Submission.objects.filter(submission_id = int(id))
                                            
                        except Exception as ex:
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                        else:
                            if(len(submission_ref) < 1):
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Submission ID")
                                                
                            else:
                                submission_ref = submission_ref[0]
                                if(submission_ref.user_credential_id != int(data_u[1])): # coordinator deleting submission ? shoud they be allowed ?
                                    # if(cor_flag == False):
                                    #     data_returned['data'][id] = CUSTOM_FALSE(666, "User not Coordinator")
                                    #     flag[1] = False
                                    # else:
                                    #     submission_ref.delete()
                                    #     data_returned['data'][id] = TRUE_CALL()
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(666, "NotBelong-USER<=>SUBMISSION")
                                                    
                                else: # self delete submissions
                                    submission_ref.delete()
                                    data_returned['data'][id] = TRUE_CALL()
                                    
                                return JsonResponse(data_returned, safe=True)

class Notification_Api(API_Prime, Authorize):
    
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
            data = self.check_authorization("user") # has to be checked later per usage
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                notification_de_serialized = Notification_Serializer(data = incoming_data)
                # check it for changes : later
                notification_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                user_credential_ref = User_Credential.objects.filter(user_credential_id = notification_de_serialized.initial_data['user_credential_id'])
                del(notification_de_serialized.initial_data['user_credential_id'])
                if(len(user_credential_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(666, f"Invalid-user_credential_id"), safe=True)
                
                else:
                    self_user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                    user_credential_ref = user_credential_ref[0]
                    if(notification_de_serialized.is_valid()):
                        notification_de_serialized.save()
                        notification_ref = Notification.objects.get(notification_id =  notification_de_serialized.data['notification_id'])
                        # for reciever
                        user_notification_ref_new = User_Notification_Int(user_credential_id = user_credential_ref,
                                                                        notification_id = notification_ref,
                                                                        made_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                        user_notification_ref_new.save()
                        # for from creator
                        message = f"NOTIFICATION : {notification_de_serialized.data['notification_body']} created by you for {user_credential_ref.user_f_name} {user_credential_ref.user_l_name}."
                        notification_ref_new = Notification(notification_body = message,
                                                            made_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                        notification_ref_new.save()
                        user_notification_ref_new = User_Notification_Int(user_credential_id = self_user_credential_ref,
                                                                        notification_id = notification_ref_new,
                                                                        made_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                        user_notification_ref_new.save()
                        self.data_returned = self.TRUE_CALL(data = {"notification" : notification_de_serialized.data['notification_id']})
                                            
                    else:
                        return JsonResponse(self.CUSTOM_FALSE(404, f"Serialise-{notification_de_serialized.errors}"), safe=True)
                                
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
            keys = ('user_id', 'notification_id') # just to remember
            incoming_keys = incoming_data.keys()
            if('user_id' in incoming_keys):
                user_ids = tuple(set(incoming_data['user_id']))
                self.data_returned['user'] = dict()
                for id in user_ids:
                    try:
                        notification_user_ref_all = User_Notification_Int.objects.filter(user_credential_id = int(id)).order_by('-notification_id')
                    
                    except Exception as ex:
                        self.data_returned['user'][id] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                    
                    else:
                        if(len(notification_user_ref_all) < 1):
                            self.data_returned['user'][id] = self.CUSTOM_FALSE(151, f"Empty-User has no Notifications")
                        
                        else:
                            temp = dict()
                            for notification in notification_user_ref_all:
                                actual_notification_serialized = Notification_Serializer(notification.notification_id, many = False).data
                                temp[f"{notification.made_date}"] = actual_notification_serialized
                            self.data_returned['user'][id] = self.TRUE_CALL(data = temp.copy())
            
            if('notification_id' in incoming_keys):
                notification_ids = tuple(set(incoming_data['notification_id']))
                self.data_returned['notification'] = dict()
                for id in notification_ids:
                    try:
                        notification_ref = Notification.objects.filter(notification_id = int(id))
                    
                    except Exception as ex:
                        self.data_returned['notification'][id] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                    
                    else:
                        if(len(notification_user_ref_all) < 1):
                            self.data_returned['notification'][id] = self.CUSTOM_FALSE(666, f"Invalid-Notification ID")
                        
                        else:
                            notification_ref_serialized = Notification_Serializer(notification_ref, many = False).data
                            self.data_returned['notification'][id] = self.TRUE_CALL(data = notification_ref_serialized)

            return JsonResponse(self.data_returned, safe=True)

    # think about it
    '''
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
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, 'Hash-not USER'), safe=True)
                                
            else:
                try:
                    diary_ref = Diary.objects.filter(lecture_id = int(incoming_data['diary_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)
                                    
                else:
                    if(len(diary_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Diary Id"), safe=True)
                                        
                    else:
                        diary_ref = diary_ref[0]
                        if(diary_ref.user_credential_id.user_credential_id != int(data[1])):
                            return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Diary does not belong to USER"), safe=True)
                                            
                        else:
                            diary_de_serialized = Diary_Serializer(diary_ref, data = incoming_data)
                            if(diary_de_serialized.is_valid()):
                                diary_de_serialized.save()
                                self.data_returned = self.TRUE_CALL(data = {"diary" : diary_de_serialized.data['diary_id'], "post" : diary_de_serialized.data['diary_id']})
                                        
                            else:
                                return JsonResponse(self.JSON_PARSER_ERROR(f"{diary_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)
    '''

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            notification_ids = tuple(set(incoming_data['notification_id_del']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(404, "Hash-not USER"), safe=True)
            
            else:
                self.data_returned['data'] = dict()
                for id in notification_ids:
                    try:
                        notification_ref = Notification.objects.filter(notification_id = int(id))
                                        
                    except Exception as ex:
                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                    else:
                        if(len(notification_ref) < 1):
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Notification Id")
                                        
                        else:
                            notification_ref.delete()
                            self.data_returned['data'][id] = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Enroll_Api(API_Prime, Authorize):
    
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
            data = self.check_authorization("user") # has to be checked later per usage
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                enroll_de_serialized = Enroll_Serializer(data = incoming_data)
                # check it for changes : later
                enroll_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                if(enroll_de_serialized.is_valid()):
                    enroll_de_serialized.save()
                    self.data_returned = self.TRUE_CALL(data = {"enroll" : enroll_de_serialized.data['pk']})
                                        
                else:
                    return JsonResponse(self.CUSTOM_FALSE(404, f"Serialise-{enroll_de_serialized.errors}"), safe=True)
                                
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
            keys = ('user_id', 'subject_id') # just to remember
            incoming_keys = incoming_data.keys()
            if('user_id' in incoming_keys):
                user_ids = tuple(set(incoming_data['user_id']))
                self.data_returned['user'] = dict()
                for id in user_ids:
                    try:
                        enroll_user_ref_all = Enroll.objects.filter(user_credential_id = int(id)).order_by('-pk')
                    
                    except Exception as ex:
                        self.data_returned['user'][id] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                    
                    else:
                        if(len(enroll_user_ref_all) < 1):
                            self.data_returned['user'][id] = self.CUSTOM_FALSE(151, f"Empty-User has no Subjects enrolled")
                        
                        else:
                            sub = list()
                            for enroll in enroll_user_ref_all:
                                sub.append(enroll.subject_id.subject_id)
                            self.data_returned['user'][id] = self.TRUE_CALL(data = {"subject" : sub})
            
            if('subject_id' in incoming_keys):
                subject_ids = tuple(set(incoming_data['subject_id']))
                self.data_returned['subject'] = dict()
                for id in subject_ids:
                    try:
                        enroll_subject_ref_all = Enroll.objects.filter(subject_id = int(id)).order_by('-pk')
                    
                    except Exception as ex:
                        self.data_returned['subject'][id] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                    
                    else:
                        if(len(enroll_subject_ref_all) < 1):
                            self.data_returned['subject'][id] = self.CUSTOM_FALSE(666, f"Invalid-Subject has no user enrolled")
                        
                        else:
                            users = list()
                            for enroll in enroll_subject_ref_all:
                                users.append(enroll.user_credential_id.user_credential_id)
                            self.data_returned['subject'][id] = self.TRUE_CALL(data = {"user" : users})

            return JsonResponse(self.data_returned, safe=True)

    # don't think there is any point in keeping edit
    '''
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
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, 'Hash-not USER'), safe=True)
                                
            else:
                try:
                    diary_ref = Diary.objects.filter(lecture_id = int(incoming_data['diary_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)
                                    
                else:
                    if(len(diary_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Diary Id"), safe=True)
                                        
                    else:
                        diary_ref = diary_ref[0]
                        if(diary_ref.user_credential_id.user_credential_id != int(data[1])):
                            return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Diary does not belong to USER"), safe=True)
                                            
                        else:
                            diary_de_serialized = Diary_Serializer(diary_ref, data = incoming_data)
                            if(diary_de_serialized.is_valid()):
                                diary_de_serialized.save()
                                self.data_returned = self.TRUE_CALL(data = {"diary" : diary_de_serialized.data['diary_id'], "post" : diary_de_serialized.data['diary_id']})
                                        
                            else:
                                return JsonResponse(self.JSON_PARSER_ERROR(f"{diary_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)
    '''

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            enrollments = tuple(set(incoming_data['enrollment']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            key = (('user_id','subject_id'),('user_id','subject_id')) # for reference
            for enroll in enrollments:
                id = f"{enroll[0]}_{enroll[1]}"
                try:
                    enroll_ref = Enroll.objects.filter(user_credential_id = int(enroll[0]),
                                                        subject_id = int(enroll[1]))
                    
                except Exception as ex:
                    self.data_returned['user'][id] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                    
                else:
                    if(len(enroll_ref) < 1):
                        self.data_returned['user'][id] = self.CUSTOM_FALSE(151, f"Empty-Invalid Pair")
                        
                    else:
                        enroll_ref = enroll_ref[0]
                        enroll_ref.delete()
                        self.data_returned['user'][id] = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

# --------------------------------

diary = Diary_Api()
submission = Submission_Api()
notification = Notification_Api()
enroll = Enroll_Api()

# --------------------------------