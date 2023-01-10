from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from users.avatars import AVATARS
from users.models import User


class UserEditForm(ModelForm):
    username = forms.CharField(
        label="Отображаемое имя",
        required=True,
        max_length=32
    )

    avatar = forms.ChoiceField(
        label="Новый моднейший аватар",
        choices=[(avatar, avatar) for avatar in AVATARS],
        widget=forms.RadioSelect,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "avatar",
        ]

    def clean_avatar(self):
        avatar = self.cleaned_data["avatar"]
        if avatar not in AVATARS:
            return self.instance.avatar
        return avatar
