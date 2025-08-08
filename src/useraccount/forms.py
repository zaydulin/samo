from moderation.models import ModerationGroups
from django import forms
from useraccount.models import Profile, Notebook
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthenticationForm(forms.Form):
    identifier = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин, email или телефон'
        }),
        label="Логин, Email или Телефон"
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label="Пароль"
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('identifier')
        password = cleaned_data.get('password')

        if not identifier or not password:
            raise forms.ValidationError("Введите логин/Email/телефон и пароль.")

        # Пытаемся найти пользователя по логину, email или телефону
        user = None
        try:
            if "@" in identifier:  # Проверяем, если это email
                user = User.objects.get(email=identifier)
            elif identifier.isdigit():  # Если это телефон
                user = User.objects.get(phone=identifier)
            else:  # В остальных случаях предполагаем, что это username
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            raise forms.ValidationError("Пользователь не найден.")

        # Аутентификация пользователя
        self.user = authenticate(self.request, username=user.username, password=password)
        if self.user is None:
            raise forms.ValidationError("Неправильный логин или пароль.")

        return cleaned_data

    def get_user(self):
        return self.user

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['username', 'email', 'password1', 'password2', 'referral_code']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] += ' form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Profile.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.referral_code = None  # Устанавливаем личный реферальный код как пустой (может быть сгенерирован позже)

        if commit:
            user.save()
            referral_code = self.cleaned_data.get('referral_code')
            if referral_code:
                try:
                    referrer = Profile.objects.get(referral_code=referral_code)
                    user.referral = referrer
                    user.save()
                except Profile.DoesNotExist:
                    print("Реферальный код не найден")
        return user


class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES = [
        (1, 'Мужской'),
        (2, 'Женский'),
    ]
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    cover = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}))
    username = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Логин',  'name':'emailaddress', 'id': 'profile-username', 'class':'form-control'}))
    # birthday = forms.CharField(required=False, max_length=64, widget=forms.TextInput(attrs={'placeholder': '31.12.2000',  'name':'birthday', 'id': 'profile-birthday', 'class':'w-full rounded-lg border-jacarta-100 py-3 hover:ring-2 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:bg-jacarta-700 dark:text-white dark:placeholder:text-jacarta-300'}))
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': '31.12.2000', 'name': 'birthday', 'id': 'profile-birthday',
                   'class': 'datepicker_input form-control'}),
    )
    first_name = forms.CharField(required=False, max_length=64, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(required=False,max_length=64, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    middle_name = forms.CharField(required=False,max_length=64, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}))
    phone = forms.CharField(required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder': 'Телефон',  'name': 'phone', 'id': 'phone', 'class':'form-control'}))
    name = forms.CharField(required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder': 'ФИО',  'name': 'name', 'id': 'name', 'class':'form-control'}))
    city = forms.CharField(required=False, max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Город',  'name':'emailaddress', 'id': 'profile-username', 'class':'form-control'}))
    email = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Email',  'name':'emailaddress', 'id': 'profile-email', 'class':'form-control'}))
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'}),
    )
    description = forms.CharField(
        max_length=5000,
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'profile-bio', 'class': 'form-control'}),
    )
    class Meta:
        model = Profile
        fields = ['avatar',  'city', 'username','first_name','last_name','middle_name', 'birthday','name', 'phone',  'gender', 'description',  'email']


class PasswordResetEmailForm(PasswordResetForm):
    email = forms.EmailField(label='Email', max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

class SetPasswordFormCustom(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='New password confirmation', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['new_password2'].widget.attrs.update({'autocomplete': 'new-password'})



class GroupsForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.none(),  # Исправлено на get_user_model()
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    types = forms.MultipleChoiceField(
        choices=ModerationGroups.TYPE_OPTIONS,  # Используем TYPE_OPTIONS из модели
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Типы доступа'
    )

    class Meta:
        model = ModerationGroups
        fields = ['name', 'users', 'types']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название', 'class': 'form-input input-default'}),
        }

    def __init__(self, *args, **kwargs):
        users_queryset = kwargs.pop('users_queryset', None)
        super().__init__(*args, **kwargs)
        if users_queryset:
            self.fields['users'].queryset = users_queryset

class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        fields = ['period', 'name', 'description']  # Поля, которые будут отображены в форме
        widgets = {
            'period': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker_input form-control'}),
            'name': forms.TextInput(attrs={'placeholder': 'Название', 'required': 'False', 'class': 'form-control', }),
            'description': forms.Textarea(
                attrs={'placeholder': 'Описание', 'required': 'False', 'class': 'form-control', }),

        }
