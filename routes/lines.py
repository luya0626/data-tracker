from flask import Blueprint, request, jsonify
from database import get_db
from config import COLOR_PALETTE

lines_bp = Blueprint('lines', __name__)


def _line_to_dict(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'color': row['color'],
        'visible': bool(row['visible']),
        'sort_order': row['sort_order'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


@lines_bp.route('/api/lines', methods=['GET'])
def list_lines():
    db = get_db()
    rows = db.execute(
        'SELECT * FROM lines ORDER BY sort_order ASC, created_at ASC'
    ).fetchall()
    return jsonify([_line_to_dict(r) for r in rows])


@lines_bp.route('/api/lines', methods=['POST'])
def create_line():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Line name is required.'}), 400

    db = get_db()

    # Check name uniqueness
    existing = db.execute('SELECT id FROM lines WHERE name = ?', (name,)).fetchone()
    if existing:
        return jsonify({'error': 'Line name already exists.'}), 409

    # Pick next available color from palette
    used_colors = {r['color'] for r in db.execute('SELECT color FROM lines').fetchall()}
    color = data.get('color')
    if not color:
        for c in COLOR_PALETTE:
            if c not in used_colors:
                color = c
                break
        if not color:
            color = COLOR_PALETTE[len(used_colors) % len(COLOR_PALETTE)]

    # Determine sort_order
    max_order = db.execute('SELECT MAX(sort_order) AS mo FROM lines').fetchone()
    sort_order = (max_order['mo'] or 0) + 1

    cursor = db.execute(
        'INSERT INTO lines (name, color, sort_order) VALUES (?, ?, ?)',
        (name, color, sort_order)
    )
    db.commit()

    row = db.execute('SELECT * FROM lines WHERE id = ?', (cursor.lastrowid,)).fetchone()
    return jsonify(_line_to_dict(row)), 201


@lines_bp.route('/api/lines/<int:line_id>', methods=['PUT'])
def update_line(line_id):
    data = request.get_json(silent=True) or {}
    db = get_db()

    row = db.execute('SELECT * FROM lines WHERE id = ?', (line_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Line not found.'}), 404

    updates = {}
    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return jsonify({'error': 'Line name cannot be empty.'}), 400
        # Check uniqueness (excluding self)
        dup = db.execute(
            'SELECT id FROM lines WHERE name = ? AND id != ?', (name, line_id)
        ).fetchone()
        if dup:
            return jsonify({'error': 'Line name already exists.'}), 409
        updates['name'] = name

    if 'color' in data:
        updates['color'] = data['color']

    if 'visible' in data:
        updates['visible'] = 1 if data['visible'] else 0

    if 'sort_order' in data:
        updates['sort_order'] = data['sort_order']

    if updates:
        updates['updated_at'] = "datetime('now','localtime')"
        set_clause = ', '.join(
            f"{k} = {v}" if k == 'updated_at' else f"{k} = ?"
            for k, v in updates.items()
        )
        params = [v for k, v in updates.items() if k != 'updated_at']
        params.append(line_id)
        db.execute(f'UPDATE lines SET {set_clause} WHERE id = ?', params)
        db.commit()

    row = db.execute('SELECT * FROM lines WHERE id = ?', (line_id,)).fetchone()
    return jsonify(_line_to_dict(row))


@lines_bp.route('/api/lines/<int:line_id>', methods=['DELETE'])
def delete_line(line_id):
    db = get_db()
    row = db.execute('SELECT id FROM lines WHERE id = ?', (line_id,)).fetchone()
    if not row:
        return jsonify({'error': 'Line not found.'}), 404
    db.execute('DELETE FROM lines WHERE id = ?', (line_id,))
    db.commit()
    return jsonify({'success': True})
