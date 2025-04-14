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



# Routes
@app.route('/')
def index():
    return render_template('index.html')

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


@app.route('/dashboard/student')
def student_dashboard():
    if 'user_role' in session and session['user_role'] == 'student':
        student_id = session['user_id']  # This should be the SRN from the session

        try:
            # Fetch student details based on the SRN (student_id)
            student_query = "SELECT * FROM STUDENT WHERE SRN = %s"
            student = fetch_one(student_query, (student_id,))

            exam_schedule_query = """
                    SELECT Exam_ID, Exam_Type, Timings, Venue, Semester,Exam_Date
                    FROM EXAM_DETAILS
                """
            exam_schedule = execute_query(exam_schedule_query)

            if student:
                
                # Fetch team details based on Team_ID
                team_query = "SELECT * FROM TEAM WHERE Team_ID = %s"
                team = fetch_one(team_query, (student['Team_ID'],))

                if team:
                    # Fetch all team members with the same Team_ID
                    team_members_query = "SELECT * FROM STUDENT WHERE Team_ID = %s"
                    team_members = execute_query(team_members_query, (student['Team_ID'],))

                    # Fetch project details using the Project_ID from the TEAM table
                    project_query = "SELECT * FROM PROJECT WHERE Project_ID = %s"
                    project = fetch_one(project_query, (team['Project_ID'],))

                    # Fetch guide details using Guide_ID from the TEAM table
                    guide_query = "SELECT * FROM GUIDE WHERE Guide_ID = %s"
                    guide = fetch_one(guide_query, (team['Guide_ID'],))

                    # Fetch exams with details including calculated total and grade
                    exams_query = """
                    SELECT EXAM.Exam_ID,  
                    EXAM.ISA1, 
                    EXAM.ISA2, 
                    EXAM.ESA,
                    (EXAM.ISA1 + EXAM.ISA2 + EXAM.ESA) AS total,
                    CASE
                        WHEN (EXAM.ISA1 + EXAM.ISA2 + EXAM.ESA) > 90 THEN 'S'
                        WHEN (EXAM.ISA1 + EXAM.ISA2 + EXAM.ESA) BETWEEN 81 AND 90 THEN 'A'
                        WHEN (EXAM.ISA1 + EXAM.ISA2 + EXAM.ESA) BETWEEN 71 AND 80 THEN 'B'
                        WHEN (EXAM.ISA1 + EXAM.ISA2 + EXAM.ESA) BETWEEN 61 AND 70 THEN 'C'
                        WHEN (EXAM.ISA1 + EXAM.ISA2 + EXAM.ESA) BETWEEN 51 AND 60 THEN 'D'
                        ELSE 'F'
                    END AS grade,
                    EXAMGRADE.Marks,
                    EXAMDETAILS.Exam_Type,
                    EXAMDETAILS.Exam_Date, 
                    EXAMDETAILS.Timings, 
                    EXAMDETAILS.Venue, 
                    EXAMDETAILS.Semester
                    FROM EXAM
                    JOIN EXAMGRADE ON EXAM.Exam_ID = EXAMGRADE.Exam_ID
                    JOIN EXAM_DETAILS AS EXAMDETAILS ON EXAM.Exam_ID = EXAMDETAILS.Exam_ID
                    WHERE EXAMGRADE.SRN = %s
                    """
                    exams = execute_query(exams_query, (student_id,))


                    total_marks_query = """
                    SELECT 
                        EXAMGRADE.SRN, 
                        SUM(EXAMGRADE.Marks) AS total_marks
                    FROM EXAMGRADE
                    JOIN EXAM ON EXAMGRADE.Exam_ID = EXAM.Exam_ID
                    WHERE EXAMGRADE.SRN = %s
                    GROUP BY EXAMGRADE.SRN
                    """
                    total_marks = execute_query(total_marks_query, (student_id,))

                    # Fetch other dashboard information such as documents and appointments
                    documents_query = "SELECT * FROM DOCUMENT WHERE Project_ID = %s"
                    documents = execute_query(documents_query, (project['Project_ID'],))

                    appointments_query = "SELECT * FROM APPOINTMENT WHERE Team_ID = %s"
                    appointments = execute_query(appointments_query, (team['Team_ID'],))

                    # Render the dashboard with all the fetched data
                    return render_template('student_dashboard.html',
                                        student=student,
                                        exam_schedule=exam_schedule,
                                        team=team,
                                        guide=guide,
                                        team_members=team_members,
                                        project=project,
                                        exams=exams,
                                        total_marks=total_marks,
                                        documents=documents,
                                        appointments=appointments)
                else:
                    flash("Team details not found.", "danger")
                    return redirect(url_for('login'))
            else:
                flash("Student details not found.", "danger")
                return redirect(url_for('login'))
        except Error as e:
            print(f"Database error: {e}")
            flash("An error occurred while accessing the database. Please try again.", "danger")
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


