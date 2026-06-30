import sqlite3

def crear_base_datos():
    conn = sqlite3.connect('pec_comunidad.db')
    cursor = conn.cursor()

    # 1. Tabla de Usuarios (Nombres en singular y columnas en inglés para coincidir con app.py)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL
    )''')

    # 2. Tabla de Responsables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS responsable (
        id_responsable INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        titulo_profesional TEXT,
        cargo TEXT NOT NULL
    )''')

    # 3. Tabla de Sedes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sede (
        id_sede INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_sede TEXT NOT NULL,
        ubicacion TEXT NOT NULL
    )''')

    # 4. Tabla de Actividades (CON LA COLUMNA ESTATUS INCLUIDA)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS actividad (
        id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_actividad TEXT NOT NULL,
        descripcion TEXT,
        fecha_programada TEXT NOT NULL,
        parcial TEXT NOT NULL,
        id_responsable INTEGER,
        id_sede INTEGER,
        estatus TEXT DEFAULT 'No empezado',
        FOREIGN KEY (id_sede) REFERENCES sede(id_sede),
        FOREIGN KEY (id_responsable) REFERENCES responsable(id_responsable)
    )''')

    # 5. Tabla de Evidencias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evidencia (
        id_evidencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_actividad INTEGER NOT NULL,
        alumno_nombre TEXT NOT NULL,
        tipo_evidencia TEXT NOT NULL,
        url_archivo TEXT NOT NULL,
        descripcion_evidencia TEXT,
        FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad)
    )''')

    conn.commit()
    conn.close()
    print("¡Base de datos 'pec_comunidad.db' sincronizada y lista para usar con el sistema!")

if __name__ == '__main__':
    crear_base_datos()