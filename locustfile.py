"""
Archivo de pruebas de rendimiento con Locust para Clínica Mente Saludable
Prueba las funcionalidades principales: login, registro, gestión de pacientes y notas clínicas
"""

from locust import HttpUser, task, between, events
import json
import random
from datetime import datetime, timedelta

class ClinicaUser(HttpUser):
    """
    Usuario simulado para pruebas de rendimiento de la clínica
    """
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre requests
    host = "https://localhost:5000"
    
    def on_start(self):
        """
        Configuración inicial del usuario
        """
        # Deshabilitar verificación SSL para certificados autofirmados
        self.client.verify = False
        
        # Datos de prueba para el usuario
        self.test_username = f"terapeuta_test_{random.randint(1000, 9999)}"
        self.test_password = "Password123!"
        self.test_email = f"{self.test_username}@clinica.com"
        self.test_nombre = f"Dr. {self.test_username}"
        self.test_especialidad = "Psicología Clínica"
        
        # Intentar login, si falla, registrar nuevo usuario
        self.login_or_register()
    
    def login_or_register(self):
        """
        Intenta hacer login, si falla registra un nuevo usuario
        """
        # Intentar login primero
        login_data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        with self.client.post("/login", 
                             json=login_data, 
                             catch_response=True,
                             name="Login") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        response.success()
                        return
                except:
                    pass
            
            # Si login falla, registrar nuevo usuario
            self.register_user()
    
    def register_user(self):
        """
        Registra un nuevo usuario terapeuta
        """
        register_data = {
            "username": self.test_username,
            "email": self.test_email,
            "nombre_completo": self.test_nombre,
            "especialidad": self.test_especialidad,
            "password": self.test_password
        }
        
        with self.client.post("/register", 
                             json=register_data, 
                             catch_response=True,
                             name="Registro") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        response.success()
                        # Hacer login después del registro
                        self.login_user()
                    else:
                        response.failure(f"Error en registro: {data.get('error', 'Error desconocido')}")
                except Exception as e:
                    response.failure(f"Error parsing response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    def login_user(self):
        """
        Hace login con las credenciales del usuario
        """
        login_data = {
            "username": self.test_username,
            "password": self.test_password
        }
        
        with self.client.post("/login", 
                             json=login_data, 
                             catch_response=True,
                             name="Login Post-Registro") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        response.success()
                    else:
                        response.failure(f"Login falló: {data.get('error', 'Error desconocido')}")
                except Exception as e:
                    response.failure(f"Error parsing response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(3)
    def view_dashboard(self):
        """
        Ver el dashboard principal (alta frecuencia)
        """
        with self.client.get("/dashboard", 
                            catch_response=True,
                            name="Dashboard") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def get_pacientes(self):
        """
        Obtener lista de pacientes (frecuencia media)
        """
        with self.client.get("/api/pacientes", 
                            catch_response=True,
                            name="Obtener Pacientes") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'pacientes' in data:
                        response.success()
                    else:
                        response.failure("Respuesta inválida: falta 'pacientes'")
                except Exception as e:
                    response.failure(f"Error parsing response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def create_paciente(self):
        """
        Crear un nuevo paciente (baja frecuencia)
        """
        paciente_data = {
            "nombre_completo": f"Paciente Test {random.randint(1000, 9999)}",
            "fecha_nacimiento": "1990-01-01",
            "telefono": f"+569{random.randint(10000000, 99999999)}",
            "email": f"paciente{random.randint(1000, 9999)}@email.com",
            "direccion": "Av. Test 123, Santiago"
        }
        
        with self.client.post("/api/pacientes", 
                             json=paciente_data, 
                             catch_response=True,
                             name="Crear Paciente") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        response.success()
                    else:
                        response.failure(f"Error creando paciente: {data.get('error', 'Error desconocido')}")
                except Exception as e:
                    response.failure(f"Error parsing response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def get_notas(self):
        """
        Obtener lista de notas clínicas (frecuencia media)
        """
        with self.client.get("/api/notas", 
                            catch_response=True,
                            name="Obtener Notas") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'notas' in data:
                        response.success()
                    else:
                        response.failure("Respuesta inválida: falta 'notas'")
                except Exception as e:
                    response.failure(f"Error parsing response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def create_nota(self):
        """
        Crear una nueva nota clínica (baja frecuencia)
        """
        # Primero obtener pacientes para usar uno existente
        pacientes_response = self.client.get("/api/pacientes")
        if pacientes_response.status_code == 200:
            try:
                pacientes_data = pacientes_response.json()
                if pacientes_data.get('pacientes'):
                    paciente_id = pacientes_data['pacientes'][0]['id']
                else:
                    # Si no hay pacientes, crear uno primero
                    self.create_paciente()
                    pacientes_response = self.client.get("/api/pacientes")
                    if pacientes_response.status_code == 200:
                        pacientes_data = pacientes_response.json()
                        paciente_id = pacientes_data['pacientes'][0]['id']
                    else:
                        return
                else:
                    return
            except:
                return
        else:
            return
        
        # Crear nota clínica
        nota_data = {
            "paciente_id": paciente_id,
            "titulo": f"Sesión de terapia {random.randint(1, 100)}",
            "fecha_sesion": datetime.now().strftime('%Y-%m-%d'),
            "cuerpo": f"""
            Observaciones de la sesión:
            - Paciente presenta mejoría en el estado de ánimo
            - Se trabajó en técnicas de relajación
            - Tarea para la próxima sesión: ejercicios de respiración
            - Próxima cita programada para la siguiente semana
            """
        }
        
        with self.client.post("/api/notas", 
                             json=nota_data, 
                             catch_response=True,
                             name="Crear Nota Clínica") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        response.success()
                    else:
                        response.failure(f"Error creando nota: {data.get('error', 'Error desconocido')}")
                except Exception as e:
                    response.failure(f"Error parsing response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def view_login_page(self):
        """
        Ver página de login (baja frecuencia)
        """
        with self.client.get("/login", 
                            catch_response=True,
                            name="Página Login") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def view_register_page(self):
        """
        Ver página de registro (baja frecuencia)
        """
        with self.client.get("/register", 
                            catch_response=True,
                            name="Página Registro") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Configuración inicial de Locust
    """
    print("🚀 Iniciando pruebas de rendimiento para Clínica Mente Saludable")
    print("📊 Configuración:")
    print(f"   - Host: {environment.host}")
    print(f"   - Usuarios: {environment.runner.user_count if environment.runner else 'No configurado'}")
    print("🔒 Nota: Las pruebas usan certificados SSL autofirmados")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Evento al inicio de las pruebas
    """
    print("✅ Iniciando pruebas de rendimiento...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Evento al finalizar las pruebas
    """
    print("🏁 Pruebas de rendimiento finalizadas")
    print("📈 Revisa el reporte en la interfaz web de Locust")


# Configuración adicional para el archivo
"""
INSTRUCCIONES PARA EJECUTAR LAS PRUEBAS:

1. Instalar Locust:
   pip install locust

2. Iniciar la aplicación de la clínica:
   python app.py

3. Ejecutar las pruebas de rendimiento:
   locust -f locustfile.py --host=https://localhost:5000

4. Abrir navegador en: http://localhost:8089

5. Configurar las pruebas:
   - Number of users: 10-50
   - Spawn rate: 2-5 usuarios/segundo
   - Host: https://localhost:5000

6. Iniciar las pruebas y monitorear los resultados

ESCENARIOS DE PRUEBA INCLUIDOS:
- Login y registro de usuarios
- Visualización del dashboard
- Gestión de pacientes (listar y crear)
- Gestión de notas clínicas (listar y crear)
- Navegación por páginas principales

MÉTRICAS QUE SE MIDEN:
- Tiempo de respuesta (Response Time)
- Tasa de requests por segundo (RPS)
- Tasa de fallos (Failure Rate)
- Número de usuarios concurrentes
- Throughput general del sistema
""" 