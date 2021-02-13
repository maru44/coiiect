from .models import Collect, Category, Place, Photo, Tag
from django import forms
from user.models import User
from django.utils.translation import ugettext as _

class PostForm(forms.ModelForm):
    name = forms.CharField(help_text="***",
        widget=forms.TextInput(
            attrs={'placeholder': 'Collection title'}
        )
    )
    acq_day = forms.DateField(
        widget=forms.DateInput(attrs={"type":"date"}),
        required = False
    )
    price = forms.IntegerField(
        widget=forms.TextInput(attrs={"type": "text"}),
        required=False
    )

    class Meta:
        model = Collect
        fields = [
        'name', 'product_name', 'maker', 'num', 'acq_day','acq_place', 'price',
        'acq_day', 'state', 'category', 'place', 'saved', 'public', 'explain'
        ]

        """   ラジオボタン
        widgets = {
            'state': forms.RadioSelect(),
        }
        """

    def __init__(self, user, *args, **kwargs):
        #author = self.request.user
        #slug = ''.join(random.choice(string.ascii_letters + string.digits + kigou) for _ in range(8))
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['place'].queryset = Place.objects.filter(user=user)


class ImageForm(forms.ModelForm):
    photo = forms.ImageField(label='Image')
    class Meta:
        models = Photo
        fields = ('photo', 'collect')

"""
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        
class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = '__all__'
"""