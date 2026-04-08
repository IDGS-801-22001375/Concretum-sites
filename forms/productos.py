from datetime import date
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, ValidationError
from wtforms import DateField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, NumberRange, Length

def fecha_hoy(form, field):
    if field.data != date.today():
        raise ValidationError("La fecha debe ser la de hoy")

class ProductoForm(FlaskForm):
    categoria_id = SelectField(
        'Categoria', 
        [DataRequired(message="Este campo es requerido")], 
        choices=[], 
        coerce=int
    )

    enlace_fotografia = FileField(
        'Fotografía',
        validators=[
            FileRequired(message="La imagen es requerida"),
            FileAllowed(['jpg', 'png', 'jpeg'], message="Solo imágenes")
        ]
    )

    sku = StringField(
        'SKU',
        [DataRequired(message="Este campo es requerido"), Length(min=8, max=12)]
    )

    nombre = StringField(
        'Nombre',
        [DataRequired(message="Este campo es requerido"), Length(max=200)]
    )

    descripcion = StringField(
        'Descripción',
        [DataRequired(message="Este campo es requerido"), Length(max=255)]
    )

    unidad_medida = SelectField(
        'Unidad de Medida',
        validators=[DataRequired(message="Este campo es requerido")],
        choices=[],
        coerce=int
    )

    resistencia_mpa = DecimalField(
        'Resistencia MPA',
        [DataRequired(message="Este campo es requerido"), NumberRange(min=0.01, message="Debe ser mayor a 0")]
    )

    color = SelectField(
        'Color',
        validators=[DataRequired(message="Este campo es requerido")],
        choices=[],
        coerce=int
    )

    precio_base = DecimalField(
        'Precio Base',
        [DataRequired(message="Este campo es requerido"), NumberRange(min=0.01, message="Debe ser mayor a 0")]
    )

    fecha_creacion = DateField(
        'Fecha de Registro',
        validators=[
            DataRequired(message="Este campo es requerido"),
        ]
    )