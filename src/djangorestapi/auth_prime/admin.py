from django.contrib import admin
from auth_prime.models import User_Table, Admin_Privilege, Admin_Table, Token_Table
# Register your models here.

admin.site.register(User_Table)
admin.site.register(Admin_Privilege)
admin.site.register(Admin_Table)
admin.site.register(Token_Table)