# Assuming you already have a function to execute queries like fetch_one or execute_query
def get_exams_by_student(student_id):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()

        exams_query = "SELECT GetExamsByStudent(%s) AS exams"
        cursor.execute(exams_query, (student_id,))
        exams_result = cursor.fetchone()
        exams = exams_result['exams'] if exams_result else "[]"

        # Parse exams JSON if needed or pass it directly to the template
        return render_template(
                'student_dashboard.html',
                exams=exams,
                student_id=student_id
            )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()


@app.route('/exam_schedule', methods=['GET'])
def exam_schedule():
    try:
        # Query to fetch all exam details
        exam_schedule_query = """
            SELECT Exam_ID, Exam_Type, Timings, Venue, Semester,Exam_Date
            FROM EXAM_DETAILS
        """
        exam_schedule = execute_query(exam_schedule_query)
        
        return render_template('exam_schedule.html', exam_schedule=exam_schedule)

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash("An error occurred while accessing the exam schedule. Please try again.", "danger")
        return redirect(url_for('login'))



@app.route('/update_progress', methods=['POST'])
def update_progress():
    try:
        # Retrieve the Project_ID and new progress from the form
        project_id = request.form['project_id']
        new_progress = int(request.form['progress'])

        # Update the progress in the PROJECT table
        update_query = "UPDATE PROJECT SET Progress = %s WHERE Project_ID = %s"
        execute_query(update_query, (new_progress, project_id))

        flash("Project progress updated successfully.", "success")
        return redirect(url_for('student_dashboard'))
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash("Could not update project progress.", "danger")
        return redirect(url_for('student_dashboard'))


