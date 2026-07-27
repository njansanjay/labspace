from django import forms
import re

class CreateSpaceForm(forms.Form):
    space_id = forms.CharField(
        max_length=30,
        min_length=3,
        label="Space ID",
        widget=forms.TextInput(attrs={
            'class': 'form-control minimal-input',
            'placeholder': 'e.g. workspace-123',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control minimal-input',
            'placeholder': 'Enter password'
        }),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control minimal-input',
            'placeholder': 'Confirm password'
        }),
        label="Confirm Password"
    )

    def clean_space_id(self):
        space_id = self.cleaned_data.get('space_id', '').strip().lower()
        if not re.match(r'^[a-zA-Z0-9_-]+$', space_id):
            raise forms.ValidationError("Space ID can only contain letters, numbers, hyphens, and underscores.")
        return space_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class OpenSpaceForm(forms.Form):
    space_id = forms.CharField(
        max_length=30,
        label="Space ID",
        widget=forms.TextInput(attrs={
            'class': 'form-control minimal-input',
            'placeholder': 'Enter Space ID',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control minimal-input',
            'placeholder': 'Enter password'
        }),
        label="Password"
    )

    def clean_space_id(self):
        return self.cleaned_data.get('space_id', '').strip().lower()


class NoteForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control minimal-input',
            'placeholder': 'Title (optional)'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control minimal-input',
            'rows': 5,
            'placeholder': 'Write or paste your content here...'
        })
    )


class SpaceFileForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control minimal-input',
            'id': 'fileInput'
        })
    )
