#!/usr/bin/env python3
"""
Script de verificación de la instalación y configuración del sistema
Verifica todos los prerequisitos antes de ejecutar el sistema
"""

import sys
import os
import subprocess
import socket
import importlib.util

class InstallationVerifier:
    """Verificador de instalación y configuración"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        
    def print_header(self, title):
        """Imprime un encabezado"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def check_python_version(self):
        """Verifica la versión de Python"""
        print("\n🐍 Verificando versión de Python...")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            self.errors.append(f"Python {version_str} no es compatible. Se requiere Python 3.7+")
            print(f"   ❌ Python {version_str} - Se requiere 3.7 o superior")
        else:
            self.success.append(f"Python {version_str}")
            print(f"   ✅ Python {version_str}")
    
    def check_required_files(self):
        """Verifica que existan los archivos necesarios"""
        print("\n📁 Verificando archivos del sistema...")
        
        required_files = [
            'server_main.py',
            'singleton_client.py',
            'observer_client.py'
        ]

        optional_files = [
            'test_suite.py',
            'dynamodb_setup.py',
            'demo_script.py',
            'requirements.txt'
        ]
        
        # Archivos requeridos
        for file in required_files:
            if os.path.exists(file):
                self.success.append(f"Archivo {file}")
                print(f"   ✅ {file}")
            else:
                self.errors.append(f"Archivo {file} no encontrado")
                print(f"   ❌ {file} - NO ENCONTRADO")
        
        # Archivos opcionales
        for file in optional_files:
            if os.path.exists(file):
                print(f"   ✅ {file}")
            else:
                self.warnings.append(f"Archivo opcional {file} no encontrado")
                print(f"   ⚠️  {file} - Opcional, no encontrado")
    
    def check_python_packages(self):
        """Verifica los paquetes Python necesarios"""
        print("\n📦 Verificando paquetes Python...")
        
        packages = {
            'boto3': 'Cliente AWS para Python',
            'botocore': 'Core de AWS SDK'
        }
        
        for package, description in packages.items():
            spec = importlib.util.find_spec(package)
            if spec is None:
                self.errors.append(f"Paquete {package} no instalado")
                print(f"   ❌ {package} - NO INSTALADO ({description})")
                print(f"      Instalar con: pip install {package}")
            else:
                try:
                    module = importlib.import_module(package)
                    version = getattr(module, '__version__', 'desconocida')
                    self.success.append(f"{package} v{version}")
                    print(f"   ✅ {package} v{version} - {description}")
                except:
                    self.success.append(package)
                    print(f"   ✅ {package} - {description}")
    
    def check_aws_credentials(self):
        """Verifica las credenciales de AWS"""
        print("\n🔑 Verificando configuración AWS...")
        
        # Verificar variables de entorno
        aws_vars = {
            'AWS_ACCESS_KEY_ID': 'Access Key ID',
            'AWS_SECRET_ACCESS_KEY': 'Secret Access Key',
            'AWS_REGION': 'Región AWS'
        }
        
        has_env_creds = True
        for var, description in aws_vars.items():
            value = os.environ.get(var)
            if value:
                if 'SECRET' in var:
                    print(f"   ✅ {var} - Configurado (oculto)")
                else:
                    print(f"   ✅ {var} = {value}")
            else:
                has_env_creds = False
                if var == 'AWS_REGION':
                    print(f"   ⚠️  {var} - No configurado (se usará us-east-1)")
                    self.warnings.append(f"{var} no configurado")
                else:
                    print(f"   ⚠️  {var} - NO CONFIGURADO")
        
        # Verificar archivo de credenciales
        aws_creds_file = os.path.expanduser('~/.aws/credentials')
        aws_config_file = os.path.expanduser('~/.aws/config')
        
        if not has_env_creds:
            if os.path.exists(aws_creds_file):
                print(f"   ℹ️  Archivo de credenciales encontrado: {aws_creds_file}")
                self.warnings.append("Usando credenciales del archivo ~/.aws/credentials")
            else:
                self.errors.append("No se encontraron credenciales AWS")
                print(f"   ❌ No se encontraron credenciales AWS")
                print("\n   📝 Configure sus credenciales con uno de estos métodos:")
                print("      1. Variables de entorno:")
                print("         export AWS_ACCESS_KEY_ID=your_key")
                print("         export AWS_SECRET_ACCESS_KEY=your_secret")
                print("      2. AWS CLI:")
                print("         aws configure")
    
    def check_dynamodb_connection(self):
        """Intenta conectar a DynamoDB"""
        print("\n🔌 Verificando conexión a DynamoDB...")
        
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Intentar conectar
            region = os.environ.get('AWS_REGION', 'us-east-1')
            dynamodb = boto3.resource('dynamodb', region_name=region)
            
            # Intentar listar tablas
            tables = list(dynamodb.tables.all())
            
            # Buscar nuestras tablas
            our_tables = ['CorporateData', 'CorporateLog']
            found_tables = []
            
            for table in tables:
                if table.name in our_tables:
                    found_tables.append(table.name)
            
            if len(found_tables) == 2:
                self.success.append("Tablas DynamoDB configuradas")
                print(f"   ✅ Conexión exitosa a DynamoDB")
                print(f"   ✅ Tablas encontradas: {', '.join(found_tables)}")
            elif len(found_tables) > 0:
                self.warnings.append(f"Solo se encontró: {', '.join(found_tables)}")
                print(f"   ⚠️  Conexión exitosa pero faltan tablas")
                print(f"   ⚠️  Encontradas: {', '.join(found_tables)}")
                print(f"   ℹ️  Ejecute: python dynamodb_setup.py")
            else:
                self.warnings.append("Tablas no encontradas en DynamoDB")
                print(f"   ⚠️  Conexión exitosa pero no se encontraron las tablas")
                print(f"   ℹ️  Ejecute: python dynamodb_setup.py")
                
        except NoCredentialsError:
            self.errors.append("No se pueden validar las credenciales AWS")
            print(f"   ❌ Error: Credenciales AWS no configuradas")
        except ClientError as e:
            self.errors.append(f"Error conectando a DynamoDB: {e}")
            print(f"   ❌ Error conectando a DynamoDB: {e}")
        except ImportError:
            self.errors.append("boto3 no está instalado")
            print(f"   ❌ boto3 no está instalado")
        except Exception as e:
            self.warnings.append(f"No se pudo verificar DynamoDB: {e}")
            print(f"   ⚠️  No se pudo verificar la conexión: {e}")
    
    def check_network_ports(self):
        """Verifica disponibilidad de puertos"""
        print("\n🌐 Verificando puertos de red...")
        
        test_ports = [8080, 8888, 9999]
        
        for port in test_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                self.warnings.append(f"Puerto {port} en uso")
                print(f"   ⚠️  Puerto {port} - EN USO")
            else:
                print(f"   ✅ Puerto {port} - Disponible")
    
    def check_permissions(self):
        """Verifica permisos de escritura"""
        print("\n📝 Verificando permisos...")
        
        # Intentar crear archivo temporal
        try:
            test_file = 'test_permissions.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            print(f"   ✅ Permisos de escritura en directorio actual")
        except:
            self.errors.append("Sin permisos de escritura en el directorio")
            print(f"   ❌ Sin permisos de escritura en el directorio actual")
    
    def print_summary(self):
        """Imprime el resumen de la verificación"""
        self.print_header("RESUMEN DE VERIFICACIÓN")
        
        total_checks = len(self.success) + len(self.warnings) + len(self.errors)
        
        print(f"\n📊 Resultados:")
        print(f"   ✅ Exitosos: {len(self.success)}")
        print(f"   ⚠️  Advertencias: {len(self.warnings)}")
        print(f"   ❌ Errores: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n" + "="*60)
        
        if self.errors:
            print("❌ El sistema NO está listo para ejecutarse")
            print("   Corrija los errores antes de continuar")
            return False
        elif self.warnings:
            print("⚠️  El sistema puede ejecutarse con limitaciones")
            print("   Revise las advertencias para mejor funcionamiento")
            return True
        else:
            print("✅ ¡El sistema está completamente listo!")
            print("   Puede ejecutar: python server_main.py")
            return True
    
    def run_verification(self):
        """Ejecuta todas las verificaciones"""
        self.print_header("VERIFICACIÓN DE INSTALACIÓN Y CONFIGURACIÓN")
        
        self.check_python_version()
        self.check_required_files()
        self.check_python_packages()
        self.check_aws_credentials()
        self.check_dynamodb_connection()
        self.check_network_ports()
        self.check_permissions()
        
        return self.print_summary()

def main():
    """Función principal"""
    verifier = InstallationVerifier()
    
    success = verifier.run_verification()
    
    if not success:
        sys.exit(1)
    
    print("\n💡 Próximos pasos:")
    print("   1. python dynamodb_setup.py        # Crear tablas en AWS")
    print("   2. python server_main.py           # Iniciar servidor")
    print("   3. python demo_script.py           # Ver demostración")
    print("\n")

if __name__ == '__main__':
    main()