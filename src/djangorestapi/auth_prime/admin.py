from django.contrib import admin
from auth_prime.models import User_Credential, Admin_Privilege, Admin_Credential, Token_Table
# Register your models here.

admin.site.register(User_Credential)
admin.site.register(Admin_Privilege)
admin.site.register(Admin_Credential)
admin.site.register(Token_Table)