@app.route('/schedule_appointment', methods=['GET', 'POST'])
def schedule_appointment():
    if request.method == 'POST':
        # Get form data
        appointment_date = request.form['date']
        description = request.form['description']

        # Get the student's SRN from the session
        student_id = session['user_id']

        # Query to fetch Team_ID and Guide_ID for the student
        query = """
            SELECT TEAM.Team_ID, TEAM.Guide_ID 
            FROM TEAM 
            JOIN STUDENT ON TEAM.Team_ID = STUDENT.Team_ID 
            WHERE STUDENT.SRN = %s
        """
        team_guide_data = execute_query(query, (student_id,))
        
        # Check if the team and guide data was found
        if team_guide_data:
            team_id = team_guide_data[0]['Team_ID']
            guide_id = team_guide_data[0]['Guide_ID']
        else:
            flash("Team or Guide information not found.", "danger")
            return redirect(url_for('student_dashboard'))

        # Convert the appointment date to a datetime object
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()

        # Prepare the SQL query to insert the new appointment
        insert_query = """
            INSERT INTO APPOINTMENT (Appointment_Date, Statuss, Descript, Team_ID, Guide_ID)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (appointment_date, "Pending", description, team_id, guide_id)

        try:
            # Execute the query to insert the new appointment
            execute_update(insert_query, params)

            flash("Appointment scheduled successfully!", "success")
            return redirect(url_for('student_dashboard'))
        except Error as e:
            flash(f"An error occurred while scheduling the appointment: {e}", "danger")

    # If GET request, render the appointment form
    return render_template('student_dashboard.html')




ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'txt'}

# Function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload folder path (ensure this is correctly set in your app config)
UPLOAD_FOLDER = 'D:/new folder/Capstone/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload_document', methods=['POST'])
def upload_document():
    # Check if a file is part of the request
    if 'document' not in request.files:
        flash('No file part in the request.', 'danger')
        return redirect(request.url)
    
    file = request.files['document']
    
    # If no file is selected
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(request.url)

    # Check if the file has an allowed extension
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Ensure the upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Construct file path and save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
        except Exception as e:
            flash(f'Error saving file: {e}', 'danger')
            return redirect(request.url)

        # Get additional form data
        upload_date_str = request.form.get('Upload_Date')
        version = request.form['Versionn']
        project_id = session.get('Project_ID')  # Assuming project_id is stored in the session

        # Convert upload_date to a datetime object
        try:
            upload_date = datetime.strptime(upload_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(request.url)

        # Insert document details into the database using execute_update
        try:
            insert_query = """
            INSERT INTO DOCUMENT (Filepath, Versionn, Upload_Date, Project_ID)
            VALUES (%s, %s, %s, %s)
            """
            params = (filepath, version, upload_date, project_id)
            execute_update(insert_query, params)  # Using execute_update function here
            flash('File uploaded and document details saved successfully.', 'success')

        except Exception as e:
            flash(f'Error saving document details: {e}', 'danger')
            return redirect(request.url)

        return redirect(url_for('student_dashboard'))

    flash('Invalid file type. Allowed file types are: pdf, doc, docx, jpg, png, txt.', 'danger')
    return redirect(request.url)





@app.route('/dashboard/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if 'user_role' in session and session['user_role'] == 'teacher':
        teacher_id = session['user_id']

        try:
            # Fetch teacher details from GUIDE table
            teacher_query = "SELECT * FROM GUIDE WHERE Faculty_ID = %s"
            teacher = fetch_one(teacher_query, (teacher_id,))

            if teacher:
                # Update EXAM table if form submission is detected
                if request.method == 'POST':
                    exam_id = request.form.get('exam_id')
                    srn = request.form.get('srn')
                    isa1 = request.form.get('isa1')
                    isa2 = request.form.get('isa2')
                    esa = request.form.get('esa')
                    feedback = request.form.get('feedback')

                    # Update query for EXAM table
                    update_query = """
                        UPDATE EXAM
                        SET ISA1 = %s, ISA2 = %s, ESA = %s, Feedback = %s
                        WHERE Exam_ID = %s AND SRN = %s;
                    """
                    execute_query(update_query, (isa1, isa2, esa, feedback, exam_id, srn))
                    flash('Marks updated successfully!', 'success')

                # Fetch teams under the teacher based on Team_ID in GUIDE table
                team_query = """
                    SELECT TEAM.Team_ID, TEAM.Team_Name, PROJECT.Project_Name, PROJECT.Project_ID 
                    FROM TEAM 
                    JOIN PROJECT ON TEAM.Project_ID = PROJECT.Project_ID 
                    WHERE TEAM.Guide_ID = %s
                """
                teams = execute_query(team_query, (teacher['Guide_ID'],))

                panel_query = """
                    SELECT 
                    PANEL.Panel_ID, 
                    PANEL.Project_ID, 
                    PANEL.Feedback, 
                    EXAMGRADE.Grade_ID, 
                    (SELECT Faculty_Name 
                    FROM FACULTY 
                    WHERE Faculty_ID = PANEL.Faculty_ID) AS Teacher1_Name,
                    (SELECT Faculty_Name 
                    FROM FACULTY 
                    WHERE Faculty_ID = PANEL.Faculty_ID1) AS Teacher2_Name,
                    (SELECT Faculty_Name 
                    FROM FACULTY 
                    WHERE Faculty_ID = PANEL.Faculty_ID2) AS Teacher3_Name
                FROM PANEL
                JOIN EXAMGRADE ON PANEL.Grade_ID = EXAMGRADE.Grade_ID
                JOIN PROJECT ON PANEL.Project_ID = PROJECT.Project_ID
                JOIN TEAM ON PROJECT.Project_ID = TEAM.Project_ID
                WHERE PANEL.Faculty_ID = %s OR PANEL.Faculty_ID1 = %s OR PANEL.Faculty_ID2 = %s

                """
                panels = execute_query(panel_query, (teacher_id, teacher_id, teacher_id))
                print(f"Panels: {panels}")  # Debug print


                # Fetch exam details for displaying in table
                exam_query = """
                    SELECT 
                        EXAM.Exam_ID, EXAM.SRN, EXAM.ISA1, EXAM.ISA2, EXAM.ESA, 
                        PROJECT.Project_ID, PANEL.Panel_ID, PANEL.Feedback
                    FROM 
                        EXAM
                    JOIN 
                        PROJECT ON PROJECT.Guide_ID = %s
                    JOIN 
                        PANEL ON PANEL.Project_ID = PROJECT.Project_ID
                    WHERE 
                        PANEL.Faculty_ID = %s
                """
                exams = execute_query(exam_query, (teacher_id, teacher_id))

                # Prepare team details for each team
                team_details = []
                for team in teams:
                    team_members_query = "SELECT * FROM STUDENT WHERE Team_ID = %s"
                    team_members = execute_query(team_members_query, (team['Team_ID'],))

                    project_query = "SELECT Progress FROM PROJECT WHERE Project_ID = %s"
                    project = fetch_one(project_query, (team['Project_ID'],))

                    documents_query = "SELECT Filepath, Versionn FROM DOCUMENT WHERE Project_ID = %s"
                    documents = execute_query(documents_query, (team['Project_ID'],))

                    appointments_query = """
                        SELECT APPOINTMENT.Appointment_ID, APPOINTMENT.Appointment_Date, APPOINTMENT.Statuss, APPOINTMENT.Descript, TEAM.Team_Name 
                        FROM APPOINTMENT 
                        JOIN TEAM ON APPOINTMENT.Team_ID = TEAM.Team_ID 
                        WHERE APPOINTMENT.Team_ID = %s
                    """
                    appointments = execute_query(appointments_query, (team['Team_ID'],))

                    insert_exam_query = """
                        INSERT INTO EXAM (Exam_ID, Team_ID, SRN, ISA1, ISA2, ESA)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """


                    team_details.append({
                        'team': team,
                        'members': team_members,
                        'project_progress': project['Progress'],
                        'documents': documents,
                        'appointments': appointments
                    })

                return render_template(
                    'teacher_dashboard.html',
                    teacher=teacher,
                    team_details=team_details,
                    panels=panels,
                    exams=exams
                )
            else:
                flash("Teacher details not found.", "danger")
                return redirect(url_for('login'))
        
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            flash("An error occurred while accessing the database. Please try again.", "danger")
            return redirect(url_for('login'))
    
    else:
        return redirect(url_for('login'))



@app.route('/update_appointment_status', methods=['POST'])
def update_appointment_status():
    if 'user_role' in session and session['user_role'] == 'teacher':
        appointment_id = request.form.get('appointment_id')
        status = request.form.get('status')

        try:
            # Update the status of the appointment
            update_query = "UPDATE APPOINTMENT SET Statuss = %s WHERE Appointment_ID = %s"
            execute_query(update_query, (status, appointment_id))

            flash("Appointment status updated successfully!", "success")
        
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            flash("An error occurred while updating the appointment. Please try again.", "danger")

        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('login'))


@app.route('/update_marks_feedback', methods=['POST'])
def update_marks_feedback():
    try:
        # Fetching form data directly from the form
        exam_id = request.form['exam_id']
        team_id = request.form['team_id']  # Get Team ID directly from form
        srn = request.form['srn']  # SRN directly from form
        isa1 = float(request.form.get('isa1', 0))
        isa2 = float(request.form.get('isa2', 0))
        esa = float(request.form.get('esa', 0))

        print(f"Exam ID: {exam_id}, Team ID: {team_id}, SRN: {srn}, ISA1: {isa1}, ISA2: {isa2}, ESA: {esa}")

        # Step 1: Insert a new record into EXAM table
        insert_exam_query = """
            INSERT INTO EXAM (Exam_ID, Team_ID, SRN, ISA1, ISA2, ESA)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        print("Executing EXAM query:", insert_exam_query)
        print("With values:", (exam_id, team_id, srn, isa1, isa2, esa))
        
        # Execute the query with the provided values
        execute_query(insert_exam_query, (exam_id, team_id, srn, isa1, isa2, esa))

        flash("Exam marks inserted successfully.", "success")
        return redirect(url_for('teacher_dashboard'))

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for('teacher_dashboard'))
    except Exception as e:
        print(f"Error: {e}")
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('teacher_dashboard'))


