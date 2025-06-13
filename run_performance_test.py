#!/usr/bin/env python3
"""
Script para ejecutar pruebas de rendimiento automáticamente
Genera reportes de rendimiento para la Clínica Mente Saludable
"""

import subprocess
import time
import os
import sys
from datetime import datetime

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado")
            return True
        else:
            print(f"❌ Error en {description}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {str(e)}")
        return False

def check_application_running():
    """Verifica si la aplicación está ejecutándose"""
    try:
        import requests
        response = requests.get("https://localhost:5000", verify=False, timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_test_report():
    """Genera un reporte de las pruebas ejecutadas"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"performance_report_{timestamp}.md"
    
    report_content = f"""# Reporte de Rendimiento - Clínica Mente Saludable

## 📊 Información General
- **Fecha de Prueba**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Aplicación**: Clínica Mente Saludable
- **Herramienta**: Locust
- **Protocolo**: HTTPS/TLS

## 🎯 Objetivos de las Pruebas
- Evaluar rendimiento bajo carga
- Verificar funcionamiento con SSL/TLS
- Probar operaciones de cifrado/descifrado
- Medir tiempos de respuesta

## 📈 Métricas Esperadas
- **Tiempo de respuesta**: < 500ms (operaciones simples)
- **Tiempo de respuesta**: < 2s (operaciones complejas)
- **Tasa de fallos**: < 1%
- **Throughput**: > 10 RPS

## 🔧 Configuración de Pruebas
- **Usuarios**: 10-50 concurrentes
- **Duración**: 2-5 minutos
- **Escenarios**: Login, Dashboard, Pacientes, Notas

## 📋 Checklist de Verificación

### ✅ Seguridad
- [ ] HTTPS/TLS habilitado
- [ ] Certificados SSL generados
- [ ] Cifrado de datos activo
- [ ] Autenticación funcionando

### ✅ Funcionalidad
- [ ] Login de usuarios
- [ ] Registro de terapeutas
- [ ] Gestión de pacientes
- [ ] Notas clínicas
- [ ] Dashboard

### ✅ Rendimiento
- [ ] Tiempos de respuesta aceptables
- [ ] Sin errores de conexión
- [ ] Throughput adecuado
- [ ] Uso de recursos controlado

## 🚀 Instrucciones para Ejecutar Pruebas

### 1. Preparar el Entorno
```bash
# Instalar dependencias
pip install -r requirements_clinica.txt

# Generar certificados SSL
python generate_cert.py
```

### 2. Iniciar la Aplicación
```bash
# Ejecutar en una terminal
python app.py
```

### 3. Ejecutar Pruebas de Rendimiento
```bash
# Prueba básica
locust -f locustfile.py --host=https://localhost:5000

# Prueba automática (headless)
locust -f locustfile.py --host=https://localhost:5000 --headless --users=10 --spawn-rate=2 --run-time=2m --csv=resultados
```

### 4. Ver Resultados
- Abrir navegador en: http://localhost:8089
- Revisar métricas en tiempo real
- Exportar reportes en formato CSV/HTML

## 🔍 Análisis de Resultados

### Indicadores de Éxito
- ✅ Tiempo de respuesta < 500ms
- ✅ Tasa de fallos < 1%
- ✅ Throughput > 10 RPS
- ✅ Sin errores de SSL/TLS

### Posibles Problemas
- ⚠️ Tiempos de respuesta altos
- ⚠️ Errores de certificados SSL
- ⚠️ Fallos de autenticación
- ⚠️ Problemas de cifrado

## 📞 Soporte Técnico

Si encuentras problemas:
1. Verificar que la aplicación esté ejecutándose
2. Comprobar certificados SSL
3. Revisar logs de la aplicación
4. Consultar documentación de Locust

---
*Reporte generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Reporte generado: {report_file}")
    return report_file

def main():
    """Función principal del script"""
    print("🚀 Iniciando pruebas de rendimiento para Clínica Mente Saludable")
    print("=" * 60)
    
    # Verificar si la aplicación está ejecutándose
    print("🔍 Verificando estado de la aplicación...")
    if not check_application_running():
        print("❌ La aplicación no está ejecutándose en https://localhost:5000")
        print("💡 Ejecuta 'python app.py' en otra terminal primero")
        return False
    
    print("✅ Aplicación detectada y ejecutándose")
    
    # Generar reporte
    report_file = generate_test_report()
    
    # Ejecutar pruebas de rendimiento
    print("\n📊 Ejecutando pruebas de rendimiento...")
    
    # Prueba 1: Carga ligera
    print("\n🔵 Prueba 1: Carga Ligera (10 usuarios, 2 minutos)")
    command1 = "locust -f locustfile.py --host=https://localhost:5000 --headless --users=10 --spawn-rate=2 --run-time=2m --csv=test_light"
    if run_command(command1, "Prueba de carga ligera"):
        print("✅ Prueba de carga ligera completada")
    
    # Prueba 2: Carga media
    print("\n🟡 Prueba 2: Carga Media (25 usuarios, 3 minutos)")
    command2 = "locust -f locustfile.py --host=https://localhost:5000 --headless --users=25 --spawn-rate=3 --run-time=3m --csv=test_medium"
    if run_command(command2, "Prueba de carga media"):
        print("✅ Prueba de carga media completada")
    
    # Prueba 3: Carga alta
    print("\n🔴 Prueba 3: Carga Alta (50 usuarios, 2 minutos)")
    command3 = "locust -f locustfile.py --host=https://localhost:5000 --headless --users=50 --spawn-rate=5 --run-time=2m --csv=test_heavy"
    if run_command(command3, "Prueba de carga alta"):
        print("✅ Prueba de carga alta completada")
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas de rendimiento completadas")
    print(f"📄 Reporte generado: {report_file}")
    print("📊 Revisa los archivos CSV para análisis detallado")
    print("🌐 Para interfaz web: locust -f locustfile.py --host=https://localhost:5000")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1) 