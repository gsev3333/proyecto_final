# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

from app.database import Base, engine, SessionLocal
import app.models as models
from app.auth import authenticate_user, create_access_token, get_current_user, get_current_user_with_role, get_password_hash
from app.models import PatientUpdate, LoginLog
from datetime import timedelta, datetime

from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear usuario médico por defecto si no existe
db = SessionLocal()
try:
    medico = db.query(models.User).filter(models.User.username == "gabriel").first()
    if not medico:
        hashed_password = get_password_hash("medico123")
        medico = models.User(username="gabriel", hashed_password=hashed_password, role="medico")
        db.add(medico)
        db.commit()
        logger.info("Usuario médico por defecto creado: gabriel / medico123")
    else:
        logger.info("Usuario médico ya existe, actualizando contraseña")
        medico.hashed_password = get_password_hash("medico123")
        db.commit()
        logger.info("Contraseña actualizada para gabriel / medico123")

    # Crear usuario admisionista por defecto si no existe
    admisionista = db.query(models.User).filter(models.User.username == "admision").first()
    if not admisionista:
        hashed_password = get_password_hash("admision123")
        admisionista = models.User(username="admision", hashed_password=hashed_password, role="admisionista")
        db.add(admisionista)
        db.commit()
        logger.info("Usuario admisionista por defecto creado: admision / admision123")
    else:
        logger.info("Usuario admisionista ya existe, actualizando contraseña")
        admisionista.hashed_password = get_password_hash("admision123")
        db.commit()
        logger.info("Contraseña actualizada para admision / admision123")
finally:
    db.close()

app = FastAPI()

# Permitir que el frontend acceda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Acceso a la raíz desde IP: {client_ip}")
    return FileResponse("app/static/index.html")

