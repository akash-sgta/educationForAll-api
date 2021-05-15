from django.contrib import admin

# -----------------------------------------------

from auth_prime.models import (
    User_Credential,
    User_Profile,
    Admin_Privilege,
    Admin_Credential,
    Admin_Cred_Admin_Prev_Int,
    User_Token_Table,
    Api_Token_Table,
    Image,
)

# -----------------------------------------------

admin.site.register(User_Credential)
admin.site.register(User_Token_Table)

admin.site.register(User_Profile)
admin.site.register(Image)

admin.site.register(Admin_Credential)
admin.site.register(Admin_Privilege)
admin.site.register(Admin_Cred_Admin_Prev_Int)

admin.site.register(Api_Token_Table)