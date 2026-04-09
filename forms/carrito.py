from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email


class AgregarAlCarritoForm(FlaskForm):
    """Formulario para agregar un producto al carrito."""

    producto_id = IntegerField(
        'Producto',
        validators=[DataRequired(message="El producto es requerido")]
    )
    cantidad = DecimalField(
        'Cantidad',
        validators=[
            DataRequired(message="La cantidad es requerida"),
            NumberRange(min=1, message="La cantidad mínima es 1")
        ],
        places=3,
        default=1
    )


class ActualizarCantidadForm(FlaskForm):
    """Formulario para actualizar la cantidad de un ítem en el carrito."""

    item_id = IntegerField(
        'Ítem',
        validators=[DataRequired(message="El ítem es requerido")]
    )
    cantidad = DecimalField(
        'Cantidad',
        validators=[
            DataRequired(message="La cantidad es requerida"),
            NumberRange(min=1, message="La cantidad mínima es 1")
        ],
        places=3
    )


class CheckoutForm(FlaskForm):
    """Formulario de checkout / pasarela de pago."""

    # Datos de entrega
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

    # Método de pago
    metodo_pago = SelectField(
        'Método de pago',
        choices=[
            ('TARJETA',       'Tarjeta de crédito / débito'),
            ('TRANSFERENCIA', 'Transferencia bancaria'),
            ('OXXO',          'Pago en OXXO'),
        ],
        validators=[DataRequired(message="Selecciona un método de pago")]
    )

    # Datos de tarjeta (solo se validan si metodo_pago == TARJETA, la lógica va en la ruta)
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