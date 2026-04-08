from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, DateField, TextAreaField
from wtforms.validators import DataRequired, NumberRange

class ProduccionForm(FlaskForm):

    receta_id = SelectField(
        'Receta',
        coerce=int,
        validators=[DataRequired()]
    )

    cantidad = DecimalField(
        'Cantidad de Producciones',
        validators=[DataRequired(), NumberRange(min=1)]
    )

    fecha_inicio = DateField(
        'Fecha de Inicio',
        validators=[DataRequired()]
    )

    observaciones = TextAreaField('Observaciones')