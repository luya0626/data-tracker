from flask import Blueprint, request, jsonify
from database import get_db

data_points_bp = Blueprint('data_points', __name__)


def _point_to_dict(row):
    return {
        'id': row['id'],
        'line_id': row['line_id'],
        'date': row['date'],
        'value': row['value'],
        'tag': row['tag'] or '',
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


@data_points_bp.route('/api/data-points', methods=['GET'])
def list_data_points():
    db = get_db()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    # Fetch all lines
    lines = db.execute(
        'SELECT * FROM lines ORDER BY sort_order ASC, created_at ASC'
    ).fetchall()

    result = []
    for line in lines:
        # Query data points for this line
        params = [line['id']]
        where_clauses = ['line_id = ?']
        if start_date:
            where_clauses.append('date >= ?')
            params.append(start_date)
        if end_date:
            where_clauses.append('date <= ?')
            params.append(end_date)

        points = db.execute(
            f"SELECT id, line_id, date, value, tag FROM data_points "
            f"WHERE {' AND '.join(where_clauses)} "
            f"ORDER BY date ASC",
            params
        ).fetchall()

        result.append({
            'line_id': line['id'],
            'line_name': line['name'],
            'line_color': line['color'],
            'visible': bool(line['visible']),
            'points': [{'id': p['id'], 'date': p['date'], 'value': p['value'], 'tag': p['tag'] or ''} for p in points]
        })

    return jsonify(result)


@data_points_bp.route('/api/data-points', methods=['POST'])
def create_or_update_data_point():
    data = request.get_json(silent=True) or {}
    line_id = data.get('line_id')
    date = (data.get('date') or '').strip()
    value = data.get('value')
    tag = (data.get('tag') or '').strip()

    if not line_id or not date or value is None:
        return jsonify({'error': 'line_id, date, and value are required.'}), 400

    try:
        value = float(value)
    except (TypeError, ValueError):
        return jsonify({'error': 'value must be a number.'}), 400

    db = get_db()

    # Check line exists
    line = db.execute('SELECT id FROM lines WHERE id = ?', (line_id,)).fetchone()
    if not line:
        return jsonify({'error': 'Line not found.'}), 404

    # Upsert
    existing = db.execute(
        'SELECT id FROM data_points WHERE line_id = ? AND date = ?',
        (line_id, date)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE data_points SET value = ?, tag = ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (value, tag, existing['id'])
        )
        db.commit()
        row = db.execute('SELECT * FROM data_points WHERE id = ?', (existing['id'],)).fetchone()
        return jsonify(_point_to_dict(row)), 200
    else:
        cursor = db.execute(
            'INSERT INTO data_points (line_id, date, value, tag) VALUES (?, ?, ?, ?)',
            (line_id, date, value, tag)
        )
        db.commit()
        row = db.execute('SELECT * FROM data_points WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(_point_to_dict(row)), 201


@data_points_bp.route('/api/data-points/<int:point_id>', methods=['PUT'])
def update_data_point(point_id):
    data = request.get_json(silent=True) or {}
    db = get_db()

    row = db.execute('SELECT * FROM data_points WHERE id = ?', (point_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Data point not found.'}), 404

    updates = {}

    if 'date' in data:
        new_date = (data['date'] or '').strip()
        if not new_date:
            return jsonify({'error': 'Date cannot be empty.'}), 400
        # Check for conflict
        conflict = db.execute(
            'SELECT id FROM data_points WHERE line_id = ? AND date = ? AND id != ?',
            (row['line_id'], new_date, point_id)
        ).fetchone()
        if conflict:
            return jsonify({'error': 'A data point for this line and date already exists.'}), 409
        updates['date'] = new_date

    if 'tag' in data:
        updates['tag'] = (data['tag'] or '').strip()

    if 'value' in data:
        try:
            updates['value'] = float(data['value'])
        except (TypeError, ValueError):
            return jsonify({'error': 'value must be a number.'}), 400

    if updates:
        updates['updated_at'] = "datetime('now','localtime')"
        set_clause = ', '.join(
            f"{k} = {v}" if k == 'updated_at' else f"{k} = ?"
            for k, v in updates.items()
        )
        params = [v for k, v in updates.items() if k != 'updated_at']
        params.append(point_id)
        db.execute(f'UPDATE data_points SET {set_clause} WHERE id = ?', params)
        db.commit()

    row = db.execute('SELECT * FROM data_points WHERE id = ?', (point_id,)).fetchone()
    return jsonify(_point_to_dict(row))


@data_points_bp.route('/api/data-points/<int:point_id>', methods=['DELETE'])
def delete_data_point(point_id):
    db = get_db()
    row = db.execute('SELECT id FROM data_points WHERE id = ?', (point_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Data point not found.'}), 404
    db.execute('DELETE FROM data_points WHERE id = ?', (point_id,))
    db.commit()
    return jsonify({'success': True})
