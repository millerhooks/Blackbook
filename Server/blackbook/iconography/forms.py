from django import forms
from datetime import datetime
from iconography.models import Tag, LightMap

__all__ = ('CoordinateForm', 'TagForm', 'LightMapForm')

class CoordinateForm(forms.ModelForm):
    class Meta:
        exclude = ('coordinates','approved_at',
            'approved_by','enabled')

class TagForm(CoordinateForm):
    class Meta(CoordinateForm.Meta):
        model = Tag

class LightMapForm(CoordinateForm):
    class Meta(CoordinateForm.Meta):
        model = LightMap

