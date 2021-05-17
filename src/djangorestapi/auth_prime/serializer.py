from rest_framework import serializers

# ---------------------------------------------------------------

from auth_prime.models import Profile, User, Privilege, Admin, Image, Api_Token

# ---------------------------------------------------------------


class Profile_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class Privilege_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Privilege
        fields = "__all__"


class Admin_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = "__all__"


class Image_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class Api_Token_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Api_Token
        fields = "__all__"


# ---------------------------------------------------------------
