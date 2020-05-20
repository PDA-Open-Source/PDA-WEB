from .models import Entity
from django import forms


class EntityForm(forms.ModelForm):

    attachment = forms.FileField(required=False)
    pin_code = forms.IntegerField(widget=forms.NumberInput(attrs={
                                                'cols': 3, 'rows': 1, 'min': 0, 'max': 9999999999,
                                                'style': 'max-height:30px; line-height:20px;'
                                                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                                                         ' color: black; background-color:white;'
                                                         ' width:120px;'
                                                         ' border:none; padding-top:0px; margin-top:30.5px;'
                                                         'font-family:Helvetica; padding:0px;font-size:14px;'
                                                        })
                                  )

    class Meta:
        model = Entity

        widgets = {
            'name': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'border:None;'
                'margin-top:30.5px; font-family:Helvetica;'}),

            'business_registration_number': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:50%;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

            'tax_registration_number': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:58%;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

            'address_line1': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:74%;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

            'address_line2': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:74%;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

            'city': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:150px;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

            'state': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:150px;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

            'country': forms.TextInput(attrs={
                'cols': 3, 'rows': 1,
                'style': 'max-height:30px; line-height:20px;'
                         ' background: repeating-linear-gradient(0, #9ec6c4,#9ec6c4 1px,#fff 1px,#fff 30px);'
                         ' color: black; background-color:white;'
                         ' width:150px;'
                         ' border:none; padding-top:0px; margin-top:30.5px;'
                         'font-family:Helvetica; padding:0px;font-size:14px;'}),

                }

        fields = ['name', 'business_registration_number', 'tax_registration_number', 'address_line1', 'address_line2', 'city', 'state', 'country', 'pin_code', 'attachment', ]

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.fields['address_line2'].required = False

