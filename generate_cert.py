from OpenSSL import crypto
import os

def generate_self_signed_cert():
    """Genera un certificado SSL autofirmado para desarrollo"""
    
    # Generar clave privada
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Crear certificado
    cert = crypto.X509()
    cert.get_subject().C = "CL"
    cert.get_subject().ST = "Santiago"
    cert.get_subject().L = "Santiago"
    cert.get_subject().O = "Clínica Mente Saludable"
    cert.get_subject().OU = "TI"
    cert.get_subject().CN = "localhost"
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Válido por 1 año
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    
    # Firmar el certificado
    cert.sign(key, 'sha256')
    
    # Guardar certificado y clave
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    print("✅ Certificados SSL generados exitosamente:")
    print("   - cert.pem (certificado)")
    print("   - key.pem (clave privada)")
    print("🔒 HTTPS habilitado para desarrollo")

if __name__ == "__main__":
    generate_self_signed_cert() 