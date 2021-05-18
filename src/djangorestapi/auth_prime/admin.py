from django.contrib import admin

# -----------------------------------------------

from auth_prime.models import (
    User,
    Profile,
    Image,
    Privilege,
    Admin,
    Admin_Privilege,
    User_Token,
    Api_Token,
)

# -----------------------------------------------

admin.site.register(Image)
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(User_Token)

admin.site.register(Admin)
admin.site.register(Privilege)
admin.site.register(Admin_Privilege)

admin.site.register(Api_Token)
