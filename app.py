import os
import secrets
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

# MySQL Configuration from Environment Variables
MYSQL_CONFIG = {
    'host': os.environ['MYSQL_HOST'],
    'user': os.environ['MYSQL_USER'],
    'password': os.environ['MYSQL_PASSWORD'],
    'database': os.environ['MYSQL_DB']
}

def get_db_connection():
    """Create database connection with error handling"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database and create table if not exists"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = mysql.connector.connect(
                host=MYSQL_CONFIG['host'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hire_date DATE NOT NULL
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Database initialized successfully")
            return True
        except Error as e:
            retry_count += 1
            print(f"❌ Attempt {retry_count}/{max_retries} failed: {e}")
            if retry_count < max_retries:
                print(f"⏳ Retrying in 5 seconds...")
                time.sleep(5)
    
    print("❌ Failed to initialize database")
    return False

@app.route('/health')
def health():
    """Health check endpoint"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return {'status': 'healthy', 'database': 'connected'}, 200
    return {'status': 'unhealthy', 'database': 'disconnected'}, 503

@app.route('/')
def index():
    """Display all employees"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('index.html', employees=[])
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM employees ORDER BY id DESC')
        employees = cursor.fetchall()
        return render_template('index.html', employees=employees)
    except Error as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('index.html', employees=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    """Add new employee"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip()
        hire_date = request.form.get('hire_date', '').strip()
        
        if not all([name, department, email, hire_date]):
            flash('All fields are required', 'error')
            return render_template('add.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('add.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO employees (name, department, email, hire_date) VALUES (%s, %s, %s, %s)',
                (name, department, email, hire_date)
            )
            conn.commit()
            flash('Employee added successfully', 'success')
            return redirect(url_for('index'))
        except mysql.connector.IntegrityError:
            flash('Email already exists', 'error')
            return render_template('add.html')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
            return render_template('add.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add.html')

@app.route('/update/<int:emp_id>', methods=['GET', 'POST'])
def update_employee(emp_id):
    """Update existing employee"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            department = request.form.get('department', '').strip()
            email = request.form.get('email', '').strip()
            hire_date = request.form.get('hire_date', '').strip()
            
            if not all([name, department, email, hire_date]):
                flash('All fields are required', 'error')
                return redirect(url_for('update_employee', emp_id=emp_id))
            
            try:
                cursor.execute(
                    'UPDATE employees SET name=%s, department=%s, email=%s, hire_date=%s WHERE id=%s',
                    (name, department, email, hire_date, emp_id)
                )
                conn.commit()
                flash('Employee updated successfully', 'success')
                return redirect(url_for('index'))
            except mysql.connector.IntegrityError:
                flash('Email already exists', 'error')
                return redirect(url_for('update_employee', emp_id=emp_id))
        
        cursor.execute('SELECT * FROM employees WHERE id = %s', (emp_id,))
        employee = cursor.fetchone()
        
        if not employee:
            flash('Employee not found', 'error')
            return redirect(url_for('index'))
        
        return render_template('update.html', employee=employee)
    
    except Error as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/delete/<int:emp_id>')
def delete_employee(emp_id):
    """Delete employee"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM employees WHERE id = %s', (emp_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash('Employee deleted successfully', 'success')
        else:
            flash('Employee not found', 'error')
    except Error as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', employees=[]), 404

if __name__ == '__main__':
    print("🚀 Starting Employee Directory Application...")
    print("⏳ Initializing database...")
    init_db()
    print("✅ Application ready!")
    app.run(host='0.0.0.0', port=5000, debug=False)
