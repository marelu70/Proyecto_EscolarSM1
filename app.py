import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clave_secreta_pec_2026"

# Carpeta de subidas organizada dentro de static/evidencias
CARPA_EVIDENCIAS = os.path.join('static', 'evidencias')
os.makedirs(CARPA_EVIDENCIAS, exist_ok=True)
app.config['UPLOAD_FOLDER'] = CARPA_EVIDENCIAS

DATABASE = "pec_comunidad.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# AUTENTICACIÓN Y CONTROL DE ACCESO
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        rol = request.form.get("rol")
        
        if not username or not password:
            flash("Por favor, llena todos los campos.", "danger")
            return render_template("login.html")
        
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM usuario WHERE username = ? AND password = ? AND rol = ?", 
            (username, password, rol)
        ).fetchone()
        conn.close()
        
        if user:
            session['usuario'] = user['username']
            session['rol'] = user['rol']
            flash(f"¡Bienvenido de vuelta, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales incorrectas o rol no coincide.", "danger")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================================
# DASHBOARD CENTRAL (FILTRADO POR ROL)
# ==========================================

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'rol' not in session:
        flash("Por favor, inicia sesión primero.", "warning")
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    
    resultado_busqueda = None
    busqueda_id = None
    modulo_busqueda = None
    modo_busqueda = False
    
    if request.method == "POST" and "buscar_id" in request.form:
        busqueda_id = request.form.get("buscar_id").strip()
        modulo_busqueda = request.form.get("modulo_busqueda")
        
        if busqueda_id and modulo_busqueda:
            modo_busqueda = True
            if modulo_busqueda == "responsable":
                resultado_busqueda = conn.execute("SELECT * FROM responsable WHERE id_responsable = ?", (busqueda_id,)).fetchone()
            elif modulo_busqueda == "sede":
                resultado_busqueda = conn.execute("SELECT * FROM sede WHERE id_sede = ?", (busqueda_id,)).fetchone()
            elif modulo_busqueda == "actividad":
                resultado_busqueda = conn.execute('''
                    SELECT a.*, r.nombre_completo AS nombre_responsable, s.nombre_sede 
                    FROM actividad a
                    LEFT JOIN responsable r ON a.id_responsable = r.id_responsable
                    LEFT JOIN sede s ON a.id_sede = s.id_sede
                    WHERE a.id_actividad = ?
                ''', (busqueda_id,)).fetchone()
            elif modulo_busqueda == "evidencia":
                resultado_busqueda = conn.execute('''
                    SELECT e.*, a.nombre_actividad 
                    FROM evidencia e
                    LEFT JOIN actividad a ON e.id_actividad = a.id_actividad
                    WHERE e.id_evidencia = ?
                ''', (busqueda_id,)).fetchone()

    responsables = conn.execute("SELECT * FROM responsable").fetchall()
    sedes = conn.execute("SELECT * FROM sede").fetchall()
    
    actividades = conn.execute('''
        SELECT a.*, r.nombre_completo AS nombre_responsable, s.nombre_sede 
        FROM actividad a
        LEFT JOIN responsable r ON a.id_responsable = r.id_responsable
        LEFT JOIN sede s ON a.id_sede = s.id_sede
    ''').fetchall()
    
    evidencias = conn.execute('''
        SELECT e.*, a.nombre_actividad 
        FROM evidencia e
        LEFT JOIN actividad a ON e.id_actividad = a.id_actividad
    ''').fetchall()
    
    conn.close()
    
    return render_template("dashboard.html", 
                           responsables=responsables, 
                           sedes=sedes, 
                           actividades=actividades, 
                           evidencias=evidencias,
                           resultado_busqueda=resultado_busqueda,
                           busqueda_id=busqueda_id,
                           modulo_busqueda=modulo_busqueda,
                           modo_busqueda=modo_busqueda)

