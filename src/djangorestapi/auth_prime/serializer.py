from rest_framework import serializers

# ---------------------------------------------------------------

from auth_prime.models import User_Profile
from auth_prime.models import User_Credential
from auth_prime.models import Admin_Privilege
from auth_prime.models import Admin_Credential

# ---------------------------------------------------------------

class User_Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = (
            'user_profile_id',
            'user_profile_headline',
            'user_bio',
            'user_english_efficiency',
            'user_git_profile',
            'user_linkedin_profile',
            'user_profile_pic',
            'user_roll_number',
            'prime',
            'made_date'
        )

class User_Credential_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Credential
        fields = (
            'user_credential_id',
            'user_profile_id',
            'user_f_name',
            'user_m_name',
            'user_l_name',
            'user_email',
            'user_password',
            'user_security_question',
            'user_security_answer'
            )

class Admin_Privilege_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Privilege
        fields = (
            "admin_privilege_id",
            "admin_privilege_name",
            "admin_privilege_description")

class Admin_Credential_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Credential
        fields = (
            'admin_credential_id',
            'user_credential_id',
            'prime')

# ---------------------------------------------------------------