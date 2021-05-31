from django import forms

from recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'name',
            'image',
            'tags',
            'description',
            'cook_time',
        ]
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'image': forms.FileInput(),
        }
