from . import proveedores_bp
from flask import render_template, request, redirect, url_for, jsonify
from . import forms
from extensions import db
from .models import Proveedores

@proveedores_bp.route('/administracion/proveedores', methods=['GET', 'POST'])
def lista():
    create_form = forms.ProveedorForm(request.form)
    if request.method == 'POST':
        proveedor = Proveedores(
            razon_social=create_form.razon_social.data,
            rfc=create_form.rfc.data,
            email=create_form.email.data,
            telefono=create_form.telefono.data
        )
        db.session.add(proveedor)
        db.session.commit()
        return redirect(url_for('proveedores_bp.lista'))
    todos = Proveedores.query.filter_by(es_activo=1).all()
    return render_template('administracion/proveedores/index.html', form=create_form, proveedores=todos)

@proveedores_bp.route('/administracion/proveedores/editar', methods=['POST'])
def editar():
    create_form = forms.ProveedorForm(request.form)
    id = create_form.id_proveedor.data
    prov1 = db.session.query(Proveedores).filter(Proveedores.id_proveedor == id).first()
    prov1.razon_social = create_form.razon_social.data
    prov1.rfc = create_form.rfc.data
    prov1.email = create_form.email.data
    prov1.telefono = create_form.telefono.data
    db.session.add(prov1)
    db.session.commit()
    return redirect(url_for('proveedores_bp.lista'))

@proveedores_bp.route('/administracion/proveedores/desactivar', methods=['POST'])
def desactivar():
    id = request.form.get('id_proveedor')
    prov1 = db.session.query(Proveedores).filter(Proveedores.id_proveedor == id).first()
    prov1.es_activo = 0
    db.session.add(prov1)
    db.session.commit()
    return redirect(url_for('proveedores_bp.lista'))