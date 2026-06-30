PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ==========================================
-- 1. TABLA: RESPONSABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS responsable (
    id_responsable INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    titulo_profesional TEXT,
    cargo TEXT NOT NULL
);

-- ==========================================
-- 2. TABLA: SEDE
-- ==========================================
CREATE TABLE IF NOT EXISTS sede (
    id_sede INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_sede TEXT NOT NULL,
    ubicacion TEXT NOT NULL
);

-- ==========================================
-- 3. TABLA: ACTIVIDAD
-- ==========================================
CREATE TABLE IF NOT EXISTS actividad (
    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_actividad TEXT NOT NULL,
    descripcion TEXT,
    fecha_programada TEXT NOT NULL,
    parcial TEXT NOT NULL,
    id_responsable INTEGER,
    id_sede INTEGER,
    FOREIGN KEY (id_responsable) REFERENCES responsable(id_responsable),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede)
);

-- ==========================================
-- 4. TABLA: EVIDENCIA
-- ==========================================
CREATE TABLE IF NOT EXISTS evidencia (
    id_evidencia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_actividad INTEGER,
    tipo_evidencia TEXT NOT NULL,
    descripcion_evidencia TEXT,
    url_archivo TEXT NOT NULL,
    alumno_nombre TEXT NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividad(id_actividad)
);

-- ==========================================
-- 5. TABLA: USUARIO (SISTEMA DE AUTENTICACIÓN)
-- ==========================================
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    rol TEXT NOT NULL
);

COMMIT;