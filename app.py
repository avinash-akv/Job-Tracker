from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '4b6ee2faa298463a9dff7af629c44ecf'  # Replace with a real secret key

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Avinash@4521',
        database='job_applications_db',
        port = 3306
    )
    return conn

# User class
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Index page
@app.route('/')
def index():
    return render_template('index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            login_user(User(user['id']))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.')

    return render_template('login.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Signup successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Dashboard (Protected)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Add job application (Protected)
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        company_name = request.form['company_name']
        job_role = request.form['job_role']
        job_description = request.form['job_description']
        location = request.form['location']
        credential_id = request.form['credential_id']
        credential_password = request.form['credential_password']
        applied = 'applied' in request.form

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO job_applications (company_name, job_role, job_description, location, credential_id, credential_password, applied, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (company_name, job_role, job_description, location, credential_id, credential_password, applied, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('list_jobs'))
    return render_template('add-job.html')

# List job applications (Protected)
@app.route('/jobs')
@login_required
def list_jobs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM job_applications WHERE user_id = %s', (current_user.id,))
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('list-jobs.html', jobs=jobs)

# Edit job application (Protected)
@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM job_applications WHERE id = %s AND user_id = %s', (job_id, current_user.id))
    job = cursor.fetchone()

    if job is None:
        flash('Job application not found.')
        return redirect(url_for('list_jobs'))

    if request.method == 'POST':
        company_name = request.form['company_name']
        job_role = request.form['job_role']
        job_description = request.form['job_description']
        location = request.form['location']
        credential_id = request.form['credential_id']
        credential_password = request.form['credential_password']
        applied = 'applied' in request.form

        cursor.execute('''
            UPDATE job_applications
            SET company_name = %s, job_role = %s, job_description = %s, location = %s,
                credential_id = %s, credential_password = %s, applied = %s
            WHERE id = %s AND user_id = %s
        ''', (company_name, job_role, job_description, location, credential_id, credential_password, applied, job_id, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Job application updated successfully!')
        return redirect(url_for('list_jobs'))

    cursor.close()
    conn.close()
    return render_template('edit-job.html', job=job)

# Delete job application (Protected)
@app.route('/delete/<int:job_id>')
@login_required
def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM job_applications WHERE id = %s AND user_id = %s', (job_id, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Job application deleted successfully!')
    return redirect(url_for('list_jobs'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
