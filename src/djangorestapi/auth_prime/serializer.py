from rest_framework import serializers
from auth_prime.models import User_Table,Admin_Table,Token_Table

# ---------------------------------------------------------------
# auth_prime

class User_Table_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Table
        fields = (
            'user_id',
            'user_f_name',
            'user_m_name',
            'user_l_name',
            'user_email',
            'user_password')

class Admin_Table_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Table
        fields = (
            'admin_id',
            'user_id')

class Token_Table_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Token_Table
        fields = (
            'token_id',
            'token_date_start',
            'token_date_end')

# ---------------------------------------------------------------