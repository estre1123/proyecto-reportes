from flask import Blueprint, render_template, session, request, url_for, redirect, jsonify, flash, send_file
from flask_mysqldb import MySQL
from reportlab.pdfgen import canvas
from datetime import datetime

# Crear el blueprint
asistencia_bp = Blueprint('asistencia', __name__)
mysql = MySQL()


def cargarMaterias():
    sql = "SELECT nom_mat FROM  materia ORDER BY nom_mat ASC"
    cur = mysql.connection.cursor()
    cur.execute(sql)
    fila = cur.fetchall()
    print(fila)
    cur.close()
    return fila


@asistencia_bp.route('/asistencia')
def asistencia():
    usuariosession = session.get('usuario')
    materia = cargarMaterias()
    return render_template('asistencia.html', usuario=usuariosession, materias=materia)


def cargarRegistros(sql):
    cur = mysql.connection.cursor()
    cur.execute(sql)
    fila = cur.fetchall()
    cur.close()
    return fila


@asistencia_bp.route('/lista', methods=['GET', 'POST'])
def lista():
    if request.method == 'POST':
        curso = request.form['curso']
        turno = request.form['turno']
        fecha = request.form['fecha']
        materia = request.form['materia']
        horario = request.form['horamateria']
        session['date'] = fecha
        session['mate'] = materia
        session['horamat'] = horario
    usuariosession = session.get('usuario')
    sql = "SELECT * FROM alumno WHERE curso_alum='" + curso + "' and turno_alum='" + turno + "' and estado_alum='A'"
    print(sql)
    alumnos = cargarRegistros(sql)
    sql2 = "SELECT idrasgos FROM rasgos"
    rasgo = cargarRegistros(sql2)
    print(alumnos)
    return render_template('asistencia.html', usuario=usuariosession, alum=alumnos, rasgos=rasgo)


@asistencia_bp.route('/get_horario/<materia>')
def get_horario(materia):
    sql = ("SELECT DISTINCT concat(hor_inicio,' - ',hor_final) FROM horario h,materia m WHERE h.cod_mat=m.cod_mat and "
           "nom_mat='" + materia + "'")
    horario = cargarRegistros(sql)
    print(horario)
    horario_list = [resultado[0] for resultado in horario]
    # Devuelve la respuesta JSON
    return jsonify({'horario': horario_list})


def buscar(sql):
    cur = mysql.connection.cursor()
    cur.execute(sql)
    cod = cur.fetchall()
    print(cod)
    cur.close()
    return cod


def insertar(sql, values):
    cur = mysql.connection.cursor()
    cur.execute(sql, values)
    mysql.connection.commit()
    cur.close()


@asistencia_bp.route('/grabarAsis', methods=['POST'])
def grabarAsis():
    if request.method == 'POST':
        fecha = session.get('date')
        disciplina = session.get('mate')
        horamateria = session.get('horamat')
        estados = request.form.getlist('asis[]')
        rasgos_seleccionados = request.form.getlist('rasgos[]')
        sql = "Select cod_mat from materia where nom_mat='" + disciplina + "'"
        codmat = buscar(sql)
        # insertar asistencia
        insertasis = "INSERT INTO asistencia(cod_mat, fecha_asis,horario_asis) VALUES (%s,%s,%s)"
        values = (codmat, fecha, horamateria)
        insertar(insertasis, values)
        # insertar detalle
        sql2 = "SELECT max(cod_asis) FROM asistencia"
        codasis = buscar(sql2)
        for seleccion in estados:
            alumno, asistencia = seleccion.split('-')
            insertdet = "INSERT INTO det_asist (cod_asis, asis_asis, cod_alum) VALUES (%s,%s,%s)"
            values = (codasis, asistencia, alumno)
            insertar(insertdet, values)
            # busqueda de los rasgos segun el ide
            for rasgos in rasgos_seleccionados:
                alum, rasgo = rasgos.split(' ')
                if alumno == alum:
                    insertrasgo = "INSERT INTO rasgosalumno(idrasgos, cod_alum, fecha, cod_mat,horario_rasgo) VALUES (%s,%s,%s,%s,%s)"
                    values = (rasgo, alum, fecha, codmat, horamateria)
                    print(insertrasgo, values)
                    insertar(insertrasgo, values)
        return redirect(url_for('asistencia.asistencia'))