# Admin dashboard to view and update GUIDE, STUDENT, TEAM tables
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_role' in session and session['user_role'] == 'admin':
        admin_id = session['user_id']  # Assuming admin's ID is stored in session
        try:
            connection = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB
            )
            cursor = connection.cursor(dictionary=True)
            
            # Fetch admin details
            cursor.execute("SELECT * FROM ADMIN_DETAILS WHERE id = %s", (admin_id,))
            admin = cursor.fetchone()  # Fetch one record for admin details
            
            # Fetch data from GUIDE, STUDENT, TEAM tables
            cursor.execute("SELECT * FROM GUIDE")
            guides = cursor.fetchall()
            
            cursor.execute("SELECT * FROM STUDENT")
            students = cursor.fetchall()
            
            cursor.execute("SELECT * FROM TEAM")
            teams = cursor.fetchall()

            # Ensure that admin details, guides, students, and teams are passed to the template
            return render_template('admin_dashboard.html', admin=admin, guides=guides, students=students, teams=teams)
        
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            flash("An error occurred while accessing the database.", "danger")
            return redirect(url_for('login'))
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return redirect(url_for('login'))



@app.route('/update_guide', methods=['POST'])
def update_guide():
    # Get form data for the guide
    guide_id = request.form.get('Guide_ID')
    first_name = request.form.get('First_Name')
    last_name = request.form.get('Last_Name')
    department = request.form.get('Department')
    email = request.form.get('Email')
    faculty_id = request.form.get('Faculty_ID')
    team_id = request.form.get('Team_ID')

    # Print out data to debug
    print(guide_id, first_name, last_name, department, email, faculty_id, team_id)

    # Ensure Guide_ID is provided for updating or adding a new guide
    if guide_id:
        # Check if the Guide_ID exists in the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM GUIDE WHERE Guide_ID = %s"
        cursor.execute(check_query, (guide_id,))
        count = cursor.fetchone()[0]
        
        # If the guide exists, update the existing record
        if count > 0:
            # Update existing guide
            query = """UPDATE GUIDE SET First_Name = %s, Last_Name = %s, Department = %s, Email = %s, Faculty_ID = %s, Team_ID = %s 
                    WHERE Guide_ID = %s"""
            data = (first_name, last_name, department, email, faculty_id, team_id, guide_id)
            execute_query(query, data)
            flash("Guide information updated successfully.", "success")
        else:
            # If Guide_ID does not exist, insert a new guide
            query = """INSERT INTO GUIDE (Guide_ID, First_Name, Last_Name, Department, Email, Faculty_ID, Team_ID) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            data = (guide_id, first_name, last_name, department, email, faculty_id, team_id)
            execute_query(query, data)
            flash("New guide added successfully.", "success")
    else:
        flash("Guide ID is required to update or add guide.", "danger")

    return redirect(url_for('admin_dashboard'))



@app.route('/update_student', methods=['POST'])
def update_student():
    # Get form data for the student
    srn = request.form.get('SRN')
    first_name = request.form.get('First_Name')
    last_name = request.form.get('Last_Name')
    department = request.form.get('Department')
    email = request.form.get('Email')
    team_id = request.form.get('Team_ID')

    # Print out data to debug
    print(srn, first_name, last_name, department, email, team_id)

    # Ensure SRN is provided for updating or adding new student
    if srn:
        # If Team_ID is empty or not provided, set it to None (NULL) in the database
        if not team_id:
            team_id = None
        
        # Check if the SRN exists in the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM STUDENT WHERE SRN = %s"
        cursor.execute(check_query, (srn,))
        count = cursor.fetchone()[0]
        
        # If the student exists, update the existing record
        if count > 0:
            # Update existing student
            query = """UPDATE STUDENT SET First_Name = %s, Last_Name = %s, Department = %s, Email = %s, Team_ID = %s 
                    WHERE SRN = %s"""
            data = (first_name, last_name, department, email, team_id, srn)
            execute_query(query, data)
            flash("Student information updated successfully.", "success")
        else:
            # If SRN does not exist, insert a new student
            query = """INSERT INTO STUDENT (SRN, First_Name, Last_Name, Department, Email, Team_ID) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            data = (srn, first_name, last_name, department, email, team_id)
            execute_query(query, data)
            flash("New student added successfully.", "success")
    else:
        flash("SRN is required to update or add student.", "danger")

    return redirect(url_for('admin_dashboard'))




