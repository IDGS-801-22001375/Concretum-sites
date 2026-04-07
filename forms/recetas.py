from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    DateField, FloatField, IntegerField,
    SelectField, TextAreaField, FieldList, FormField, ValidationError
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


def fecha_hoy(form, field):
    if field.data != date.today():
        raise ValidationError("La fecha debe ser la de hoy")


class RecetaDetalleForm(FlaskForm):
    class Meta:
        csrf = False  # obligatorio en subformularios con FormField

    materia_prima_id = SelectField(
        'Materia prima',
        coerce=int,
        choices=[],
        validators=[DataRequired(message="Selecciona una materia prima")]
    )

    cantidad = IntegerField(
        'Cantidad',
        validators=[
            DataRequired(message="La cantidad es obligatoria"),
            NumberRange(min=1, message="Debe ser mayor a 0")
        ]
    )

    # Nombre alineado al modelo: unidad_id
    unidad_id = SelectField(
        'Unidad de medida',
        coerce=int,
        choices=[],
        validators=[DataRequired(message="Selecciona una unidad")]
    )


class RecetaForm(FlaskForm):

    producto_id = SelectField(
        'Producto',
        coerce=int,
        choices=[],
        validators=[DataRequired(message="Selecciona un producto")]
    )

    descripcion = TextAreaField(
        'Descripción / Notas',
        validators=[
            Optional(),
            Length(max=255, message="Máximo 255 caracteres")
        ]
    )

    cuanto_produce = IntegerField(
        'Cantidad que produce',
        validators=[
            DataRequired(message="Este campo es obligatorio"),
            NumberRange(min=1, message="Debe ser mayor a 0")
        ]
    )

    tiempo_produccion = FloatField(
        'Tiempo de producción (h)',
        validators=[
            DataRequired(message="Este campo es obligatorio"),
            NumberRange(min=1, message="Debe ser mayor a 0")
        ]
    )

    resistencia = FloatField(
        "Resistencia f'c (kg/cm²)",
        validators=[
            DataRequired(message="Este campo es obligatorio"),
            NumberRange(min=1, message="Debe ser mayor a 0")
        ]
    )

    fecha_creacion = DateField(
        'Fecha de Registro',
        validators=[
            DataRequired(message="Este campo es requerido"),
            fecha_hoy
        ]
    )

    ingredientes = FieldList(
        FormField(RecetaDetalleForm),
        min_entries=1
    )