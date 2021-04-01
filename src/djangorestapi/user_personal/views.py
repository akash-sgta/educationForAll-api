from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

from datetime import datetime
from overrides import overrides

# ------------------------------------------------------------

from user_personal.models import (
        Diary,
        Submission,
        Notification,
        User_Notification_Int,
        Enroll,
    )

from user_personal.serializer import (
        Diary_Serializer,
        Submission_Serializer,
        Notification_Serializer,
        User_Notification_Int_Serializer,
        Enroll_Serializer,
    )

from auth_prime.models import User_Credential

from content_delivery.models import Post
from content_delivery.models import Coordinator

from auth_prime.important_modules import API_Prime
from auth_prime.important_modules import am_I_Authorized

from auth_prime.authorize import Authorize

# ------------------------------------------------------------

@csrf_exempt
def api_diary_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            data = dict()
            diary_serialized = Diary_Serializer(data=request.data)
            diary_serialized.initial_data['user_credential_id'] = int(user_id)
            if(diary_serialized.is_valid()):
                diary_serialized.save()
                data['success'] = True
                data['data'] = diary_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = f"error:SERIALIZING_ERROR, message:{diary_serialized.errors}"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0):
                    diary_ref = Diary.objects.filter(user_credential_id = user_id)
                    diary_serialized = Diary_Serializer(diary_ref, many=True)
                else:
                    diary_ref = Diary.objects.get(user_credential_id = user_id, diary_id=pk)
                    diary_serialized = Diary_Serializer(diary_ref, many=False)
            except Diary.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                data['success'] = True
                data['data'] = diary_serialized.data
                return Response(data=data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                diary_ref = Diary.objects.filter(user_credential_id=user_id, diary_id=pk)
                if(len(diary_ref) < 1):
                    data['success'] = False
                    data['message'] = "item does not belong to user"
                    return Response(data = data)

            except Diary.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                diary_ref = diary_ref[0]
                diary_serialized = Diary_Serializer(diary_ref, data=request.data)
                diary_serialized.initial_data['user_credential_id'] = int(user_id)
                diary_serialized.initial_data['post_id'] = diary_ref.post_id.post_id
                if(diary_serialized.is_valid()):
                    diary_serialized.save()
                    data['success'] = True
                    data['data'] = diary_serialized.data
                    return Response(data = data)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{diary_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                diary_ref = Diary.objects.filter(user_credential_id = user_id, diary_id = pk)
                if(len(diary_ref) < 1):
                    data['success'] = False
                    data['message'] = "item does not belong to user"
                    return Response(data = data)
            except Diary.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                diary_ref = diary_ref[0]
                diary_ref.delete()
                data['success'] = True
                return Response(data = data)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/diary/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/diary/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/diary/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# ------------------------------------------------------------

@csrf_exempt
def api_submission_view(request, job, pk=None):

    @api_view(['POST', ])
    def create(request, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            data = dict()
            submission_serialized = Submission_Serializer(data=request.data)
            submission_serialized.initial_data['user_credential_id'] = int(user_id)
            if(submission_serialized.is_valid()):
                submission_serialized.save()
                data['success'] = True
                data['data'] = submission_serialized.data
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data['success'] = False
                data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET', ])
    def read(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                if(int(pk) == 0):
                    submission_ref = Submission.objects.filter(user_credential_id = user_id)
                    submission_serialized = Submission_Serializer(submission_ref, many=True)
                else:
                    submission_ref = Submission.objects.get(user_credential_id = user_id)
                    submission_serialized = Submission_Serializer(submission_ref, many=False)
            except Submission.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                data['success'] = True
                data['data'] = submission_serialized.data
                return Response(data=data, status=status.HTTP_202_ACCEPTED)

    @api_view(['PUT', ])
    def edit(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.filter(user_credential_id = user_id, submission_id = pk)
                if(len(submission_ref) < 1):
                    data['success'] = False
                    data['message'] = "item does not belong to user"
                    return Response(data = data)

            except Submission.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                submission_ref = submission_ref[0]
                submission_serialized = Submission_Serializer(submission_ref, data=request.data)
                submission_serialized.initial_data['user_credential_id'] = int(user_id)
                submission_serialized.initial_data['assignment_id'] = submission_ref.assignment_id.assignment_id
                if(submission_serialized.is_valid()):
                    submission_serialized.save()
                    data['success'] = True
                    data['data'] = submission_serialized.data
                    return Response(data = data)
                else:
                    data['success'] = False
                    data['message'] = f"error:SERIALIZING_ERROR, message:{submission_serialized.errors}"
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE', ])
    def delete(request, pk, auth):
        data = dict()
        if(auth[0] == False):
            data['success'] = False
            data['message'] = f"error:USER_NOT_AUTHORIZED, message:{auth[1]}"
            return Response(data = data)
        else:
            user_id = auth[1]
            try:
                submission_ref = Submission.objects.filter(user_credential_id = user_id, submission_id = pk)
                if(len(submission_ref) < 1):
                    data['success'] = False
                    data['message'] = "item does not belong to user"
                    return Response(data = data)
            except Submission.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                submission_ref = submission_ref[0]
                submission_ref.delete()
                data['success'] = True
                return Response(data = data)

    # active point
    data = am_I_Authorized(request, "API")
    if(data[0] == False):
        return JsonResponse({"error":"API_KEY_UNAUTHORIZED", "message" : data[1]}, safe=True)
    else:
        data = am_I_Authorized(request, "USER")
        if(job == 'create'):
            return create(request, data)
        elif(job == 'read'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/submission/read/<id>"}, safe=True)
            else:
                return read(request, pk, data)
        elif(job == 'edit'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/submission/edit/<id>"}, safe=True)
            else:
                return edit(request, pk, data)
        elif(job == 'delete'):
            if(pk in (None, '')):
                return JsonResponse({"error":"URL_FORMAT_ERROR","message":"api/personal/submission/delete/<id>"}, safe=True)
            else:
                return delete(request, pk, data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------
# ------------------------------------------------------------

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

# diary = Diary_Api()
submission = Submission_Api()
notification = Notification_Api()
enroll = Enroll_Api()

# --------------------------------