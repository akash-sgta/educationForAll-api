from django.contrib import admin

# -----------------------------------------------

from auth_prime.models import User_Credential
from auth_prime.models import User_Profile
from auth_prime.models import Admin_Privilege
from auth_prime.models import Admin_Credential
from auth_prime.models import Admin_Cred_Admin_Prev_Int
from auth_prime.models import User_Token_Table
from auth_prime.models import  Api_Token_Table

# -----------------------------------------------

admin.site.register(User_Credential)
admin.site.register(User_Profile)

admin.site.register(Admin_Credential)
admin.site.register(Admin_Privilege)
admin.site.register(Admin_Cred_Admin_Prev_Int)

admin.site.register(User_Token_Table)
admin.site.register(Api_Token_Table)