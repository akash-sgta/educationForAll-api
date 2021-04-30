from rest_framework import serializers

# ---------------------------------------------------------------

from auth_prime.models import (
        User_Profile,
        User_Credential,
        Admin_Privilege,
        Admin_Credential,
        Image,
        Api_Token_Table
    )

# ---------------------------------------------------------------

class User_Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Profile
        fields = "__all__"

class User_Credential_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Credential
        fields = "__all__"

class Admin_Privilege_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Privilege
        fields = "__all__"

class Admin_Credential_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Credential
        fields = "__all__"

class Image_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

class Api_Token_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Api_Token_Table
        fields = "__all__"

# ---------------------------------------------------------------