@app.post("/token/medico")
def login_medico(request: Request, username: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Intento de login médico desde IP: {client_ip} para usuario: {username}")
    db = SessionLocal()

    user = authenticate_user(db, username, password)

    if not user or user.role != "medico":
        logger.warning(f"Intento de login médico fallido para usuario: {username}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    logger.info(f"Login médico exitoso para usuario: {username}")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=60)
    )

    # Registrar log de login
    log_entry = models.LoginLog(
        username=username,
        role=user.role,
        timestamp=datetime.now().isoformat(),
        ip_address=request.client.host if request.client else None
    )
    db.add(log_entry)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

@app.post("/token/paciente")
def login_paciente(request: Request, documento_id: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Intento de login paciente desde IP: {client_ip} para documento: {documento_id}")
    db = SessionLocal()

    user = authenticate_user(db, documento_id, password)

    if not user or user.role != "paciente":
        logger.warning(f"Intento de login paciente fallido para documento: {documento_id}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    logger.info(f"Login paciente exitoso para documento: {documento_id}")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=60)
    )

    # Registrar log de login
    log_entry = models.LoginLog(
        username=documento_id,
        role=user.role,
        timestamp=datetime.now().isoformat(),
        ip_address=request.client.host if request.client else None
    )
    db.add(log_entry)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

@app.post("/token/admisionista")
def login_admisionista(request: Request, username: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Intento de login admisionista desde IP: {client_ip} para usuario: {username}")
    db = SessionLocal()

    user = authenticate_user(db, username, password)

    if not user or user.role != "admisionista":
        logger.warning(f"Intento de login admisionista fallido para usuario: {username}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    logger.info(f"Login admisionista exitoso para usuario: {username}")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=60)
    )

    # Registrar log de login
    log_entry = models.LoginLog(
        username=username,
        role=user.role,
        timestamp=datetime.now().isoformat(),
        ip_address=request.client.host if request.client else None
    )
    db.add(log_entry)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

@app.get("/paciente/{documento_id}")
def get_paciente(documento_id: str, user=Depends(get_current_user)):
    db = SessionLocal()
    patient = db.query(models.Patient).filter(models.Patient.documento_id == documento_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Si el usuario es paciente, solo puede ver su propia historia
    if user.role == "paciente" and documento_id != user.username:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta historia")

    # Obtener admisiones del paciente
    admissions = db.query(models.Admission).filter(models.Admission.documento_id == documento_id).all()

    return {
        "documento_id": patient.documento_id,
        "nombre": patient.nombre,
        "apellido": patient.apellido,
        "fecha_nacimiento": patient.fecha_nacimiento,
        "fecha_creacion": patient.fecha_creacion,
        "antecedentes_interes": patient.antecedentes_interes,
        "anamnesis_exploracion": patient.anamnesis_exploracion,
        "evolucion_clinica": patient.evolucion_clinica,
        "ordenes_medicas": patient.ordenes_medicas,
        "tratamiento_farmacologico": patient.tratamiento_farmacologico,
        "planificacion_cuidados": patient.planificacion_cuidados,
        "constantes_datos_basicos": patient.constantes_datos_basicos,
        "interconsulta": patient.interconsulta,
        "exploraciones_complementarias": patient.exploraciones_complementarias,
        "consentimientos_informados": patient.consentimientos_informados,
        "informacion_alta": patient.informacion_alta,
        "otra_informacion_clinica": patient.otra_informacion_clinica,
        "informacion_anestesia": patient.informacion_anestesia,
        "informacion_quirurgica": patient.informacion_quirurgica,
        "informacion_urgencia": patient.informacion_urgencia,
        "informacion_parto": patient.informacion_parto,
        "informacion_anatomia_patologica": patient.informacion_anatomia_patologica,
        "datos_sociales": patient.datos_sociales,
        "notas_medico": patient.notas_medico,
        "admissions": [{"id": a.id, "fecha_ingreso": a.fecha_ingreso, "motivo": a.motivo} for a in admissions]
    }

@app.put("/paciente/{documento_id}")
def update_paciente(
    documento_id: str,
    antecedentes_interes: str = Form(""),
    anamnesis_exploracion: str = Form(""),
    evolucion_clinica: str = Form(""),
    ordenes_medicas: str = Form(""),
    tratamiento_farmacologico: str = Form(""),
    planificacion_cuidados: str = Form(""),
    constantes_datos_basicos: str = Form(""),
    interconsulta: str = Form(""),
    exploraciones_complementarias: str = Form(""),
    consentimientos_informados: str = Form(""),
    informacion_alta: str = Form(""),
    otra_informacion_clinica: str = Form(""),
    informacion_anestesia: str = Form(""),
    informacion_quirurgica: str = Form(""),
    informacion_urgencia: str = Form(""),
    informacion_parto: str = Form(""),
    informacion_anatomia_patologica: str = Form(""),
    datos_sociales: str = Form(""),
    notas_medico: str = Form(""),
    user=Depends(get_current_user)
):
    if user.role not in ["medico", "admisionista"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar historias clínicas")
    db = SessionLocal()
    patient = db.query(models.Patient).filter(models.Patient.documento_id == documento_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if user.role == "medico":
        # Médico solo puede actualizar notas_medico
        patient.notas_medico = notas_medico
        message = "Notas del médico actualizadas"
    else:
        # Admisionista puede actualizar todo
        patient.antecedentes_interes = antecedentes_interes
        patient.anamnesis_exploracion = anamnesis_exploracion
        patient.evolucion_clinica = evolucion_clinica
        patient.ordenes_medicas = ordenes_medicas
        patient.tratamiento_farmacologico = tratamiento_farmacologico
        patient.planificacion_cuidados = planificacion_cuidados
        patient.constantes_datos_basicos = constantes_datos_basicos
        patient.interconsulta = interconsulta
        patient.exploraciones_complementarias = exploraciones_complementarias
        patient.consentimientos_informados = consentimientos_informados
        patient.informacion_alta = informacion_alta
        patient.otra_informacion_clinica = otra_informacion_clinica
        patient.informacion_anestesia = informacion_anestesia
        patient.informacion_quirurgica = informacion_quirurgica
        patient.informacion_urgencia = informacion_urgencia
        patient.informacion_parto = informacion_parto
        patient.informacion_anatomia_patologica = informacion_anatomia_patologica
        patient.datos_sociales = datos_sociales
        patient.notas_medico = notas_medico
        message = "Historia clínica actualizada"

    db.commit()
    db.refresh(patient)
    return {"message": message}

@app.post("/admission")
def create_admission(request: dict, user=Depends(get_current_user_with_role("admisionista"))):
    db = SessionLocal()
    documento_id = request.get("documento_id")
    fecha_ingreso = request.get("fecha_ingreso")
    motivo = request.get("motivo")

    if not documento_id or not fecha_ingreso:
        raise HTTPException(status_code=400, detail="Documento ID y fecha de ingreso son requeridos")

    # Verificar si el paciente existe
    patient = db.query(models.Patient).filter(models.Patient.documento_id == documento_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    admission = models.Admission(
        documento_id=documento_id,
        fecha_ingreso=fecha_ingreso,
        motivo=motivo,
        admisionista_id=user.id
    )
    db.add(admission)
    db.commit()
    db.refresh(admission)

    return {"message": "Admisión creada", "id": admission.id}

@app.get("/exportar_pdf/{documento_id}")
def exportar_pdf(documento_id: str, user=Depends(get_current_user)):
    if user.role not in ["resultados", "medico", "admisionista", "paciente"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para exportar PDF")
    # Pacientes solo pueden descargar su propio PDF
    if user.role == "paciente" and documento_id != user.username:
        raise HTTPException(status_code=403, detail="Solo puedes descargar tu propio PDF")

    db = SessionLocal()
    patient = db.query(models.Patient).filter(models.Patient.documento_id == documento_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Obtener admisiones del paciente
    admissions = db.query(models.Admission).filter(models.Admission.documento_id == documento_id).all()
    admissions_text = "\n".join([f"Fecha: {a.fecha_ingreso}, Motivo: {a.motivo or 'Sin motivo'}" for a in admissions]) if admissions else "(Sin admisiones)"

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8
    )

    story = []

    # Título principal
    story.append(Paragraph("Historia Clínica Electrónica", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Información del paciente
    story.append(Paragraph(f"<b>Documento:</b> {patient.documento_id}", normal_style))
    story.append(Paragraph(f"<b>Nombre:</b> {patient.nombre} {patient.apellido}", normal_style))
    story.append(Paragraph(f"<b>Fecha de Nacimiento:</b> {patient.fecha_nacimiento}", normal_style))
    story.append(Paragraph(f"<b>Fecha de Creación:</b> {patient.fecha_creacion}", normal_style))
    story.append(Spacer(1, 0.3*inch))

    sections = [
        ("Admisiones", admissions_text),
        ("Antecedentes de Interés", patient.antecedentes_interes),
        ("Anamnesis y Exploración", patient.anamnesis_exploracion),
        ("Evolución Clínica", patient.evolucion_clinica),
        ("Órdenes Médicas", patient.ordenes_medicas),
        ("Tratamiento Farmacológico", patient.tratamiento_farmacologico),
        ("Planificación de Cuidados", patient.planificacion_cuidados),
        ("Constantes y Datos Básicos", patient.constantes_datos_basicos),
        ("Interconsulta", patient.interconsulta),
        ("Exploraciones Complementarias", patient.exploraciones_complementarias),
        ("Consentimientos Informados", patient.consentimientos_informados),
        ("Información de Alta", patient.informacion_alta),
        ("Otra Información Clínica", patient.otra_informacion_clinica),
        ("Información de Anestesia", patient.informacion_anestesia),
        ("Información Quirúrgica", patient.informacion_quirurgica),
        ("Información de Urgencia", patient.informacion_urgencia),
        ("Información del Parto", patient.informacion_parto),
        ("Información de Anatomía Patológica", patient.informacion_anatomia_patologica),
        ("Datos Sociales", patient.datos_sociales),
        ("Notas del Médico", patient.notas_medico)
    ]

    for title, text in sections:
        story.append(Paragraph(title, section_title_style))

        if text and text.strip():
            # Procesar el texto para manejar saltos de línea
            formatted_text = text.replace('\n', '<br/>')
            story.append(Paragraph(formatted_text, normal_style))
        else:
            story.append(Paragraph("<i>(Sin información)</i>", normal_style))

    doc.build(story)
    buffer.seek(0)

    from fastapi.responses import Response
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=historia_{documento_id}.pdf"})

@app.get("/perfil")
def perfil(user=Depends(get_current_user)):
    return {"username": user.username, "role": user.role}

@app.get("/login_logs")
def get_login_logs(user=Depends(get_current_user_with_role("admisionista")), limit: int = 50):
    db = SessionLocal()
    try:
        logs = db.query(models.LoginLog).order_by(models.LoginLog.timestamp.desc()).limit(limit).all()
        return [
            {
                "id": log.id,
                "username": log.username,
                "role": log.role,
                "timestamp": log.timestamp,
                "ip_address": log.ip_address
            }
            for log in logs
        ]
    finally:
        db.close()

@app.post("/users")
def create_user(
    documento_id: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    antecedentes_interes: str = Form(""),
    anamnesis_exploracion: str = Form(""),
    evolucion_clinica: str = Form(""),
    ordenes_medicas: str = Form(""),
    tratamiento_farmacologico: str = Form(""),
    planificacion_cuidados: str = Form(""),
    constantes_datos_basicos: str = Form(""),
    interconsulta: str = Form(""),
    exploraciones_complementarias: str = Form(""),
    consentimientos_informados: str = Form(""),
    informacion_alta: str = Form(""),
    otra_informacion_clinica: str = Form(""),
    informacion_anestesia: str = Form(""),
    informacion_quirurgica: str = Form(""),
    informacion_urgencia: str = Form(""),
    informacion_parto: str = Form(""),
    informacion_anatomia_patologica: str = Form(""),
    datos_sociales: str = Form(""),
    role: str = Form(...),
    user=Depends(get_current_user_with_role("admisionista"))
):
    db = SessionLocal()
    try:
        # Validar que documento_id sea numérico
        if not documento_id.isdigit():
            raise HTTPException(status_code=400, detail="Documento ID debe ser numérico")

        # Verificar si paciente ya existe
        existing_patient = db.query(models.Patient).filter(models.Patient.documento_id == documento_id).first()
        if existing_patient:
            raise HTTPException(status_code=400, detail="No se puede crear el paciente porque ya existe un paciente con este ID")

        # Para pacientes, username y password = documento_id
        username = documento_id
        password = documento_id

        # Verificar si usuario ya existe
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        hashed_password = get_password_hash(password)
        new_user = models.User(username=username, hashed_password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Si es paciente, crear también el paciente con todos los campos
        if role == "paciente":
            new_patient = models.Patient(
                documento_id=documento_id,
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento,
                fecha_creacion=datetime.now().isoformat(),
                antecedentes_interes=antecedentes_interes,
                anamnesis_exploracion=anamnesis_exploracion,
                evolucion_clinica=evolucion_clinica,
                ordenes_medicas=ordenes_medicas,
                tratamiento_farmacologico=tratamiento_farmacologico,
                planificacion_cuidados=planificacion_cuidados,
                constantes_datos_basicos=constantes_datos_basicos,
                interconsulta=interconsulta,
                exploraciones_complementarias=exploraciones_complementarias,
                consentimientos_informados=consentimientos_informados,
                informacion_alta=informacion_alta,
                otra_informacion_clinica=otra_informacion_clinica,
                informacion_anestesia=informacion_anestesia,
                informacion_quirurgica=informacion_quirurgica,
                informacion_urgencia=informacion_urgencia,
                informacion_parto=informacion_parto,
                informacion_anatomia_patologica=informacion_anatomia_patologica,
                datos_sociales=datos_sociales
            )
            db.add(new_patient)
            db.commit()

        message = "Paciente creado correctamente" if role == "paciente" else "Usuario creado exitosamente"
        return {"message": message, "username": username, "role": role, "password": password}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
