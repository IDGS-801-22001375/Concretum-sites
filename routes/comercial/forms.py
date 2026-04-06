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


class TicketForm(FlaskForm):
    venta_id  = SelectField('Folio / Venta', coerce=int, validators=[DataRequired()])
    tipo      = SelectField('Tipo de Documento', choices=[
        ('ticket',  'Ticket de Remisión'),
        ('factura', 'Factura'),
    ])
    rfc       = StringField('RFC del Cliente', validators=[Optional()])
    uso_cfdi  = SelectField('Uso de CFDI', choices=[
        ('G03', 'G03 - Gastos en general'),
        ('P01', 'P01 - Por definir'),
    ])
    submit    = SubmitField('Generar Documento')