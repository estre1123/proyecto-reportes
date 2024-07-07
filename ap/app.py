# import
from builtins import print
from datetime import datetime
from flask import Flask, render_template, request, flash, session
from flask_session import Session
from flask_mysqldb import MySQL
from asistencia import asistencia_bp



#### se inicializa la aplicacion con flask###
app = Flask(__name__)
app.debug = True  # actualizar el navegador
app.secret_key = 'Abbb1234@'

# Registrar el blueprint
app.register_blueprint(asistencia_bp)

# session
# Configurar la clave secreta para proteger las sesiones
app.config['SECRET_KEY'] = 'clave12345'
# Configurar el tipo de almacenamiento de sesiones (puedes ajustar según tus necesidades)
app.config['SESSION_TYPE'] = 'filesystem'
# Inicializar la extensión de sesión
Session(app)

###configuracion de mysql###
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'informatica'
app.config['MYSQL_HOST'] = 'localhost'
mysql = MySQL(app)


########rutas##########
# redirecciona al index
@app.route("/")
def main():
    return render_template("index.html")


# verifica el usuario
def contar(sql):
    cur = mysql.connection.cursor()
    print(sql)
    cur.execute(sql)
    fila = cur.fetchall()
    print(fila)
    cur.close()
    return fila





def grabarUsuario(param, cod):
    cur = mysql.connection.cursor()
    if param == 1:
        sql = "INSERT INTO acceso_registro(ingreso, cod_alum, cod_prof) VALUES (%s,%s,%s)"
        values = (datetime.now(), cod, 0)
    else:
        sql = "INSERT INTO acceso_registro(ingreso, cod_alum, cod_prof) VALUES (%s,%s,%s)"
        values = (datetime.now(), 0, cod)

    cur.execute(sql, values)
    mysql.connection.commit()
    cur.close()


def cantReg():
    cant=[]
    cantM = contar("select count(*) from materia")
    cantP = contar("select count(*) from profesor")
    cantS = contar("select count(*) from alumno")
    cantA = contar("select count(*) from asistencia")
    cant.append(cantM[0][0])
    cant.append(cantP[0][0])
    cant.append(cantS[0][0])
    cant.append(cantA[0][0])
    return cant


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['username']
        password = request.form['userpass']
        if nombre.upper() == "ALUMNO":
            sql = "SELECT COUNT(*),cod_alum, nom_alum FROM alumno WHERE ced_alum= " + password + ""
            row = contar(sql)
            if row[0][0] == 1:
                # insertar en la base de datos
                grabarUsuario(1, row[0][1])
                # guardar alumno
                session['usuario'] = row[0][2]
                valor_en_sesion = session.get('usuario', 'Sin Usuario')
                cantidades=cantReg()
                sql = """SELECT concat(day(ingreso),'/',month(ingreso),'/',YEAR(ingreso)) as fecha ,concat(HOUR(ingreso),':',MINUTE(`ingreso`),':',SECOND(`ingreso`)) as hora, nom_alum 
                              FROM acceso_registro r, alumno a 
                              WHERE r.cod_alum = a.cod_alum  
                              ORDER by ingreso DESC LIMIT 4"""
                ingreso=contar(sql)
                return render_template("home.html", usuario=valor_en_sesion, cant=cantidades,ingresos=ingreso)
            else:
                flash('Contraseña Invalida', 'error')
                return render_template("index.html")
        elif nombre.upper() == "PROFESOR":
            sql = "SELECT COUNT(*),cod_prof,nom_prof FROM profesor where ced_prof= " + password + ""
            row = contar(sql)
            if row[0][0] == 1:
                grabarUsuario(2, row[0][1])
                session['usuario'] = row[0][2]
                valor_en_sesion = session.get('usuario', 'Sin Usuario')
                cantidades = cantReg()
                sql = """SELECT concat(day(ingreso),'/',month(ingreso),'/',YEAR(ingreso)) as fecha ,concat(HOUR(ingreso),':',MINUTE(`ingreso`),':',SECOND(`ingreso`)) as hora, nom_alum 
                                        FROM acceso_registro r, alumno a 
                                        WHERE r.cod_alum = a.cod_alum  
                                        ORDER by ingreso DESC LIMIT 4"""
                ingreso = contar(sql)
                return render_template("home.html", usuario=valor_en_sesion,cant=cantidades,ingresos=ingreso)
            else:
                flash('Contraseña Invalida', 'error')
                return render_template("index.html")

        else:
            flash('Usuario Invalido', 'error')
            return render_template("index.html")

@app.route("/inicio")
def inicio():
    valor_en_sesion = session.get('usuario', 'Sin Usuario')
    cantidades = cantReg()
    sql = """SELECT concat(day(ingreso),'/',month(ingreso),'/',YEAR(ingreso)) as fecha ,concat(HOUR(ingreso),':',MINUTE(`ingreso`),':',SECOND(`ingreso`)) as hora, nom_alum 
                                           FROM acceso_registro r, alumno a 
                                           WHERE r.cod_alum = a.cod_alum  
                                           ORDER by ingreso DESC LIMIT 4"""
    ingreso = contar(sql)
    return render_template("home.html", usuario=valor_en_sesion, cant=cantidades, ingresos=ingreso)


if __name__ == "__main__":
    app.run()
