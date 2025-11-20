# Proyecto de Historias Clínicas Electrónicas

## Descripción General

Este proyecto es un sistema de gestión de historias clínicas electrónicas diseñado para facilitar la administración y consulta de información médica en entornos clínicos. Permite a diferentes tipos de usuarios (médicos, admisionistas y pacientes) interactuar con las historias clínicas de manera segura y eficiente. El sistema incluye funcionalidades como autenticación basada en roles, gestión de admisiones, actualización de información clínica, exportación de historias a PDF y registro de logs de acceso.

El proyecto está desarrollado con tecnologías modernas para asegurar escalabilidad, seguridad y facilidad de despliegue.

## Arquitectura

La arquitectura del sistema se basa en una separación clara de responsabilidades:

- **Backend**: Implementado con FastAPI, un framework web moderno para Python que proporciona una API RESTful rápida y eficiente. Maneja la lógica de negocio, autenticación, validación de datos y comunicación con la base de datos.
- **Base de Datos**: Utiliza Citus, una extensión de PostgreSQL que permite bases de datos distribuidas para escalabilidad horizontal. Esto permite manejar grandes volúmenes de datos y consultas distribuidas en múltiples nodos.
- **Frontend**: Consiste en archivos estáticos (HTML, CSS y JavaScript) servidos directamente por el backend de FastAPI. Proporciona una interfaz de usuario simple y responsiva para la interacción con el sistema.

La arquitectura soporta despliegue en contenedores Docker y orquestación con Kubernetes para entornos de producción.

## Capturas de Pantalla

A continuación, se muestran capturas de pantalla de la aplicación en funcionamiento:

### 1. Página de Login
![Página de Login](images/login.png)
Interfaz principal de autenticación con opciones para Médico, Admisionista y Paciente.

### 2. Panel de Médico
![Panel de Médico](images/panel_medico.png)
Vista del médico para cargar y editar historias clínicas de pacientes.

### 3. Panel de Admisionista
![Panel de Admisionista](images/panel_admisionista.png)
Interfaz del admisionista para crear admisiones y gestionar pacientes.

### 4. Vista del Paciente
![Vista del Paciente](images/vista_paciente.png)
Panel del paciente mostrando su información y citas médicas.

### 5. Formulario de Creación de Paciente
![Creación de Paciente](images/crear_paciente.png)
Formulario para registrar nuevos pacientes en el sistema.

### 6. PDF Exportado
![PDF Exportado](images/pdf_exportado.png)
Ejemplo del PDF generado con la historia clínica completa, incluyendo admisiones.

## Instalación y Configuración Local

Para ejecutar el proyecto en un entorno local, sigue estos pasos:

1. **Clona el repositorio**:
   ```
   git clone <url-del-repositorio>
   cd final_pro
   ```

2. **Instala las dependencias**:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**:
   Crea un archivo `.env` en el directorio `backend/` o establece las variables en tu entorno:
   - `DATABASE_URL`: URL de conexión a la base de datos (por defecto: `sqlite:///./clinical.db` para desarrollo local)
   - `JWT_SECRET`: Clave secreta para la generación de tokens JWT (por defecto: `"secreto_super_seguro"`)

4. **Ejecuta la aplicación**:
   ```
   uvicorn app.main:app --reload --host 0.0.0.0
   ```

   La aplicación estará disponible en `http://localhost:8000` y accesible desde otros dispositivos en la red local usando la IP de la máquina host (ej. `http://192.168.1.X:8000`).

Nota: Para desarrollo local, se utiliza SQLite por defecto. Para producción, configura PostgreSQL con Citus.

## Construcción y Ejecución con Docker

El proyecto incluye un Dockerfile para contenerización y está configurado para ejecutarse con SQLite por defecto:

1. **Construye la imagen Docker**:
   ```
   cd backend
   docker build -t fastapi-app .
   ```

2. **Ejecuta el contenedor**:
   ```
   docker run -d -p 0.0.0.0:8000:8000 fastapi-app
   ```

   La aplicación estará disponible en `http://localhost:8000` y accesible desde otros dispositivos en la red local usando la IP de la máquina host (ej. `http://192.168.1.X:8000`). Esto permite el acceso desde celulares, tablets u otros dispositivos conectados a la misma red.

   Nota: El contenedor utiliza SQLite por defecto, por lo que no requiere configuración adicional de base de datos.

## Despliegue en Kubernetes

Para desplegar en un clúster de Kubernetes, utiliza los manifiestos proporcionados en el directorio `k8s/`:

1. **Asegúrate de tener un clúster Kubernetes ejecutándose** (por ejemplo, con Minikube).

2. **Crea el secreto para JWT**:
   ```
   kubectl create secret generic jwt-secret --from-literal=JWT_SECRET="tu_secreto_jwt"
   ```

3. **Aplica los manifiestos**:
   ```
   kubectl apply -f k8s/citus-coordinator.yaml
   kubectl apply -f k8s/citus-worker.yaml
   kubectl apply -f k8s/fastapi-deployment.yaml
   kubectl apply -f k8s/fastapi-service-nodeport.yaml
   ```

4. **Accede a la aplicación**:
   - Encuentra la IP del nodo: `kubectl get nodes -o wide`
   - Accede en `http://<node-ip>:30080`

Los manifiestos incluyen:
- `citus-coordinator.yaml`: Despliegue del coordinador Citus con 1 réplica.
- `citus-worker.yaml`: Despliegue de workers Citus con 2 réplicas.
- `fastapi-deployment.yaml`: Despliegue de la aplicación FastAPI.
- `fastapi-service-nodeport.yaml`: Servicio NodePort para exponer la aplicación en el puerto 30080.

