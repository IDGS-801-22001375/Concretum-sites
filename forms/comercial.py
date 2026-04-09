from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class VentaForm(FlaskForm):
    cliente_id  = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    metodo_pago = SelectField('Método de Pago', choices=[
        ('EFECTIVO',      'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('CHEQUE',        'Cheque'),
        ('CREDITO',       'Crédito'),
    ], validators=[DataRequired()])
    submit = SubmitField('Registrar Venta')


class CorteForm(FlaskForm):
    fondo_inicial      = DecimalField('Fondo Inicial', places=2, validators=[
        DataRequired(), NumberRange(min=0)
    ])
    salida_proveedores = DecimalField('Salida por Proveedores', places=2, default=0, validators=[
        Optional(), NumberRange(min=0)
    ])
    submit = SubmitField('Realizar Corte')
