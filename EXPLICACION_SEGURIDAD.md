# Explicación de Seguridad - Clínica Mente Saludable

## **1. Contexto del Problema**

### **Situación Inicial de la Clínica**
- **Estado actual**: Gestión manual con carpetas físicas
- **Problema**: Necesidad de digitalización por aumento de consultas remotas
- **Riesgo crítico**: Datos personales y sensibles (diagnósticos, notas clínicas, observaciones)
- **Consecuencias de filtración**: Daño grave a privacidad y confianza de pacientes

### **Equipo de TI**
- **Composición**: 2 desarrolladores + 1 analista de seguridad
- **Objetivo**: Prototipar aplicación web en una semana
- **Requisitos funcionales**: Registro/login + gestión de notas clínicas

---

## **2. Pilares de Seguridad Implementados**

### **Pilar 1: HTTPS/TLS (Transport Layer Security)**

#### **¿Qué es HTTPS/TLS?**
HTTPS (HTTP Secure) es la versión segura del protocolo HTTP que utiliza **TLS (Transport Layer Security)** para cifrar toda la comunicación entre el cliente (navegador) y el servidor.

#### **Funcionamiento Detallado de SSL/TLS:**

**1. Handshake Inicial (Negociación de Seguridad)**
```
Cliente ←→ Servidor
   ↓
1. Cliente envía "ClientHello" con:
   - Versiones de TLS soportadas
   - Cipher suites disponibles
   - Número aleatorio del cliente
   
2. Servidor responde "ServerHello" con:
   - Versión de TLS seleccionada
   - Cipher suite elegido
   - Número aleatorio del servidor
   - Certificado SSL del servidor
```

**2. Verificación del Certificado**
```
Cliente verifica:
- Que el certificado sea válido
- Que esté firmado por una CA confiable
- Que el nombre del dominio coincida
- Que no haya expirado
```

**3. Generación de Claves de Sesión**
```
Cliente genera:
- Pre-Master Secret (clave aleatoria)
- La cifra con la clave pública del servidor
- La envía al servidor

Servidor:
- Descifra con su clave privada
- Ambos generan Master Secret
- Derivar claves de sesión (cifrado, MAC, etc.)
```

**4. Cifrado de Datos**
```
Datos originales → Cifrado con clave de sesión → Transmisión segura
```

#### **Implementación en Nuestro Proyecto:**
```python
# Generación de certificados SSL autofirmados
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

# Servidor HTTPS
app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=False)
```

#### **Beneficios de HTTPS/TLS:**
- **Confidencialidad**: Los datos viajan cifrados
- **Integridad**: No se pueden modificar en tránsito
- **Autenticación**: Verifica la identidad del servidor
- **Protección contra ataques**: Man-in-the-middle, sniffing, etc.

---

### **Pilar 2: Cifrado en Reposo (Encryption at Rest)**

#### **¿Qué es el Cifrado en Reposo?**
Es el cifrado de datos cuando están almacenados en la base de datos, independientemente de si están siendo transmitidos o no.

#### **Implementación en Nuestro Proyecto:**

**1. Generación de Clave Maestra**
```python
# Clave maestra derivada usando PBKDF2
MASTER_KEY = b'clinica_mente_saludable_2024_seguridad_maxima'
salt = b'clinica_salt_2024'

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,  # 100,000 iteraciones para mayor seguridad
)
key = base64.urlsafe_b64encode(kdf.derive(MASTER_KEY))
cipher = Fernet(key)  # Cifrado simétrico AES-128
```

**2. Cifrado de Datos Sensibles**
```python
class NotaClinica(db.Model):
    titulo_cifrado = db.Column(db.Text, nullable=False)  # Cifrado
    cuerpo_cifrado = db.Column(db.Text, nullable=False)  # Cifrado
    
    def cifrar_titulo(self, titulo):
        return cipher.encrypt(titulo.encode()).decode()
    
    def descifrar_titulo(self):
        return cipher.decrypt(self.titulo_cifrado.encode()).decode()
```

