from django import forms

from .models import Athlete


class AthleteForm(forms.ModelForm):
    """Форма добавления/редактирования спортсмена с валидацией."""

    class Meta:
        model = Athlete
        fields = ['name', 'sport', 'age', 'country', 'achievements']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sport': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 100}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('ФИО должно содержать минимум 2 символа')
        return name

    def clean_sport(self):
        sport = self.cleaned_data['sport'].strip()
        if len(sport) < 2:
            raise forms.ValidationError('Вид спорта должен содержать минимум 2 символа')
        return sport

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 10 or age > 100:
            raise forms.ValidationError('Возраст должен быть от 10 до 100 лет')
        return age

    def clean_country(self):
        country = self.cleaned_data['country'].strip()
        if len(country) < 2:
            raise forms.ValidationError('Страна должна содержать минимум 2 символа')
        return country
