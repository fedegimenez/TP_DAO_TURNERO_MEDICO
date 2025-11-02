-- db/init.sql
-- Crea el esquema base acorde a los modelos del backend

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =======================
-- Usuarios (autenticación)
-- =======================
CREATE TABLE IF NOT EXISTS users (
  id               SERIAL PRIMARY KEY,
  email            VARCHAR(120) UNIQUE NOT NULL,
  name             VARCHAR(80)  NOT NULL,
  hashed_password  VARCHAR(255) NOT NULL,
  role             VARCHAR(20)  NOT NULL DEFAULT 'admin'
);

-- =========
-- Pacientes
-- =========
CREATE TABLE IF NOT EXISTS patients (
  id                SERIAL PRIMARY KEY,
  nombre            VARCHAR(80)  NOT NULL,
  apellido          VARCHAR(80)  NOT NULL,
  dni               VARCHAR(20)  NOT NULL UNIQUE,
  fecha_nacimiento  DATE         NOT NULL,
  genero            VARCHAR(20),
  direccion         VARCHAR(120),
  telefono          VARCHAR(30),
  email             VARCHAR(120) UNIQUE,
  obra_social       VARCHAR(120),
  nro_afiliado      VARCHAR(50),
  activo            BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_patients_apellido ON patients (apellido, nombre);

-- =======
-- Médicos
-- =======
CREATE TABLE IF NOT EXISTS doctors (
  id         SERIAL PRIMARY KEY,
  nombre     VARCHAR(80)  NOT NULL,
  apellido   VARCHAR(80)  NOT NULL,
  dni        VARCHAR(20)  NOT NULL UNIQUE,
  genero     VARCHAR(20),
  email      VARCHAR(120) UNIQUE,
  telefono   VARCHAR(30),
  direccion  VARCHAR(120),
  matricula  VARCHAR(40)  NOT NULL UNIQUE,
  activo     BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS ix_doctors_apellido ON doctors (apellido, nombre);

-- =============
-- Especialidades
-- =============
CREATE TABLE IF NOT EXISTS specialties (
  id          SERIAL PRIMARY KEY,
  nombre      VARCHAR(120) NOT NULL UNIQUE,
  descripcion VARCHAR(255),
  activa      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS doctor_specialties (
  doctor_id     INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
  specialty_id  INTEGER NOT NULL REFERENCES specialties(id) ON DELETE RESTRICT,
  PRIMARY KEY (doctor_id, specialty_id)
);

CREATE TABLE IF NOT EXISTS doctor_availability (
  id            SERIAL PRIMARY KEY,
  doctor_id     INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
  day_of_week   SMALLINT NOT NULL,
  start_time    TIME      NOT NULL,
  end_time      TIME      NOT NULL,
  slot_minutes  INTEGER   NOT NULL DEFAULT 30
);

-- ==========
-- Turnos/HC
-- ==========
-- Estados permitidos: Reservado | Cancelado | Reprogramado | Atendido
CREATE TABLE IF NOT EXISTS appointments (
  id               SERIAL PRIMARY KEY,
  paciente_id      INTEGER NOT NULL REFERENCES patients(id)    ON DELETE RESTRICT,
  medico_id        INTEGER NOT NULL REFERENCES doctors(id)     ON DELETE RESTRICT,
  especialidad_id  INTEGER NOT NULL REFERENCES specialties(id) ON DELETE RESTRICT,
  fecha            TIMESTAMP  NOT NULL,
  duracion_min     INTEGER    NOT NULL DEFAULT 30,
  estado           VARCHAR(20) NOT NULL DEFAULT 'Reservado'
    CHECK (estado IN ('Reservado','Cancelado','Reprogramado','Atendido')),
  receta_url       VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_appointments_medico_fecha
  ON appointments (medico_id, fecha);
CREATE INDEX IF NOT EXISTS ix_appointments_paciente_fecha
  ON appointments (paciente_id, fecha);

-- ============
-- Consultas HC
-- ============
CREATE TABLE IF NOT EXISTS consultations (
  id             SERIAL PRIMARY KEY,
  appointment_id INTEGER NOT NULL UNIQUE REFERENCES appointments(id) ON DELETE CASCADE,
  motivo         TEXT,
  observaciones  TEXT,
  diagnostico    TEXT,
  indicaciones   TEXT,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ========
-- Recetas
-- ========
CREATE TABLE IF NOT EXISTS prescriptions (
  id              SERIAL PRIMARY KEY,
  consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
  fecha_emision   DATE     NOT NULL,
  estado          VARCHAR(20) NOT NULL,
  firma_digital   VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS prescription_items (
  id              SERIAL PRIMARY KEY,
  prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
  medicamento     VARCHAR(200) NOT NULL,
  dosis           VARCHAR(160),
  frecuencia      VARCHAR(160),
  duracion        VARCHAR(160),
  indicaciones    TEXT
);

-- ============
-- Recordatorios
-- ============
CREATE TABLE IF NOT EXISTS reminders (
  id               SERIAL PRIMARY KEY,
  appointment_id   INTEGER NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
  canal            VARCHAR(20) NOT NULL,
  programado_para  TIMESTAMP  NOT NULL,
  enviado_en       TIMESTAMP,
  estado           VARCHAR(20) NOT NULL,
  error_msg        VARCHAR(200)
);
