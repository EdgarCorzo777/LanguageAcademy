-- ==============================================================
-- LANGUAGE ACADEMY ADMISSIONS SYSTEM - ESQUEMA RELACIONAL SQL
-- Norma SENA 220501095 (Diseño de Base de Datos)
-- Norma SENA 220501096 (Scripts SQL y Persistencia de Software)
-- Motor: SQLite 3 / Compatible con PostgreSQL y MySQL ANSI SQL
-- ==============================================================

-- 1. Tabla de Programas Académicos Oficiales
CREATE TABLE IF NOT EXISTS programas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    idioma VARCHAR(30) NOT NULL,
    nivel_mcer VARCHAR(10) NOT NULL,            -- A1, A2, B1, B2, C1, C2
    duracion_semanas INTEGER NOT NULL,
    horas_totales INTEGER NOT NULL,
    precio_contado_cop INTEGER NOT NULL,
    precio_cuotas_cop INTEGER NOT NULL,
    numero_cuotas INTEGER DEFAULT 4,
    activo BOOLEAN DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Sedes y Modalidades
CREATE TABLE IF NOT EXISTS sedes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    ciudad VARCHAR(50) NOT NULL,
    nombre_sede VARCHAR(100) NOT NULL,
    direccion VARCHAR(150) NOT NULL,
    modalidad VARCHAR(30) NOT NULL,             -- Presencial, Hibrida, 100% Online
    telefono_contacto VARCHAR(30),
    horario_atencion VARCHAR(120),
    activo BOOLEAN DEFAULT 1
);

-- 3. Tabla Intermedia: Disponibilidad de Programas por Sede (M:N)
CREATE TABLE IF NOT EXISTS programas_sedes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    programa_id INTEGER NOT NULL,
    sede_id INTEGER NOT NULL,
    cupos_disponibles INTEGER DEFAULT 25,
    activo BOOLEAN DEFAULT 1,
    FOREIGN KEY (programa_id) REFERENCES programas(id) ON DELETE CASCADE,
    FOREIGN KEY (sede_id) REFERENCES sedes(id) ON DELETE CASCADE,
    UNIQUE(programa_id, sede_id)
);

-- 4. Tabla de Estudiantes y Prospectos (Leads)
CREATE TABLE IF NOT EXISTS estudiantes_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_documento VARCHAR(10) DEFAULT 'CC',    -- CC, TI, CE, Pasaporte, PPT
    numero_documento VARCHAR(30),
    nombre_completo VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL,
    telefono VARCHAR(30),
    ciudad VARCHAR(50) DEFAULT 'Bogota',
    sede_preferida_id INTEGER,
    origen_lead VARCHAR(40) DEFAULT 'Web Form RAG',
    nivel_interes VARCHAR(30) DEFAULT 'Alto',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sede_preferida_id) REFERENCES sedes(id) ON DELETE SET NULL
);

-- 5. Tabla de Agendamiento de Exámenes Diagnósticos (Placement Tests)
CREATE TABLE IF NOT EXISTS agendamientos_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_confirmacion VARCHAR(30) NOT NULL UNIQUE,
    estudiante_id INTEGER NOT NULL,
    programa_id INTEGER,
    sede_id INTEGER,
    idioma VARCHAR(30) NOT NULL,
    modalidad VARCHAR(30) DEFAULT 'Online',     -- Online, Presencial Bogota, Presencial Medellin
    fecha_preferida DATE,
    hora_preferida VARCHAR(20),
    estado VARCHAR(20) DEFAULT 'Programado',    -- Programado, Confirmado, Completado, Cancelado
    calificacion_mcer VARCHAR(10),              -- Asignada tras la prueba (ej: B1)
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes_leads(id) ON DELETE CASCADE,
    FOREIGN KEY (programa_id) REFERENCES programas(id) ON DELETE SET NULL,
    FOREIGN KEY (sede_id) REFERENCES sedes(id) ON DELETE SET NULL
);

-- 6. Tabla de Cotizaciones de Matrícula Generadas
CREATE TABLE IF NOT EXISTS cotizaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_cotizacion VARCHAR(30) NOT NULL UNIQUE,
    estudiante_id INTEGER,
    programa_id INTEGER NOT NULL,
    plan_pago VARCHAR(30) NOT NULL,             -- upfront (contado) o installments (cuotas)
    codigo_descuento VARCHAR(40) DEFAULT 'none',
    nombre_descuento VARCHAR(80),
    porcentaje_descuento DECIMAL(5,2) DEFAULT 0.00,
    valor_base_cop INTEGER NOT NULL,
    descuento_cop INTEGER NOT NULL,
    valor_final_cop INTEGER NOT NULL,
    info_cuotas VARCHAR(100),
    canal VARCHAR(30) DEFAULT 'Web Assistant',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes_leads(id) ON DELETE SET NULL,
    FOREIGN KEY (programa_id) REFERENCES programas(id) ON DELETE RESTRICT
);

