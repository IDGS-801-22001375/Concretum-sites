from flask import render_template, request, jsonify, make_response
from flask_security import login_required, roles_accepted
from models import User
from . import auditoria_bp
import datetime
import csv
from io import StringIO
import re

@auditoria_bp.route('/')
@login_required
@roles_accepted('ADMINISTRADOR')
def index():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    return render_template('auditoria/index.html', start_date=start_date, end_date=end_date)

@auditoria_bp.route('/api', methods=['GET'])
@login_required
@roles_accepted('ADMINISTRADOR')
def api_auditoria():
    from app import mongo_db
    import re
    
    page = 1
    per_page = 10
    search = request.args.get('search', '')
    start_date_str = None
    end_date_str = None

    full_query = request.query_string.decode('utf-8')
    
    page_match = re.search(r'page=(\d+)', full_query)
    if page_match:
        page = int(page_match.group(1))

    per_page_match = re.search(r'per_page=(\d+)', full_query)
    if per_page_match:
        per_page = int(per_page_match.group(1))
        
    start_match = re.search(r'start_date=(\d{4}-\d{2}-\d{2})', full_query)
    if start_match:
        start_date_str = start_match.group(1)
        
    end_match = re.search(r'end_date=(\d{4}-\d{2}-\d{2})', full_query)
    if end_match:
        end_date_str = end_match.group(1)

    query = {}

    # Filtro de fechas
    if start_date_str and end_date_str:
        try:
            start = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query['fecha_creacion'] = {'$gte': start, '$lte': end}
        except ValueError:
            pass

    # Filtro de búsqueda
    if search:
        search = search.split('/api?')[0].split('?')[0]
        regex = re.compile(search, re.IGNORECASE)
        query['$or'] = [
            {'evento': regex},
            {'modulo': regex},
            {'detalles': regex}
        ]

    # Paginación y ordenamiento
    total_docs = mongo_db.auditoria_eventos.count_documents(query)
    cursor = mongo_db.auditoria_eventos.find(query).sort('fecha_creacion', -1).skip((page - 1) * per_page).limit(per_page)

    users_cache = {}
    items = []
    
    for log in cursor:
        uid = log.get('usuario_id')
        if uid and uid not in users_cache:
            user = User.query.filter_by(id_usuario=int(uid)).first()
            users_cache[uid] = user.username if user else 'Usuario Borrado'
        
        usuario_nombre = users_cache.get(uid, 'Sistema') if uid else 'Sistema'

        fecha = log.get('fecha_creacion')
        fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S') if isinstance(fecha, datetime.datetime) else 'N/A'

        items.append({
            'id': str(log['_id']),
            'fecha': fecha_str,
            'modulo': log.get('modulo', 'General'),
            'evento': log.get('evento', 'Desconocido'),
            'usuario': usuario_nombre,
            'detalles': log.get('detalles', ''),
            'ip': log.get('ip', 'N/A')
        })

    return jsonify({
        'items': items,
        'total': total_docs,
        'page': page,
        'pages': (total_docs + per_page - 1) // per_page if per_page else 1,
        'per_page': per_page
    })

@auditoria_bp.route('/exportar')
@login_required
@roles_accepted('ADMINISTRADOR')
def exportar():
    from app import mongo_db
    import re
    
    full_query = request.query_string.decode('utf-8')
    start_date_str = None
    end_date_str = None
    
    start_match = re.search(r'start_date=(\d{4}-\d{2}-\d{2})', full_query)
    if start_match:
        start_date_str = start_match.group(1)
        
    end_match = re.search(r'end_date=(\d{4}-\d{2}-\d{2})', full_query)
    if end_match:
        end_date_str = end_match.group(1)

    query = {}
    if start_date_str and end_date_str:
        try:
            start = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query['fecha_creacion'] = {'$gte': start, '$lte': end}
        except ValueError:
            pass

    logs = mongo_db.auditoria_eventos.find(query).sort('fecha_creacion', -1)

    si = StringIO()
    si.write('\ufeff')
    cw = csv.writer(si)
    cw.writerow(['Fecha', 'Modulo', 'Evento', 'Usuario', 'Detalles', 'IP'])

    users_cache = {}
    for log in logs:
        uid = log.get('usuario_id')
        if uid and uid not in users_cache:
            user = User.query.filter_by(id_usuario=int(uid)).first()
            users_cache[uid] = user.username if user else 'Usuario Borrado'
        
        usuario_nombre = users_cache.get(uid, 'Sistema') if uid else 'Sistema'
        fecha = log.get('fecha_creacion')
        fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S') if isinstance(fecha, datetime.datetime) else 'N/A'

        cw.writerow([
            fecha_str,
            log.get('modulo', ''),
            log.get('evento', ''),
            usuario_nombre,
            log.get('detalles', ''),
            log.get('ip', '')
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=auditoria_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8-sig"
    return output