# Pruebas de Rendimiento - Clínica Mente Saludable

## 📊 Descripción

Este archivo contiene las pruebas de rendimiento para la aplicación web de la Clínica Mente Saludable utilizando **Locust**, una herramienta de testing de carga escrita en Python.

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias
```bash
pip install -r requirements_clinica.txt
```

### 2. Generar Certificados SSL
```bash
python generate_cert.py
```

### 3. Iniciar la Aplicación
```bash
python app.py
```

### 4. Ejecutar Pruebas de Rendimiento
```bash
locust -f locustfile.py --host=https://localhost:5000
```

## 🌐 Interfaz Web de Locust

Una vez ejecutado Locust, abre tu navegador en:
```
http://localhost:8089
```

## ⚙️ Configuración de Pruebas

### Parámetros Recomendados:
- **Number of users**: 10-50 usuarios
- **Spawn rate**: 2-5 usuarios por segundo
- **Host**: https://localhost:5000

### Escenarios de Prueba:
1. **Carga Ligera**: 10 usuarios, 2 usuarios/seg
2. **Carga Media**: 25 usuarios, 3 usuarios/seg
3. **Carga Alta**: 50 usuarios, 5 usuarios/seg

## 📈 Métricas que se Miden

### Tiempo de Respuesta
- **Response Time**: Tiempo promedio de respuesta
- **Min/Max Response Time**: Tiempos mínimo y máximo
- **Percentiles**: P50, P90, P95, P99

### Throughput
- **Requests per second (RPS)**: Peticiones por segundo
- **Total Requests**: Número total de peticiones
- **Failure Rate**: Tasa de fallos

### Usuarios
- **Number of users**: Usuarios concurrentes
- **User count**: Conteo de usuarios activos

## 🔍 Funcionalidades Probadas

### Autenticación (Frecuencia: Media)
- ✅ Login de usuarios
- ✅ Registro de nuevos terapeutas
- ✅ Verificación de credenciales

### Dashboard (Frecuencia: Alta)
- ✅ Carga de página principal
- ✅ Estadísticas en tiempo real
- ✅ Navegación entre secciones

### Gestión de Pacientes (Frecuencia: Media)
- ✅ Listar pacientes
- ✅ Crear nuevos pacientes
- ✅ Validación de datos

### Notas Clínicas (Frecuencia: Media)
- ✅ Listar notas clínicas
- ✅ Crear nuevas notas
- ✅ Cifrado/descifrado de datos

### Páginas Estáticas (Frecuencia: Baja)
- ✅ Página de login
- ✅ Página de registro

## 📊 Interpretación de Resultados

### Indicadores de Rendimiento Óptimo:
- **Response Time**: < 500ms para operaciones simples
- **Response Time**: < 2s para operaciones complejas
- **Failure Rate**: < 1%
- **RPS**: > 10 requests/segundo

### Posibles Cuellos de Botella:
1. **Base de Datos**: Consultas lentas
2. **Cifrado**: Operaciones de cifrado/descifrado
3. **SSL/TLS**: Overhead de conexiones seguras
4. **Memoria**: Uso excesivo de RAM

## 🔧 Configuración Avanzada

### Ejecutar Pruebas desde Línea de Comandos:
```bash
# Prueba rápida (30 segundos, 10 usuarios)
locust -f locustfile.py --host=https://localhost:5000 --users=10 --spawn-rate=2 --run-time=30s

# Prueba de carga (5 minutos, 50 usuarios)
locust -f locustfile.py --host=https://localhost:5000 --users=50 --spawn-rate=5 --run-time=5m

# Prueba de estrés (10 minutos, 100 usuarios)
locust -f locustfile.py --host=https://localhost:5000 --users=100 --spawn-rate=10 --run-time=10m
```

### Exportar Resultados:
```bash
# Exportar a CSV
locust -f locustfile.py --host=https://localhost:5000 --headless --users=10 --spawn-rate=2 --run-time=1m --csv=resultados

# Exportar a HTML
locust -f locustfile.py --host=https://localhost:5000 --headless --users=10 --spawn-rate=2 --run-time=1m --html=reporte.html
```

## 🚨 Solución de Problemas

### Error de Certificado SSL:
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solución**: El archivo `locustfile.py` ya está configurado para ignorar certificados autofirmados.

### Error de Conexión:
```
Connection refused
```
**Solución**: Asegúrate de que la aplicación esté ejecutándose en `https://localhost:5000`

### Error de Importación:
```
ModuleNotFoundError: No module named 'locust'
```
**Solución**: Instala Locust con `pip install locust`

## 📋 Checklist de Pruebas

### Antes de Ejecutar:
- [ ] Aplicación ejecutándose en HTTPS
- [ ] Certificados SSL generados
- [ ] Locust instalado
- [ ] Base de datos inicializada

### Durante las Pruebas:
- [ ] Monitorear uso de CPU
- [ ] Monitorear uso de memoria
- [ ] Verificar logs de la aplicación
- [ ] Observar tasa de errores

### Después de las Pruebas:
- [ ] Revisar métricas de rendimiento
- [ ] Identificar cuellos de botella
- [ ] Generar reporte de resultados
- [ ] Documentar hallazgos

## 📊 Ejemplo de Reporte

### Resultados Típicos (10 usuarios, 2 minutos):

| Endpoint | Avg Response Time | Min Response Time | Max Response Time | RPS | Failure Rate |
|----------|------------------|-------------------|-------------------|-----|--------------|
| Dashboard | 245ms | 120ms | 890ms | 15.2 | 0% |
| Login | 180ms | 95ms | 450ms | 8.1 | 0% |
| Obtener Pacientes | 320ms | 150ms | 1200ms | 12.3 | 0% |
| Crear Paciente | 450ms | 280ms | 1800ms | 4.2 | 0% |
| Obtener Notas | 380ms | 200ms | 1500ms | 10.1 | 0% |
| Crear Nota | 520ms | 350ms | 2200ms | 3.8 | 0% |

### Análisis:
- ✅ **Rendimiento General**: Excelente
- ✅ **Tiempo de Respuesta**: Dentro de parámetros aceptables
- ✅ **Tasa de Fallos**: 0% (sin errores)
- ✅ **Throughput**: Suficiente para carga esperada

## 🔒 Consideraciones de Seguridad

### Durante las Pruebas:
- Las pruebas usan certificados SSL autofirmados
- Los datos de prueba son ficticios
- No se afectan datos reales de pacientes
- Las operaciones de cifrado se mantienen activas

### Recomendaciones:
- Ejecutar pruebas en entorno de desarrollo
- No usar datos reales de pacientes
- Monitorear logs de seguridad
- Verificar que el cifrado funcione correctamente

## 📞 Soporte

Si encuentras problemas con las pruebas:

1. **Verificar logs**: Revisa la consola de la aplicación
2. **Comprobar conectividad**: Asegúrate de que HTTPS funcione
3. **Revisar certificados**: Regenera si es necesario
4. **Consultar documentación**: Revisa la documentación de Locust

---

**Nota**: Estas pruebas están diseñadas para evaluar el rendimiento de la aplicación en condiciones realistas de uso, incluyendo todas las medidas de seguridad implementadas (HTTPS/TLS y cifrado de datos). 