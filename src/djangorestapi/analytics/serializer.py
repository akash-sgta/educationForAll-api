from rest_framework import serializers

# ---------------------------------------------------------------

from analytics.models import Ticket
from analytics.models import Log

# ---------------------------------------------------------------

class Ticket_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            'ticket_id',
            'ticket_body',
            'user_credential_id',
            'made_date',
            'prime'
        )

class Log_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = (
            'log_id',
            'log_body',
            'made_date',
            'api_token_id'
        )
