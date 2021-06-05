from django import forms

from recipes.models import Recipe


class RecipeForm(forms.ModelForm):

    cook_time = forms.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'name',
            'image',
            'cook_time',
            'tags',
            'description',
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
