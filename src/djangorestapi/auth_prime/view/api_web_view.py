from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.contrib import messages

# --------------------------------------------------------------------------

from auth_prime.models import Api_Token

from user_personal.models import Notification
from user_personal.serializer import Notification_Serializer

from auth_prime.important_modules import Cookie, create_password_hashed, random_generator

# ------------------------------------------------------------
class API_Web_View(View):
    def __init__(self):
        super().__init__()

    def get(self, request, word=None):
        cookie = Cookie()

        if word in (None, ""):
            data_returned = dict()
            isAuthorizedAPI = cookie.check_authentication_info(request)
            if isAuthorizedAPI[0]:
                api_ref = Api_Token.objects.get(pk=isAuthorizedAPI[1])
                data_returned["user"] = api_ref.name.upper()
                data_returned["AWT"] = api_ref.hash
                data_returned["endpoint"] = api_ref.endpoint
                data_returned["pinned"] = Notification_Serializer(
                    Notification.objects.filter(prime=True).order_by("-pk"), many=True
                ).data
                return render(request, "auth_prime/index.html", data_returned)
            else:
                return render(request, "auth_prime/signin.html")
        elif word.lower() == "signup":
            isAuthorizedAPI = cookie.check_authentication_info(request)
            if isAuthorizedAPI[0]:
                return redirect("API_TOKEN", word="")
            else:
                return render(request, "auth_prime/signup.html")
        else:
            return redirect("API_TOKEN", word="")

    def post(self, request, word=None):
        cookie = Cookie()

        data_returned = dict()
        if word in (None, ""):
            return redirect("API_TOKEN", word="")
        else:
            temp = dict(request.POST)
            if word.lower() == "signup":
                keys = ("user_f_name", "user_l_name", "user_email", "user_password", "api_endpoint")

                try:
                    data = create_password_hashed(temp["user_password"][0])
                except Exception as ex:
                    messages.add_message(request, messages.INFO, str(ex))
                    return render(request, "auth_prime/signup.html", data_returned)
                else:
                    try:
                        api_ref = Api_Token(
                            name=f"{temp['user_f_name'][0]} {temp['user_l_name'][0]}",
                            email=f"{temp['user_email'][0].lower()}",
                            password=data,
                            hash=random_generator(),
                            endpoint=temp["api_endpoint"][0],
                        )
                        api_ref.save()
                    except Exception as ex:
                        print("-" * 25)
                        print(f"[.] API TOKEN GENERATION : UNSUCCESSFUL")
                        print(f"[x] Exception : {str(ex)}")
                        print("-" * 25)
                        return redirect("API_TOKEN", word="")
                    else:
                        print("-" * 25)
                        print(f"[.] API TOKEN GENERATION : SUCCESSFUL")
                        print("-" * 25)
                        data_returned["user"] = api_ref.name.upper()
                        data_returned["AWT"] = api_ref.hash
                        data_returned["endpoint"] = api_ref.endpoint
                        data_returned["pinned"] = Notification_Serializer(
                            Notification.objects.filter(prime=True).order_by("-pk"), many=True
                        ).data
                        return cookie.set_authentication_info(
                            request=request, file_path="auth_prime/index.html", data=data_returned, pk=api_ref.pk
                        )
            elif word.lower() == "signin":
                try:
                    data = create_password_hashed(temp["user_password"][0])
                except Exception as ex:
                    messages.add_message(request, messages.INFO, str(ex))
                    return render(request, "auth_prime/signin.html", data_returned)
                else:
                    try:
                        api_ref = Api_Token.objects.get(email=f"{temp['user_email'][0].lower()}", password=data)
                    except Api_Token.DoesNotExist:
                        messages.add_message(request, messages.INFO, "Wrong Credentials ! Try again !")
                        return render(request, "auth_prime/signin.html", data_returned)
                    else:
                        data_returned["user"] = api_ref.name.upper()
                        data_returned["AWT"] = api_ref.hash
                        data_returned["endpoint"] = api_ref.endpoint
                        data_returned["pinned"] = Notification_Serializer(
                            Notification.objects.filter(prime=True).order_by("-pk"), many=True
                        ).data
                        return cookie.set_authentication_info(
                            request=request, file_path="auth_prime/index.html", data=data_returned, pk=api_ref.pk
                        )
            elif word.lower() == "signout":
                return cookie.revoke_authentication_info(request, "auth_prime/signin.html", data_returned)
            else:
                return redirect("API_TOKEN", word="")
