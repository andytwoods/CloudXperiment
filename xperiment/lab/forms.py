from django.forms import ModelForm

from .models import Lab

class LabForm(ModelForm):

    class Meta:
        model = Lab
        exclude = (
            'creator',
            'slug',
            'logo',
            'balance',
        )