import re

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import CustomUser

PHONE_RE = re.compile(r'^\+?[0-9\s().-]{7,20}$')
MAX_PROFILE_PICTURE_SIZE = 2 * 1024 * 1024


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('school', 'role', 'email', 'phone')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'profile_picture')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and not PHONE_RE.match(phone):
            raise ValidationError('Enter a valid phone number.')
        return phone

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture and getattr(picture, 'size', 0) > MAX_PROFILE_PICTURE_SIZE:
            raise ValidationError('Profile picture must be 2MB or smaller.')
        return picture
