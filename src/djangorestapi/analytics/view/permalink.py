from analytics.models import Permalink
from auth_prime.important_modules import am_I_Authorized
from django.shortcuts import render
from django.views import View
from rest_framework import status
from django.http import HttpResponseRedirect

# ------------------------------------------------------------


class Permalink_View(View):
    def __init__(self):
        super().__init__()

    def get(self, request, word=None):
        try:
            perm_ref = Permalink.objects.get(name=word)
        except Permalink.DoesNotExist:
            return render(request, "404.html", status=status.HTTP_404_NOT_FOUND)
        else:
            return HttpResponseRedirect(perm_ref.body)
