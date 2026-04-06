from wtforms import Form, validators, StringField, IntegerField, EmailField

class ProveedorForm(Form):
    id_proveedor = IntegerField('id_proveedor')
    razon_social = StringField('razon_social', [
        validators.DataRequired(message='La razón social es requerida'),
        validators.Length(min=3, max=200, message='Entre 3 y 200 caracteres')
    ])
    rfc = StringField('rfc', [
        validators.DataRequired(message='El RFC es requerido'),
        validators.Length(min=12, max=20, message='Entre 3 y 200 caracteres')
    ])
    email = EmailField('correo', [
        validators.DataRequired(message='El correo es requerido'),
        validators.Email(message='Ingresa un correo valido')
    ])
    telefono = StringField('telefono', [
        validators.DataRequired(message='El telefono es requerido'),
        validators.Length(min=10, max=10, message='Debe tener exactamente 10 digitos')
    ])