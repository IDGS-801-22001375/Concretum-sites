from flask_login.utils import login_required
from routes.inventario_produccion import stock_bp
from flask import render_template, request, redirect, url_for, flash
from models import db, Existencias, Productos, MovimientosInventario
from decimal import Decimal


def obtener_productos(page=1):
    pagination = db.session.query(Existencias)\
        .join(Productos, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .paginate(page=page, per_page=5)

    todas = db.session.query(Existencias)\
        .join(Productos, Productos.id_producto == Existencias.producto_id)\
        .filter(Productos.es_active == 1)\
        .all()

    bajo_stock = sum(1 for e in todas if e.estado_stock == 'BAJO')
    precaucion = sum(1 for e in todas if e.estado_stock == 'PRECAUCION')
    stock_ok   = sum(1 for e in todas if e.estado_stock == 'ALTO')

    return pagination, pagination.items, bajo_stock, precaucion, stock_ok


# =========================
# OBTENER STOCK (para HTML)
# =========================
@stock_bp.route('/stock-productos')
@login_required
def get_stock():
    page = request.args.get('page', 1, type=int)
    pagination, productos, bajo_stock, precaucion, stock_ok = obtener_productos(page)

    return render_template(
        'produccion/inventario/inventario.html',
        productos=productos,
        pagination=pagination,
        bajo_stock=bajo_stock,
        precaucion=precaucion,
        stock_ok=stock_ok
    )


# =========================
# EDITAR STOCK (SET DIRECTO)
# =========================
@stock_bp.route('/editar-stock/<int:id>', methods=['POST'])
@login_required
def editar_stock(id):
    existencia = Existencias.query.get_or_404(id)

    try:
        nuevo_stock = Decimal(request.form.get('stock', 0))
        diferencia = nuevo_stock - existencia.stock_actual

        if diferencia != 0:
            movimiento = MovimientosInventario(
                existencia_id=existencia.id_existencias,
                tipo='AJUSTE',
                cantidad=abs(diferencia),
                motivo='Edición directa de stock'
            )
            existencia.stock_actual = nuevo_stock
            db.session.add(movimiento)
            db.session.commit()
            db.session.refresh(existencia)

        flash('Stock actualizado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar stock: {str(e)}', 'error')

    return redirect(url_for('stock_bp.get_stock'))


# =========================
# AJUSTAR STOCK (+ / -)
# =========================
@stock_bp.route('/ajustar-stock/<int:id>', methods=['POST'])
@login_required
def ajustar_stock(id):
    existencia = Existencias.query.get_or_404(id)

    try:
        tipo     = request.form.get('tipo')
        cantidad = Decimal(request.form.get('cantidad', 0))

        if cantidad <= 0:
            flash('Cantidad inválida', 'error')
            return redirect(url_for('stock_bp.get_stock'))

        if tipo == 'entrada':
            existencia.stock_actual += cantidad
            tipo_mov = 'AJUSTE'

        elif tipo == 'salida':
            if cantidad > existencia.stock_actual:
                flash('No puedes sacar más de lo disponible', 'error')
                return redirect(url_for('stock_bp.get_stock'))
            existencia.stock_actual -= cantidad
            tipo_mov = 'SALIDA'

        else:
            flash('Tipo inválido', 'error')
            return redirect(url_for('stock_bp.get_stock'))

        movimiento = MovimientosInventario(
            existencia_id=existencia.id_existencias,
            tipo=tipo_mov,
            cantidad=cantidad,
            motivo='Ajuste manual'
        )
        db.session.add(movimiento)
        db.session.commit()
        db.session.refresh(existencia)

        flash('Ajuste aplicado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error en ajuste: {str(e)}', 'error')

    return redirect(url_for('stock_bp.get_stock'))


# =========================
# OBTENER STOCK ACTUAL (JSON)
# =========================
@stock_bp.route('/stock-actual/<int:id>', methods=['GET'])
@login_required
def obtener_stock_actual(id):
    existencia = Existencias.query.get_or_404(id)

    return {
        "producto":     existencia.producto.nombre,
        "stock_actual": float(existencia.stock_actual),
        "estado_stock": existencia.estado_stock
    }