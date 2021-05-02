from django.shortcuts import render, redirect
from django.contrib import messages

# --------------------------------------------------------------------------

from auth_prime.models import (
        Api_Token_Table
    )

from auth_prime.important_modules import (
        Cookie,
        create_password_hashed,
        random_generator
    )

# ------------------------------------------------------------

# -------------------------USER_CREDENTIAL-----------------------------------

from auth_prime.view.user_credential import User_Credential_View as ucView

# -------------------------USER_PROFILE-----------------------------------

from auth_prime.view.user_profile import User_Profile_View as upView

# -------------------------ADMIN_CREDENTIAL-----------------------------------

from auth_prime.view.admin_credential import Admin_Credential_View as acView

# -------------------------ADMIN_PRIVILEGE-----------------------------------

from auth_prime.view.admin_privilege import Admin_Privilege_View as apView

# -------------------------USER_PROFILE_IMAGE-----------------------------------

from auth_prime.view.user_profile_image import User_Profile_Image_View as upiView

# ------------------------------------------------------------


# ------------------------------VIEW_SPACE-------------------------------------

template_PINNED = ['<span style="color: yellow;">[', ']</span>']

pinned = [
    "{}{}{}{}".format(template_PINNED[0], "dd-mm-yyyy", template_PINNED[1], "message")
]

def api_token_web(request, word=None):
    cookie = Cookie()
    data_returned = dict()

    data_returned['site_name'] = 'API'

    if(request.method == 'GET'):
        if(word != None):
            if(word.upper() == 'signin'.upper()):
                type = 'signin'.upper()
            else:
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
            
            try:
                data = create_password_hashed(temp['user_password'][0])
            except Exception as ex:
                messages.add_message(request, messages.INFO, str(ex))
                data_returned['type'] = 'signup'.upper()
                return render(request, 'auth_prime/api.html', data_returned)
            else:
                try:
                    api_new = Api_Token_Table(user_name = f"{temp[keys[0]][0]} {temp[keys[1]][0]}",
                                                user_email = f"{temp[keys[2]][0].lower()}",
                                                user_password = data,
                                                user_key_private = random_generator(),
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

            try:
                data = create_password_hashed(temp['user_password'][0])
            except Exception as ex:
                messages.add_message(request, messages.INFO, str(ex))
                data_returned['type'] = 'signin'.upper()
                return render(request, 'auth_prime/api.html', data_returned)
            else:
                try:
                    api_ref = Api_Token_Table.objects.filter(user_email = f"{temp[keys[0]][0].lower()}",
                                                                user_password = data)
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
        