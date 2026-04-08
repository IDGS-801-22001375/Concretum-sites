from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, Length

class ClienteForm(FlaskForm):
    id_cliente    = HiddenField()
    razon_social  = StringField('Razón Social', validators=[DataRequired(), Length(max=200)])
    rfc           = StringField('RFC', validators=[Optional(), Length(max=20)])
    email         = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=254)])
    telefono      = StringField('Teléfono', validators=[Optional(), Length(max=10)])
    direccion     = StringField('Dirección', validators=[Optional(), Length(max=255)])
    ciudad        = StringField('Ciudad', validators=[Optional(), Length(max=50)])
    estado        = StringField('Estado', validators=[Optional(), Length(max=50)])
    codigo_postal = StringField('C.P.', validators=[Optional(), Length(max=5)])
    notas         = TextAreaField('Notas', validators=[Optional()])