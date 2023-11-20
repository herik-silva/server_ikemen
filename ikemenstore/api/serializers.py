import secrets
from rest_framework import serializers
from ikemenstore import models

from django.contrib.auth.models import User, AnonymousUser

from rest_framework import serializers, validators, status, response

from ikemenstore.core.utils.send_mail import Email

import datetime

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        label='Usuário',
        max_length=150,
        required=True,
        validators=[validators.UniqueValidator(
            queryset=models.User.objects.all(),
            message='Nome de usuário já existe.'
        )]
    )
    email = serializers.EmailField(
        label='Endereço de email',
        max_length=255,
        required=False,
        validators=[validators.UniqueValidator(
            queryset=models.User.objects.all(),
            message='Endereço de email já cadastrado.'
        )]
    )
    password = serializers.CharField(
        label='Senha',
        max_length=255,
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    first_name = serializers.CharField(
        label='Nome',
        max_length=150,
        required=True
    )

    email_confirmation = serializers.BooleanField(
        label='Confirmação de Email',
        default=False
    )


    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'email_confirmation']


class GetUserClientSerializer(serializers.Serializer):
    user = UserSerializer(write_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    email_confirmation = serializers.BooleanField(source="user.email_confirmation", read_only=True)
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    birth_date = serializers.DateField(read_only=True)
    created_at = serializers.DateField(read_only=True)
    updated_at = serializers.DateField(read_only=True)
    country = serializers.CharField(read_only=True)
    
    class Meta:
        model = models.UserClient
        fields = '__all__'


class UserClientSerializer(serializers.Serializer):
    user = UserSerializer(write_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    email_confirmation = serializers.BooleanField(source="user.email_confirmation", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    confirm_password = serializers.CharField(
        label='Confirmar Senha',
        max_length=255,
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    birth_date = serializers.DateField(
        label='Data de Nascimento'
    )

    created_at = serializers.DateField(read_only=True)

    updated_at = serializers.DateField(read_only=True)

    country = serializers.CharField(
        label='País',
        max_length=90
    )
    
    class Meta:
        model = models.UserClient
        fields = '__all__'

    def create(self, validated_data):
        print('Recebi\n', validated_data)
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            if(user_data['password'] != validated_data['confirm_password']):
                raise serializers.ValidationError({'password': 'As senhas não são iguais.'})
            
            email_confirmation_token = secrets.token_urlsafe(30)

            user_instance = User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
            )
            
            email_confirmation_token=email_confirmation_token
            user_instance.set_password(user_data['password'])
            user_instance.is_staff = False
            user_instance.is_active = True
            user_instance.is_superuser = False
            user_instance.save()

            validated_data.pop('confirm_password')
            validated_data['email_confirmation_token'] = email_confirmation_token

            user_client_instance = models.UserClient.objects.create(
                user=user_instance, **validated_data
            )

            email = Email()

            email.send_confirm_email(user_instance.email, user_instance.first_name, email_confirmation_token)

            return user_client_instance


class UserClientDeleteSerializer(serializers.Serializer):
    def delete(self, instance):
        instance.user.delete()
        instance.delete()


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        label='Nome Completo',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(
        label='Endereço de email',
        max_length=255,
        required=False,
    )

    class Meta:
        model = User
        fields = ['first_name', 'email']


class UserClientUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(write_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = models.UserClient
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user_instance = User.objects.get(id=instance.user.id)

            user_instance.first_name = user_data['first_name']
            user_instance.email = user_data['email']
            user_instance.save()
            instance.user = user_instance

        instance.country = validated_data.get('country', instance.country)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.updated_at = datetime.date.today()
        instance.save()

        return instance
    
class CurrentUserClientDefault(serializers.CurrentUserDefault):
    def __call__(self, serializer_field):
        user = serializer_field.context['request'].user
        if user and not isinstance(user, AnonymousUser):
            return user.userclient
        return None
    
    
class CharactersSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(
        default=CurrentUserClientDefault()
    )

    images = serializers.PrimaryKeyRelatedField(
        queryset=models.Image.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = models.Characters
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        images = validated_data.pop('images', [])  
        character = models.Characters.objects.create(**validated_data)
        id_images =  [image.id for image in images]
        print("PERSONAGENS IMAGENS")
        print(id_images)

        character.images.set(id_images)
        return character

    def to_representation(self, instance):
        response = super().to_representation(instance)
        user_client = GetUserClientSerializer(instance.creator).data
        response['creator'] = {"username": user_client.get("username"), "id": user_client.get("id")}
        response['id'] = instance.id
        
        # Inclua as imagens relacionadas ao personagem na resposta
        images = Image(instance.images.all(), many=True).data
        response['images'] = images
        print("\n\nRESPOSTA\n")
        print(response)
        
        return response


class Image(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    buyer = serializers.HiddenField(
        default=CurrentUserClientDefault()
    )

    character = serializers.PrimaryKeyRelatedField(
        queryset=models.Characters.objects.all(),
        many=False,
        required=True
    )

    class Meta:
        model = models.Sale
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        character = validated_data.get('character')
        validated_data.pop('character')
        print("Personagem")
        for key, value in character.__dict__.items():
            print(f"{key}: {value}")
        sale = models.Sale.objects.create(**validated_data)
        print("ID PERSONAGEM")
        print(character.id)

        sale.character = character
        sale.save()

        return sale

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # print("VALORES DA INSTÂNCIA:")
        # for key, value in instance.__dict__.items():
        #     print(f"{key}: {value}")
        character = CharactersSerializer(instance.character).data
        print("CHAR")
        for key, value in character.__dict__.items():
            print(f"{key}: {value}")
        image = character.get("images")[0].get("image")

        # print("IMG")
        # for key, value in image.__dict__.items():
        #     print(f"{key}: {value}")
        # print(image.get_attribute("_args").get("image"))
        if response["payment_done"] == True:
            response['character'] = {"name": character.get("name"), "id": character.get("id"), "sale_value": character.get("sale_value"), "file_to_download": character.get("file_to_download"), "image": image}
        else:
            response['character'] = {"name": character.get("name"), "id": character.get("id"), "sale_value": character.get("sale_value")}



        response['id'] = instance.id
        
        # Inclua as imagens relacionadas ao personagem na resposta
        print("\n\nRESPOSTA\n")
        print(response)
        
        return response