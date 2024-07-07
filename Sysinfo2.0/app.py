# import
from datetime import datetime
from flask import Flask, render_template, request, flash, session
from flask_session import Session
from flask_mysqldb import MySQL

# Se inicializa la aplicación Flask
app = Flask(__name__)
app.debug = True  # Para actualizar el navegador
app.secret_key = 'Abbb1234@'

# Configuración de sesión
app.config['SECRET_KEY'] = 'clave12345'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configuración de MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'informatica'
app.config['MYSQL_HOST'] = 'localhost'
mysql = MySQL(app)

# Rutas
@app.route("/")
def main():
    return render_template("index.html")

@app.route("/test_db")
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        if result:
            return "Conexión exitosa a la base de datos"
        else:
            return "No se pudo realizar la consulta"
    except Exception as e:
        return f"Error al conectar a la base de datos: {e}"

def execute_query(sql):
    try:
        cur = mysql.connection.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        return f"Error al ejecutar la consulta: {e}"

def insert_access_record(user_type, user_id):
    try:
        cur = mysql.connection.cursor()
        if user_type == 'alumno':
            sql = "INSERT INTO acceso_registro(ingreso, cod_alum, cod_prof) VALUES (%s, %s, %s)"
            values = (datetime.now(), user_id, 0)
        elif user_type == 'profesor':
            sql = "INSERT INTO acceso_registro(ingreso, cod_alum, cod_prof) VALUES (%s, %s, %s)"
            values = (datetime.now(), 0, user_id)
        cur.execute(sql, values)
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        return f"Error al insertar registro de acceso: {e}"

def count_access_records():
    try:
        cur = mysql.connection.cursor()
        sql = "SELECT COUNT(*) FROM acceso_registro"
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
        return row[0]
    except Exception as e:
        return f"Error al contar registros de acceso: {e}"

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre"]
        password = request.form["password"]
        if nombre.upper() == "ALUMNO":
            sql = "SELECT COUNT(*), id_alumno, nombre FROM Alumno WHERE ci = %s"
            params = (password,)
            row = execute_query(sql, params)
            if row and row[0][0] == 1:
                insert_access_record('alumno', row[0][1])
                session['usuario'] = row[0][2]
                user_session = session.get('usuario', 'Sin Usuario')
                access_count = count_access_records()
                sql = """SELECT DATE_FORMAT(ingreso, '%d/%m/%Y') as fecha,
                                TIME_FORMAT(ingreso, '%H:%i:%s') as hora,
                                nombre 
                         FROM acceso_registro r JOIN Alumno a ON r.cod_alum = a.id_alumno  
                         ORDER by ingreso DESC LIMIT 4"""
                access_logs = execute_query(sql)
                return render_template("home.html", usuario=user_session, cant=access_count, ingresos=access_logs)
            else:
                flash('Contraseña Inválida', 'error')
                return render_template("index.html")
        elif nombre.upper() == "PROFESOR":
            sql = "SELECT COUNT(*), id_profesor, nombre FROM Profesor WHERE ci = %s"
            params = (password,)
            row = execute_query(sql, params)
            if row and row[0][0] == 1:
                insert_access_record('profesor', row[0][1])
                session['usuario'] = row[0][2]
                user_session = session.get('usuario', 'Sin Usuario')
                access_count = count_access_records()
                sql = """SELECT DATE_FORMAT(ingreso, '%d/%m/%Y') as fecha,
                                TIME_FORMAT(ingreso, '%H:%i:%s') as hora,
                                nombre 
                         FROM acceso_registro r JOIN Profesor p ON r.cod_prof = p.id_profesor  
                         ORDER by ingreso DESC LIMIT 4"""
                access_logs = execute_query(sql)
                return render_template("home.html", usuario=user_session, cant=access_count, ingresos=access_logs)
            else:
                flash('Contraseña Inválida', 'error')
                return render_template("index.html")
        else:
            flash('Usuario Inválido', 'error')
            return render_template("index.html")

def execute_query(sql, params=None):
    try:
        cur = mysql.connection.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as e:
        return f"Error al ejecutar la consulta: {e}"


@app.route("/inicio")
def inicio():
    user_session = session.get('usuario', 'Sin Usuario')
    access_count = count_access_records()
    sql = """SELECT DATE_FORMAT(ingreso, '%d/%m/%Y') as fecha,
                    TIME_FORMAT(ingreso, '%H:%i:%s') as hora,
                    nombre 
             FROM acceso_registro r LEFT JOIN Alumno a ON r.cod_alum = a.id_alumno  
             ORDER by ingreso DESC LIMIT 4"""
    access_logs = execute_query(sql)
    return render_template("home.html", usuario=user_session, cant=access_count, ingresos=access_logs)

if __name__ == "__main__":
    app.run()