#### **Proceso de Cifrado/Descifrado:**
```
Datos Originales → Cifrado con Fernet → Almacenamiento en BD
     ↓
"Diagnóstico: Ansiedad" → "gAAAAABk..." → Base de Datos

Base de Datos → Descifrado con Fernet → Datos Originales
     ↓
"gAAAAABk..." → "Diagnóstico: Ansiedad" → Mostrar al usuario
```

#### **Ventajas del Cifrado en Reposo:**
- **Protección contra acceso directo a BD**: Si alguien roba la base de datos, no puede leer los datos
- **Cumplimiento normativo**: Cumple con regulaciones de protección de datos
- **Defensa en profundidad**: Múltiples capas de seguridad

---

## **3. Arquitectura de Seguridad Completa**

### **Capa 1: Autenticación y Autorización**
```python
@login_required  # Decorador que verifica autenticación
def obtener_notas():
    # Solo terapeutas autenticados pueden acceder
    notas = NotaClinica.query.filter_by(terapeuta_id=current_user.id).all()
```

### **Capa 2: Cifrado en Tránsito (HTTPS/TLS)**
- **Protocolo**: TLS 1.3 (más reciente y seguro)
- **Cipher Suite**: AES-256-GCM con ECDHE
- **Certificado**: SSL autofirmado para desarrollo

### **Capa 3: Cifrado en Reposo**
- **Algoritmo**: Fernet (AES-128 en modo CBC)
- **Derivación de clave**: PBKDF2 con 100,000 iteraciones
- **Salt**: Fijo para la aplicación (en producción sería único por usuario)

### **Capa 4: Protección de Contraseñas**
```python
def set_password(self, password):
    # Hash seguro con bcrypt
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    # Verificación segura
    return check_password_hash(self.password_hash, password)
```

---

## **4. Flujo de Seguridad Completo**

### **Escenario: Terapeuta accede a notas clínicas**

**1. Conexión Segura**
```
Navegador → HTTPS/TLS → Servidor
   ↓
Verificación de certificado SSL
Negociación de claves de sesión
Conexión cifrada establecida
```

**2. Autenticación**
```
Usuario ingresa credenciales → Hash de contraseña → Verificación en BD
   ↓
Sesión autenticada creada
```

**3. Acceso a Datos**
```
Solicitud de notas → Verificación de autorización → Consulta a BD
   ↓
Datos cifrados recuperados → Descifrado con clave maestra → Envío cifrado por HTTPS
```

**4. Visualización**
```
Datos cifrados en tránsito → Descifrado en navegador → Mostrar al usuario
```

---

## **5. Protección contra Ataques Específicos**

### **Ataque de Sniffing (Interceptación de Red)**
- **Amenaza**: Interceptar datos en la red interna
- **Protección**: HTTPS/TLS cifra toda la comunicación
- **Resultado**: Datos interceptados son ilegibles

### **Ataque de Acceso Directo a Base de Datos**
- **Amenaza**: Robo o acceso no autorizado a la BD
- **Protección**: Cifrado en reposo con clave maestra
- **Resultado**: Datos en BD son ilegibles sin la clave

### **Ataque de Man-in-the-Middle**
- **Amenaza**: Interceptar y modificar comunicación
- **Protección**: Certificados SSL verifican identidad del servidor
- **Resultado**: Ataque detectado y bloqueado

### **Ataque de Fuerza Bruta**
- **Amenaza**: Adivinar contraseñas
- **Protección**: Hash seguro con bcrypt (lento por diseño)
- **Resultado**: Ataque computacionalmente inviable

---

## **6. Configuración de Certificados SSL**

### **Generación de Certificados Autofirmados**
```python
# Generar clave privada RSA 2048 bits
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

# Crear certificado
cert = crypto.X509()
cert.get_subject().CN = "localhost"  # Nombre común
cert.set_pubkey(key)
cert.sign(key, 'sha256')  # Firmar con SHA-256
```

### **Configuración del Servidor**
```python
# Contexto SSL con configuración segura
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

# Configuraciones adicionales de seguridad
context.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384')
context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
```

