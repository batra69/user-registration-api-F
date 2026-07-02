from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- Database Config ----------
# Update these to match your local MySQL setup before running
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Batra@2003',
    'database': 'registration_db'
}

# Columns allowed to be sorted on (whitelist, to avoid SQL injection via sort_by)
SORTABLE_COLUMNS = {
    'reg_no': 'reg_no',
    'name': 'name',
    'gender': 'gender',
    'state': 'state'
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Pages ----------

@app.route('/')
def register_page():
    return render_template('register.html')


@app.route('/listing')
def listing_page():
    return render_template('listing.html')


# ---------- Form submission ----------

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '').strip()[:25]
    gender = request.form.get('gender', '')
    dob_raw = request.form.get('dob', '').strip()  # expected DD/MM/YYYY
    email = request.form.get('email', '').strip()
    mobile = request.form.get('mobile', '').strip()
    phone = request.form.get('phone', '').strip()
    state = request.form.get('state', '')
    city = request.form.get('city', '')
    hobbies_list = request.form.getlist('hobby')
    hobbies = ','.join(hobbies_list)

    # Server-side safety net (client already validates these)
    if not name or not gender or not dob_raw or not state or (not mobile and not phone):
        return "Missing mandatory fields", 400

    try:
        day, month, year = dob_raw.split('/')
        dob_sql = f"{year}-{month}-{day}"
        datetime.strptime(dob_sql, '%Y-%m-%d')
    except Exception:
        return "Invalid date of birth format", 400

    # Handle photo upload (optional, jpeg/png only)
    photo_filename = None
    photo_file = request.files.get('photo')
    if photo_file and photo_file.filename:
        if allowed_file(photo_file.filename):
            photo_filename = secure_filename(
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_file.filename}"
            )
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        else:
            return "Only JPEG or PNG photos are allowed", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO employees (name, gender, dob, email, mobile, phone, state, city, hobbies, photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            name, gender, dob_sql, email or None, mobile or None, phone or None,
            state, city or None, hobbies or None, photo_filename
        )
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('listing_page'))


# ---------- API: single endpoint drives search + filter + sort + paging ----------

@app.route('/api/records')
def api_records():
    # --- Filters ---
    name_filter = request.args.get('name', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    state_filter = request.args.get('state', '').strip()

    # --- Sorting ---
    sort_by = request.args.get('sort_by', 'reg_no').strip()
    sort_order = request.args.get('sort_order', 'desc').strip().lower()
    if sort_by not in SORTABLE_COLUMNS:
        sort_by = 'reg_no'
    if sort_order not in ('asc', 'desc'):
        sort_order = 'desc'
    sort_column = SORTABLE_COLUMNS[sort_by]

    # --- Paging ---
    try:
        page = max(int(request.args.get('page', 1)), 1)
    except ValueError:
        page = 1
    try:
        page_size = min(max(int(request.args.get('page_size', 10)), 1), 100)
    except ValueError:
        page_size = 10

    where_clause = "WHERE 1=1"
    params = []

    if name_filter:
        where_clause += " AND LOWER(name) LIKE %s"
        params.append(f"%{name_filter.lower()}%")
    if gender_filter:
        where_clause += " AND gender = %s"
        params.append(gender_filter)
    if state_filter:
        where_clause += " AND state = %s"
        params.append(state_filter)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total count (for paging)
    cursor.execute(f"SELECT COUNT(*) AS total FROM employees {where_clause}", tuple(params))
    total = cursor.fetchone()['total']
    total_pages = max((total + page_size - 1) // page_size, 1)
    page = min(page, total_pages)
    offset = (page - 1) * page_size

    query = f"""
        SELECT reg_no, name, email, gender, state, photo
        FROM employees {where_clause}
        ORDER BY {sort_column} {sort_order.upper()}
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, tuple(params) + (page_size, offset))
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        'records': records,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'sort_by': sort_by,
        'sort_order': sort_order
    })


if __name__ == '__main__':
    app.run(debug=True)