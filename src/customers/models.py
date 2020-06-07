import uuid

from django.contrib.auth.models import User
from django.db import models

from cores.models import CommonInfo


class Customer(CommonInfo):
    MALE = 'male'
    FEMALE = 'female'
    SEX_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    guid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    identity_number = models.CharField(max_length=60, unique=True)
    address = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(choices=SEX_CHOICES, max_length=6)

    def __str__(self):
        return self.user.username
