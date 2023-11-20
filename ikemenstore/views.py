from rest_framework import views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from ikemenstore.models import UserClient


# Create your views here.
class SessionUserView(views.APIView):
    @staticmethod
    def get(request):
        content = {
            'id': request.user.id,
            'user': str(request.user)
        }

        return Response(content)

class EmailConfirmationView(generics.GenericAPIView):
    authentication_classes = []      # Removendo a autenticação
    permission_classes = []          # Removendo as permissões

    def get(self, request, token):
        # Verifique o token recebido com o token armazenado no banco de dados
        user = get_object_or_404(UserClient, email_confirmation_token=token)
        print(user.user.is_active)
        if(user.user.is_active == True):
            return Response({'message': 'E-mail já foi confirmado!'})
        
        user.user.is_active = True
        user.user.save()
        user.save()

        return Response({'message': 'E-mail confirmado com sucesso!'}, status=status.HTTP_200_OK)