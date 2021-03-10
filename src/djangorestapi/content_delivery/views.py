from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from datetime import datetime
from overrides import overrides

# ------------------------------------------------------

from content_delivery.models import Coordinator
from content_delivery.models import Subject
from content_delivery.models import Subject_Coordinator_Int
from content_delivery.models import Forum
from content_delivery.models import Reply
from content_delivery.models import Lecture
from content_delivery.models import Assignment
from content_delivery.models import Post

from content_delivery.serializer import Coordinator_Serializer
from content_delivery.serializer import Subject_Serializer
from content_delivery.serializer import Forum_Serializer
from content_delivery.serializer import Reply_Serializer
from content_delivery.serializer import Lecture_Serializer
from content_delivery.serializer import Assignment_Serializer
from content_delivery.serializer import Post_Serializer

from auth_prime.important_modules import Api_Prime

from auth_prime.models import User_Credential
from auth_prime.models import Admin_Credential
from auth_prime.models import Admin_Cred_Admin_Prev_Int
from auth_prime.models import Admin_Privilege

from auth_prime.authorize import Authorize

# ------------------------------------------------------

# ---------------------------------------------API SPACE-------------------------------------------------------

class Coordinator_Api(API_Prime, Authorize):
    
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
            data = self.check_authorization("admin", "cagp") # Coordinators can be placed by admins only
            if(data[0] == False):
                return JsonResponse(CUSTOM_FALSE(111, "Hash-not ADMIN"), safe=True)

            else:
                try:
                    user_ids = tuple(set(incoming_data['user_id']))
                                            
                except Exception as ex:
                    return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)

                else:
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-At least one id required"), safe=True)

                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()
                        for id in user_ids:
                            try:
                                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))
                                                        
                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                                        
                            else:
                                if(len(coordinator_ref) > 0):
                                    self.data_returned['data'][id] = self.AMBIGUOUS_404("USER already CORDINATOR")

                                else:
                                    user_credential_ref = User_Credential.objects.filter(user_credential_id = int(id))
                                    if(len(user_credential_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-USER id")

                                    else:
                                        user_credential_ref = user_credential_ref[0]
                                        coordinator_ref_new = Coordinator(user_credential_id = user_credential_ref)
                                        coordinator_ref_new.save()
                                        self.data_returned['data'][id] = self.TRUE_CALL(data = {"coordinator" : coordinator_ref_new.data['coordinator_id']})

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
            if('user_id' in incoming_data.keys()): # force fetch
                try:
                    user_ids = tuple(set(incoming_data["user_id"]))
                                    
                except Exception as ex:
                    return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)

                else:
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                        
                    else:
                        data = self.check_authorization("user")
                        # from parent
                        if(data[0] == False):
                            return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

                        else:
                            self.data_returned['data'] = dict()
                            temp = dict()
                                                
                            if(0 in user_ids):
                                coordinator_ref_all = Coordinator.objects.all()
                                if(len(coordinator_ref_all) < 1):
                                    self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Coordinator Tray")
                                    return JsonResponse(self.data_returned, safe=True)

                                else:
                                    coordinator_serialized_all = Coordinator_Serializer(coordinator_ref_all, many=True).data
                                    self.data_returned['data'][0] = self.TRUE_CALL(data = coordinator_ref_all)

                            else:
                                for id in user_ids:
                                    try:
                                        coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))
                                            
                                    except Exception as ex:
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                    else:
                                        if(len(coordinator_ref) < 1):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(103, "Invalid-Coordinate id")
                                                                
                                        else:
                                            coordinator_ref = coordinator_ref[0]
                                            coordinator_serialized = Coordinator_Serializer(coordinator_ref, many=False).data
                                            self.data_returned['data'][id] = self.TRUE_CALL(data = coordinator_serialized)
                                
            else: # self fetch
                data = self.check_authorization("user")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                    
                else:
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                    if(len(coordinator_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(103, "NotFound-USER not COORDINATOR"), safe=True)
                                        
                    else:
                        coordinator_ref = coordinator_ref[0]
                        coordinator_serialized = Coordinator_Serializer(coordinator_ref, many=False).data
                        self.data_returned = self.TRUE_CALL(data = coordinator_serialized)
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def edit(self, incoming_data):
        self.data_returned['action'] += "-EDIT"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']

        except Exception as ex:
            return JsonResponse(MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("admin", "cagp")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, f"Hash-{data[1]}"), safe=True)
                                
            else:
                if('updates' not in incoming_data.keys()):
                    return JsonResponse(self.MISSING_KEY('Updates required'), safe=True)

                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    updates = tuple(incoming_data['updates'])
                    if(len(updates) < 1):
                        self.data_returned['data'] = self.CUSTOM_FALSE(151, "Empty-At least one update required")
                        return JsonResponse(self.data_returned, safe=True)
                                    
                    else:
                        for update in updates:
                            try:
                                key = f"{int(update['coordinator_id'])}_{int(update['subject_id'])}"
                                if(int(update['subject_id']) < 0):
                                    update['subject_id'] = int(update['subject_id'])*(-1)
                                    flag = False
                                else:
                                    flag = True
                                coordinator_ref = Coordinator.objects.filter(coordinator_id = int(update['coordinator_id']))
                                subject_ref = Subject.objects.filter(subject_id = int(update['subject_id']))
                                                        
                            except Exception as ex:
                                self.data_returned['data'][key] = self.CUSTOM_FALSE(408, "DataType-{str(ex)}")
                                                        
                            else:
                                if(len(coordinator_ref) < 1):
                                    self.data_returned['data'][key] = self.CUSTOM_FALSE(114, "Invalid-Coordinator id")

                                else:
                                    if(len(subject_ref) < 1):
                                        self.data_returned['data'][key] = self.CUSTOM_FALSE(114, "Invalid-Subject id")

                                    else:
                                        coordinator_ref = coordinator_ref[0]
                                        subject_ref = subject_ref[0]
                                        many_to_many_ref = Subject_Coordinator_Int.objects.filter(coordinator_id = coordinator_ref.coordinator_id,
                                                                                                    subject_id = subject_ref.subject_id)
                                        if(flag == True): # create pair
                                            if(len(many_to_many_ref) > 0):
                                                self.data_returned['data'][key] = self.CUSTOM_FALSE(404, "Pair-Exists Coordinator<=>Subject")

                                            else:
                                                many_to_many_ref_new = Subject_Coordinator_Int(coordinator_id = coordinator_ref,
                                                                                                subject_id = subject_ref)
                                                many_to_many_ref_new.save()
                                                self.data_returned['data'][key] = self.TRUE_CALL(message = "COORDINATE<=>SUBJECT Created")
                                                            
                                        else: # remove pair
                                            if(len(many_to_many_ref) < 1):
                                                self.data_returned['data'][key] = self.CUSTOM_FALSE(404, "Pair-Not Exist Coordinator<=>Subject")

                                            else:
                                                many_to_many_ref = many_to_many_ref[0]
                                                many_to_many_ref.delete()
                                                self.data_returned['data'][key] = self.TRUE_CALL(message = "COORDINATE<=>SUBJECT Deleted")
            
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
            if('user_id' in incoming_data.keys()): # force delete
                try:
                    user_ids = tuple(set(incoming_data["user_id"]))
                                    
                except Exception as ex:
                    return JsonResponse(self.AMBIGUOUS_404(ex), safe=True)
                                    
                else:
                    if(len(user_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id reqired"), safe=True)

                    else:
                        data = self.check_authorization("admin", "capg") # Coordinators can be removed by admins
                        if(data[0] == False):
                            return JsonResponse(self.CUSTOM_FALSE(102, f"Hash-{data[1]}"), safe=True)
                                            
                        else:
                            self.data_returned['data'] = dict()
                            temp = dict()
                            for id in user_ids:
                                try:
                                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(id))

                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                else:
                                    if(len(coordinator_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(103, "Invalid-Coordinate id")

                                    else:
                                        coordinator_ref = coordinator_ref[0]
                                        coordinator_ref.delete()
                                        self.data_returned['data'][id] = self.TRUE_CALL()
                                
            else: # self delete
                data = self.check_authorization("user")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                    
                else:
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                    if(len(coordinator_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(103, "NotFound-USER not COORDINATOR"), safe=True)
                                        
                    else:
                        coordinator_ref = coordinator_ref[0]
                        coordinator_ref.delete()
                        self.data_returned = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Subject_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()

    @overrides
    def method_get(self):
        self.data_returned['action'] = "GET"
        subject_ref = Subject.objects.all().exclude(prime=True)
        if(len(subject_ref) < 1):
            return JsonResponse(self.CUSTOM_FALSE(151, "Empty-SUBJECT Tray"), safe=True)
        
        else:
            subject_serialized = Subject_Serializer(subject_ref, many=True).data
            self.data_returned = self.TRUE_CALL(data = subject_serialized)
        
        return JsonResponse(self.data_returned, safe=True)

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
            data = self.check_authorization("admin") # admin + coordinators can add or remove subjects
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not ADMIN"), safe=True)
                                
            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(103, "NotFound-USER not COORDINATOR"), safe=True)

                else:
                    try:
                        incoming_data['subject_name'] = incoming_data['subject_name'].upper()
                        incoming_data['subject_description'] = incoming_data['subject_description'].lower()
                        subject_ref = Subject.objects.filter(subject_name__contains = incoming_data['subject_name'])

                    except Exception as ex:
                        return JsonResponse(MISSING_KEY(ex), safe=True)

                    else:
                        if(len(subject_ref) < 1): # new subject
                            try: # some special job
                                name = incoming_data['subject_name'].split()
                                name = [word[0] for word in name]
                                name = "".join(name)
                                temp = Subject.objects.filter(subject_name__icontains = name)
                                if(len(temp) > 0):
                                    temp = temp[0]
                                    temp = int(temp.subject_name.split(name)[1]) + 1
                                else:
                                    temp = 1
                                                
                            except Exception as ex:
                                print(f"[x] SUBJECT CREATION - NAMING - {str(ex)}")
                                                
                            else:
                                incoming_data['subject_name'] = f"{incoming_data['subject_name']} {name}{temp}"
                            
                            subject_de_serialized = Subject_Serializer(data=incoming_data)
                            if(subject_de_serialized.is_valid()):
                                subject_de_serialized.save()
                                subject_ref = Subject.objects.get(subject_id = int(subject_de_serialized.data['subject_id']))
                                coordinator_ref = coordinator_ref[0]
                                many_to_many_ref = Subject_Coordinator_Int.objects.filter(subject_id = subject_ref.subject_id, coordinator_id = coordinator_ref.coordinator_id)
                                if(len(many_to_many_ref) > 0):
                                    return JsonResponse(self.CUSTOM_FALSE(119, "Pair-Exists Coordinator <=> Subject"), safe=True)

                                else:
                                    many_to_many_ref_new = Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref)
                                    many_to_many_ref_new.save()
                                    self.data_returned = self.TRUE_CALL(data = {"subject" : many_to_many_ref_new.data['subject_id'], "coordinator" : many_to_many_ref_new.data['coordinator_id']})

                            else:
                                return JsonResponse(self.JSON_PARSER_ERROR(f"{subject_de_serialized.errors}"), safe=True)

                        else: # old subject but maybe new admin coordinator
                            coordinator_ref = coordinator_ref[0]
                            subject_ref = subject_ref[0]
                            many_to_many_ref = Subject_Coordinator_Int.objects.filter(subject_id = subject_ref.subject_id, coordinator_id = coordinator_ref.coordinator_id)
                            if(len(many_to_many_ref) > 0):
                                return JsonResponse(self.CUSTOM_FALSE(119, "Pair-Exists Coordinator <=> Subject"), safe=True)
                                
                            else:
                                many_to_many_ref_new = Subject_Coordinator_Int(subject_id = subject_ref, coordinator_id = coordinator_ref)
                                many_to_many_ref_new.save()
                                self.data_returned = self.TRUE_CALL(data = {"subject" : many_to_many_ref_new.data['subject_id'], "coordinator" : many_to_many_ref_new.data['coordinator_id']})

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            subject_ids = tuple(set(incoming_data['subject_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            if(len(subject_ids) < 1):
                return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                
            else:
                data = self.check_authorization("user") # every one can see subject data
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    if(0 in subject_ids):
                        subject_ref = Subject.objects.all()
                        if(len(subject_ref) < 1):
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-SUBJECT Tray")
                            return JsonResponse(self.data_returned, safe=True)
                                            
                        else:
                            subject_serialized = Subject_Serializer(subject_ref, many=True).data
                            self.data_returned['data'][0] = self.TRUE_CALL(data = subject_serialized)

                    else:
                        for id in subject_ids:
                            try:
                                subject_ref = Subject.objects.filter(subject_id = int(id))
                                                
                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(408, "DataType-{str(ex)}")

                            else:
                                if(len(subject_ref) < 1):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(107, "Invalid-Subject id")

                                else:
                                    subject_ref = subject_ref[0]
                                    subject_serialized = Subject_Serializer(subject_ref, many=False).data
                                    self.data_returned['data'][id] = self.TRUE_CALL(data = subject_serialized)

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
            return JsonResponse(MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("admin") # admin + coordinators can add or remove subjects
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not ADMIN"), safe=True)
                                
            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(103, "NotFound-USER not COORDINATOR"), safe=True)
                    
                else:
                    try:
                        subject_ref_self = Subject.objects.filter(subject_id = incoming_data['subject_id'])
                                        
                    except Exception as ex:
                        return JsonResponse(self.MISSING_KEY(ex), safe=True)

                    else:
                        if(len(subject_ref_self) < 1):
                            return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Subject id"), safe=True)

                        else:
                            subject_ref_self = subject_ref_self[0]
                            try:
                                incoming_data['subject_name'] = incoming_data['subject_name'].upper()
                                incoming_data['subject_description'] = incoming_data['subject_description'].lower()
                                subject_ref = Subject.objects.filter(subject_name__icontains = incoming_data['subject_name'])
                                        
                            except Exception as ex:
                                return JsonResponse(self.MISSING_KEY(ex), safe=True)
                                        
                            else:
                                if(len(subject_ref) < 1):
                                    pass
                                                    
                                else: # old subject renaming
                                    subject_ref = subject_ref[0]
                                    if(subject_ref.subject_id != subject_ref_self.subject_id):
                                        return JsonResponse(self.CUSTOM_FALSE(402, "Found-Subject Name Exists"), safe=True)
                                                        
                                    else:
                                        pass
                                                    
                                try: # some special job
                                    name = incoming_data['subject_name'].split()
                                    name = [word[0] for word in name]
                                    name = "".join(name)
                                    temp = Subject.objects.filter(subject_name__contains = name)
                                    if(len(temp) > 0):
                                        temp = temp[0]
                                        temp = int(temp.subject_name.split(name)[1]) + 1
                                    else:
                                        temp = 1
                                                            
                                except Exception as ex:
                                    print(f"[x] SUBJECT CREATION - NAMING - {str(ex)}")
                                                            
                                else:
                                    incoming_data['subject_name'] = f"{incoming_data['subject_name']} {name}{temp}"
                                    subject_de_serialized = Subject_Serializer(subject_ref_self, data=incoming_data)
                                    if(subject_de_serialized.is_valid()):
                                        subject_de_serialized.save()
                                        self.data_returned = self.TRUE_CALL(data = {"subject" : subject_de_serialized.data['subject_id']})

                                    else:
                                        return JsonResponse(self.CUSTOM_FALSE(402, f"Serialize-{subject_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            subject_ids = tuple(set(incoming_data['subject_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            if(len(subject_ids) < 1):
                return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id is required'"), safe=True)

            else:
                data = self.check_authorization("admin", "alpha") # admin + alpha + coordinators can remove subjects
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(111, f"Hash-{data[1]}"), safe=True)

                else:
                    coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                    if(len(coordinator_ref) < 1):
                        return JsonResponse(CUSTOM_FALSE(103, "NotFound-ADMIN not COORDINATOR"), safe=True)

                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()
                        for id in subject_ids:
                            try:
                                subject_ref = Subject.objects.filter(subject_id = int(id))

                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                                
                            else:
                                if(len(subject_ref) < 1):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(107, "Invalid-Subject id")

                                else:
                                    subject_ref = subject_ref[0]
                                    subject_ref.delete()
                                    self.data_returned['data'][id] = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Forum_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()

    @overrides
    def create(self, incoming_data):
        self.data_returned['action'] += "-CREATE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self..token = incoming_data['hash']
            incoming_data = incoming_data['data']

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("user") # only coordinator can add posts

            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(404, "NotFound-USER not COORDINATOR"), safe=True)
                                    
                else:
                    # coordinator_ref = coordinator_ref[0]
                    forum_de_serialized = Forum_Serializer(data = incoming_data)
                    forum_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    if(forum_de_serialized.is_valid()):
                        forum_de_serialized.save()
                        self.data_returned = self.TRUE_CALL(data ={"forum" : forum_de_serialized.data['forum_id']})
                                        
                    else:
                        return JsonResponse(self.CUSTOM_FALSE(405, f"Serialize-{forum_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            forum_ids = tuple(set(incoming_data['forum_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(len(forum_ids) < 1):
                return JsonResponse(self.CUSTOM_FALSE(151, 'Empty-Atleast one id required'), safe=True)

            else:
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    for id in forum_ids:
                        try:
                            forum_ref = Forum.objects.filter(forum_id = int(id))
                                            
                        except Exception as ex:
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(408, "DataType-{str(ex)}")
                                            
                        else:
                            if(len(forum_ref) < 1):
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-Forum ID")

                            else:
                                forum_ref = forum_ref[0]
                                forum_serialized = Forum_Serializer(forum_ref, many=False).data
                                replies_for_forum = Reply.objects.filter(forum_id = forum_ref.forum_id)
                                reply_list = list()
                                if(len(replies_for_forum) > 0):
                                    for reply in replies_for_forum:
                                        reply_list.append(reply.reply_id)

                                self.data_returned['data'][id] = self.TRUE_CALL(data = {"forum" : forum_serialized, "reply" : reply_list})

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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(404, "NotFound-USER not COORDINATOR"), safe=True)
                                    
                else:
                    try:
                        forum_ref = Forum.objects.filter(forum_id = incoming_data['forum_id'])
                                        
                    except Exception as ex:
                        return JsonResponse(self.MISSING_KEY(ex), safe=True)
                                        
                    else:
                        if(len(forum_ref) < 1):
                            return JsonResponse(self.CUSTOM_FALSE(114, "Invalid-Forum ID"), safe=True)

                        else:
                            forum_ref = forum_ref[0]
                            forum_de_serialized = Forum_Serializer(forum_ref, data = incoming_data)
                            if(forum_de_serialized.is_valid()):
                                forum_de_serialized.save()
                                self.data_returned = self.TRUE_CALL(data = {"forum" : forum_de_serialized.data['forum_id']})
                                        
                            else:
                                return JsonResponse(self.CUSTOM_FALSE(405, f"Serialize-{forum_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            forum_ids = tuple(set(incoming_data['forum_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(forum_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)

                else:
                    if(len(coordinator_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "NotFound-USER not COORDINATOR"), safe=True)

                    else:
                        self.data_returned['data'] = dict()
                        temp = dict()
                        if(0 in forum_ids): # wholesale delete user+coordinator+admin+alpha
                            data = self.check_authorization("admin", "alpha") # only for admin + alpha
                            if(data[0] == False):
                                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not ADMIN ALPHA"), safe=True)
                                                
                            else:
                                forum_ref_all = Forum.objects.all()
                                if(len(forum_ref_all) < 1):
                                    self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Operation-Forum tray empty")
                                    return JsonResponse(self.data_returned, safe=True)
                                                    
                                else:
                                    forum_ref_all.delete()
                                    self.data_returned['data'][0] = self.TRUE_CALL()

                        else: # id based delete user+coordinator
                            for id in forum_ids:
                                try:
                                    forum_ref = Forum.object.filter(forum_id = int(id))
                                                        
                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                                else:
                                    if(len(forum_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-FORUM id")
                                                            
                                    else:
                                        forum_ref = forum_ref[0]
                                        forum_ref.delete()
                                        self.data_returned['data'][id] = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Reply_Api(API_Prime, Authorize):
    
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
                reply_de_serialized = Reply_Serializer(data = incoming_data)
                user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                reply_de_serialized.initial_data['user_credential_id'] = user_credential_ref.user_credential_id
                reply_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                if(reply_de_serialized.is_valid()):
                    reply_de_serialized.save()
                    self.data_returned = self.TRUE_CALL(data = {"reply" : reply_de_serialized.data['reply_id'], "forum" : reply_de_serialized.data['forum_id']})

                else:
                    return JsonResponse(self.CUSTOM_FALSE(404, f"Serialize-{reply_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            reply_ids = tuple(set(incoming_data['reply_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                self.data_returned['data'] = dict()
                temp = dict()
                for id in reply_ids:
                    try:
                        reply_ref = Reply.objects.filter(reply_id = int(id))
                                        
                    except Exception as ex:
                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                        
                    else:
                        if(len(reply_ref) < 1):
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-Reply Id")

                        else:
                            reply_ref = reply_ref[0]
                            reply_serialized = Reply_Serializer(reply_ref, many = False).data
                            self.data_returned['data'][id] = self.TRUE_CALL(data = reply_serialized)

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
                return JsonResponse(self.CUSTOM_FALSE(102, "ERROR-Hash-not USER"), safe=True)

            else:
                user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                try:
                    reply_ref = Reply.objects.filter(user_credential_id = user_credential_ref.user_credential_id,
                                                    reply_id = int(incoming_data['reply_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)
                                    
                else:
                    if(len(reply_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Reply does not belong to USER"), safe=True)
                                        
                    else:
                        reply_ref = reply_ref[0]
                        reply_de_serialized = Reply_Serializer(reply_ref, data = incoming_data)
                        if(reply_de_serialized.is_valid()):
                            reply_de_serialized.save()
                            self.data_returned = self.TRUE_CALL(data = {"reply" : reply_de_serialized.data['reply_id'], "forum" : reply_de_serialized.data['forum_id']})
                                    
                        else:
                            return JsonResponse(self.CUSTOM_FALSE(403, f"Serialize-{reply_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            reply_ids = tuple(set(incoming_data['reply_id']))

        except Exception as ex:
            return JsonResponse(MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                self.data_returned['data'] = dict()
                temp = dict()
                for id in reply_ids:
                    try:
                        reply_ref = Reply.objects.filter(reply_id = int(id))
                                        
                    except Exception as ex:
                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                    else:
                        if(len(reply_ref) < 1):
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Reply Id")

                        else:
                            reply_ref = reply_ref[0]
                            if(reply_ref.user_credential_id.user_credential_id != int(data[1])):
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "NotFound-Reply does not belong to USER")
                                                
                            else:
                                reply_ref.delete()
                                self.data_returned['data'][id] = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Lecture_Api(API_Prime, Authorize):
    
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
            data = self.check_authorization("user") # only coordinator can add lectures
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-USER not COORDINATOR"), safe=True)
                                    
                else:
                    # coordinator_ref = coordinator_ref[0]
                    lecture_de_serialized = Lecture_Serializer(data = incoming_data)
                    lecture_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    if(lecture_de_serialized.is_valid()):
                        lecture_de_serialized.save()
                        self.data_returned = self.TRUE_CALL(data = {"lecture" : lecture_de_serialized.data['lecture_id']})
                                        
                    else:
                        return JsonResponse(self.CUSTOM_FALSE(404, f"Serialise-{lecture_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            lecture_ids = tuple(set(incoming_data['lecture_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                if(len(lecture_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    for id in lecture_ids:
                        try:
                            lecture_ref = Lecture.objects.filter(lecture_id = int(id))
                                            
                        except Exception as ex:
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                            
                        else:
                            if(len(lecture_ref) < 1):
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Lecture ID")
                                                
                            else:
                                lecture_ref = lecture_ref[0]
                                lecture_serialized = Lecture_Serializer(lecture_ref, many=False).data
                                self.data_returned['data'][id] = self.TRUE_CALL(data = lecture_serialized)

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
                # user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                try:
                    lecture_ref = Lecture.objects.filter(lecture_id = int(incoming_data['lecture_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)

                else:
                    if(len(lecture_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Lecture Id"), safe=True)
                                        
                    else:
                        lecture_ref = lecture_ref[0]
                        lecture_de_serialized = Lecture_Serializer(lecture_ref, data = incoming_data)
                        if(lecture_de_serialized.is_valid()):
                            lecture_de_serialized.save()
                            self.data_returned = self.TRUE_CALL(data = {"lecture" : lecture_de_serialized.data['lecture_id']})

                        else:
                            return JsonResponse(self.JSON_PARSER_ERROR(f"{lecture_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            lecture_ids = tuple(set(incoming_data['lecture_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)

        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)

            else:
                self.data_returned['data'] = dict()
                temp = dict()
                for id in lecture_ids:
                    try:
                        lecture_ref = Lecture.objects.filter(lecture_id = int(id))
                                        
                    except Exception as ex:
                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                    else:
                        if(len(lecture_ref) < 1):
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Reply Id")

                        else:
                            lecture_ref = lecture_ref[0]
                            lecture_ref.delete()
                            self.data_returned['data'][id] = self.TRUE_CALL()

            return JsonResponse(self.data_returned, safe=True)

class Assignment_Api(API_Prime, Authorize):
    
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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-USER not COORDINATOR"), safe=True)
                                    
                else:
                    # coordinator_ref = coordinator_ref[0]
                    assignment_de_serialized = Assignment_Serializer(data = incoming_data)
                    assignment_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    if(assignment_de_serialized.is_valid()):
                        assignment_de_serialized.save()
                        self.data_returned = self.TRUE_CALL(data = {"assignment" : assignment_de_serialized.data['assignment_id']})
                                        
                    else:
                        return JsonResponse(self.JSON_PARSER_ERROR(f"{assignment_de_serialized.errors}"), safe=True)
                                
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            assignment_ids = tuple(set(incoming_data['assignment_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                if(len(assignment_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    for id in assignment_ids:
                        try:
                            assignment_ref = Assignment.objects.filter(assignment_id = int(id))
                                            
                        except Exception as ex:
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")

                        else:
                            if(len(assignment_ref) < 1):
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Assignment id")
                                                
                            else:
                                assignment_ref = assignment_ref[0]
                                assignment_serialized = Assignment_Serializer(assignment_ref, many=False).data
                                self.data_returned['data'][id] = self.TRUE_CALL(true = assignment_serialized)

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
                # user_credential_ref = User_Credential.objects.get(user_credential_id = int(data[1]))
                try:
                    assignment_ref = Assignment.objects.filter(assignment_id = int(incoming_data['assignment_id']))

                except Exception as ex:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"DataType-{str(ex)}"), safe=True)
                                    
                else:
                    if(len(assignment_ref) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-Assignment Id"), safe=True)
                                        
                    else:
                        assignment_ref = assignment_ref[0]
                        assignment_de_serialized = Assignment_Serializer(assignment_ref, data = incoming_data)
                        if(assignment_de_serialized.is_valid()):
                            assignment_de_serialized.save()
                            self.data_returned = self.TRUE_CALL(data = {"assignment" : assignment_de_serialized.data['assignment_id']})
                                    
                        else:
                            return JsonResponse(self.JSON_PARSER_ERROR(f"{assignment_de_serialized.errors}"), safe=True)

            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            assignment_ids = tuple(set(incoming_data['assignment_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                self.data_returned['data'] = dict()
                temp = dict()
                for id in assignment_ids:
                    try:
                        assignment_ref = Assignment.objects.filter(assignment_id = int(id))
                                        
                    except Exception as ex:
                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                        
                    else:
                        if(len(assignment_ref) < 1):
                            self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Assignment Id")
                                            
                        else:
                            assignment_ref = assignment_ref[0]
                            assignment_ref.delete()
                                                
                            self.data_returned['data'][id] = self.TRUE_CALL()
                                    
            return JsonResponse(self.data_returned, safe=True)

class Post_Api(API_Prime, Authorize):
    
    def __init__(self):
        super().__init__()
    
    @overrides
    def method_get(self):
        post_ref_all = Post.objects.filter(prime=False).order_by('-post_id')
        if(len(post_ref_all) < 1):
            return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Post tray"), safe=True)
        
        else:
            post_serialized = Post_Serializer(data = post_ref_all, many=True).data
            self.data_returned = self.TRUE_CALL(data = post_serialized)

        return JsonResponse(self.data_returned, safe=True)

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
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-USER not COORDINATOR"), safe=True)
                                    
                else:
                    post_de_serialized = Post_Serializer(data = incoming_data)
                    post_de_serialized.initial_data['user_credential_id'] = int(data[1])
                    post_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    if(post_de_serialized.is_valid()):
                        post_de_serialized.save()
                        self.data_returned = self.TRUE_CALL(data = {"post" : post_de_serialized.data['post_id'], "user" : data[1]})
                                        
                    else:
                        return JsonResponse(self.CUSTOM_FALSE(403, f"Serialize-{post_de_serialized.errors}"), safe=True)
                            
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def read(self, incoming_data):
        self.data_returned['action'] += "-READ"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            post_ids = tuple(set(incoming_data['post_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                if(len(post_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    if(0 not in post_ids): # selective fetch
                        for id in post_ids:
                            try:
                                post_ref = Post.objects.filter(post_id = int(id))
                                                
                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                                
                            else:
                                if(len(post_ref) < 1):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Post id")

                                else:
                                    post_ref = post_ref[0]
                                    post_serialized = Post_Serializer(post_ref, many=False).data
                                    self.data_returned['data'][id] = self.TRUE_CALL(data = post_serialized)
                                        
                    else: # fetch all
                        post_ref = Post.objects.all().order_by('-post_id')
                        if(len(post_ref) < 1):
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Post Tray")
                            return JsonResponse(self.data_returned, safe=True)
                                            
                        else:
                            post_serialized = Post_Serializer(post_ref, many=True).data
                            self.data_returned['data'][0] = self.TRUE_CALL(data = post_serialized)

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
            data = self..check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = int(data[1]))
                if(len(coordinator_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(404, "Invalid-USER not COORDINATOR"), safe=True)
                                    
                else:
                    try:
                        post_ref_self = Post.objects.filter(post_id = int(incoming_data['post_id']))
                                        
                    except Exception as ex:
                        return JsonResponse(self.CUSTOM_FALSE(403, f"DataType-{str(ex)}"), safe=True)
                                        
                    else:
                        if(len(post_ref_self) < 1):
                            return JsonResponse(self.CUSTOM_FALSE(403, "Invalid-POST id"), safe=True)
                                            
                        else:
                            post_ref_self = post_ref_self[0]
                            if(post_ref_self.user_credential_id != int(data[1])):
                                return JsonResponse(self.AMBIGUOUS_404("USER<=>POST not authorized"), safe=True)
                                                
                            else:
                                post_de_serialized = Post_Serializer(post_ref_self, data = incoming_data)
                                if(post_de_serialized.is_valid()):
                                    post_de_serialized.save()
                                    self.data_returned = self.TRUE_CALL(data = {"post" : post_de_serialized.data['post_id'], "user" : data[1]})
                                                    
                                else:
                                    return JsonResponse(self.CUSTOM_FALSE(403, f"Serialize-{post_de_serialized.errors}"), safe=True)
                            
            return JsonResponse(self.data_returned, safe=True)

    @overrides
    def delete(self, incoming_data):
        self.data_returned['action'] += "-DELETE"
        self.clear()
        try:
            incoming_data = incoming_data['data']
            self.token = incoming_data['hash']
            post_ids = tuple(set(incoming_data['post_id']))

        except Exception as ex:
            return JsonResponse(self.MISSING_KEY(ex), safe=True)
                    
        else:
            data = self.check_authorization("user")
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-not USER"), safe=True)
                                
            else:
                if(len(post_ids) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Atleast one id required"), safe=True)
                                    
                else:
                    self.data_returned['data'] = dict()
                    temp = dict()
                    if(0 not in post_ids): # selective fetch only to be done to self or by prime_admin
                        for id in post_ids:
                            try:
                                post_ref = Post.objects.filter(post_id = int(id))
                                                
                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"DataType-{str(ex)}")
                                                
                            else:
                                if(len(post_ref) < 1):
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Invalid-Post id")

                                else:
                                    post_ref = post_ref[0]
                                    if(post_ref.user_credential_id == int(data[1])):
                                        flag = True
                                    else:
                                        data = self.check_authorization("admin", "alpha")
                                        if(data[0] == True):
                                            flag = True
                                        else:
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(404, "Hash-not ADMIN ALPHA")
                                            flag = False
                                                        
                                    if(flag == True):
                                        if(post_ref.video_id not in (None,"")):
                                            post_ref.video_id.delete() # more here on video operations
                                        if(post_ref.forum_id not in (None,"")):
                                            post_ref.forum_id.delete()
                                        if(post_ref.lecture_id not in (None,"")):
                                            post_ref.lecture_id.delete()
                                        if(post_ref.assignment_id not in (None,"")):
                                            post_ref.assignment_id.delete()
                                                            
                                        post_ref.delete()
                                        self.data_returned['data'][id] = self.TRUE_CALL()

                    else: # delete all only by admin + alpha
                        data = self.check_authorization("admin", "alpha")
                        if(data[0] == True):
                            post_ref_all = Post.objects.all()
                            if(len(post_ref_all) < 1):
                                self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Post Tray")
                                return JsonResponse(self.data_returned, safe=True)
                                                
                            else:
                                for post_ref in post_ref_all:
                                    if(post_ref.video_id not in (None,"")):
                                        post_ref.video_id.delete() # more here on video operations
                                    if(post_ref.forum_id not in (None,"")):
                                        post_ref.forum_id.delete()
                                    if(post_ref.lecture_id not in (None,"")):
                                        post_ref.lecture_id.delete()
                                    if(post_ref.assignment_id not in (None,"")):
                                        post_ref.assignment_id.delete()
                                                            
                                    post_ref.delete()
                                    self.data_returned['data'][0] = self.TRUE_CALL()

                        else:
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(404, "Hash-not ADMIN ALPHA")
                            return JsonResponse(self.data_returned, safe=True)

            return JsonResponse(self.data_returned, safe=True)

# ----------------------------------------------

coordinator = Coordinator_Api()
subject = Subject_Api()

forum = Forum_Api()
reply = Reply_Api()
lecture = Lecture_Api()
assignment = Assignment_Api()

post = Post_Api()

# ----------------------------------------------

# ---------------------------------------------VIEW SPACE-------------------------------------------------------
