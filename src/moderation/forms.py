from ckeditor.fields import RichTextField
from django import forms
from django.forms import Textarea
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django_grapesjs.forms import GrapesJsWidget
from slugify import slugify
from django.forms import inlineformset_factory
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.forms import modelformset_factory

from .models import Applications,DocumentationsModer,DocumentationsModerMedia, TicketComment, ModerationGroups
from webmain.models import Landing, Organizations, Jobs, SettingsGlobale, Testimonial,  ContactPage, Faqs, Blogs, Categorys, Pages, Seo
from useraccount.models import Profile, Withdrawal, Notificationgroups, Notebook, Schedule
from useraccount.models import Notification
from lms.models import Needcourse, Qwiz, CategorysCourse, StreamSession, Schedulestream
from ckeditor.widgets import CKEditorWidget
from django_ace import AceWidget
from django.contrib.auth import get_user_model
from integration_payment.models import PaymentType

from lms.models import Files, Assumptioncourse, Schedulestream, Course, Question, Themes


alphanumeric_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]+$',
    message='Поле должно содержать только латинские буквы и цифры.'
)

class AssumptioncourseForm(forms.ModelForm):
    class Meta:
        model = Assumptioncourse
        fields = ['price', 'description', 'needcourse']
        widgets = {
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Стоимость'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Обращение', 'rows': 4}),
            'needcourse': forms.HiddenInput(),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Applications
        fields = ['email', 'phone', 'content']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E mail'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Обращение', 'rows': 4}),
        }

class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Add your comment here'}),
        }
    files = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'multiple': True}),
    )

