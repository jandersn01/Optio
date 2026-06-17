from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, NotificationPreference
from search.choices import SearchArea, SearchModality
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html


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
    
    policy_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'Você precisa aceitar a Política de Privacidade para criar uma conta.'}
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
        
        url_privacidade = reverse('core:privacy_policy')
        self.fields['policy_accepted'].label = format_html(
            'Li e aceito a <a href="{}" target="_blank" class="btn-link">Política de Privacidade</a>',
            url_privacidade
        )
        
        self.order_fields(['nome', 'email', 'password1', 'password2', 'policy_accepted'])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.policy_accepted = self.cleaned_data['policy_accepted']
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserIdentityForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email']
        labels = {'first_name': 'Nome', 'email': 'E-mail'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input'

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email


class NotificationPreferenceForm(forms.ModelForm):
    area = forms.MultipleChoiceField(
        choices=SearchArea.choices,
        required=False,
        label='Áreas de interesse',
        widget=forms.MultipleHiddenInput,
    )
    modality = forms.ChoiceField(
        choices=[('', 'Todas')] + list(SearchModality.choices),
        required=False,
        label='Modalidade preferida',
    )

    class Meta:
        model = NotificationPreference
        fields = ['area', 'modality', 'active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Converte o TextField CSV → lista para o MultipleChoiceField
        if self.instance and self.instance.pk:
            self.initial['area'] = self.instance.area_list

    def clean_area(self):
        return ','.join(self.cleaned_data.get('area') or [])
