from django.db import models

from datetime import datetime

from utilities.pool import string2hashHex, randomGenerator, epochms2datetime, datetime2epochms
from utilities.constant import REFRESH_TOKEN_LIMIT, ACCESS_TOKEN_LIMIT

## ============================================================================= ##


class Identity(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=31, unique=True)
    password = models.CharField(max_length=255)
    created_on = models.PositiveBigIntegerField(blank=True, null=True)  # ms from epoch
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.created_on in (None, ""):  # fill once at creation of entity
            self.created_on = datetime2epochms(datetime.now())

        if self.password in (None, ""):
            raise ValueError("Password required")
        elif self.password[:4] == "md5_":
            pass
        else:
            self.password = string2hashHex(self.password)

        return super(Identity, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} | {self.username}"


class ActiveToken(models.Model):
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)  # Identity (1:N) ActiveToken

    device = models.CharField(max_length=127)
    unique_id = models.CharField(max_length=31, null=True, blank=True)

    accessT = models.CharField(max_length=31, null=True, blank=True)  # Access token length = 31
    a_till = models.PositiveBigIntegerField(null=True, blank=True)  # Access token limit in ms

    refreshT = models.CharField(max_length=255, null=True, blank=True)  # Refresh token length = 255
    r_till = models.PositiveBigIntegerField(null=True, blank=True)  # Access token limit in ms

    created_on = models.PositiveBigIntegerField(null=True, blank=True)  # ms from epoch
    last_logged = models.PositiveBigIntegerField(null=True, blank=True)  # ms from epoch

    def save(self, *args, **kwargs):
        if self.created_on in (None, ""):  # fill once at creation of entity
            self.created_on = datetime2epochms(datetime.now())

            self.refreshT = randomGenerator(length=225)
            self.r_till = datetime2epochms(datetime.now(), add_Days=REFRESH_TOKEN_LIMIT)

            self.unique_id = randomGenerator(onlyNum=True, length=31)

            self.accessT = randomGenerator(length=31)
            self.a_till = datetime2epochms(datetime.now(), add_minutes=ACCESS_TOKEN_LIMIT)

            self.last_logged = datetime2epochms(datetime.now())
        else:
            pass

        return super(ActiveToken, self).save(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        if datetime2epochms(datetime.now()) > self.r_till:  # time passed beyond refresh token time
            raise ValueError("Refresh limit exceeded")
        else:
            self.accessT = randomGenerator(length=31)
            self.a_till = datetime2epochms(datetime.now(), add_minutes=ACCESS_TOKEN_LIMIT)
            self.last_logged = datetime2epochms(datetime.now())

        return super(ActiveToken, self).save(*args, **kwargs)

    #    def login -> # FIX: WOrk on it

    def __str__(self):
        return f"{self.identity} - {self.device} | {self.unique_id}"


class BlacklistToken(models.Model):
    id = models.AutoField(primary_key=True)
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)  # Identity (1:N) BlacklistToken
    refreshT = models.CharField(max_length=255, null=True, blank=True)  # Refresh token length = 255
    created_on = models.PositiveBigIntegerField(null=True, blank=True)  # ms from epoch

    def save(self, *args, **kwargs):
        if self.created_on in (None, ""):  # fill once at creation of entity
            self.created_on = datetime2epochms(datetime.now())

        return super(BlacklistToken, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.identity}"


## ============================================================================= ##


class App(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=31)
    details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.details in (None, ""):
            self.details = None
        if self.name not in (None, ""):
            self.name = self.name.upper()

        return super(App, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class Table(models.Model):
    id = models.AutoField(primary_key=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.details in (None, ""):
            self.details = None
        if self.name not in (None, ""):
            self.name = self.name.upper()

        return super(Table, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.app} - {self.name}"


## ============================================================================= ##


class Access(models.Model):
    class CredActions(models.IntegerChoices):
        POST = 1
        GET = 2
        PUT = 3
        DELETE = 4

    id = models.AutoField(primary_key=True)
    action = models.IntegerField(choices=CredActions.choices)
    app_model = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.app_model} | {self.action}"


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=31)
    details = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.details in (None, ""):
            self.details = None
        if self.name not in (None, ""):
            self.name = self.name.upper()

        return super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class AccessGroup(models.Model):  # Access (M:N) Group
    id = models.AutoField(primary_key=True)
    access = models.ForeignKey(Access, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.access} - {self.group}"


## ============================================================================= ##