class WorkerUpdateProfileForm(forms.ModelForm):
    GENDER_CHOICES = [
        (1, 'Мужской'),
        (2, 'Женский'),
    ]
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    cover = forms.ImageField(required=False,
                             widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}))
    username = forms.CharField(max_length=64,disabled=True, widget=forms.TextInput(
        attrs={'placeholder': 'Логин', 'name': 'emailaddress', 'id': 'profile-username', 'class': 'form-control'}))
    # birthday = forms.CharField(required=False, max_length=64, widget=forms.TextInput(attrs={'placeholder': '31.12.2000',  'name':'birthday', 'id': 'profile-birthday', 'class':'w-full rounded-lg border-jacarta-100 py-3 hover:ring-2 hover:ring-accent/10 focus:ring-accent dark:border-jacarta-600 dark:bg-jacarta-700 dark:text-white dark:placeholder:text-jacarta-300'}))
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': '31.12.2000', 'name': 'birthday', 'id': 'profile-birthday',
                   'class': 'datepicker_input form-control'}),
    )
    first_name = forms.CharField(required=False, max_length=64,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(required=False, max_length=64,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    middle_name = forms.CharField(required=False, max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Отчество'}))
    phone = forms.CharField(required=False, max_length=11, widget=forms.TextInput(
        attrs={'placeholder': 'Телефон', 'name': 'phone', 'id': 'phone', 'class': 'form-control'}))
    name = forms.CharField(required=False, max_length=11, widget=forms.TextInput(
        attrs={'placeholder': 'ФИО', 'name': 'name', 'id': 'name', 'class': 'form-control'}))
    city = forms.CharField(required=False, max_length=64, widget=forms.TextInput(
        attrs={'placeholder': 'Город', 'name': 'emailaddress', 'id': 'profile-username', 'class': 'form-control'}))
    email = forms.CharField(max_length=64, widget=forms.TextInput(
        attrs={'placeholder': 'Email', 'name': 'emailaddress', 'id': 'profile-email', 'class': 'form-control'}))
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
        fields = ['avatar', 'city', 'username', 'first_name', 'last_name', 'middle_name', 'birthday', 'name',
                  'phone', 'gender', 'description', 'email']


class SettingsGlobaleForm(forms.ModelForm):
    logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-file-input form-control', 'id': 'general_logo'}))
    doplogo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-file-input form-control', 'id': 'doplogo'}))
    favicon = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-file-input form-control', 'id': 'favicon'}))
    paymentmethod = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-file-input form-control', 'id': 'paymentmethod'}))
    name = forms.CharField(required=True, max_length=256, widget=forms.TextInput(attrs={'placeholder': 'Название', 'id': 'global_name', 'class': 'form-control input-default '}))
    content = forms.CharField(max_length=256, required=False, widget=forms.Textarea(attrs={'placeholder': 'Копирайт', 'class': 'form-control input-default '}),)
    description = forms.CharField(widget=CKEditorWidget(),)
    message_header = forms.CharField(widget=AceWidget(mode='html', width="100%", height="500px", readonly=False, behaviours=True, showgutter=True,  wordwrap=False, usesofttabs=True))
    message_footer = forms.CharField(widget=AceWidget(mode='html', width="100%", height="500px", readonly=False, behaviours=True, showgutter=True,  wordwrap=False, usesofttabs=True))
    yandex_metrica = forms.CharField(max_length=1024, required=False, widget=forms.Textarea(attrs={'placeholder': 'Яндекс Метрика', 'class': 'form-control input-default '}),)
    google_analitic = forms.CharField(max_length=1024, required=False, widget=forms.Textarea(attrs={'placeholder': 'Google Аналитика', 'class': 'form-control input-default '}),)

    class Meta:
        model = SettingsGlobale
        fields = [
            'logo', 'doplogo', 'favicon', 'paymentmethod',
            'name', 'description', 'content', 'message_header', 'message_footer', 'yandex_metrica','google_analitic',
        ]
    def __init__(self, *args, **kwargs):
        super(SettingsGlobaleForm, self).__init__(*args, **kwargs)




class SignUpWorkerForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    GENDER_CHOICES = [
        (1, 'Мужской'),
        (2, 'Женский'),
    ]
    TYPE = [
        (0, 'Ученик'),
        (1, 'Учитель'),
        (2, 'Модератор'),
    ]
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    cover = forms.ImageField(required=False,
                             widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}))
    username = forms.CharField(max_length=64, widget=forms.TextInput(
        attrs={'placeholder': 'Логин', 'name': 'emailaddress', 'id': 'profile-username', 'class': 'form-control'}))
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': '31.12.2000', 'name': 'birthday', 'id': 'profile-birthday',
                   'class': 'datepicker_input form-control'}),
    )
    first_name = forms.CharField(required=False, max_length=64,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}))
    last_name = forms.CharField(required=False, max_length=64,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}))
    middle_name = forms.CharField(required=False, max_length=64, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Отчество'}))
    phone = forms.CharField(required=False, max_length=11, widget=forms.TextInput(
        attrs={'placeholder': 'Телефон', 'name': 'phone', 'id': 'phone', 'class': 'form-control'}))
    name = forms.CharField(required=False, max_length=11, widget=forms.TextInput(
        attrs={'placeholder': 'ФИО', 'name': 'name', 'id': 'name', 'class': 'form-control'}))
    city = forms.CharField(required=False, max_length=64, widget=forms.TextInput(
        attrs={'placeholder': 'Город', 'name': 'emailaddress', 'id': 'profile-username', 'class': 'form-control'}))
    email = forms.CharField(max_length=64, widget=forms.TextInput(
        attrs={'placeholder': 'Email', 'name': 'emailaddress', 'id': 'profile-email', 'class': 'form-control'}))
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'}),
    )
    type = forms.ChoiceField(
        choices=TYPE,
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
        fields = ['avatar', 'city', 'username', 'first_name', 'last_name', 'middle_name', 'birthday', 'name',
                  'phone', 'gender', 'description', 'email','password1','password2','type']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user



class ModerationGroupsForm(forms.ModelForm):
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





class DocumentationCreateForm(forms.ModelForm):
    TYPE_CHOICES = [
        (0, 'Для модераторов'),
        (1, 'Для пользователей'),
        (2, 'Для преподавателей'),
    ]
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = DocumentationsModer
        fields = ['name', 'description', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'description': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Описание'}),
        }
    files = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'multiple': True, 'class': 'form-control form-file-input'}),
    )

class DocumentationForm(forms.ModelForm):
    TYPE_CHOICES = [
        (0, 'Для модераторов'),
        (1, 'Для пользователей'),
        (2, 'Для преподавателей'),
    ]
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = DocumentationsModer
        fields = ['name', 'description', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'description': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Описание'}),
        }



class DocumentationMediaForm(forms.ModelForm):
    class Meta:
        model = DocumentationsModerMedia
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }



