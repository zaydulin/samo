from django import forms

from conference.models import VideoChatRoom




"""Форма создания конференции"""
class VideoChatRoomForm(forms.ModelForm):
    #spiker = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    #participants = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    #visitors = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = VideoChatRoom
        fields = ['type',  'descriptions', 'logo', 'cover', 'banner', 'name', 'start_data', 'start_time', 'time', 'count_participants']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'descriptions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'cover': forms.FileInput(attrs={'class': 'form-control-file'}),
            'banner': forms.FileInput(attrs={'class': 'form-control-file'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'start_data': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'count_participants': forms.NumberInput(attrs={'class': 'form-input w-auto'}),
            'time': forms.NumberInput(attrs={'class': 'form-input w-auto'}),

        }