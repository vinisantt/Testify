import unicodedata
from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'id':"login-username",
                'required data-msg':"Você deve preencher o campo de usuário",
                'placeholder':"Digite seu nome de usuário" ,
                'class':"input-material"
            }
        ),
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                'id':"login-password",
                'required data-msg':"Você deve preencher o campo de senha",
                'class':"input-material",
                'placeholder':'Digite sua senha'
            }
        ),
    )

class FeatureForm(forms.Form):

    feature = forms.ModelChoiceField(
        queryset=Feature.objects.filter(author__isnull=True),
        label=("Funcionalidade"),
        widget=forms.Select(
            attrs={
                'required data-msg':"Selecione uma funcionalidade",
                'class':'custom-select mr-sm-2'
                }
            ),
        help_text='Funcionalidade no qual você ficará responsável por criar casos de teste.'
    )

    def clean(self):
        feature = self.cleaned_data.get('feature')
    
        return self.cleaned_data

class CaseForm(forms.Form):
    
    name = forms.CharField(
        label=('Nome'),
        widget=forms.TextInput(
            attrs={
                'class':"form-control"
                }
            ),
        help_text='Nome do caso de teste.'
    )
    component = forms.ModelChoiceField(
        queryset=Componentes.objects.all(),
        label=("Componente"),
        widget=forms.Select(
            attrs={
                'class':'custom-select mr-sm-2'
                }
            ),
        help_text='Componente que faz parte desta funcionalidade.'     
    )
    precondition = forms.CharField(
        label=('Pré-Condição'),
        widget=forms.TextInput(
            attrs={
                'class':"form-control"
                }
            ),
        help_text='Condição necessária para que seja possível realizar este caso de teste.'
    )
    inputs = forms.CharField(
        label=('Entradas'),
        widget=forms.TextInput(
            attrs={
                'class':"form-control"
                }
            ),
        required=False,
        help_text='Entradas necessárias para realizar este caso de teste (Deixe em branco caso não precise).'

    )
    action = forms.CharField(
        label=('Ação'),
        widget=forms.TextInput(
            attrs={
                'class':"form-control"
                }
            ),
        help_text='Procedimento a ser realizado (Passo a passo).'
    )
    expected = forms.CharField(
        label=('Resultado Esperado'),
        widget=forms.TextInput(
            attrs={
                'class':"form-control"
                }
            ),
        help_text='O que se espera que aconteça após pôr em prática este caso de teste.'
    )
    postcondition = forms.CharField(
        label=('Pós-Condição'),
        widget=forms.TextInput(
            attrs={
                'class':"form-control"
                }
            ),
        help_text='O que será verdade após realizar o procedimento.'
    )

    def clean(self):
        name = self.cleaned_data.get('name')
        component = self.cleaned_data.get('component')
        precondition = self.cleaned_data.get('precondition')
        inputs = self.cleaned_data.get('inputs')
        action = self.cleaned_data.get('action')
        expected = self.cleaned_data.get('expected')
        postcondition = self.cleaned_data.get('postcondition')


        return self.cleaned_data

class EditForm(forms.Form):
    
    def __init__(self,feature,case,*args,**kwargs):
        
        super(EditForm, self).__init__(*args, **kwargs)
        
        self.fields['name'] = forms.CharField(
            label=('Nome'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control"
                }
            ),
            initial=case.name
        )
        self.fields['component'] = forms.ModelChoiceField(
            queryset=Componentes.objects.all(),
            label=("Componente"),
            widget=forms.Select(
                attrs={
                    'class':'custom-select mr-sm-2'
                    }
                ),
            initial=case.component
                 
        )
        self.fields['precondition'] = forms.CharField(
            label=('Pré-Condição'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control"
                    }
                ),
            initial=case.precondition
        )
        self.fields['inputs'] = forms.CharField(
            label=('Entradas'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control"
                    }
                ),
            required=True,
            initial=case.inputs
        )
        self.fields['action'] = forms.CharField(
            label=('Ação'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control"
                    }
                ),
            initial=case.action
        )
        self.fields['expected'] = forms.CharField(
            label=('Resultado Esperado'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control"
                    }
                ),
            initial=case.expected
        )
        self.fields['postcondition'] = forms.CharField(
            label=('Pós-Condição'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control"
                    }
                ),
            initial=case.precondition
        )

    def clean(self):
        name = self.cleaned_data.get('name')
        component = self.cleaned_data.get('component')
        precondition = self.cleaned_data.get('precondition')
        inputs = self.cleaned_data.get('inputs')
        action = self.cleaned_data.get('action')
        expected = self.cleaned_data.get('expected')
        postcondition = self.cleaned_data.get('postcondition')


        return self.cleaned_data

class CaseViewForm(forms.Form):
    
    def __init__(self,feature,case,*args,**kwargs):
        
        super(CaseViewForm, self).__init__(*args, **kwargs)
        
        self.fields['name'] = forms.CharField(
            label=('Nome'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control",
                    'disabled': 'disabled'
                    }
                ),
            initial=case.name
        )
        self.fields['component'] = forms.ModelChoiceField(
            queryset=Componentes.objects.all(),
            label=("Componente"),
            widget=forms.Select(
                attrs={
                    'class':'custom-select mr-sm-2',
                    'disabled': 'disabled'
                    }
                ),
            initial=case.component
                 
        )
        self.fields['precondition'] = forms.CharField(
            label=('Pré-Condição'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control",
                    'disabled': 'disabled'
                    }
                ),
            initial=case.precondition
        )
        self.fields['inputs'] = forms.CharField(
            label=('Entradas'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control",
                    'disabled': 'disabled'}
                ),
            required=False,
            initial=case.inputs
        )
        self.fields['action'] = forms.CharField(
            label=('Ação'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control",
                    'disabled': 'disabled'
                    }
                ),
            initial=case.action
        )
        self.fields['expected'] = forms.CharField(
            label=('Resultado Esperado'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control",
                    'disabled': 'disabled'
                    }
                ),
            initial=case.expected
        )
        self.fields['postcondition'] = forms.CharField(
            label=('Pós-Condição'),
            widget=forms.TextInput(
                attrs={
                    'class':"form-control",
                    'disabled': 'disabled'
                    }
                ),
            initial=case.precondition
        )

    def clean(self):
        name = self.cleaned_data.get('name')
        component = self.cleaned_data.get('component')
        precondition = self.cleaned_data.get('precondition')
        inputs = self.cleaned_data.get('inputs')
        action = self.cleaned_data.get('action')
        expected = self.cleaned_data.get('expected')
        postcondition = self.cleaned_data.get('postcondition')


        return self.cleaned_data
