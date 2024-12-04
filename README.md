Aquí tienes un archivo `README.md` para documentar tu proyecto:

---

# **Automatización de Redes**

Este proyecto es una aplicación web desarrollada con Flask para automatizar configuraciones de red en dispositivos mediante protocolos de enrutamiento dinámico. La aplicación permite gestionar dispositivos, configurar protocolos como RIPv2, EIGRP, OSPF y BGP, y aplicar estas configuraciones automáticamente utilizando Nornir.

## **Características**
- Gestión de dispositivos de red:
  - Agregar, editar y eliminar dispositivos.
  - Asignar credenciales para cada dispositivo.
- Configuración automática de protocolos de enrutamiento:
  - **RIPv2**: Redes a anunciar.
  - **EIGRP**: Número de sistema autónomo (AS) y redes a anunciar.
  - **OSPF**: ID de proceso, redes, máscaras wildcard y áreas.
  - **BGP**: Número de AS, redes y vecinos.
- Generación dinámica de inventario para Nornir basado en los dispositivos registrados en la base de datos.
- Uso de plantillas Jinja2 para la generación de configuraciones.

---

## **Requisitos Previos**

### **Software**
- Python 3.8 o superior.
- PostgreSQL para la base de datos.
- Un entorno virtual (recomendado).

### **Instalación de Dependencias**
Todas las dependencias necesarias están listadas en el archivo `requirements.txt`. Instálalas ejecutando:

```bash
pip install -r requirements.txt
```

---

## **Configuración del Proyecto**

### **Base de Datos**
Ejecuta el siguiente script SQL para crear las tablas necesarias:

```sql
CREATE TABLE device (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hostname VARCHAR(100) NOT NULL,
    model VARCHAR(50),
    brand VARCHAR(50),
    connection_port INTEGER DEFAULT 22,
    protocol VARCHAR(10) DEFAULT 'SSH',
    platform VARCHAR(50) DEFAULT 'generic'
);

CREATE TABLE device_credentials (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES device(id) ON DELETE CASCADE,
    username VARCHAR(50) NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE routing_protocol (
    id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES device(id) ON DELETE CASCADE,
    protocol VARCHAR(10) NOT NULL,
    config_data JSONB NOT NULL
);
```

### **Archivo de Configuración**
Crea un archivo `config.py` en el directorio principal del proyecto:

```python
class Config:
    SECRET_KEY = 'admin'
    SQLALCHEMY_DATABASE_URI = 'postgresql://usuario:contraseña@localhost/nombre_base_datos'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### **Plantillas Jinja2**
Crea las plantillas de configuración para los protocolos en el directorio `templates-jinja/`. Ejemplo de la plantilla para OSPF:

```jinja2
router ospf {{ ospf.process_id }}
{% for entry in ospf_networks %}
 network {{ entry.network }} {{ entry.wildcard }} area {{ entry.area }}
{% endfor %}
```

---

## **Ejecución del Proyecto**

### **Iniciar la Aplicación**
1. Activa tu entorno virtual (opcional).
2. Inicia la aplicación Flask:

   ```bash
   python app.py
   ```

3. Accede a la aplicación en tu navegador en [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## **Uso de la Aplicación**

### **1. Gestión de Dispositivos**
- Desde la sección **Dispositivos**, puedes:
  - Agregar nuevos dispositivos.
  - Editar o eliminar dispositivos existentes.

### **2. Credenciales**
- Asigna credenciales específicas a cada dispositivo.

### **3. Configuración de Protocolos**
- Asigna protocolos como RIPv2, EIGRP, OSPF o BGP a cada dispositivo.
- Ingresa los datos necesarios para la configuración, como redes, áreas o vecinos.

### **4. Generar Inventario**
- Crea un inventario dinámico (`hosts.yaml`) para Nornir basado en los dispositivos registrados.

### **5. Aplicación de Configuración**
- Las configuraciones generadas se envían automáticamente a los dispositivos utilizando Nornir y Netmiko.

---

## **Estructura del Proyecto**

```
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── device_list.html
│   │   ├── add_device.html
│   │   ├── edit_device.html
│   │   ├── assign_protocol.html
│   │   ├── assign_credentials.html
│   ├── static/
│   │   ├── style.css
├── templates-jinja/
│   ├── ospf_template.jinja2
│   ├── rip_template.jinja2
│   ├── eigrp_template.jinja2
│   ├── bgp_template.jinja2
├── requirements.txt
├── config.py
├── README.md
```

---

## **Tecnologías Usadas**

- **Backend**: Flask, SQLAlchemy, Nornir, Netmiko.
- **Frontend**: HTML, CSS, Bootstrap.
- **Base de Datos**: PostgreSQL.
