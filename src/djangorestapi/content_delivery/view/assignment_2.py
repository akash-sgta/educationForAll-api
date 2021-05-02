from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# ------------------------------------------------------------

from auth_prime.important_modules import (
        am_I_Authorized,
    )

from content_delivery.models import (
        Coordinator,
        Assignment,
    )
from content_delivery.serializer import (
        Assignment_Serializer,
    )

from user_personal.models import (
    Assignment_Submission_Int
)
from user_personal.serializer import (
    Assignment_Submission_Int_Serializer
)

# ------------------------------------------------------------

class Assignment_2_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()
    
    def get(self, request, pk_a=None, pk_s=None):
        data = dict()
        if(pk_a not in (None, "") and pk_s not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    one_ref = Assignment_Submission_Int.objects.get(assignment_id = pk_a, submission_id = pk_s)
                except Assignment_Submission_Int.DoesNotExist:
                    data['success'] = False
                    data['message'] = "item does not exist"
                    return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                except ValueError or TypeError:
                    data['success'] = False
                    data['message'] = {
                            'URL_FORMAT' : '/api/content/mark/<assignent_id>-<submission_id>'
                        }
                    return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    one_serialized = Assignment_Submission_Int_Serializer(one_ref).data
                    data['success'] = True
                    data['data'] = one_serialized
                    return Response(data = data, status=status.HTTP_202_ACCEPTED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'GET',
                'URL_FORMAT' : '/api/content/mark/<assignent_id>-<submission_id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk_a=None, pk_s=None):
        data = dict()
        if(pk_a not in (None, "") and pk_s not in (None, "")):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if(isAuthorizedUSER[0] == False):
                data['success'] = False
                data['message'] = f"error:USER_NOT_AUTHORIZED, message:{isAuthorizedUSER[1]}"
                return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                coordinator_ref = Coordinator.objects.filter(user_credential_id = isAuthorizedUSER[1])
                if(len(coordinator_ref) < 1):
                    data['success'] = False
                    data['message'] = "USER not COORDINATOR"
                    return Response(data = data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    try:
                        user_data = request.data
                        user_data["assignment_id"] = pk_a
                        if("marks" not in user_data.keys()):
                            data['success'] = False
                            data['message'] = "KEY_VALUE_MISSING_JSON : marks"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            one_ref = Assignment_Submission_Int.objects.get(assignment_id = pk_a, submission_id = pk_s)
                    except Assignment_Submission_Int.DoesNotExist:
                        data['success'] = False
                        data['message'] = "item does not exist"
                        return Response(data = data, status=status.HTTP_404_NOT_FOUND)
                    except ValueError or TypeError:
                        data['success'] = False
                        data['message'] = "INVALID_DATA_JSON"
                        return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        try:
                            one_ref.marks = int(user_data["marks"])
                        except ValueError or TypeError:
                            data['success'] = False
                            data['message'] = "MARKS need to be INTEGER"
                            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            one_ref.save()
                            data['success'] = True
                            data['data'] = Assignment_Submission_Int_Serializer(one_ref, many=False).data
                            return Response(data = data, status=status.HTTP_201_CREATED)
        else:
            data['success'] = False
            data['message'] = {
                'METHOD' : 'PUT',
                'URL_FORMAT' : '/api/content/mark/<assignent_id>?<submission_id>'
            }
            return Response(data = data, status=status.HTTP_400_BAD_REQUEST)
