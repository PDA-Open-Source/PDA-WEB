from .models import Program, Topic, Content
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget


class ProgramForm(forms.ModelForm):

    class Meta:

        model = Program
        widgets = {
            'name': forms.TextInput(attrs={

                'max_length': 50, 'min_length': 10,
                'style': 'border-bottom: 1px Solid #d0d0d0;'
                         'font-family:AvenirNext; '}),

            'description': forms.Textarea(attrs={

                'cols': 30, 'rows': 10,
                'style': 'max-height:90px; min-height:90px; line-height:30px;'
                         ' background: repeating-linear-gradient(0, #d0d0d0,#d0d0d0 1px,#fff 1px,#fff 31px);'
                         ' color: black; background-color:white;'
                         ' max-width:100%; min-width:100%;'
                         ' border:none; padding-top:0px;'
                         'font-family:AvenirNext; padding:0px;font-size:14px;'}),

            'start_date': forms.DateInput(attrs={
                'placeholder': 'Start Date',
                'class': 'textbox-n', 'type': 'text',
                'required': True,
                'input_formats': settings.DATE_INPUT_FORMATS,
                'id': 'datepicker-1',
                'style': 'border: solid 1px rgba(241, 113, 103, 0.42); background-color: white;'
                         'width:138px;'
                         'border-radius:4px; height:36px;'
                         'padding-left:14px;font-size:12px;font-family:AvenirNext;',
                'autocomplete': 'off'}),

            'end_date': forms.DateInput(attrs={
                'placeholder': 'End date',
                'class': 'textbox-n', 'type': 'text',
                'required': True,
                'input_formats': settings.DATE_INPUT_FORMATS,
                'id': 'datepicker-2',
                'style': 'border: solid 1px rgba(241, 113, 103, 0.42);'
                         'background-color: white;width:138px; '
                         'border-radius:4px;height:36px; padding-left:14px;'
                         ' font-size:12px;margin-left: 10px;font-family:AvenirNext;',
                'autocomplete': 'off'}),

            'user_limit': forms.NumberInput(attrs={
                'autocomplete': 'off',
                'id': 'user-limit',
                'style': 'width:213.6px; font-size:13px; '
                         'height:30px;'
                         'padding-left:10px; margin-left:13.5px;'
                         'border-bottom: 1px solid #d0d0d0;'
                         'border-top: none;'
                         'border-left: none;'
                         'border-right: none;'}),

        }

        fields = ['name', 'description', 'start_date', 'end_date', 'user_limit', ]


class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Add Topic',
                                           'style': 'border-bottom: 1px solid #d8e9e1;'
                                           'margin-top:1.5px; font-family:Helvetica; padding-bottom:10px;font-size: 14px;'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description',
                                                 'cols': 30, 'rows': 10,
                                                  ' style': 'max-height:90px; min-height:90px; line-height:30px;'
                                                  ' background: repeating-linear-gradient(0, #d8e9e1,#d8e9e1 1px,#fff 1px,#fff 31px);'
                                                  ' color: black; background-color:white;'
                                                  ' max-width:100%; min-width:100%;'
                                                  ' border:none; padding-top:0px; margin-top:30.5px;'
                                                  'font-family:Helvetica; padding:0px;font-size:14px;'}),
        }
        fields = ['name', 'description', ]


class TopicUpdateForm(forms.ModelForm):

    attachment = forms.FileField(required=False)

    class Meta:
        model = Content

        widgets = {

            'topic': forms.HiddenInput()
        }

        fields = ['topic', ]


class TopicUpdateForm1(forms.ModelForm):

    class Meta:
        model = Topic

        widgets = {

            'name': forms.TextInput(attrs={'placeholder': 'Enter Topic Name',
                                           'style': 'border:none; margin-top:1.5px; width: 60%; font-family:Helvetica; padding-bottom:10px; color:#024f9d; font-size:16px;'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description',
                                                  'cols': 30, 'rows': 10,
                                                  ' style': 'max-height:90px; min-height:90px; line-height:30px;'
                                                  ' color: black; background-color:white;'
                                                  ' max-width:100%; min-width:100%;'
                                                  ' border:none; padding-top:0px; margin-top:3px;'
                                                  'font-family:NotoSans; padding:0px;font-size:14px;'}),

        }
        fields = ['name', 'description', ]


class ContentForm(forms.ModelForm):

    attachment = forms.FileField(required=False)

    class Meta:
        model = Content

        fields = ['attachment', ]
