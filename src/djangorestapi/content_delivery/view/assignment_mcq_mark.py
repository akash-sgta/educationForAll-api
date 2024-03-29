from auth_prime.important_modules import am_I_Authorized
from content_delivery.models import AssignmentMCQ, Coordinator
from content_delivery.serializer import AssignmentMCQ_Serializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from user_personal.models import SubmissionMCQ
from user_personal.serializer import SubmissionMCQ_Serializer

# ------------------------------------------------------------


class Assignment_Mark_View(APIView):

    renderer_classes = [JSONRenderer]

    def __init__(self):
        super().__init__()

    def get(self, request, pk_a=None, pk_s=None):  # TODO : Anyone can fetch marks data
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk_a not in (None, "") and pk_s not in (None, ""):
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    submission_ref = SubmissionMCQ.objects.get(assignment_ref=pk_a, pk=pk_s)
                except SubmissionMCQ.DoesNotExist:
                    data["success"] = False
                    data["message"] = "INVALID_ASSIGNMENT_SUBMISSION_PAIR"
                    return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                except ValueError or TypeError:
                    data["success"] = False
                    data["message"] = {"URL_FORMAT": "/api/content/multi_mark/<assignent_id>/<submission_id>"}
                    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data["success"] = True
                    data["data"] = SubmissionMCQ_Serializer(submission_ref, many=False).data
                    return Response(data=data, status=status.HTTP_202_ACCEPTED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "GET", "URL_FORMAT": "/api/content/multi_mark/<assignent_id>/<submission_id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk_a=None, pk_s=None):  # TODO : Only Coordinator can change marks
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        if pk_a not in (None, "") or pk_s not in (None, ""):  # TODO : Both have to be populated
            isAuthorizedUSER = am_I_Authorized(request, "USER")
            if isAuthorizedUSER[0] == False:
                data["success"] = False
                data["message"] = f"USER_NOT_AUTHORIZED"
                return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    coordinator_ref = Coordinator.objects.get(user_ref=isAuthorizedUSER[1])
                except Coordinator.DoesNotExist:
                    data["success"] = False
                    data["message"] = "USER_NOT_COORDINATOR"
                    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    if "marks" not in request.data.keys():
                        data["success"] = False
                        data["message"] = "KEY_VALUE_MISSING_JSON : marks"
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        marks = request.data["marks"]
                        try:
                            submission_ref = SubmissionMCQ.objects.get(assignment_ref=pk_a, pk=pk_s)
                        except SubmissionMCQ.DoesNotExist:
                            data["success"] = False
                            data["message"] = "INVALID_ASSIGNMENT_SUBMISSION_PAIR"
                            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
                        except ValueError or TypeError:
                            data["success"] = False
                            data["message"] = "INVALID_DATA_JSON"
                            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            try:
                                submission_ref.marks = int(marks)
                                submission_ref.checked = True
                            except ValueError or TypeError:
                                data["success"] = False
                                data["message"] = "MARKS_SHOULD_BE_INTEGER"
                                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                submission_ref.save()
                                data["success"] = True
                                data["data"] = SubmissionMCQ_Serializer(submission_ref, many=False).data
                                return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            data["success"] = False
            data["message"] = {"METHOD": "PUT", "URL_FORMAT": "/api/content/multi_mark/<assignent_id>/<submission_id>"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, pk=None):
        data = dict()

        isAuthorizedAPI = am_I_Authorized(request, "API")
        if not isAuthorizedAPI[0]:
            data["success"] = False
            data["message"] = "error:ENDPOINT_NOT_AUTHORIZED"
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

        temp = dict()

        data["Allow"] = "GET PUT OPTIONS".split()

        temp["Content-Type"] = "application/json"
        temp["Authorization"] = "Token JWT"
        temp["uauth"] = "Token JWT"
        data["HEADERS"] = temp.copy()
        temp.clear()

        data["name"] = "Assignment_Mark"

        temp["POST"] = {"marks": "Number"}
        temp["GET"] = None
        temp["PUT"] = {"marks": "Number"}
        temp["DELETE"] = None
        data["method"] = temp.copy()
        temp.clear()

        return Response(data=data, status=status.HTTP_200_OK)