class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['data', 'time_start', 'time_end', 'name', 'description']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker_input form-control'}),
            'time_end': forms.TimeInput(attrs={'type': 'time', 'class': 'datepicker_input form-control'}),
            'time_start': forms.TimeInput(attrs={'type': 'time', 'class': 'datepicker_input form-control'}),
            'name': forms.TextInput(attrs={'placeholder': 'Название', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'class': 'form-control'}),
        }

    # Устанавливаем required=False для полей, которые не должны быть обязательными
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False  # Название не обязательно
        self.fields['description'].required = False  # Описание не обязательно

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'category', 'previev', 'title', 'content',
                  'propertytitle', 'propertydescription', 'slug', 'cover','image', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'previev': forms.FileInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

        # Особые случаи
        self.fields['category'].widget.attrs['class'] = 'js-example-placeholder-multiple col-sm-12'

class CourseUpdateForm(CourseForm):
    class Meta(CourseForm.Meta):
        fields = CourseForm.Meta.fields + ['assistants']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assistants'].widget.attrs['class'] = 'js-example-placeholder-multiple col-sm-12'

class ThemesForm(forms.ModelForm):
    class Meta:
        model = Themes
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'id': 'id_description', 'rows': 3}),
        }

class FilesForm(forms.ModelForm):
    class Meta:
        model = Files
        fields = ['files', 'content', 'link']

class StreamSessionForm(forms.ModelForm):
    class Meta:
        model = StreamSession
        fields = ['date', 'time', 'time_start', 'time_end']

FilesFormSet = inlineformset_factory(Themes, Files, form=FilesForm, extra=1, can_delete=True)
StreamSessionFormSet = inlineformset_factory(Themes, StreamSession, form=StreamSessionForm, extra=1, can_delete=True)








class CategorysCourseForm(forms.ModelForm):
    class Meta:
        model = CategorysCourse
        fields = ['name', 'slug', 'description', 'title', 'content', 'parent', 'icon', 'image', 'cover']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
            'description': Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Описание'}),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание'}),
            'parent': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Родитель'}),
            'icon': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Генерация slug из name с помощью slugify
        instance.slug = slugify(instance.name)  # Используем slugify для генерации slug
        if commit:
            instance.save()
        return instance





class ContactPageForm(forms.ModelForm):
    class Meta:
        model = ContactPage
        fields = [
            'phone', 'email','adress', 'telegram', 'whatsapp', 'vk', 'site'
        ]
        widgets = {
            'setting': forms.Select(attrs={'class': 'form-control input-default'}),
            'phone': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Телефон'}),
            'email': forms.EmailInput(attrs={'class': 'form-control input-default', 'placeholder': 'Эл.Почта'}),
            'adress': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Адрес'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Телеграм'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Вацап'}),
            'vk': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'ВКонтакте'}),
            'site': forms.Select(attrs={'class': 'form-control input-default'}),
        }

    def __init__(self, *args, **kwargs):
        super(ContactPageForm, self).__init__(*args, **kwargs)


class FaqsForm(forms.ModelForm):
    class Meta:
        model = Faqs
        fields = ['question', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Введите вопрос'}),
            'answer': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Введите ответ'}),

        }


class BlogsForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Categorys.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'default-select form-control wide', 'id': 'id_category', 'aria-label': 'Выберите категории' }),
    )
    draft = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Черновик'
    )
    class Meta:
        model = Blogs
        fields = ['name', 'description', 'title', 'content', 'author', 'resource',
                  'category', 'slug', 'propertytitle', 'propertydescription',
                  'previev', 'cover', 'draft']
        widgets = {
            'author': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Автор'}),
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'resource': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Источник'}),
            'description': forms.CharField(widget=CKEditorWidget(),),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Содержимое'}),
            'category': forms.SelectMultiple(attrs={'class': 'default-select form-control wide', 'id': 'id_category', 'aria-label': 'Выберите категории', 'name': 'category' }),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок свойства'}),
            'propertydescription': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Описание свойства'}),
            'previev': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Генерация slug из name с помощью slugify
        instance.slug = slugify(instance.name)  # Используем slugify для генерации slug
        if commit:
            instance.save()
        return instance

class PagesForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = ['name', 'pagetype', 'description', 'title', 'content', 'slug', 'propertytitle', 'propertydescription', 'previev']
        widgets = {
            'pagetype': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Тип страницы'}),
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'description': forms.CharField(widget=CKEditorWidget(),),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание'}),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-заголовок ссылки'}),
            'propertydescription': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание ссылки'}),
            'previev': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Генерация slug из name с помощью slugify
        instance.slug = slugify(instance.name)  # Используем slugify для генерации slug
        if commit:
            instance.save()
        return instance


