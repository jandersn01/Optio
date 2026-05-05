from django import forms

from .models import SearchRequest


class SearchRequestForm(forms.ModelForm):
    class Meta:
        model = SearchRequest
        fields = [
            "keywords",
            "area",
            "modality",
            "state",
        ]

        labels = {
            "keywords": "EX: engenharia de software...",
            "area": "EX: Ciências Exatas e da Terra",
            "modality": "EX: EAD",
            "state": "EX: PB",
        }

        widgets = {
            "keywords": forms.TextInput(attrs={
                "placeholder": "Ex: engenharia de software...",
                "class": "form-control",
            }),
            "area": forms.Select(attrs={
                "class": "form-control",
            }),
            "modality": forms.Select(attrs={
                "class": "form-control",
            }),
            "state": forms.Select(attrs={
                "class": "form-control",
            }),
        }

    def clean_keywords(self):
        keywords = self.cleaned_data["keywords"].strip()

        if len(keywords) < 3:
            raise forms.ValidationError("Informe pelo menos 3 caracteres para a busca.")

        return keywords