from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import secrets
from datetime import datetime
import ssl

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clave maestra para cifrado (en producción debería estar en variables de entorno)
MASTER_KEY = b'clinica_mente_saludable_2024_seguridad_maxima'
salt = b'clinica_salt_2024'

# Generar clave de cifrado derivada
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = base64.urlsafe_b64encode(kdf.derive(MASTER_KEY))
cipher = Fernet(key)

# Modelos de base de datos
class Terapeuta(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nombre_completo = db.Column(db.String(120), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(120), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    terapeuta_id = db.Column(db.Integer, db.ForeignKey('terapeuta.id'), nullable=False)
    
    # Relación con el terapeuta
    terapeuta = db.relationship('Terapeuta', backref='pacientes')

class NotaClinica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo_cifrado = db.Column(db.Text, nullable=False)  # Cifrado
    cuerpo_cifrado = db.Column(db.Text, nullable=False)  # Cifrado
    fecha_sesion = db.Column(db.Date, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    terapeuta_id = db.Column(db.Integer, db.ForeignKey('terapeuta.id'), nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    
    # Relaciones
    terapeuta = db.relationship('Terapeuta', backref='notas')
    paciente = db.relationship('Paciente', backref='notas')
    
    def cifrar_titulo(self, titulo):
        """Cifra el título de la nota"""
        return cipher.encrypt(titulo.encode()).decode()
    
    def descifrar_titulo(self):
        """Descifra el título de la nota"""
        return cipher.decrypt(self.titulo_cifrado.encode()).decode()
    
    def cifrar_cuerpo(self, cuerpo):
        """Cifra el cuerpo de la nota"""
        return cipher.encrypt(cuerpo.encode()).decode()
    
    def descifrar_cuerpo(self):
        """Descifra el cuerpo de la nota"""
        return cipher.decrypt(self.cuerpo_cifrado.encode()).decode()

@login_manager.user_loader
def load_user(user_id):
    return Terapeuta.query.get(int(user_id))

# Rutas de autenticación
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        terapeuta = Terapeuta.query.filter_by(username=username).first()
        if terapeuta and terapeuta.check_password(password):
            login_user(terapeuta)
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'error': 'Credenciales inválidas'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        # Verificar si el usuario ya existe
        if Terapeuta.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'El nombre de usuario ya existe'})
        
        if Terapeuta.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'El email ya está registrado'})
        
        # Crear nuevo terapeuta
        terapeuta = Terapeuta(
            username=data['username'],
            email=data['email'],
            nombre_completo=data['nombre_completo'],
            especialidad=data['especialidad']
        )
        terapeuta.set_password(data['password'])
        
        db.session.add(terapeuta)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registro exitoso'})
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rutas principales
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# API para pacientes
@app.route('/api/pacientes', methods=['GET'])
@login_required
def obtener_pacientes():
    pacientes = Paciente.query.filter_by(terapeuta_id=current_user.id).all()
    return jsonify({
        'pacientes': [{
            'id': p.id,
            'nombre_completo': p.nombre_completo,
            'fecha_nacimiento': p.fecha_nacimiento.strftime('%Y-%m-%d'),
            'telefono': p.telefono,
            'email': p.email,
            'fecha_registro': p.fecha_registro.strftime('%Y-%m-%d %H:%M')
        } for p in pacientes]
    })

@app.route('/api/pacientes', methods=['POST'])
@login_required
def crear_paciente():
    data = request.get_json()
    
    paciente = Paciente(
        nombre_completo=data['nombre_completo'],
        fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date(),
        telefono=data.get('telefono', ''),
        email=data.get('email', ''),
        direccion=data.get('direccion', ''),
        terapeuta_id=current_user.id
    )
    
    db.session.add(paciente)
    db.session.commit()
    
    return jsonify({'success': True, 'id': paciente.id})

# API para notas clínicas
@app.route('/api/notas', methods=['GET'])
@login_required
def obtener_notas():
    notas = NotaClinica.query.filter_by(terapeuta_id=current_user.id).all()
    return jsonify({
        'notas': [{
            'id': n.id,
            'titulo': n.descifrar_titulo(),
            'fecha_sesion': n.fecha_sesion.strftime('%Y-%m-%d'),
            'fecha_creacion': n.fecha_creacion.strftime('%Y-%m-%d %H:%M'),
            'paciente_nombre': n.paciente.nombre_completo
        } for n in notas]
    })

@app.route('/api/notas', methods=['POST'])
@login_required
def crear_nota():
    data = request.get_json()
    
    nota = NotaClinica(
        titulo_cifrado=NotaClinica().cifrar_titulo(data['titulo']),
        cuerpo_cifrado=NotaClinica().cifrar_cuerpo(data['cuerpo']),
        fecha_sesion=datetime.strptime(data['fecha_sesion'], '%Y-%m-%d').date(),
        terapeuta_id=current_user.id,
        paciente_id=data['paciente_id']
    )
    
    db.session.add(nota)
    db.session.commit()
    
    return jsonify({'success': True, 'id': nota.id})

@app.route('/api/notas/<int:nota_id>', methods=['GET'])
@login_required
def obtener_nota(nota_id):
    nota = NotaClinica.query.filter_by(id=nota_id, terapeuta_id=current_user.id).first()
    if not nota:
        return jsonify({'error': 'Nota no encontrada'}), 404
    
    return jsonify({
        'id': nota.id,
        'titulo': nota.descifrar_titulo(),
        'cuerpo': nota.descifrar_cuerpo(),
        'fecha_sesion': nota.fecha_sesion.strftime('%Y-%m-%d'),
        'fecha_creacion': nota.fecha_creacion.strftime('%Y-%m-%d %H:%M'),
        'paciente_nombre': nota.paciente.nombre_completo
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Configurar SSL para HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    print("🚀 Iniciando servidor HTTPS para Clínica Mente Saludable...")
    print("🔒 Seguridad habilitada: TLS/HTTPS + Cifrado de datos")
    print("📱 Accede a: https://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=False)