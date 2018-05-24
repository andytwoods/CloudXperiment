from django import forms

from .models import ExptInfo


class ExptForm_v2(forms.ModelForm):

    class Meta:
        model = ExptInfo
        exclude = (
            'expt_id',
            'creator',
            'slug',
            'lab',
            'is_paid',
            'is_publish',
            'secret_key',
            'expt_headers',
            'participant_count'
        )


class RenameForm(forms.ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        super(RenameForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ExptInfo
        fields = (
            'name',
        )


class ExptEditForm(forms.ModelForm):
    def __init__(self, user=None, *args, **kwargs):
        super(ExptEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ExptInfo
        exclude = (
            'expt_headers',
            'expt_id',
            'creator',
            'slug',
            'participant_count',
            'lab',
            'is_paid',
            'is_password',
            'is_encrypt',
            'is_publish',
            'secret_key',
        )