# ==========================================
# RUTA EXCLUSIVA: ALUMNOS CAMBIAR ESTATUS
# ==========================================
@app.route("/actividades/estatus/<int:id>", methods=["POST"])
def actualizar_estatus_actividad(id):
    if session.get('rol') != 'alumno':
        flash("Solo los alumnos pueden cambiar el estado de avance.", "danger")
        return redirect(url_for('dashboard'))
        
    nuevo_estatus = request.form.get("nuevo_estatus")
    conn = get_db_connection()
    conn.execute("UPDATE actividad SET estatus = ? WHERE id_actividad = ?", (nuevo_estatus, id))
    conn.commit()
    conn.close()
    flash("Estatus de la actividad actualizado correctamente.", "success")
    return redirect(url_for("dashboard"))

# ==========================================
# ACCIONES CRUD (RESPONSABLES)
# ==========================================
@app.route("/responsables/crear", methods=["POST"])
def crear_responsable():
    if session.get('rol') != 'admin': return redirect(url_for('dashboard'))
    nombre = request.form.get("nombre_completo")
    titulo = request.form.get("titulo_profesional")
    cargo = request.form.get("cargo")
    conn = get_db_connection()
    conn.execute("INSERT INTO responsable (nombre_completo, titulo_profesional, cargo) VALUES (?, ?, ?)", (nombre, titulo, cargo))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/responsables/editar/<int:id>", methods=["GET", "POST"])
def editar_responsable(id):
    if session.get('rol') != 'admin': return redirect(url_for('dashboard'))
    conn = get_db_connection()
    if request.method == "POST":
        nombre = request.form.get("nombre_completo")
        titulo = request.form.get("titulo_profesional")
        cargo = request.form.get("cargo")
        conn.execute("UPDATE responsable SET nombre_completo=?, titulo_profesional=?, cargo=? WHERE id_responsable=?", (nombre, titulo, cargo, id))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    r = conn.execute("SELECT * FROM responsable WHERE id_responsable=?", (id,)).fetchone()
    conn.close()
    return render_template("editar_docente.html", r=r)

