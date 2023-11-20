from django.core.mail import send_mail
import os

class Email:
    def send_confirm_email(self, email: str, name: str, confirmation_url: str):
        if(not(email or name or confirmation_url)):
            raise "Necessário os parâmetros email, name e confirmation_url."

        body = f"<table width='100%' cellspacing='0' cellpadding='0'><tr><td align='center'><img src='https://ikemenstore.netlify.app/assets/email-logo.webp' width='128px' style='background: #FFF;'><div style='max-width:600px;text-align:center;'><h2>Seja Bem-Vindo(a) ao IkemenStore, {name}</h2><p>Recentemente, você se registrou em IkemenStore. Para concluir o processo de registro, precisamos que você confirme seu endereço de e-mail.</p><table cellspacing='0' cellpadding='0' border='0' style='background-color:#92E994;border-radius:10px;margin:0 auto;'><a href='http://localhost:5173/account-confirm/{confirmation_url}/' target='_blank' style='text-decoration:none;'><tr><td style='padding:15px 35px;background-color:#92E994;color:#424242;font-weight:bold;border-radius:10px;border:none;cursor:pointer;font-size:16px;'><a href='http://localhost:5173/account-confirm/{confirmation_url}/' target='_blank' style='text-decoration:none;color:#424242;display:block;'>Confirmar Cadastro</a></td></tr></a></table><p>Se você não conseguir clicar no botão, copie e cole o seguinte URL na barra de endereços do seu navegador: <a href='http://localhost:5173/account-confirm/{confirmation_url}/' target='_blank'>http://localhost:5173/account-confirm/{confirmation_url}/</a></p><p>Se você não criou uma conta em IkemenStore, por favor, ignore este e-mail.</p></div></td></tr></table>"
        
        send_mail(
            subject="Confirmação de Cadastro IkemenStore",
            message="",
            html_message=body,
            from_email="no_reply@ikemenstore.com",
            recipient_list=[email]
        )