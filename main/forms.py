from .models import DesignRequest, Category
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async


async def check_username_exists(username):
    return await sync_to_async(User.objects.filter(username=username).exists)()
class CustomUserCreationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        min_length=3,
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'Введите логин (только латиница и дефис)'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Введите email'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        # Проверяем, занят ли логин
        if User.objects.filter(username=username).exists():
            raise ValidationError('Этот логин уже занят.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        # Проверяем, занят ли email
        if User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже зарегистрирован.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают.')
        return password2


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2


class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'photo', 'is_important']
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Опишите требования к дизайну'}),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("Размер изображения не должен превышать 2MB.")
            valid_extensions = ['jpg', 'jpeg', 'png', 'bmp']
            ext = photo.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Фото должно быть в одном из форматов: jpg, jpeg, png, bmp.")
        return photo

class StatusChangeForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['status']

    # Добавим выбор доступных статусов
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.Select(choices=DesignRequest.STATUS_CHOICES)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']  # Поле для ввода имени категории