-- 7. Tabla de Tickets de Escalamiento a Asesor Humano
CREATE TABLE IF NOT EXISTS tickets_escalamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_ticket VARCHAR(30) NOT NULL UNIQUE,
    estudiante_id INTEGER,
    canal_origen VARCHAR(30) DEFAULT 'RAG Chatbot',
    motivo_escalamiento VARCHAR(80) NOT NULL,   -- Solicitud explicita, Caso financiero PSE, Convenio corporativo
    consulta_usuario TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'Abierto',       -- Abierto, En Atencion, Resuelto, Cerrado
    prioridad VARCHAR(20) DEFAULT 'Media',      -- Baja, Media, Alta, Urgente
    asesor_asignado VARCHAR(80),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes_leads(id) ON DELETE SET NULL
);

-- 8. Índices de Rendimiento
CREATE INDEX IF NOT EXISTS idx_leads_email ON estudiantes_leads(email);
CREATE INDEX IF NOT EXISTS idx_agendamientos_codigo ON agendamientos_test(codigo_confirmacion);
CREATE INDEX IF NOT EXISTS idx_cotizaciones_numero ON cotizaciones(numero_cotizacion);
CREATE INDEX IF NOT EXISTS idx_tickets_estado ON tickets_escalamiento(estado);
CREATE INDEX IF NOT EXISTS idx_agendamientos_sede ON agendamientos_test(sede_id);
CREATE INDEX IF NOT EXISTS idx_programas_sedes_prog ON programas_sedes(programa_id);

-- ==============================================================
-- INSERCIÓN DE DATOS SEMILLA (SEED DATA)
-- ==============================================================
INSERT OR IGNORE INTO programas (codigo, nombre, idioma, nivel_mcer, duracion_semanas, horas_totales, precio_contado_cop, precio_cuotas_cop, numero_cuotas) VALUES
('ENG-STD', 'Ingles General Estandar', 'Ingles', 'A1-C1', 16, 96, 1450000, 1580000, 4),
('ENG-INT', 'Ingles Intensivo de Inmersion', 'Ingles', 'A1-C1', 8, 96, 1650000, 1750000, 2),
('ENG-BIZ', 'Business English & Negocios', 'Ingles', 'B2-C1', 12, 48, 1200000, 1290000, 3),
('ENG-CERT', 'Preparacion IELTS / TOEFL / Cambridge', 'Ingles', 'B2-C2', 10, 60, 980000, 980000, 1),
('FRA-STD', 'Frances General y Diplomas DELF', 'Frances', 'A1-B2', 16, 96, 1450000, 1580000, 4),
('DEU-STD', 'Aleman Integral Goethe-Institut', 'Aleman', 'A1-B2', 18, 108, 1550000, 1680000, 4),
('ITA-STD', 'Italiano Conversacional CELI', 'Italiano', 'A1-B2', 14, 70, 1350000, 1450000, 3),
('POR-STD', 'Portugues Brasil Celpe-Bras', 'Portugues', 'A1-B2', 14, 70, 1350000, 1450000, 3);

INSERT OR IGNORE INTO sedes (codigo, ciudad, nombre_sede, direccion, modalidad, telefono_contacto, horario_atencion) VALUES
('BOG-CHAP', 'Bogota', 'Sede Chapinero Central', 'Carrera 13 # 54-20', 'Presencial e Hibrida', '+57 (601) 745-8900', 'L-V 7:00 AM - 9:00 PM | Sab 8:00 AM - 5:00 PM'),
('BOG-C100', 'Bogota', 'Sede Calle 100 (Chico Norte)', 'Calle 100 # 19-61', 'Presencial', '+57 (601) 745-8901', 'L-V 7:00 AM - 9:00 PM | Sab 8:00 AM - 4:00 PM'),
('MED-POB', 'Medellin', 'Sede El Poblado', 'Carrera 43A # 7-50A', 'Presencial e Hibrida', '+57 (604) 604-3200', 'L-V 7:00 AM - 8:30 PM | Sab 8:00 AM - 4:00 PM'),
('MED-LAUR', 'Medellin', 'Sede Laureles', 'Avenida Nutibara # 73-22', 'Presencial', '+57 (604) 604-3201', 'L-V 7:00 AM - 8:30 PM | Sab 8:00 AM - 2:00 PM'),
('ONLINE', 'Nacional / Global', 'Campus Virtual en Vivo', 'campus.languageacademy.edu.co', '100% Online en Vivo', '+57 (300) 123-4567', 'Plataforma 24/7 | Clases L-S manana, tarde y noche');

-- Relacion Programas - Sedes
INSERT OR IGNORE INTO programas_sedes (programa_id, sede_id, cupos_disponibles) VALUES
(1, 1, 20), (1, 2, 20), (1, 3, 20), (1, 4, 20), (1, 5, 50),
(2, 1, 15), (2, 3, 15), (2, 5, 40),
(3, 2, 12), (3, 3, 12), (3, 5, 30),
(4, 1, 15), (4, 5, 35),
(5, 1, 18), (5, 3, 18), (5, 5, 30),
(6, 1, 15), (6, 5, 25),
(7, 1, 15), (7, 5, 25),
(8, 3, 15), (8, 5, 25);
