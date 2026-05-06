from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CadastroForm(UserCreationForm):
    nome = forms.CharField(
        label='Nome completo',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo',
            'autofocus': True,
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
        })
        self.fields['email'].label = 'E-mail'
        self.fields['email'].widget.attrs.pop('autofocus', None)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
        })
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repita a senha',
        })
        self.fields['password2'].label = 'Confirmação de senha'
        self.order_fields(['nome', 'email', 'password1', 'password2'])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        if commit:
            user.save()
            self.save_m2m()
        return user