@app.route('/update_team', methods=['POST'])
def update_team():
    # Get form data for the team
    team_id = request.form.get('Team_ID')
    team_name = request.form.get('Team_Name')
    project_id = request.form.get('Project_ID')
    guide_id = request.form.get('Guide_ID')

    # Print out data to debug
    print(team_id, team_name, project_id, guide_id)

    # Ensure Team_ID is provided for updating or adding a new team
    if team_id:
        # Check if the Team_ID exists in the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM TEAM WHERE Team_ID = %s"
        cursor.execute(check_query, (team_id,))
        count = cursor.fetchone()[0]
        
        # If the team exists, update the existing record
        if count > 0:
            # Update existing team
            query = """UPDATE TEAM SET Team_Name = %s, Project_ID = %s, Guide_ID = %s 
                    WHERE Team_ID = %s"""
            data = (team_name, project_id, guide_id, team_id)
            execute_query(query, data)
            flash("Team information updated successfully.", "success")
        else:
            # If Team_ID does not exist, insert a new team
            query = """INSERT INTO TEAM (Team_ID, Team_Name, Project_ID, Guide_ID) 
                    VALUES (%s, %s, %s, %s)"""
            data = (team_id, team_name, project_id, guide_id)
            execute_query(query, data)
            flash("New team added successfully.", "success")
    else:
        flash("Team ID is required to update or add team.", "danger")

    return redirect(url_for('admin_dashboard'))


