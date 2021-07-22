from rest_framework import serializers

from analytics.models import Log, Permalink, Ticket

# ---------------------------------------------------------------


class Ticket_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class Log_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"


class Permalink_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Permalink
        fields = "__all__"
