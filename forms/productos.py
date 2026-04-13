from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class ProductoForm(FlaskForm):
    categoria_id = SelectField(
        'Categoria', 
        validators=[DataRequired(message="Este campo es requerido")], 
        choices=[], 
        coerce=int
    )

    enlace_fotografia = FileField(
        'Fotografía',
        validators=[
            FileAllowed(['jpg', 'png', 'jpeg'], message="Solo se permiten imágenes")
        ]
    )

    sku = StringField(
        'SKU',
        validators=[DataRequired(message="Este campo es requerido"), Length(max=100)]
    )

    nombre = StringField(
        'Nombre',
        validators=[DataRequired(message="Este campo es requerido"), Length(max=200)]
    )

    descripcion = StringField(
        'Descripción',
        validators=[Optional(), Length(max=255)] 
    )

    unidad_medida_id = SelectField(
        'Unidad de Medida',
        validators=[DataRequired(message="Este campo es requerido")],
        choices=[],
        coerce=int
    )

    resistencia_mpa = DecimalField(
        'Resistencia MPA',
        validators=[Optional(), NumberRange(min=0, message="Debe ser 0 o mayor")] 
    )

    color_id = SelectField(
        'Color',
        validators=[DataRequired(message="Este campo es requerido")],
        choices=[],
        coerce=int
    )

    precio_base = DecimalField(
        'Precio Base',
        validators=[DataRequired(message="Este campo es requerido"), NumberRange(min=0, message="No puede ser negativo")]
    )
