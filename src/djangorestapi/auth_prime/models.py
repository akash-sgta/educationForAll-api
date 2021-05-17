from django.db import models

from django.core.validators import RegexValidator


from datetime import datetime, timedelta

# Create your models here.

# ---------------------------------------------------------------------------------------------------------------------------------------
# TODO : Profile <=1======N=> Image
class Image(models.Model):
    image = models.ImageField(max_length=255, null=True, upload_to="uploads/%Y/%m/%d/")

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        data = f"I [{self.pk}, {self.image.url}]"
        return data


# ---------------------------------------------------------------------------------------------------------------------------------------
# TODO : User <=1======N=> Profile
class Profile(models.Model):
    image_ref = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)

    headline = models.CharField(max_length=128, null=False, blank=False)
    bio = models.TextField()
    english_efficiency = models.PositiveSmallIntegerField(
        choices=((1, "BEGINNER"), (2, "INTERMEDIATE"), (3, "ADVANCED")), default=1
    )
    git_profile = models.URLField(max_length=256, null=True, blank=True)
    linkedin_profile = models.URLField(max_length=256, null=True, blank=True)
    roll_number = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r"^[1-9]{1}[0-9]{11}$",
                message="12 Digit University Roll Number.",
                code="invalid_roll_number",
            )
        ],
        null=True,
        blank=True,
    )
    prime = models.BooleanField(default=True)  # TODO : T -> Is Student
    made_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = f" P [{self.pk} {self.prime}] || {self.image_ref}"
        return data


class User(models.Model):
    profile_ref = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)

    first_name = models.CharField(max_length=32, null=False, blank=False)
    middle_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=False, blank=False)
    email = models.EmailField(max_length=128, null=False, blank=False, unique=True)
    password = models.CharField(max_length=64, null=False, blank=False)
    telegram_id = models.CharField(max_length=64, null=True, blank=True)
    security_question = models.CharField(max_length=128, null=True, blank=True)
    security_answer = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        data = f"U [{self.pk} {self.first_name}_{self.last_name}] || {self.profile_ref}"
        return data


# TODO : User <=1======N=> Token
class User_Token(models.Model):
    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    hash = models.TextField(default="")
    start = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = f"{self.user_ref} || TK [{self.pk} {self.start+timedelta(hours=48)}]"
        return data


# ---------------------------------------------------------------------------------------------------------------------------------------


class Privilege(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()

    def __str__(self):
        data = f"PR [{self.pk} {self.name}]"
        return data


class Admin(models.Model):
    user_ref = models.ForeignKey(User, on_delete=models.CASCADE)

    prime = models.BooleanField(default=False)  # TODO : T -> Is ADMIN PRIME

    def __str__(self):
        data = f"{self.user_ref} || A [{self.pk} {self.prime}]"
        return data


# TODO : Admin <=M======N=> Privilege
class Admin_Privilege(models.Model):
    admin_ref = models.ForeignKey(Admin, on_delete=models.CASCADE)
    privilege_ref = models.ForeignKey(Privilege, on_delete=models.CASCADE)

    def __str__(self):
        data = f"{self.admin_ref} || {self.privilege_ref}"
        return data


# ---------------------------------------------------------------------------------------------------------------------------------------


class Api_Token(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)

    hash = models.CharField(max_length=255, null=False, blank=False)
    endpoint = models.PositiveSmallIntegerField(
        choices=(
            (1, "Web Development"),
            (2, "Android App Development"),
            (3, "Apple App Development"),
            (4, "Windows Software Development"),
            (5, "Linux Software Development"),
            (6, "Others"),
        ),
        default=1,
    )

    def __str__(self):
        data = f"API [{self.pk} {self.name} {self.endpoint}]"
        return data


# ---------------------------------------------------------------------------------------------------------------------------------------
