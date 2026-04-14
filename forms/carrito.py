from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email


class AgregarAlCarritoForm(FlaskForm):
    producto_id = IntegerField(
        'Producto',
        validators=[DataRequired(message="El producto es requerido")]
    )
    cantidad = IntegerField(
        'Cantidad',
        validators=[
            DataRequired(message="La cantidad es requerida"),
            NumberRange(min=1, message="La cantidad mínima es 1")
        ],
        default=1
    )


class ActualizarCantidadForm(FlaskForm):
    item_id = IntegerField(
        'Ítem',
        validators=[DataRequired(message="El ítem es requerido")]
    )

    cantidad = IntegerField(
        'Cantidad',
        validators=[
            DataRequired(message="La cantidad es requerida"),
            NumberRange(min=1, message="La cantidad mínima es 1")
        ]
    )


class CheckoutForm(FlaskForm):
    direccion_entrega = StringField(
        'Dirección de entrega',
        validators=[
            DataRequired(message="La dirección es requerida"),
            Length(max=500, message="Máximo 500 caracteres")
        ]
    )

    notas = TextAreaField(
        'Notas adicionales',
        validators=[Optional(), Length(max=1000)]
    )

    metodo_pago = SelectField(
        'Método de pago',
        choices=[
            ('TARJETA',       'Tarjeta de crédito / débito'),
            ('TRANSFERENCIA', 'Transferencia bancaria'),
            ('OXXO',          'Pago en OXXO'),
        ],
        validators=[DataRequired(message="Selecciona un método de pago")]
    )

    nombre_titular = StringField(
        'Nombre del titular',
        validators=[Optional(), Length(max=100)]
    )
    numero_tarjeta = StringField(
        'Número de tarjeta',
        validators=[Optional(), Length(min=16, max=19)]
    )
    mes_vencimiento = SelectField(
        'Mes',
        choices=[(str(m).zfill(2), str(m).zfill(2)) for m in range(1, 13)],
        validators=[Optional()]
    )
    anio_vencimiento = SelectField(
        'Año',
        choices=[(str(a), str(a)) for a in range(2026, 2035)],
        validators=[Optional()]
    )
    cvv = StringField(
        'CVV',
        validators=[Optional(), Length(min=3, max=4)]
    )


class ContactoClienteForm(FlaskForm):
    """Formulario de contacto desde el portal del cliente."""

    asunto = StringField(
        'Asunto',
        validators=[
            DataRequired(message="El asunto es requerido"),
            Length(max=200)
        ]
    )
    mensaje = TextAreaField(
        'Mensaje',
        validators=[
            DataRequired(message="El mensaje es requerido"),
            Length(max=2000)
        ]
    )