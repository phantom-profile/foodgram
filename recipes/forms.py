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

    def clean_cook_time(self):
        data = self.cleaned_data['cook_time']
        if data < 1:
            raise forms.ValidationError('Значение должно быть больше 0')
        return data