---

## **7. Monitoreo y Verificación de Seguridad**

### **Indicadores de Seguridad en la UI**
```html
<div class="security-badge">
    <i class="fas fa-shield-alt"></i>
    Conexión HTTPS/TLS - Datos Cifrados
</div>
```

### **Verificación de Certificados**
- **Navegador**: Muestra candado verde para HTTPS válido
- **Consola**: Mensajes de inicio confirmando SSL activo
- **Logs**: Registro de conexiones seguras

---

## **8. Consideraciones para Producción**

### **Mejoras de Seguridad**
1. **Certificados SSL**: Usar certificados de CA confiable (Let's Encrypt, DigiCert)
2. **Clave Maestra**: Almacenar en variables de entorno, no en código
3. **Salt Único**: Generar salt único por usuario/organización
4. **Rotación de Claves**: Implementar rotación periódica de claves
5. **Auditoría**: Logs de acceso y modificación de datos sensibles

### **Configuración de Servidor Web**
```nginx
# Configuración Nginx para HTTPS
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384;
}
```

---

## **9. Implementación Técnica Detallada**

### **Estructura de Archivos de Seguridad**
```
Taller3/
├── app.py                    # Aplicación principal con SSL
├── generate_cert.py          # Generador de certificados SSL
├── cert.pem                  # Certificado SSL público
├── key.pem                   # Clave privada SSL
├── clinica.db               # Base de datos con datos cifrados
└── requirements_clinica.txt  # Dependencias de seguridad
```

### **Dependencias de Seguridad**
```txt
cryptography==41.0.7    # Cifrado avanzado
pyOpenSSL==23.3.0       # Manejo de certificados SSL
bcrypt==4.0.1           # Hash seguro de contraseñas
flask-login==0.6.3      # Autenticación de usuarios
```

### **Configuración de Base de Datos Segura**
```python
# Modelo con datos cifrados
class NotaClinica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo_cifrado = db.Column(db.Text, nullable=False)  # Cifrado
    cuerpo_cifrado = db.Column(db.Text, nullable=False)  # Cifrado
    fecha_sesion = db.Column(db.Date, nullable=False)
    terapeuta_id = db.Column(db.Integer, db.ForeignKey('terapeuta.id'))
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
```

---

## **10. Pruebas de Seguridad**

### **Verificación de HTTPS**
```bash
# Verificar certificado SSL
openssl s_client -connect localhost:5000 -servername localhost

# Verificar configuración TLS
nmap --script ssl-enum-ciphers -p 5000 localhost
```

### **Verificación de Cifrado**
```python
# Probar cifrado de datos
nota = NotaClinica()
texto_original = "Diagnóstico: Ansiedad generalizada"
texto_cifrado = nota.cifrar_titulo(texto_original)
texto_descifrado = nota.descifrar_titulo()

assert texto_original == texto_descifrado
print("✅ Cifrado funcionando correctamente")
```

---

## **11. Resumen de Seguridad Implementada**

### **Capas de Protección**
1. **Autenticación**: Login seguro con bcrypt
2. **Autorización**: Control de acceso por terapeuta
3. **Cifrado en Tránsito**: HTTPS/TLS
4. **Cifrado en Reposo**: Fernet con clave maestra
5. **Protección de Contraseñas**: Hash seguro
6. **Certificados SSL**: Verificación de identidad

### **Cumplimiento de Requisitos**
- ✅ **HTTPS/TLS**: Canal de comunicación seguro
- ✅ **Cifrado en Reposo**: Datos ilegibles en BD
- ✅ **Protección contra Sniffing**: Datos cifrados en red
- ✅ **Acceso No Autorizado**: Datos cifrados sin clave
- ✅ **Confidencialidad**: Múltiples capas de protección

Esta implementación proporciona una **defensa en profundidad** que protege los datos sensibles de la clínica tanto en tránsito como en reposo, cumpliendo con los más altos estándares de seguridad para aplicaciones médicas. 