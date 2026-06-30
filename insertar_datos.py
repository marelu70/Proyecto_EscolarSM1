import sqlite3

import sqlite3

def insertar_datos_iniciales():
    conexion = sqlite3.connect("pec_comunidad.db")
    cursor = conexion.cursor()
    
    # Lista organizada: (username, password, rol)
    # Roles perfectamente alineados con el Login: 'admin', 'docente', 'alumno'
    usuarios = [
        # --- ADMINISTRADOR FICTICIO ---
        ('admin_pec', 'control2026', 'admin'),
        
        # --- 6 ALUMNOS (Tu Equipo) ---
        ('marely', 'marely123', 'alumno'),          # Marely Anastacio Salazar
        ('estefania', 'estefania123', 'alumno'),    # Estefania Vazquez Tellez
        ('jorge', 'jorge123', 'alumno'),            # Jorge Samano Hernandez
        ('abigail', 'abigail123', 'alumno'),        # Abigail Ramirez Toribio
        ('alexa', 'alexa123', 'alumno'),            # Alexa Lizbeth Garcia Sanchez
        ('eduardo', 'eduardo123', 'alumno'),        # Jose Eduardo Cruz Javier
        
        # --- 6 DOCENTES / RESPONSABLES ---
        ('oralia_portillo', 'profe1', 'docente'),    # Oralia Portillo Quintero
        ('jos_luis', 'profe2', 'docente'),          # Jose Luis Anaya Reyes
        ('edith_b', 'profe3', 'docente'),           # Edith Bartolo Trujillo
        ('beatriz_t', 'profe4', 'docente'),          # Beatriz Tellez Salgadop
        ('victor_j', 'profe5', 'docente'),           # Victor Javier Martinez Sanchez
        ('rosa_c', 'profe6', 'docente')             # Rosa Cayetano Cruz
    ]
    
    # Inserta ignorando duplicados si se vuelve a ejecutar
    cursor.executemany("""
        INSERT OR IGNORE INTO usuario (username, password, rol) 
        VALUES (?, ?, ?)
    """, usuarios)
    
    conexion.commit()
    conexion.close()
    print("¡Todos los Alumnos, Docentes (corregidos) y el Administrador fueron registrados con éxito!")

if __name__ == "__main__":
    insertar_datos_iniciales()