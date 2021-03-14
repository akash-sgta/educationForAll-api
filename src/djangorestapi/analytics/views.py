from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from auth_prime.authorize import Authorize
from auth_prime.authorize import Cookie

from auth_prime.important_modules import API_Prime

from auth_prime.models import User_Credential
from auth_prime.models import Api_Token_Table

from analytics.models import Ticket
from analytics.models import Log

from analytics.serializer import Ticket_Serializer
from analytics.serializer import Log_Serializer

from overrides import overrides
from datetime import datetime

#------------------------------------------------------------------
# Create your views here.

class Ticket_Api(API_Prime, Authorize):
    
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
                return JsonResponse(self.CUSTOM_FALSE(102, "Hash-Not USER"), safe=True)

            else:
                ticket_de_serialized = Ticket_Serializer(data = incoming_data)
                ticket_de_serialized.initial_data['user_credential_id'] = int(data[1])
                ticket_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                if(ticket_de_serialized.is_valid()):
                    ticket_de_serialized.save()
                    self.data_returned = self.TRUE_CALL()
                else:
                    return JsonResponse(self.CUSTOM_FALSE(666,f'Ticket Not Submitted-{ticket_de_serialized.errors}'), safe=True)

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
            if('ticket_id' not in incoming_data.keys()): # self fetch
                return JsonResponse(self.CUSTOM_FALSE(666, "Ticket Id required"), safe=True)

            else: # fetching as an admin+alpha
                self.data_returned['data'] = dict()
                temp = dict()
                data = self.check_authorization("admin")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(113, f"Hash-{data[1]}"), safe=True)

                else:
                    ticket_ids = tuple(set(incoming_data['ticket_id']))
                    if(len(ticket_ids) < 1):
                        return JsonResponse(self.CUSTOM_FALSE(151, "Empty-At least one id required"), safe=True)
                                                
                    else:
                        if(0 in ticket_ids): # 0 -> fetch all
                            ticket_ref_all = Ticket.objects.all().order_by("-ticket_id")
                            if(len(ticket_ids) < 1):
                                self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Ticket tray empty")
                                return JsonResponse(self.data_returned, safe=True)
                                            
                            else:
                                ticket_serialized_all = Ticket_Serializer(ticket_ref_all, many=True).data
                                for ticket in ticket_serialized_all:
                                    key = int(ticket['ticket_id'])
                                    temp[key] = ticket
                                self.data_returned[0] = self.TRUE_CALL(temp.copy())
                                temp.clear()
                                        
                        else: # fetch using using ids
                            for id in ticket_ids:
                                try:
                                    ticket_ref = Ticket.objects.filter(user_credential_id = int(id))
                                                            
                                except Exception as ex:
                                    self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"Formatting-{str(ex)}")
                                                            
                                else:
                                    if(len(ticket_ref) < 1):
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-Ticket id")

                                    else:
                                        ticket_ref = ticket_ref[0]
                                        ticket_serialized = Ticket_Serializer(ticket_ref, many=False).data
                                        self.data_returned['data'][id] = self.TRUE_CALL(ticket_ref)

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
            data = self.check_authorization("admin") # only admin change applicable for now
            if(data[0] == False):
                return JsonResponse(self.CUSTOM_FALSE(102, f"Hash-{data[1]}"), safe=True)

            else:
                try:
                    ticket_ref = Ticket.objects.filter(ticket_id = int(incoming_data['ticket_id']))
                
                except:
                    return JsonResponse(self.CUSTOM_FALSE(408, f"Formatting-{str(ex)}"), safe=True)
                
                else:
                    ticket_de_serialized = Ticket_Serializer(ticket_ref, data = incoming_data)
                    if(ticket_de_serialized.is_valid()):
                        ticket_de_serialized.save()
                        self.data_returned = self.TRUE_CALL()
                        
                    else:
                        return JsonResponse(self.CUSTOM_FALSE(666, f"Invalid Format-{ticket_de_serialized.errors}"), safe=True)

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
            if('ticket_id' in incoming_data.keys()): # prime admin deleting others
                self.data_returned['data'] = dict()
                data = self.check_authorization("admin")
                if(data[0] == False):
                    return JsonResponse(self.CUSTOM_FALSE(111, data[1]), safe=True)
                                    
                else:
                    ticket_ids = tuple(set(incoming_data['ticket_id']))
                    if(0 in ticket_ids): # 0 -> delete all
                        ticket_ref_all = Ticket.objects.all()
                        if(len(ticket_ref_all) < 1):
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Ticket Tray empty")
                            return JsonResponse(self.data_returned, safe=True)
                                        
                        else:
                            ticket_ref_all.delete()
                            self.data_returned['data'][0] = self.TRUE_CALL()
                                    
                    else: # individual id deletes
                        for id in ticket_ids:
                            try:
                                if(int(id) == int(data[1])):
                                    self.data_returned['data'][id] = self.AMBIGUOUS_404("Empty-Ticket not found")

                                else:
                                    try:
                                        ticket_ref = Ticket.objects.filter(ticket_id = int(id))
                                                    
                                    except Exception as ex:
                                        self.data_returned['data'][id] = self.CUSTOM_FALSE(408, f"Data Type-{str(ex)}")
                                                    
                                    else:
                                        if(len(ticket_ref) < 1):
                                            self.data_returned['data'][id] = self.CUSTOM_FALSE(114, "Invalid-Ticket id")
                                                        
                                        else:
                                            ticket_ref = ticket_ref[0]
                                            ticket_ref.delete()
                                            self.data_returned['data'][id] = self.TRUE_CALL()
                                            
                            except Exception as ex:
                                self.data_returned['data'][id] = self.AMBIGUOUS_404(ex)
                                                        
            else:
                return JsonResponse(self.CUSTOM_FALSE(666, "Ticket id required"), safe=True)
            
            return JsonResponse(self.data_returned, safe=True)

