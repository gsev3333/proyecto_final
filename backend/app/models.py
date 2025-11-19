# app/models.py
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_nacimiento = Column(String, nullable=False)  # Mandatory
    fecha_creacion = Column(String, nullable=False)  # Fecha de creación del paciente

    # Clinical sections - all optional
    antecedentes_interes = Column(Text, nullable=True)
    anamnesis_exploracion = Column(Text, nullable=True)
    evolucion_clinica = Column(Text, nullable=True)
    ordenes_medicas = Column(Text, nullable=True)
    tratamiento_farmacologico = Column(Text, nullable=True)
    planificacion_cuidados = Column(Text, nullable=True)
    constantes_datos_basicos = Column(Text, nullable=True)
    interconsulta = Column(Text, nullable=True)
    exploraciones_complementarias = Column(Text, nullable=True)
    consentimientos_informados = Column(Text, nullable=True)
    informacion_alta = Column(Text, nullable=True)
    otra_informacion_clinica = Column(Text, nullable=True)
    informacion_anestesia = Column(Text, nullable=True)
    informacion_quirurgica = Column(Text, nullable=True)
    informacion_urgencia = Column(Text, nullable=True)
    informacion_parto = Column(Text, nullable=True)
    informacion_anatomia_patologica = Column(Text, nullable=True)

    # Social data
    datos_sociales = Column(Text, nullable=True)

    # Notas del médico
    notas_medico = Column(Text, nullable=True)

class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(String, index=True, nullable=False)
    fecha_ingreso = Column(String, nullable=False)
    motivo = Column(Text, nullable=True)
    admisionista_id = Column(Integer, nullable=False)  # ID del admisionista que lo creó

class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)  # ISO format
    ip_address = Column(String, nullable=True)

# Pydantic models for API
from pydantic import BaseModel

class PatientUpdate(BaseModel):
    antecedentes_interes: str = ""
    anamnesis_exploracion: str = ""
    evolucion_clinica: str = ""
    ordenes_medicas: str = ""
    tratamiento_farmacologico: str = ""
    planificacion_cuidados: str = ""
    constantes_datos_basicos: str = ""
    interconsulta: str = ""
    exploraciones_complementarias: str = ""
    consentimientos_informados: str = ""
    informacion_alta: str = ""
    otra_informacion_clinica: str = ""
    informacion_anestesia: str = ""
    informacion_quirurgica: str = ""
    informacion_urgencia: str = ""
    informacion_parto: str = ""
    informacion_anatomia_patologica: str = ""
    datos_sociales: str = ""
