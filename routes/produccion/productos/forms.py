from wtforms import DecimalField, Form, StringField, SelectField, NumberRange
from wtforms import IntegerField, DateField, SubmitField, validators, SelectMultipleField
from .routes import get_colores, get_unidades


class ProductoForm(Form):
    categoria_id = SelectField('categoria', [validators.DataRequired(message="Este campo es requerido")], coerce=int)
    enlace_fotografia = StringField('enlace', [validators.DataRequired(message="Este campo es requerido")], validators.Length(max=200))
    sku = StringField('sku', [validators.DataRequired(message="Este campo es requerido")], validators.Length(min=8, max=12))
    nombre = StringField('nombre', [validators.DataRequired(message="Este campo es requerido")], validators.Length(max=200))
    descripcion = StringField('descripcion', [validators.DataRequired(message="Este campo es requerido")], validators.Length(max=255))
    unidad_medida = SelectField('unidad_medida', validators=[validators.DataRequired()], choices=[], coerce=int)
    resistencia_mpa = DecimalField('resistencia_mpa', [validators.DataRequired(message="Este campo es requerido"), NumberRange(min=0.01, message="Debe ser mayor a 0")])
    color = SelectField('color', validators=[validators.DataRequired()], choices=[], coerce=int)
    precio_base = DecimalField('precio_base', [validators.DataRequired(message="Este campo es requerido")], NumberRange(min=0.01, message="Debe ser mayor a 0"))
    fecha_creacion = StringField('fecha_creacion', [validators.DataRequired(message="Este campo es requerido")], validators.Length(min=8, max=12))