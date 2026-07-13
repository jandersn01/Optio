from django.dispatch import receiver
from allauth.account.signals import email_confirmed

@receiver(email_confirmed)
def activate_user_account(sender, request, email_address, **kwargs):
    user = email_address.user
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])