## Endpoints API Principales

La API RESTful proporciona los siguientes endpoints principales:

### Autenticación
- `POST /token/medico`: Login para médicos. Requiere `username` y `password`. Retorna token JWT.
- `POST /token/paciente`: Login para pacientes. Requiere `documento_id` y `password`. Retorna token JWT.
- `POST /token/admisionista`: Login para admisionistas. Requiere `username` y `password`. Retorna token JWT.

### Gestión de Pacientes
- `GET /paciente/{documento_id}`: Obtiene la historia clínica completa de un paciente. Requiere autenticación.
- `PUT /paciente/{documento_id}`: Actualiza la información clínica de un paciente. Solo médicos pueden actualizar notas, admisionistas pueden actualizar todo.
- `POST /users`: Crea un nuevo usuario/paciente. Solo para admisionistas.

### Admisiones
- `POST /admission`: Crea una nueva admisión para un paciente. Solo para admisionistas.

### Exportación y Utilidades
- `GET /exportar_pdf/{documento_id}`: Exporta la historia clínica a PDF.
- `GET /perfil`: Obtiene el perfil del usuario autenticado.
- `GET /login_logs`: Obtiene los logs de login (últimos 50). Solo para admisionistas.

Todos los endpoints requieren autenticación JWT excepto la raíz (`GET /`) que sirve el frontend estático.

## Modelos de Datos

Los modelos de datos están definidos usando SQLAlchemy:

- **User**: Representa usuarios del sistema.
  - `id`: Identificador único.
  - `username`: Nombre de usuario único.
  - `hashed_password`: Contraseña hasheada.
  - `role`: Rol del usuario (medico, admisionista, paciente).

- **Patient**: Representa la historia clínica de un paciente.
  - `id`: Identificador único.
  - `documento_id`: Documento de identidad único.
  - `nombre`, `apellido`: Información personal.
  - `fecha_nacimiento`, `fecha_creacion`: Fechas relevantes.
  - Campos clínicos opcionales: `antecedentes_interes`, `anamnesis_exploracion`, `evolucion_clinica`, `ordenes_medicas`, `tratamiento_farmacologico`, `planificacion_cuidados`, `constantes_datos_basicos`, `interconsulta`, `exploraciones_complementarias`, `consentimientos_informados`, `informacion_alta`, `otra_informacion_clinica`, `informacion_anestesia`, `informacion_quirurgica`, `informacion_urgencia`, `informacion_parto`, `informacion_anatomia_patologica`, `datos_sociales`, `notas_medico`.

- **Admission**: Representa admisiones de pacientes.
  - `id`: Identificador único.
  - `documento_id`: ID del paciente.
  - `fecha_ingreso`: Fecha de ingreso.
  - `motivo`: Motivo de la admisión.
  - `admisionista_id`: ID del admisionista que la creó.

- **LoginLog**: Registra accesos al sistema.
  - `id`: Identificador único.
  - `username`: Usuario que inició sesión.
  - `role`: Rol del usuario.
  - `timestamp`: Fecha y hora del login.
  - `ip_address`: Dirección IP del cliente.

## Sistema de Autenticación

El sistema utiliza autenticación basada en JSON Web Tokens (JWT) con los siguientes componentes:

- **Roles**: Tres tipos de usuarios con permisos diferenciados:
  - `medico`: Puede ver y actualizar notas médicas.
  - `admisionista`: Puede gestionar pacientes, admisiones y actualizar toda la información clínica.
  - `paciente`: Solo puede ver su propia historia clínica.

- **Tokens**: Los tokens JWT expiran después de 60 minutos. Se generan al hacer login y deben incluirse en el header `Authorization: Bearer <token>` para acceder a endpoints protegidos.

- **Hashing de contraseñas**: Utiliza PBKDF2 con SHA256 para almacenar contraseñas de forma segura.

- **Logs de acceso**: Registra cada intento de login con timestamp e IP para auditoría.

Usuarios por defecto creados automáticamente:
- Médico: `gabriel` / `medico123`
- Admisionista: `admision` / `admision123`

## Dependencias y Variables de Entorno

### Dependencias Principales
- `fastapi`: Framework web para la API.
- `uvicorn`: Servidor ASGI para FastAPI.
- `psycopg2-binary`: Driver para PostgreSQL.
- `sqlalchemy`: ORM para bases de datos.
- `python-jose[cryptography]`: Para manejo de JWT.
- `passlib[bcrypt]`: Para hashing de contraseñas.
- `reportlab`: Para generación de PDFs.
- `python-multipart`: Para manejo de formularios.
- `weasyprint`: Alternativa para PDFs (no utilizada actualmente).

Ver `backend/requirements.txt` para la lista completa.

### Variables de Entorno
- `DATABASE_URL`: URL completa de conexión a la base de datos. Ejemplo: `postgresql://postgres:postgres@citus-coordinator:5432/historias`
- `JWT_SECRET`: Clave secreta para firmar tokens JWT. Debe ser segura y única.

### Información Técnica Adicional
- **Base de Datos**: Soporta tanto SQLite (desarrollo) como PostgreSQL con Citus (producción).
- **CORS**: Configurado para permitir acceso desde cualquier origen.
- **Logging**: Registra accesos y errores con nivel INFO.
- **PDF Generation**: Utiliza ReportLab para crear PDFs formateados con la historia clínica.
- **Validación**: Los documento_id deben ser numéricos para pacientes.
- **Seguridad**: Los pacientes solo pueden acceder a sus propias historias; los médicos solo actualizan notas específicas.