import os
import secrets
import time
import sys
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# SECRET_KEY - Required for Flask sessions
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    print("❌ CRITICAL ERROR: SECRET_KEY environment variable is not set!")
    print("   This is required for secure session management.")
    sys.exit(1)

app.secret_key = SECRET_KEY

# MySQL Configuration - ALL from environment variables (NO DEFAULTS)
required_env_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    print("❌ CRITICAL ERROR: Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n   Set these variables before starting the application.")
    sys.exit(1)

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
        print(f"❌ Database connection error: {e}")
        return None

def init_db():
    """Initialize database and create table if not exists"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Connect without database first
            conn = mysql.connector.connect(
                host=MYSQL_CONFIG['host'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password']
            )
            cursor = conn.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")
            
            # Create table
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
            print(f"❌ Database initialization attempt {retry_count}/{max_retries} failed: {e}")
            if retry_count < max_retries:
                print(f"⏳ Retrying in 5 seconds...")
                time.sleep(5)
    
    print("❌ Failed to initialize database after all retries")
    return False

@app.route('/health')
def health():
    """Health check endpoint for Docker and monitoring"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Error as e:
            print(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'database': 'error', 'error': str(e)}, 503
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
        flash(f'Error fetching employees: {str(e)}', 'error')
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
        
        # Validation
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
            flash(f'Error adding employee: {str(e)}', 'error')
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
        
        # GET request - fetch employee data
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
        flash(f'Error deleting employee: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', employees=[]), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return render_template('index.html', employees=[]), 500

if __name__ == '__main__':
    print("🚀 Starting Employee Directory Application...")
    print(f"   MySQL Host: {MYSQL_CONFIG['host']}")
    print(f"   MySQL User: {MYSQL_CONFIG['user']}")
    print(f"   MySQL Database: {MYSQL_CONFIG['database']}")
    print(f"   Environment: Production")
    print("⏳ Initializing database...")
    
    if init_db():
        print("✅ Application ready!")
        print(f"🌐 Server starting on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Failed to initialize database. Exiting...")
        sys.exit(1)
