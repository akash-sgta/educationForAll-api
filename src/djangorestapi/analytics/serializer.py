from rest_framework import serializers

# ---------------------------------------------------------------

from analytics.models import (
        Ticket,
        Log
    )

# ---------------------------------------------------------------

class Ticket_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"

class Log_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"