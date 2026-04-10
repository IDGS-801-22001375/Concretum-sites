import datetime
import uuid
import os
from werkzeug.utils import secure_filename
from flask import render_template, request, jsonify, url_for
from flask_security import login_required, roles_accepted, current_user
from routes.productos import productos_bp
from models import db, Productos, CategoriasProducto, UnidadMedida, Color, Existencias

def get_colores():
    return [{'value': c.id_color, 'label': c.nombre} for c in Color.query.filter_by(es_active=True).all()]

def get_unidades():
    return [{'value': u.id_unidad, 'label': u.nombre} for u in UnidadMedida.query.filter_by(es_active=True).all()]

def get_categorias():
    return [{'value': ca.id_categoria, 'label': ca.nombre} for ca in CategoriasProducto.query.filter_by(es_active=True).all()]

def convertir_ruta_imagen(enlace_fotografia):
    filename = secure_filename(enlace_fotografia.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"
    ruta_relativa = f"images/productos/{unique_name}"
    ruta_fisica = os.path.join("static", ruta_relativa)
    enlace_fotografia.save(ruta_fisica)
    return ruta_relativa

@productos_bp.route('/productos')
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def get_datos():
    # KPIs rápidos
    total_productos = Productos.query.count()
    activos = Productos.query.filter_by(es_active=1).count()
    inactivos = Productos.query.filter_by(es_active=0).count()

    todas_existencias = Existencias.query.join(Productos).filter(Productos.es_active == 1).all()
    bajo_stock = sum(1 for e in todas_existencias if e.estado_stock == 'BAJO')

    kpis = {
        'total': total_productos,
        'activos': activos,
        'inactivos': inactivos,
        'bajo_stock': bajo_stock
    }

    return render_template(
        'produccion/productos/productos.html',
        kpis=kpis,
        categorias_options=get_categorias(),
        unidades_options=get_unidades(),
        colores_options=get_colores()
    )

@productos_bp.route('/productos/api', methods=['GET'])
@login_required
def api_productos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')
    categoria_filter = request.args.get('categoria', '')

    query = Productos.query

    if search:
        query = query.filter(Productos.nombre.ilike(f'%{search}%') | Productos.sku.ilike(f'%{search}%'))
    if categoria_filter:
        query = query.filter(Productos.categoria_id == int(categoria_filter))

    if sort_order == 'asc':
        from sqlalchemy import asc
        query = query.order_by(asc(getattr(Productos, sort_by, Productos.nombre)))
    else:
        from sqlalchemy import desc
        query = query.order_by(desc(getattr(Productos, sort_by, Productos.nombre)))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for p in paginated.items:
        stock_actual = float(p.existencia.stock_actual) if p.existencia else 0.0
        
        items.append({
            'id': p.id_producto,
            'enlace_fotografia': url_for('static', filename=p.enlace_fotografia),
            'sku': p.sku,
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'categoria': p.categoria.nombre if p.categoria else '',
            'unidad_medida': p.unidad_medida.nombre if p.unidad_medida else '',
            'stock': stock_actual,  
            'resistencia_mpa': float(p.resistencia_mpa) if p.resistencia_mpa else None,
            'color_nombre': p.color.nombre if p.color else '',
            'color_hex': p.color.codigo_hex if p.color else '',
            'precio_base': float(p.precio_base),
            'es_activo': p.es_active == 1
        })

    return jsonify({
        'items': items,
        'total': paginated.total,
        'page': paginated.page,
        'pages': paginated.pages,
        'per_page': paginated.per_page
    })

@productos_bp.route('/productos/obtener/<int:id>', methods=['GET'])
@login_required
def obtener_producto(id):
    p = Productos.query.get_or_404(id)
    return jsonify({
        'id_producto': p.id_producto,
        'categoria_id': p.categoria_id,
        'sku': p.sku,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'unidad_medida_id': p.unidad_medida_id,
        'resistencia_mpa': float(p.resistencia_mpa) if p.resistencia_mpa else '',
        'color_id': p.color_id,
        'precio_base': float(p.precio_base)
    })

@productos_bp.route('/productos/guardar', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def guardar_producto():
    data = request.form
    id_prod = data.get('id_producto')

    # Manejo de la subida de imagen
    enlace_fotografia = request.files.get('enlace_fotografia')
    filename = None
    if enlace_fotografia and enlace_fotografia.filename:
        filename = convertir_ruta_imagen(enlace_fotografia)

    if id_prod:
        # Edición
        p = Productos.query.get_or_404(int(id_prod))

        # Validar SKU único
        if data.get('sku') != p.sku and Productos.query.filter_by(sku=data.get('sku')).first():
            return jsonify({'success': False, 'message': 'El SKU ya está registrado en otro producto.'}), 400

        p.categoria_id = data.get('categoria_id')
        p.sku = data.get('sku')
        p.nombre = data.get('nombre')
        p.descripcion = data.get('descripcion')
        p.unidad_medida_id = data.get('unidad_medida_id')
        p.resistencia_mpa = data.get('resistencia_mpa') or 0
        p.color_id = data.get('color_id')
        p.precio_base = data.get('precio_base')

        if filename:
            p.enlace_fotografia = filename

        db.session.commit()
        return jsonify({'success': True, 'message': 'Producto actualizado exitosamente.'})
    else:
        # Creación
        if Productos.query.filter_by(sku=data.get('sku')).first():
            return jsonify({'success': False, 'message': 'El SKU ya está registrado.'}), 400

        if not filename:
            return jsonify({'success': False, 'message': 'La imagen es obligatoria.'}), 400

        nuevo_producto = Productos(
            categoria_id=data.get('categoria_id'),
            enlace_fotografia=filename,
            sku=data.get('sku'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            unidad_medida_id=data.get('unidad_medida_id'),
            resistencia_mpa=data.get('resistencia_mpa') or 0,
            color_id=data.get('color_id'),
            precio_base=data.get('precio_base'),
            fecha_creacion=datetime.datetime.now()
        )
        db.session.add(nuevo_producto)
        db.session.flush()

        # Crear registro de existencias en 0 automáticamente
        nueva_existencia = Existencias(
            producto_id=nuevo_producto.id_producto,
            stock_actual=0.000,
            stock_minimo=0.000,
            estado_stock='BAJO'
        )
        db.session.add(nueva_existencia)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Producto registrado correctamente.'})

@productos_bp.route('/productos/alternar_estado/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMINISTRADOR', 'PRODUCCION')
def alternar_estado(id):
    p = Productos.query.get_or_404(id)
    p.es_active = 0 if p.es_active == 1 else 1
    estado_txt = "Activado" if p.es_active == 1 else "Desactivado"
    db.session.commit()
    return jsonify({'success': True, 'message': f'Producto {estado_txt.lower()} correctamente.'})