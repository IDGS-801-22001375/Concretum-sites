from flask import render_template, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from models import db, Proveedor, Compra, PagoProveedor, CategoriaProveedor
from . import proveedores_bp
from sqlalchemy import or_, asc, desc, func
import datetime

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Proveedores",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

# ----------------------------------------------------------------------
# VISTA PRINCIPAL
# ----------------------------------------------------------------------
@proveedores_bp.route('/proveedores')
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS', 'COMPRADOR')
def index():
    # Calculamos KPIs
    total_activos = Proveedor.query.filter_by(es_activo=True).count()
    volumen_mensual = db.session.query(func.sum(Compra.total)).filter(
        Compra.fecha_compra >= datetime.datetime.utcnow() - datetime.timedelta(days=30)
    ).scalar() or 0
    # Cuentas vencidas: pagos con fecha_vencimiento < hoy y fecha_pago nulo
    hoy = datetime.date.today()
    cuentas_vencidas = PagoProveedor.query.filter(
        PagoProveedor.fecha_vencimiento < hoy,
        PagoProveedor.fecha_pago == None
    ).count()
    monto_vencido = db.session.query(func.sum(PagoProveedor.monto)).filter(
        PagoProveedor.fecha_vencimiento < hoy,
        PagoProveedor.fecha_pago == None
    ).scalar() or 0

    kpis = {
        'total_activos': total_activos,
        'volumen_mensual': float(volumen_mensual),
        'cuentas_vencidas': cuentas_vencidas,
        'monto_vencido': float(monto_vencido)
    }
    return render_template('proveedores/index.html', kpis=kpis)

