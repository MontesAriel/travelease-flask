# 🌍 TravelEase - Agencia de Viajes

**TravelEase** es una plataforma web de reservas de viajes que permite a los usuarios buscar destinos turísticos, reservar vuelos y alojamientos, y realizar pagos en línea.  
El proyecto fue desarrollado como trabajo práctico integrador para la materia **Comunicaciones y Redes**.

---

## 🚀 Tecnologías Utilizadas

| Componente | Tecnología |
|-------------|-------------|
| **Backend** | Python 3.12 + Flask |
| **Base de Datos** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Frontend** | HTML, CSS (Bootstrap 5.3), JS |
| **Autenticación** | Flask-Bcrypt + Sesiones |
| **Versionado** | Git + GitHub |
| **Entorno virtual** | venv (.venv) |

---

## ⚙️ Instalación y Ejecución

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/usuario/travelease-flask.git
cd travelease-flask
```
### 2️⃣ Crear entorno virtual
```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3️⃣ Configurar la base de datos
```bash
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "travelease",
    "user": "postgres",
    "password": "admin"
}
```

### 4️⃣ Inicializar la base de datos:
```bash
flask shell
>>> from config import db
>>> from models.model import *
>>> db.create_all()
```

### 5️⃣ Ejecutar el proyecto
```bash
flask run
```

#### 💳 Flujo de Reserva
```bash
El usuario explora destinos desde la página principal (/).

Al seleccionar un destino, puede ver detalles, itinerarios, vuelos y alojamientos.

Si inicia sesión, puede crear una reserva seleccionando fechas y pasajeros.

Se genera una reserva pendiente y el usuario pasa al flujo de pago.

Al completar el pago, se actualiza el estado de la reserva y se muestra la página de confirmación.
```

#### 🧩 Panel Administrativo
```bash
Ruta principal: /admin

Funciones disponibles:

📍 CRUD de Destinos

✈️ CRUD de Vuelos (en desarrollo)

🏨 CRUD de Alojamientos (en desarrollo)
```

#### 🏷️ Versionado
```bash
Versión	Descripción
v1.0.0	Creación del proyecto y estructura inicial
v1.1.0	Flujo completo de reserva y pago
v1.2.0	Estilo visual TravelEase + íconos Bootstrap + documentación actualizada
```

#### ✅ Cumplido
```bash
- Creación de backlog (Trello)  
- Diagramas DFD, DER y Clases  
- Story Mapping con MVP definido  
- Proyecto en GitHub con estructura inicial  
- Configuración de Flask + PostgreSQL  
- Implementación de modelos ORM  
- Flujo completo de:
  - Registro / Login
  - Reserva
  - Pago
- CRUD de destinos (panel admin)
- Documentación técnica y README actualizados
```

#### 🔧 En Progreso
```bash
- CRUD de vuelos, alojamientos, pagos, reservas, usuarios, aeropuertos, aerolineas...
```

#### ⏳ Pendiente
```bash
- Web scraping para comparación de precios
- Envío de correos de confirmación
```