@app.route('/delete_student/<srn>', methods=['POST'])
def delete_student(srn):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()

        delete_query = "DELETE FROM STUDENT WHERE SRN = %s"
        cursor.execute(delete_query, (srn,))
        connection.commit()

        return jsonify({"success": True})
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"success": False, "error": str(err)})
    finally:
        cursor.close()
        connection.close()




@app.route('/delete_guide/<guide_id>', methods=['POST'])
def delete_guide(guide_id):
    try:
        # Establishing a connection to the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()

        # SQL query to delete the guide by Guide_ID
        delete_query = "DELETE FROM GUIDE WHERE Guide_ID = %s"
        cursor.execute(delete_query, (guide_id,))
        connection.commit()

        # Successful deletion response
        return jsonify({"success": True})

    except mysql.connector.Error as err:
        # Error handling and response
        print(f"Error: {err}")
        return jsonify({"success": False, "error": str(err)})

    finally:
        # Closing the cursor and connection
        cursor.close()
        connection.close()


@app.route('/delete_team/<team_id>', methods=['POST'])
def delete_team(team_id):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()

        delete_query = "DELETE FROM TEAM WHERE Team_ID = %s"
        cursor.execute(delete_query, (team_id,))
        connection.commit()

        return jsonify({"success": True})

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"success": False, "error": str(err)})
    finally:
        cursor.close()
        connection.close()






@app.route('/schedule_exam', methods=['POST'])
def schedule_exam():
    if 'user_role' in session and session['user_role'] == 'admin':
        try:
            # Retrieve form data
            exam_id = request.form['exam_id']
            exam_date = request.form['exam_date']
            exam_type = request.form['exam_type']
            timings = request.form['timings']
            venue = request.form['venue']
            semester = request.form['semester']
            
            
            # Insert data into EXAM_DETAILS table, now including Exam_Date
            insert_exam_details_query = """
                INSERT INTO EXAM_DETAILS (Exam_ID, Exam_Date, Exam_Type, Timings, Venue, Semester)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_query(insert_exam_details_query, (exam_id, exam_date, exam_type, timings, venue, semester))
            
            flash("Exam scheduled successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))



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
