from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import datetime

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')


# Conexión a SQL Server
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-M9L8G75;'
    'DATABASE=citas_medicas;'
    'UID=coder;'
    'PWD=coder;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# -----------------------------
# PACIENTES
# -----------------------------
@app.route('/pacientes')
def pacientes():
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/pacientes/registrar', methods=['GET', 'POST'])
def registrar_paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        cursor.execute("INSERT INTO Pacientes (nombre, edad, telefono, direccion) VALUES (?, ?, ?, ?)", (nombre, edad, telefono, direccion))
        conn.commit()
        return redirect(url_for('pacientes'))
    return render_template('registrar_paciente.html')

# Editar paciente
@app.route('/pacientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        cursor.execute("UPDATE Pacientes SET nombre=?, edad=?, telefono=?, direccion=? WHERE id=?", (nombre, edad, telefono, direccion, id))
        conn.commit()
        return redirect(url_for('pacientes'))
    cursor.execute("SELECT * FROM Pacientes WHERE id=?", (id,))
    paciente = cursor.fetchone()
    return render_template('editar_paciente.html', paciente=paciente)

# Eliminar paciente
@app.route('/pacientes/eliminar/<int:id>')
def eliminar_paciente(id):
    cursor.execute("DELETE FROM Pacientes WHERE id=?", (id,))
    conn.commit()
    return redirect(url_for('pacientes'))

# -----------------------------
# DOCTORES
# -----------------------------
@app.route('/doctores')
def doctores():
    cursor.execute("SELECT * FROM Doctores")
    doctores = cursor.fetchall()
    return render_template('doctores.html', doctores=doctores)

@app.route('/doctores/registrar', methods=['GET', 'POST'])
def registrar_doctor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        telefono = request.form['telefono']
        cursor.execute("INSERT INTO Doctores (nombre, especialidad, telefono) VALUES (?, ?, ?)", (nombre, especialidad, telefono))
        conn.commit()
        return redirect(url_for('doctores'))
    return render_template('registrar_doctor.html')

@app.route('/doctores/editar/<int:id>', methods=['GET', 'POST'])
def editar_doctor(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        telefono = request.form['telefono']
        cursor.execute("UPDATE Doctores SET nombre=?, especialidad=?, telefono=? WHERE id=?", (nombre, especialidad, telefono, id))
        conn.commit()
        return redirect(url_for('doctores'))
    cursor.execute("SELECT * FROM Doctores WHERE id=?", (id,))
    doctor = cursor.fetchone()
    return render_template('editar_doctor.html', doctor=doctor)

@app.route('/doctores/eliminar/<int:id>')
def eliminar_doctor(id):
    cursor.execute("DELETE FROM Doctores WHERE id=?", (id,))
    conn.commit()
    return redirect(url_for('doctores'))

# -----------------------------
# CITAS
# -----------------------------
@app.route('/citas')
def citas():
    cursor.execute("""
        SELECT c.id, p.nombre AS paciente, d.nombre AS doctor, c.fecha, c.motivo
        FROM Citas c
        JOIN Pacientes p ON c.paciente_id = p.id
        JOIN Doctores d ON c.doctor_id = d.id
    """)
    citas = cursor.fetchall()
    return render_template('citas.html', citas=citas)


@app.route('/citas/programar', methods=['GET', 'POST'])
def programar_cita():
    if request.method == 'POST':
        paciente_id = int(request.form['paciente_id'])
        doctor_id = int(request.form['doctor_id'])
        fecha_str = request.form['fecha']  
        motivo = request.form['motivo']

        # ✅ Convertir a datetime
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            return "Formato de fecha inválido. Asegúrate de usar el selector correctamente."

        # Insertar en la base de datos
        cursor.execute("""
            INSERT INTO Citas (paciente_id, doctor_id, fecha, motivo)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, doctor_id, fecha, motivo))
        conn.commit()
        return redirect(url_for('citas'))

    # GET: Cargar doctores y pacientes para el formulario
    cursor.execute("SELECT id, nombre FROM Pacientes")
    pacientes = cursor.fetchall()
    cursor.execute("SELECT id, nombre FROM Doctores")
    doctores = cursor.fetchall()
    return render_template('programar_cita.html', pacientes=pacientes, doctores=doctores)


@app.route('/citas/editar/<int:id>', methods=['GET', 'POST'])
def editar_cita(id):
    if request.method == 'POST':
        fecha_str = request.form['fecha']  
        motivo = request.form['motivo']

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')  
        except ValueError:
            return "Fecha inválida, asegúrate de usar el selector correctamente."

        cursor.execute("UPDATE Citas SET fecha = ?, motivo = ? WHERE id = ?", (fecha, motivo, id))
        conn.commit()
        return redirect(url_for('citas'))

    # GET: cargar cita actual
    cursor.execute("SELECT id, fecha, motivo FROM Citas WHERE id = ?", (id,))
    cita = cursor.fetchone()
    return render_template('editar_cita.html', cita=cita)

@app.route('/citas/eliminar/<int:id>')
def eliminar_cita(id):
    cursor.execute("DELETE FROM Citas WHERE id = ?", (id,))
    conn.commit()
    return redirect(url_for('citas'))

# -----------------------------
# HISTORIAL DE PACIENTE
# -----------------------------
@app.route('/pacientes/<int:id>/historial')
def historial_paciente(id):
    cursor.execute("SELECT nombre FROM Pacientes WHERE id = ?", (id,))
    paciente = cursor.fetchone()
    cursor.execute("""
        SELECT c.fecha, c.motivo, d.nombre AS doctor
        FROM Citas c
        JOIN Doctores d ON c.doctor_id = d.id
        WHERE c.paciente_id = ?
        ORDER BY c.fecha DESC
    """, (id,))
    historial = cursor.fetchall()
    return render_template('historial_paciente.html', paciente=paciente, historial=historial)

if __name__ == '__main__':
    app.run(debug=True)
