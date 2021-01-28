from rest_framework import serializers

from auth_prime.models import User_Profile, User_Credential, Admin_Privilege, Admin_Credential, Token_Table

# ---------------------------------------------------------------

class User_Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = (
            'user_profile_id',
            'user_profie_headline',
            'user_bio',
            'user_english_efficiency',
            'user_git_profile',
            'user_linkedin_profile',
            'user_profile_pic_url',
            'user_roll_number'
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
            'privilege_id_1',
            'privilege_id_2',
            'privilege_id_3')

class Token_Table_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Token_Table
        fields = (
            'token_id',
            'user_credential_id',
            'token_hash',
            'token_start',
            'token_end')

# ---------------------------------------------------------------