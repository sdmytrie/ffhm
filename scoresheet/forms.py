from api.models import *
from django import forms
from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _


class ScoresheetAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the scoresheet app.
    """
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a staff "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class ScoresheetPasswordChangeForm(PasswordChangeForm):
    required_css_class = 'required'


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'


class CompetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget = forms.widgets.TextInput(attrs={
                                                                'size': '50'})
        self.fields['gender'] = forms.ModelChoiceField(widget=forms.RadioSelect,
                                                       queryset=Gender.objects.all(),
                                                       empty_label=None)
        self.fields['place'].widget = forms.widgets.TextInput(attrs={
                                                              'size': '50'})
        self.fields['name'].widget = forms.widgets.TextInput(attrs={
                                                             'size': '50'})
        self.fields['troop'].widget = forms.widgets.TextInput(
            attrs={'size': '5', 'value': '100'})
        self.fields['start_date'] = forms.DateField(input_formats=['%d-%m-%Y'])
        self.fields['start_date'].widget = forms.widgets.DateInput(
            attrs={'class': 'datepicker', 'size': '10', 'readonly': 'readonly'}, format=('%d-%m-%Y'))

    class Meta:
        model = Competition
        fields = ['address', 'gender', 'kind', 'isteam', 'place', 'name',
                  'start_date', 'troop', 'ismasters', 'isminime', 'isrecordeligible']


class ListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.fields['start_date'] = forms.DateField(input_formats=['%d-%m-%Y'])

    class Meta:
        model = Event
        fields = '__all__'


class RankingForm(forms.Form):
    GENDER = (
        ('2', 'masculin'),
        ('3', 'féminin')
    )
    AGE = (
        ('U15', 'U15'),
        ('U17', 'U17'),
        ('U20', 'U20'),
        ('SENIOR', 'SENIOR'),
        ('Scratch', 'Scratch')
    )
    gender = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=GENDER,
        required=True)

    age = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=AGE,
        required=True)