@asistencia_bp.route('/reporte')
def reporte():
    return render_template("reportes.html")


@asistencia_bp.route('/cargareporte', methods=['GET', 'POST'])
def cargareporte():
    if request.method == 'POST':
        curso = request.form['curso']
        turno = request.form['turno']
        fechadesde = request.form['fechadesde']
        fechahasta = request.form['fechahasta']
        session['fd'] = fechadesde
        session['fh'] = fechahasta
        print(curso, turno, fechadesde, fechahasta)
        if fechadesde > fechahasta:
            flash('La Fecha Desde debe ser menor a Fecha Hasta', 'error')
            return render_template("reportes.html")
        else:
            sql = "SELECT * FROM informatica.vista_asistencia where curso_alum='" + curso + "' and turno_alum='" + turno + "' and fecha_asis BETWEEN '" + fechadesde + "' AND '" + fechahasta + "';"
            ausencia = cargarRegistros(sql)
            sql2 = "SELECT * FROM informatica.vista_rasgos where curso_alum='" + curso + "' and turno_alum='" + turno + "' and fecha BETWEEN '" + fechadesde + "' AND '" + fechahasta + "';"
            print(sql)
            rasgo = cargarRegistros(sql2)
               # Crear una nueva tupla con solo las columnas deseadas
            nueva_tupla = [(registro[2], registro[6], registro[7], registro[8]) for registro in rasgo]
            rasgo_sin_duplicados = set(nueva_tupla)
            return render_template("reportes.html", ausencias=ausencia, rasgos=rasgo_sin_duplicados)

@asistencia_bp.route("/generarpdf" ,methods=['POST'])
def generar_pdf():
    nombre = request.form.get('nom')
    fdesde=session.get('fd')
    fhasta=session.get('fh')
    sql = "SELECT * FROM vista_asistencia where nom_alum='"+nombre+"' and fecha_asis BETWEEN '"+fdesde+"' AND '"+fhasta+"'"
    datosasistencia = cargarRegistros(sql)
    sql1 = "SELECT * FROM vista_rasgos where nom_alum='" + nombre + "' and fecha BETWEEN '" + fdesde + "' AND '" + fhasta + "'"
    datosrasgos = cargarRegistros(sql1)
    # Lógica para generar el PDF con ReportLab
    pdf_filename = nombre+'.pdf'
    pdf = canvas.Canvas(pdf_filename)

    # Cabecera
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(200, 800, 'Reporte Asistencias/Rasgos')
    pdf.setFont("Helvetica", 12)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    pdf.drawString(50, 780, f'Fecha: {fecha_actual}')
    pdf.drawString(50, 760, 'Alumno:')
    pdf.drawString(100, 760, nombre)
    #cuerpo
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 730, 'Fecha')
    pdf.drawString(120, 730, 'Materia')
    pdf.drawString(200, 730, 'Horario')
    pdf.drawString(280, 730, 'Rasgo')
    pdf.drawString(340, 730, 'Descripción')
    pdf.setFont("Helvetica", 12)
    y_position = 710
    #asistencia
    for dato in datosasistencia:
        pdf.drawString(50, y_position,  dato[1].strftime("%d/%m/%Y"))
        pdf.drawString(120, y_position, dato[3])
        pdf.drawString(200, y_position, dato[2])
        pdf.drawString(280, y_position, dato[4])
        pdf.drawString(340, y_position, '----')
        pdf.line(50, y_position - 5, 550, y_position - 5)
        y_position -= 20  # Ajusta el valor del salto de línea

        # rasgos
        for dato in datosrasgos:
            pdf.drawString(50, y_position, dato[2].strftime("%d/%m/%Y"))
            pdf.drawString(120, y_position, dato[4])
            pdf.drawString(200, y_position, dato[3])
            pdf.drawString(280, y_position, dato[0])
            pdf.drawString(340, y_position, dato[1])
            pdf.line(50, y_position - 5, 550, y_position - 5)
            y_position -= 20  # Ajusta el valor del salto de línea

    pdf.save()
    return send_file(nombre+'.pdf', as_attachment=True)