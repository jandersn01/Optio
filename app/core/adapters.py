from allauth.account.adapter import DefaultAccountAdapter
from django.template.loader import render_to_string
from core.emails import send_html_email, EmailDeliveryError
import logging

logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Padrão Adaptador (Adapter) para interceptar eventos do django-allauth
    e roteá-los para a infraestrutura interna do Optio.
    """
    def send_mail(self, template_prefix, email, context):
        """
        Intercepta TODOS os e-mails disparados pelo allauth (confirmação, 
        reset de senha, etc) e os envia através do nosso helper centralizado.
        """
        #O allauth envia prefixos como: 'account/email/email_confirmation_signup'
        
        subject_template = f"{template_prefix}_subject.txt"
        subject = render_to_string(subject_template, context).strip()
        
        html_template = f"{template_prefix}_message.html"
        
        try:
            send_html_email(
                subject=subject,
                template=html_template,
                context=context,
                to_email=email
            )
        except EmailDeliveryError as e:
            # Capturamos o erro customizado do Optio e geramos log
            logger.error(f"Falha ao enviar e-mail de autenticação para {email}: {e}")