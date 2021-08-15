from django.db import models

## ============================================================================= ##
# Utility Models placed here


class U_Country(models.Model):
    id = models.AutoField(primary_key=True)
    isd_code = models.CharField(max_length=7, unique=True)  # phone code
    name = models.CharField(max_length=127, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper() if self.name not in (None, "") else None
        return super(U_Country, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} | {self.name}"


class U_State(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(U_Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=127, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper() if self.name not in (None, "") else None
        return super(U_Country, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.country_id.name} || {self.id} | {self.name}"


class U_City(models.Model):
    id = models.AutoField(primary_key=True)
    state_id = models.ForeignKey(U_State, on_delete=models.CASCADE)
    name = models.CharField(max_length=127, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper() if self.name not in (None, "") else None
        return super(U_Country, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.state_id.name} || {self.id} | {self.name}"


## ============================================================================= ##
# Abstract Models placed here


class A_Address(models.Model):
    class Meta:
        abstract = True

    line_1 = models.CharField(max_length=127)
    line_2 = models.CharField(max_length=127)
    pincode = models.CharField(max_length=7)
    city = models.ForeignKey(U_City, on_delete=models.SET_NULL, null=True)  # serializer D = 3


class A_Name(models.Model):
    class Meta:
        abstract = True

    first_name = models.CharField(max_length=63)
    middle_name = models.CharField(max_length=127, null=True)
    last_name = models.CharField(max_length=63)


class A_Contact(models.Model):
    class Meta:
        abstract = True

    phone_1 = models.CharField(max_length=63)
    phone_2 = models.CharField(max_length=63, null=True)  # telegram contact
    email_1 = models.EmailField()
    email_2 = models.EmailField(null=True)