class NeedcourseForm(forms.ModelForm):
    GENDER_CHOICES = [
        (1, 'Опубликован'),
        (2, 'Закрыт'),
        (3, 'Найден исполнитель'),
    ]
    type = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Needcourse
        fields = ['name', 'description', 'slug', 'price', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'price': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Стоимость'}),
            'description': CKEditorWidget(),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Генерация slug из name с помощью slugify
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance



class OrganizationsForm(forms.ModelForm):
    class Meta:
        model = Organizations
        fields = ['name', 'longitude', 'width','icon','description', 'title', 'content', 'slug', 'propertytitle', 'propertydescription', 'previev']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Долгота', 'readonly': 'readonly'}),
            'width': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Широта', 'readonly': 'readonly'}),
            'description': forms.CharField(widget=CKEditorWidget(),),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание'}),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-заголовок ссылки'}),
            'propertydescription': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание ссылки'}),
            'previev': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'icon': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Генерация slug из name с помощью slugify
        instance.slug = slugify(instance.name)  # Используем slugify для генерации slug
        if commit:
            instance.save()
        return instance



class JobsForm(forms.ModelForm):
    class Meta:
        model = Jobs
        fields = ['name', 'location', 'description', 'requirements', 'salary', 'job_type',
                  'experience_level', 'is_active', 'title', 'content', 'previev',
                  'propertytitle', 'propertydescription', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'location': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Местоположение'}),
            'description': CKEditorWidget(),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Требования'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control input-default', 'placeholder': 'Зарплата'}),
            'job_type': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Тип занятости'}),
            'experience_level': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Уровень опыта'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание'}),
            'previev': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-заголовок ссылки'}),
            'propertydescription': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание ссылки'}),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class SeoForm(forms.ModelForm):
    class Meta:
        model = Seo
        fields = ['pagetype', 'description', 'title', 'propertytitle', 'propertydescription', 'previev', 'setting']
        widgets = {
            'pagetype': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Тип страницы'}),
            'setting': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Настройка'}),
            'description': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание'}),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-заголовок'}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-заголовок ссылки'}),
            'propertydescription': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание ссылки'}),
            'previev': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }

class NotificationForm(forms.ModelForm):
    user = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'default-select form-control wide', 'id': 'id_user',
                                           'aria-label': 'Выберите пользователей'}),
    )
    class Meta:
        model = Notificationgroups
        fields = ['content_type', 'user', 'message', 'object_id']
        widgets = {
            'content_type': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Тип контента'}),
            'message': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Сообщение'}),
            'object_id': forms.NumberInput(attrs={'class': 'form-control input-default', 'placeholder': 'ID объекта'}),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),

        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Написать сообщение', 'class': 'form-control input-default'}),
        }

    files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )


class CategorysForm(forms.ModelForm):
    class Meta:
        model = Categorys
        fields = ['name', 'slug', 'description', 'title', 'content', 'parent', 'icon', 'image', 'cover']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Название'}),
            'slug': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Slug'}),
            'description': Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Описание'}),
            'title': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Мета-описание'}),
            'parent': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Родитель'}),
            'icon': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Генерация slug из name с помощью slugify
        instance.slug = slugify(instance.name)  # Используем slugify для генерации slug
        if commit:
            instance.save()
        return instance


class PaymentTypeForm(forms.ModelForm):
    turn_on = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Включить'
    )

    class Meta:
        model = PaymentType
        fields = ['type', 'content', 'key_1', 'key_2', 'shop_key', 'image', 'turn_on']
        widgets = {
            'type': forms.Select(attrs={'class': 'default-select form-control wide', 'placeholder': 'Тип'}),
            'content': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Описание'}),
            'key_1': forms.Textarea(attrs={'class': 'form-control input-default', 'placeholder': 'Первый ключ (public key)'}),
            'key_2': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Второй ключ (secret key)'}),
            'shop_key': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Ключ магазина (shop key)'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input form-control'}),
        }


class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control input-default', 'placeholder': 'Сумма'}),
        }


class SchedulestreamForm(forms.ModelForm):
    class Meta:
        model = Schedulestream
        fields = [
            'data', 'time_start', 'time_end', 'themes',
            'users', 'link', 'logo', 'cover',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'time_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'themes': forms.Select(attrs={'class': 'form-control'}),
            'users': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ссылку'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # Проверяем, если экземпляр существует
            if self.instance.data:
                self.initial['data'] = self.instance.data.strftime('%Y-%m-%d')


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(widget=forms.FileInput(attrs={'accept': '.xlsx, .xls', 'class': 'hidden', 'id': 'excel-file-input'}))