class Log_Api(API_Prime, Authorize):
    
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
            token_ref = Api_Token_Table.filter.objects(user_key_private = self.token)
            if(len(token_ref) < 1):
                return JsonResponse(self.CUSTOM_FALSE(666, "Token not present in DB"), safe=True)

            else:
                token_ref = token_ref[0]
                log_de_serialized = Log_Serializer(data = incoming_data)
                log_de_serialized.initial_data['made_date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                log_de_serialized.initial_data['api_token_id'] = token_ref.pk
                if(log_de_serialized.is_valid()):
                    log_de_serialized.save()
                    self.data_returned = self.TRUE_CALL()
                else:
                    return JsonResponse(self.CUSTOM_FALSE(666,f'Log Not Submitted-{log_de_serialized.errors}'), safe=True)

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
            token_ref = Api_Token_Table.filter.objects(user_key_private = self.token)
            if(len(token_ref) < 1):
                return JsonResponse(self.CUSTOM_FALSE(666, "Token not present in DB"), safe=True)

            else:
                token_ref = token_ref[0]
                self_log_ref_all = Log.objects.filter(api_token_id = token_ref.pk).order_by('-pk')
                if(len(self_log_ref_all) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(151, "Empty-Log tray empty"), safe=True)
                                                
                else:
                    log_serialized = Log_Serializer(self_log_ref_all, many=True).data
                    self.data_returned = self.TRUE_CALL(data = log_serialized)

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
            if('log_id' in incoming_data.keys()): # prime admin deleting others
                self.data_returned['data'] = dict()
                token_ref = Api_Token_Table.filter.objects(user_key_private = self.token)
                if(len(token_ref) < 1):
                    return JsonResponse(self.CUSTOM_FALSE(666, "Token not present in DB"), safe=True)

                else:
                    token_ref = token_ref[0]
                    log_ids = tuple(set(incoming_data['log_id']))
                    if(0 in log_ids): # 0 -> delete all
                        log_ref_all = Log.objects.filter(api_token_id = token_ref.pk)
                        if(len(log_ref_all) < 1):
                            self.data_returned['data'][0] = self.CUSTOM_FALSE(151, "Empty-Ticket Tray empty")
                            return JsonResponse(self.data_returned, safe=True)
                                        
                        else:
                            log_ref_all.delete()
                            self.data_returned['data'][0] = self.TRUE_CALL()
                                    
                    else: # individual id deletes
                        for id in log_ids:
                            try:
                                log_ref = Log.objects.filter(log_id = int(id), api_token_id = token_ref.pk)
                            
                            except Exception as ex:
                                self.data_returned['data'][id] = self.CUSTOM_FALSE(666, f"DataType-{str(ex)}")
                            
                            else:
                                if(len(log_ref) < 1):
                                    self.data_returned['data'][id] = self.AMBIGUOUS_404("Empty-Log not found")

                                else:
                                    log_ref = log_ref[0]
                                    log_ref.delete()
                                    self.data_returned['data'][id] = self.TRUE_CALL()
                                                        
            else:
                return JsonResponse(self.CUSTOM_FALSE(666, "Log id required"), safe=True)
            
            return JsonResponse(self.data_returned, safe=True)


ticket = Ticket_Api()
log = Log_Api()

#------------------------------------------------------------------