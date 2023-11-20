from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserClient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )

    birth_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True, null=True)
    country = models.CharField(max_length=90)
    email_confirmation_token = models.CharField(max_length=40)
    is_creator = models.BooleanField(default=False)


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.ImageField(upload_to="./character")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True, null=True)

class Characters(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=90, unique=True)
    description = models.CharField(max_length=500)
    sale_value = models.FloatField()
    version = models.IntegerField()
    file_to_download = models.FileField(upload_to="./files")
    creator = models.ForeignKey(
        to=UserClient,
        on_delete=models.SET_NULL,
        null=True
    )
    images = models.ManyToManyField(Image, related_name="characters")
    updated_at = models.DateField(auto_now=True, null=True)
    created_at = models.DateField(auto_now=True, null=True)

class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    buyer = models.ForeignKey(
        to=UserClient,
        on_delete=models.SET_NULL,
        null=True
    )
    character = models.ForeignKey(
        to=Characters,
        on_delete=models.SET_NULL,
        null=True
    )
    payment_done = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True, null=True)