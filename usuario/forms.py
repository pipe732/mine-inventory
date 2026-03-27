from django import forms
from .models import Usuario, Rol


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'numero_documento',
            'id_rol',
            'nombre_completo',
            'correo',
            'telefono',
            'tipo_documento',
            'destinado',
            'solicitado',
        ]
        widgets = {
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1234567890'
            }),
            'id_rol': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3001234567'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'destinado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'solicitado': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'numero_documento': 'Número de Documento',
            'id_rol': 'Rol',
            'nombre_completo': 'Nombre Completo',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'tipo_documento': 'Tipo de Documento',
            'destinado': 'Destinado a',
            'solicitado': 'Solicitado por',
        }

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento')
        if not numero.isdigit():
            raise forms.ValidationError('El número de documento solo debe contener dígitos.')
        return numero

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener dígitos.')
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exclude(numero_documento=self.instance.numero_documento).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return correo