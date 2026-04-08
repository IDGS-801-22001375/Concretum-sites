from flask import render_template, request, jsonify
from flask_security import login_required, roles_accepted, current_user
from models import db, Cliente, ClienteDetalle
from forms import ClienteForm
from . import clientes_bp
from sqlalchemy import or_, asc, desc
import datetime

def registrar_auditoria(usuario_accion, accion, detalles):
    from app import mongo_db
    try:
        mongo_db.auditoria_eventos.insert_one({
            "usuario_id": usuario_accion,
            "evento": accion,
            "detalles": detalles,
            "modulo": "Clientes",
            "user_agent": request.headers.get('User-Agent'),
            "fecha_creacion": datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error Mongo: {e}")

@clientes_bp.route('/')
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_VENTAS', 'VENDEDOR')
def index():
    form = ClienteForm()
    total_activos = Cliente.query.filter_by(es_activo=1).count()
    
    # Clientes nuevos este mes
    mes_actual = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0)
    nuevos_mes = Cliente.query.filter(Cliente.fecha_creacion >= mes_actual).count()
    
    kpis = {
        'total_activos': total_activos,
        'nuevos_mes': nuevos_mes
    }
    return render_template('clientes/index.html', kpis=kpis, form=form)

@clientes_bp.route('/api', methods=['GET'])
@login_required
def api_clientes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'razon_social')
    sort_order = request.args.get('sort_order', 'asc')
    search = request.args.get('search', '')
    active_filter = request.args.get('active', '')

    query = Cliente.query

    if search:
        query = query.filter(or_(
            Cliente.razon_social.ilike(f'%{search}%'),
            Cliente.rfc.ilike(f'%{search}%'),
            Cliente.email.ilike(f'%{search}%')
        ))
    if active_filter:
        estado = 1 if active_filter == 'true' else 0
        query = query.filter(Cliente.es_activo == estado)

    if sort_order == 'asc':
        query = query.order_by(asc(getattr(Cliente, sort_by, Cliente.razon_social)))
    else:
        query = query.order_by(desc(getattr(Cliente, sort_by, Cliente.razon_social)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for c in paginated.items:
        telefono = c.detalle_info.telefono if c.detalle_info and c.detalle_info.telefono else '—'
        ciudad = c.detalle_info.ciudad if c.detalle_info and c.detalle_info.ciudad else '—'
        items.append({
            'id': c.id_cliente,
            'razon_social': c.razon_social,
            'rfc': c.rfc or '—',
            'email': c.email or '—',
            'telefono': telefono,
            'ciudad': ciudad,
            'es_activo': c.es_activo == 1
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@clientes_bp.route('/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_VENTAS', 'VENDEDOR')
def guardar_cliente():
    data = request.form
    id_cli = data.get('id_cliente')
    
    if id_cli:
        # Edición
        cliente = Cliente.query.get_or_404(int(id_cli))
        
        # Validar RFC único si se cambia
        if data.get('rfc') and data.get('rfc') != cliente.rfc and Cliente.query.filter_by(rfc=data.get('rfc')).first():
            return jsonify({'success': False, 'errors': {'rfc': 'El RFC ya está registrado en otro cliente.'}}), 400
            
        cliente.razon_social = data.get('razon_social')
        cliente.rfc = data.get('rfc')
        cliente.email = data.get('email')
        
        if not cliente.detalle_info:
            cliente.detalle_info = ClienteDetalle(cliente_id=cliente.id_cliente)
            
        cliente.detalle_info.telefono = data.get('telefono')
        cliente.detalle_info.direccion = data.get('direccion')
        cliente.detalle_info.ciudad = data.get('ciudad')
        cliente.detalle_info.estado = data.get('estado')
        cliente.detalle_info.codigo_postal = data.get('codigo_postal')
        cliente.detalle_info.notas = data.get('notas')
        
        db.session.commit()
        registrar_auditoria(current_user.id, "Editar Cliente", f"Cliente editado: {cliente.razon_social}")
        return jsonify({'success': True, 'message': 'Cliente actualizado exitosamente.'})
    else:
        # Nuevo Cliente
        if data.get('rfc') and Cliente.query.filter_by(rfc=data.get('rfc')).first():
            return jsonify({'success': False, 'errors': {'rfc': 'El RFC ya está registrado.'}}), 400
            
        nuevo_cliente = Cliente(
            razon_social=data.get('razon_social'),
            rfc=data.get('rfc'),
            email=data.get('email'),
            es_activo=1
        )
        db.session.add(nuevo_cliente)
        db.session.flush() # Para obtener el ID generado
        
        detalle = ClienteDetalle(
            cliente_id=nuevo_cliente.id_cliente,
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            ciudad=data.get('ciudad'),
            estado=data.get('estado'),
            codigo_postal=data.get('codigo_postal'),
            notas=data.get('notas')
        )
        db.session.add(detalle)
        db.session.commit()
        
        registrar_auditoria(current_user.id, "Crear Cliente", f"Cliente creado: {nuevo_cliente.razon_social}")
        return jsonify({'success': True, 'message': 'Cliente registrado correctamente.'})

@clientes_bp.route('/obtener/<int:id>', methods=['GET'])
@login_required
def obtener_cliente(id):
    c = Cliente.query.get_or_404(id)
    det = c.detalle_info
    return jsonify({
        'id': c.id_cliente,
        'razon_social': c.razon_social,
        'rfc': c.rfc,
        'email': c.email,
        'telefono': det.telefono if det else '',
        'direccion': det.direccion if det else '',
        'ciudad': det.ciudad if det else '',
        'estado': det.estado if det else '',
        'codigo_postal': det.codigo_postal if det else '',
        'notas': det.notas if det else '',
        'es_activo': c.es_activo == 1
    })

@clientes_bp.route('/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'GERENTE_VENTAS')
def alternar_estado(id):
    c = Cliente.query.get_or_404(id)
    c.es_activo = 0 if c.es_activo == 1 else 1
    estado_txt = "Activado" if c.es_activo == 1 else "Desactivado"
    db.session.commit()
    registrar_auditoria(current_user.id, "Estado Cliente", f"Cliente {c.razon_social} {estado_txt}")
    return jsonify({'success': True, 'message': f'Cliente {estado_txt.lower()} correctamente.'})