@app.route("/responsables/eliminar/<int:id>")
def eliminar_responsable(id):
    if session.get('rol') != 'admin': return redirect(url_for('dashboard'))
    conn = get_db_connection()
    conn.execute("DELETE FROM responsable WHERE id_responsable=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ==========================================
# ACCIONES CRUD (SEDES)
# ==========================================
@app.route("/sedes/crear", methods=["POST"])
def crear_sede():
    if session.get('rol') not in ['admin', 'docente']: return redirect(url_for('dashboard'))
    nombre = request.form.get("nombre_sede")
    ubicacion = request.form.get("ubicacion")
    conn = get_db_connection()
    conn.execute("INSERT INTO sede (nombre_sede, ubicacion) VALUES (?, ?)", (nombre, ubicacion))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/sedes/editar/<int:id>", methods=["GET", "POST"])
def editar_sede(id):
    if session.get('rol') not in ['admin', 'docente']: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    if request.method == "POST":
        nombre = request.form.get("nombre_sede")
        ubicacion = request.form.get("ubicacion")
        conn.execute("UPDATE sede SET nombre_sede=?, ubicacion=? WHERE id_sede=?", (nombre, ubicacion, id))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    sede = conn.execute("SELECT * FROM sede WHERE id_sede=?", (id,)).fetchone()
    conn.close()
    return render_template("editar_sede.html", sede=sede)

@app.route("/sedes/eliminar/<int:id>")
def eliminar_sede(id):
    if session.get('rol') not in ['admin', 'docente']: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    conn.execute("DELETE FROM sede WHERE id_sede=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ==========================================
# ACCIONES CRUD (ACTIVIDADES)
# ==========================================
@app.route("/actividades/crear", methods=["POST"])
def crear_actividad():
    if session.get('rol') not in ['admin', 'docente']: return redirect(url_for('dashboard'))
    nombre = request.form.get("nombre_actividad")
    descripcion = request.form.get("descripcion")
    fecha = request.form.get("fecha_programada")
    parcial = request.form.get("parcial")
    id_resp = request.form.get("id_responsable")
    id_sede = request.form.get("id_sede")
    estatus_inicial = "No empezado"
    
    conn = get_db_connection()
    conn.execute("INSERT INTO actividad (nombre_actividad, descripcion, fecha_programada, parcial, id_responsable, id_sede, estatus) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (nombre, descripcion, fecha, parcial, id_resp, id_sede, estatus_inicial))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/actividades/editar/<int:id>", methods=["GET", "POST"])
def editar_actividad(id):
    if session.get('rol') not in ['admin', 'docente']: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    if request.method == "POST":
        nombre = request.form.get("nombre_actividad")
        descripcion = request.form.get("descripcion")
        fecha = request.form.get("fecha_programada")
        parcial = request.form.get("parcial")
        id_resp = request.form.get("id_responsable")
        id_sede = request.form.get("id_sede")
        conn.execute("UPDATE actividad SET nombre_actividad=?, descripcion=?, fecha_programada=?, parcial=?, id_responsable=?, id_sede=? WHERE id_actividad=?",
                     (nombre, descripcion, fecha, parcial, id_resp, id_sede, id))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    actividad = conn.execute("SELECT * FROM actividad WHERE id_actividad=?", (id,)).fetchone()
    responsables = conn.execute("SELECT * FROM responsable").fetchall()
    sedes = conn.execute("SELECT * FROM sede").fetchall()
    conn.close()
    return render_template("editar_actividad.html", actividad=actividad, responsables=responsables, sedes=sedes)

@app.route("/actividades/eliminar/<int:id>")
def eliminar_actividad(id):
    if session.get('rol') not in ['admin', 'docente']: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    conn.execute("DELETE FROM actividad WHERE id_actividad=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ==========================================
# ACCIONES CRUD (EVIDENCIAS)
# ==========================================
@app.route("/evidencias/crear", methods=["POST"])
def crear_evidencia():
    if session.get('rol') not in ['admin', 'alumno']: return redirect(url_for('dashboard'))
    id_act = request.form.get("id_actividad")
    tipo = request.form.get("tipo_evidencia")
    desc = request.form.get("descripcion_evidencia")
    alumno = request.form.get("alumno_nombre")
    archivo = request.files.get("archivo_evidencia")
    url_final = "sin_archivo.png"
    
    if archivo and archivo.filename != "":
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        url_final = filename

    conn = get_db_connection()
    conn.execute("INSERT INTO evidencia (id_actividad, tipo_evidencia, descripcion_evidencia, url_archivo, alumno_nombre) VALUES (?, ?, ?, ?, ?)",
                 (id_act, tipo, desc, url_final, alumno))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/evidencias/editar/<int:id>", methods=["GET", "POST"])
def editar_evidencia(id):
    if session.get('rol') not in ['admin', 'alumno']: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    if request.method == "POST":
        id_act = request.form.get("id_actividad")
        tipo = request.form.get("tipo_evidencia")
        desc = request.form.get("descripcion_evidencia")
        alumno = request.form.get("alumno_nombre")
        archivo = request.files.get("archivo_evidencia")
        
        if archivo and archivo.filename != "":
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn.execute("UPDATE evidencia SET id_actividad=?, tipo_evidencia=?, descripcion_evidencia=?, url_archivo=?, alumno_nombre=? WHERE id_evidencia=?",
                         (id_act, tipo, desc, filename, alumno, id))
        else:
            conn.execute("UPDATE evidencia SET id_actividad=?, tipo_evidencia=?, descripcion_evidencia=?, alumno_nombre=? WHERE id_evidencia=?",
                         (id_act, tipo, desc, alumno, id))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
        
    evidencia = conn.execute("SELECT * FROM evidencia WHERE id_evidencia=?", (id,)).fetchone()
    actividades = conn.execute("SELECT * FROM actividad").fetchall()
    conn.close()
    return render_template("editar_evidencia.html", evidencia=evidencia, actividades=actividades)

@app.route("/evidencias/eliminar/<int:id>")
def eliminar_evidencia(id):
    if session.get('rol') not in ['admin', 'alumno']: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    conn.execute("DELETE FROM evidencia WHERE id_evidencia=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

# ==========================================
# RUTA INTEGRADA Y PROTEGIDA PARA ARCHIVOS
# ==========================================
@app.route('/ver-evidencia/<filename>')
def ver_archivo_evidencia(filename):
    """Fuerza al navegador a procesar y renderizar el PDF independientemente de las rutas estáticas"""
    # Si es un PDF, inyectamos explícitamente el mimetype para resolver el error de carga de Chrome/Firefox
    if filename.lower().endswith('.pdf'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False, mimetype='application/pdf')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
