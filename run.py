from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'A@1sdfgHjk2$%3Asdf'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SECRET_KEY'] = 'A@1sdfgHjk2$%3Asdf'

MYSQL_HOST='localhost'
MYSQL_USER='root'
MYSQL_PASSWORD='varshini@2004'
MYSQL_DB='dbms'

connection=mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

# Database configuration
"""db_config = {
    'user': 'root',
    'password': 'varshini@2004',
    'host': 'localhost',
    'port': 33060,
    'database': 'dbms',
}"""

# Function to create a database connection
'''def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error: {e}")
    return connection'''





@app.route('/register_choice')
def register_choice():
    return render_template('register_choice.html')

# Registration Routes
@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        srn = request.form['srn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        cursor = connection.cursor()
        try:
            insert_query = """
            INSERT INTO STUDENT_DETAILS (srn, first_name, last_name, department, email, password)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (srn, first_name, last_name, department, email, password))
            connection.commit()
            flash("Student registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Error as e:
            print(f"Error: {e}")
            flash("An error occurred while registering. Please try again.", "danger")
        finally:
            cursor.close()

    return render_template('register_student.html')



@app.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        faculty_id = request.form['Faculty_ID']  # Capture Faculty_ID
        faculty_name = request.form['Faculty_Name']
        department = request.form['Department']
        expertise = request.form['Expertise']
        email = request.form['Email']
        password = generate_password_hash(request.form['Password'], method='pbkdf2:sha256')

        cursor = connection.cursor()
        try:
            # SQL query to insert new teacher record with Faculty_ID
            insert_query = """
            INSERT INTO FACULTY_DETAILS (Faculty_ID, Faculty_Name, Department, Expertise, Email, Password)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (faculty_id, faculty_name, department, expertise, email, password))
            connection.commit()
            flash("Teacher registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Error as e:
            print(f"Error: {e}")
            flash("An error occurred while registering. Please try again.", "danger")
        finally:
            cursor.close()

    return render_template('register_teacher.html')




@app.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        cursor = connection.cursor()
        try:
            # Insert new admin details into ADMIN_DETAILS
            insert_query = "INSERT INTO ADMIN_DETAILS (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (name, email, password))
            connection.commit()
            flash("Admin registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Error as e:
            print(f"Error: {e}")
            flash("An error occurred during registration. Please try again.", "danger")
        finally:
            cursor.close()  # Ensure cursor is closed

    return render_template('register_admin.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        
        # Connect to the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Set the query and password index based on the role
            if role == 'student':
                query = "SELECT * FROM STUDENT_DETAILS WHERE email = %s"
                password_index = 6
            elif role == 'teacher':
                query = "SELECT * FROM FACULTY_DETAILS WHERE email = %s"
                password_index = 5
            elif role == 'admin':
                query = "SELECT * FROM ADMIN_DETAILS WHERE email = %s"
                password_index = 3
            else:
                flash("Invalid role selected.", "danger")
                return redirect(url_for('login'))

            # Execute query to fetch user details
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if user:
                # Verify the password using the role-specific password index
                if check_password_hash(user[password_index], password):
                    session['user_role'] = role
                    session['user_id'] = user[0]  # Assuming user[0] is the unique user identifier (e.g., SRN)
                    
                    # Redirect based on user role
                    if role == 'student':
                        return redirect(url_for('student_dashboard'))
                    elif role == 'teacher':
                        return redirect(url_for('teacher_dashboard'))
                    elif role == 'admin':
                        return redirect(url_for('admin_dashboard'))
                else:
                    flash("Invalid password. Please try again.", "danger")
            else:
                flash("No user found with that email. Please check your credentials.", "danger")
                
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            flash("An error occurred while accessing the database. Please try again.", "danger")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('login.html')



def execute_query(query, params=()):
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        
        # Commit only if the query modifies data
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            connection.commit()

        # Fetch results only if it's a SELECT query
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            result = None  # No result to fetch for non-SELECT queries

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        connection.rollback()  # Rollback in case of error
        raise e  # Re-raise exception to handle it outside if needed

    finally:
        cursor.close()
        connection.close()

    return result


# Function to fetch a single record
def fetch_one(query, params=()):
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def execute_update(query, params=()):
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()  # Clear the session data
        flash("You have been logged out.", "info")
        return redirect(url_for('index'))  # Redirect to the home page (or another page after logout)
    return redirect(url_for('index'))  # Redirect to home if the method is GET



import secrets
from datetime import datetime, timedelta

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        
        # Determine which table to query based on role
        if role == 'student':
            table = 'STUDENT_DETAILS'
        elif role == 'teacher':
            table = 'FACULTY_DETAILS'
        elif role == 'admin':
            table = 'ADMIN_DETAILS'
        else:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('forgot_password'))
        
        # Check if the email exists in the selected table
        query = f"SELECT * FROM {table} WHERE email = %s"
        user = fetch_one(query, (email,))
        
        if user:
            # Generate a token for password reset
            token = secrets.token_urlsafe(32)
            
            # Set expiration time (1 hour from now)
            expiry = datetime.now() + timedelta(hours=1)
            expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                # Store token in password_reset_tokens table
                insert_query = """
                INSERT INTO PASSWORD_RESET_TOKENS (email, role, token, expires_at)
                VALUES (%s, %s, %s, %s)
                """
                execute_query(insert_query, (email, role, token, expiry_str))
                
                # Redirect directly to reset password page with the token
                return redirect(url_for('reset_password', token=token))
                
            except Exception as e:
                print(f"Error generating reset token: {e}")
                flash("An error occurred while processing your request.", "danger")
        else:
            flash("No account found with that email address.", "danger")
        
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify the token
    query = "SELECT * FROM PASSWORD_RESET_TOKENS WHERE token = %s AND expires_at > NOW()"
    token_data = fetch_one(query, (token,))
    
    if not token_data:
        flash("Invalid or expired password reset link.", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('reset_password.html', token=token)
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        # Determine which table to update based on role
        role = token_data['role']
        email = token_data['email']
        
        if role == 'student':
            table = 'STUDENT_DETAILS'
            password_column = 'password'
        elif role == 'teacher':
            table = 'FACULTY_DETAILS'
            password_column = 'Password'
        elif role == 'admin':
            table = 'ADMIN_DETAILS'
            password_column = 'password'
        
        # Update the password
        update_query = f"UPDATE {table} SET {password_column} = %s WHERE email = %s"
        try:
            execute_update(update_query, (hashed_password, email))
            
            # Delete the used token
            delete_query = "DELETE FROM PASSWORD_RESET_TOKENS WHERE token = %s"
            execute_query(delete_query, (token,))
            
            flash("Your password has been successfully reset. Please log in with your new password.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error resetting password: {e}")
            flash("An error occurred while resetting your password.", "danger")
    
    return render_template('reset_password.html', token=token)











# Run the App
if __name__ == '__main__':
    app.run(debug=True)