# ----------------------------------------------------------------------
# API PARA OBTENER PROVEEDORES (formato tarjetas)
# ----------------------------------------------------------------------
@proveedores_bp.route('/proveedores/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS', 'COMPRADOR')
def api_proveedores():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'razon_social')
    sort_order = request.args.get('sort_order', 'asc')
    search = request.args.get('search', '')
    active_filter = request.args.get('active', '')
    categoria_filter = request.args.get('categoria', '')

    query = Proveedor.query

    if search:
        query = query.filter(or_(
            Proveedor.razon_social.ilike(f'%{search}%'),
            Proveedor.rfc.ilike(f'%{search}%'),
            Proveedor.email.ilike(f'%{search}%')
        ))
    if active_filter:
        if active_filter == 'true':
            query = query.filter(Proveedor.es_activo == True)
        elif active_filter == 'false':
            query = query.filter(Proveedor.es_activo == False)
    if categoria_filter:
        query = query.filter(Proveedor.categoria == categoria_filter)

    # Ordenamiento
    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Proveedor, sort_by, Proveedor.razon_social)))
    else:
        query = query.order_by(desc(getattr(Proveedor, sort_by, Proveedor.razon_social)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for p in paginated.items:
        items.append({
            'id': p.id,
            'razon_social': p.razon_social,
            'rfc': p.rfc,
            'email': p.email,
            'telefono': p.telefono,
            'contacto': p.contacto,
            'telefono_contacto': p.telefono_contacto,
            'domicilio': p.domicilio,
            'categoria': p.categoria.value if p.categoria else '',
            'dias_credito': p.dias_credito,
            'limite_credito': float(p.limite_credito),
            'es_activo': p.es_activo,
            'total_compras': p.total_compras,
            'compras_ultimo_mes': p.compras_ultimo_mes,
            'monto_vencido': p.monto_vencido
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

# ----------------------------------------------------------------------
# GUARDAR PROVEEDOR (incluyendo nuevos campos)
# ----------------------------------------------------------------------
@proveedores_bp.route('/proveedores/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS')
def guardar_proveedor():
    data = request.form
    id_prov = data.get('id_proveedor')
    if id_prov:
        prov = Proveedor.query.get_or_404(int(id_prov))
        prov.razon_social = data['razon_social']
        prov.rfc = data['rfc']
        prov.email = data['email']
        prov.telefono = data['telefono']
        prov.contacto = data.get('contacto')
        prov.telefono_contacto = data.get('telefono_contacto')
        prov.domicilio = data.get('domicilio')
        prov.categoria = data.get('categoria')
        prov.dias_credito = int(data.get('dias_credito', 0))
        prov.limite_credito = float(data.get('limite_credito', 0))
        db.session.commit()
        registrar_auditoria(current_user.id, "Editar Proveedor", f"Proveedor editado: {prov.razon_social}")
        return jsonify({'success': True, 'message': 'Proveedor actualizado.'})
    else:
        if Proveedor.query.filter_by(rfc=data['rfc']).first():
            return jsonify({'success': False, 'errors': {'rfc': 'El RFC ya existe.'}}), 400
        prov = Proveedor(
            razon_social=data['razon_social'],
            rfc=data['rfc'],
            email=data['email'],
            telefono=data['telefono'],
            contacto=data.get('contacto'),
            telefono_contacto=data.get('telefono_contacto'),
            domicilio=data.get('domicilio'),
            categoria=data.get('categoria'),
            dias_credito=int(data.get('dias_credito', 0)),
            limite_credito=float(data.get('limite_credito', 0)),
            es_activo=True
        )
        db.session.add(prov)
        db.session.commit()
        registrar_auditoria(current_user.id, "Crear Proveedor", f"Proveedor creado: {prov.razon_social}")
        return jsonify({'success': True, 'message': 'Proveedor creado.'})

# ----------------------------------------------------------------------
# OBTENER UN PROVEEDOR (para edición)
# ----------------------------------------------------------------------
@proveedores_bp.route('/proveedores/obtener/<int:id>', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS')
def obtener_proveedor(id):
    prov = Proveedor.query.get_or_404(id)
    return jsonify({
        'id': prov.id,
        'razon_social': prov.razon_social,
        'rfc': prov.rfc,
        'email': prov.email,
        'telefono': prov.telefono,
        'contacto': prov.contacto,
        'telefono_contacto': prov.telefono_contacto,
        'domicilio': prov.domicilio,
        'categoria': prov.categoria.value if prov.categoria else '',
        'dias_credito': prov.dias_credito,
        'limite_credito': float(prov.limite_credito),
        'es_activo': prov.es_activo
    })

# ----------------------------------------------------------------------
# ALTERNAR ESTADO
# ----------------------------------------------------------------------
@proveedores_bp.route('/proveedores/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS')
def alternar_estado(id):
    prov = Proveedor.query.get_or_404(id)
    prov.es_activo = not prov.es_activo
    estado_txt = "Activado" if prov.es_activo else "Desactivado"
    registrar_auditoria(current_user.id, "Estado Proveedor", f"Proveedor {prov.razon_social} {estado_txt}")
    db.session.commit()
    return jsonify({'success': True, 'message': f'Proveedor {estado_txt.lower()} correctamente.'})

# ----------------------------------------------------------------------
# HISTORIAL DE PAGOS DE UN PROVEEDOR
# ----------------------------------------------------------------------
@proveedores_bp.route('/proveedores/<int:id>/pagos', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_COMPRAS', 'COMPRADOR')
def pagos_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    # Obtener todas las compras y sus pagos
    compras = proveedor.compras.all()
    pagos = []
    for compra in compras:
        for pago in compra.pagos:
            pagos.append({
                'id': pago.id,
                'compra_folio': compra.folio,
                'fecha_vencimiento': pago.fecha_vencimiento.strftime('%Y-%m-%d'),
                'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d') if pago.fecha_pago else None,
                'monto': float(pago.monto),
                'forma_pago': pago.forma_pago,
                'estatus': pago.estatus,
                'observaciones': pago.observaciones
            })
    return jsonify({'pagos': pagos})