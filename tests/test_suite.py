#!/usr/bin/env python3
"""
Test Suite Automatizado para el Sistema SingletonProxyObserver
Incluye pruebas de aceptación y verificación de patrones
"""

import unittest
import json
import socket
import subprocess
import time
import os
import tempfile
import threading
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Auto-load environment variables from config/.env
# This ensures AWS credentials are always available for tests
env_path = Path(__file__).parent.parent / 'config' / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment variables from {env_path}")

# Configuración de pruebas
TEST_PORT = 8080  # Puerto del servidor ya ejecutado
TEST_HOST = 'localhost'
SERVER_STARTUP_TIME = 2
AWS_REGION = 'us-east-1'
USE_EXTERNAL_SERVER = True  # Usar servidor externo ya ejecutado

class TestHelpers:
    """Funciones auxiliares para las pruebas"""
    
    @staticmethod
    def is_port_open(host: str, port: int) -> bool:
        """Verifica si un puerto está abierto"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    
    @staticmethod
    def create_temp_json(data: Dict) -> str:
        """Crea un archivo JSON temporal con los datos proporcionados"""
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        return path
    
    @staticmethod
    def send_tcp_request(host: str, port: int, data: Dict) -> Optional[Dict]:
        """Envía una petición TCP y retorna la respuesta"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            request = json.dumps(data) + '\n'
            sock.sendall(request.encode('utf-8'))
            
            response = b''
            while b'\n' not in response:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            
            if response:
                return json.loads(response.decode('utf-8').strip())
            return None
        except Exception as e:
            print(f"Error sending TCP request: {e}")
            return None

class TestServerPatterns(unittest.TestCase):
    """Pruebas para verificar la implementación correcta de los patrones"""

    server_process = None

    @classmethod
    def setUpClass(cls):
        """Inicia el servidor antes de las pruebas"""
        print("\n" + "="*60)
        print("INICIANDO PRUEBAS DE PATRONES")
        print("="*60)

        if USE_EXTERNAL_SERVER:
            # Verificar que el servidor externo esté disponible
            print(f"Usando servidor externo en puerto {TEST_PORT}")
            if not TestHelpers.is_port_open(TEST_HOST, TEST_PORT):
                raise RuntimeError(f"External server not running on port {TEST_PORT}")
            print("✓ Servidor externo detectado")
        else:
            # Iniciar servidor
            cls.server_process = subprocess.Popen(
                [sys.executable, '-m', 'singleton_proxy_observer.server.main', '-p', str(TEST_PORT), '-v'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Esperar a que el servidor inicie
            time.sleep(SERVER_STARTUP_TIME)

            if not TestHelpers.is_port_open(TEST_HOST, TEST_PORT):
                cls.tearDownClass()
                raise RuntimeError("Server failed to start")

    @classmethod
    def tearDownClass(cls):
        """Detiene el servidor después de las pruebas"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
    
    def test_01_singleton_pattern(self):
        """Verifica que se implemente correctamente el patrón Singleton"""
        print("\n→ Test: Verificación del patrón Singleton")

        # Importar las clases DAO desde el paquete
        from singleton_proxy_observer.dao import CorporateDataDAO, CorporateLogDAO
        from singleton_proxy_observer.patterns import SingletonMeta

        # Limpiar instancias previas para este test
        SingletonMeta._instances.clear()

        # Crear múltiples instancias
        dao1 = CorporateDataDAO()
        dao2 = CorporateDataDAO()
        log1 = CorporateLogDAO()
        log2 = CorporateLogDAO()

        # Verificar que son la misma instancia
        self.assertIs(dao1, dao2, "CorporateDataDAO no es un Singleton")
        self.assertIs(log1, log2, "CorporateLogDAO no es un Singleton")

        print("  ✓ Patrón Singleton verificado correctamente")
    
    def test_02_proxy_pattern(self):
        """Verifica que se implemente correctamente el patrón Proxy"""
        print("\n→ Test: Verificación del patrón Proxy")
        
        # El proxy debe interceptar las operaciones SET y notificar a observers
        # Primero, crear un observer
        observer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        observer_socket.settimeout(5)
        observer_socket.connect((TEST_HOST, TEST_PORT))
        
        # Suscribir el observer
        subscribe_request = {
            'UUID': 'test-observer-uuid',
            'ACTION': 'subscribe'
        }
        observer_socket.sendall(
            (json.dumps(subscribe_request) + '\n').encode('utf-8')
        )
        
        # Recibir confirmación
        response = observer_socket.recv(4096)
        self.assertIn(b'subscribed', response, "Observer subscription failed")
        
        # Ahora hacer un SET desde otro cliente
        set_data = {
            'UUID': 'test-client-uuid',
            'ACTION': 'set',
            'ID': 'test-proxy-item',
            'cp': '1234',
            'CUIT': '30-12345678-9'
        }
        
        response = TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, set_data)
        self.assertIsNotNone(response, "SET request failed")
        
        # El observer debería recibir una notificación (Proxy interceptando)
        observer_socket.settimeout(2)
        try:
            notification = observer_socket.recv(4096)
            self.assertIsNotNone(notification, "Proxy didn't notify observer")
            print("  ✓ Patrón Proxy verificado (interceptación y notificación)")
        except socket.timeout:
            self.fail("Proxy pattern not working - no notification received")
        finally:
            observer_socket.close()
    
    def test_03_observer_pattern(self):
        """Verifica que se implemente correctamente el patrón Observer"""
        print("\n→ Test: Verificación del patrón Observer")
        
        # Crear múltiples observers
        observers = []
        for i in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((TEST_HOST, TEST_PORT))
            
            subscribe = {
                'UUID': f'observer-{i}',
                'ACTION': 'subscribe'
            }
            sock.sendall((json.dumps(subscribe) + '\n').encode('utf-8'))
            
            # Verificar suscripción
            response = sock.recv(4096)
            self.assertIn(b'subscribed', response)
            observers.append(sock)
        
        # Hacer un cambio
        set_data = {
            'UUID': 'test-client',
            'ACTION': 'set',
            'ID': 'observer-test-item',
            'cp': '5678'
        }
        
        TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, set_data)
        
        # Todos los observers deberían recibir notificación
        notifications_received = 0
        for sock in observers:
            try:
                sock.settimeout(2)
                notification = sock.recv(4096)
                if notification:
                    notifications_received += 1
            except socket.timeout:
                pass
            finally:
                sock.close()
        
        self.assertEqual(
            notifications_received, 3,
            f"Observer pattern failed: only {notifications_received}/3 observers notified"
        )
        
        print("  ✓ Patrón Observer verificado (múltiples suscriptores)")

class TestFunctionalRequirements(unittest.TestCase):
    """Pruebas funcionales del sistema"""

    server_process = None

    @classmethod
    def setUpClass(cls):
        """Inicia el servidor antes de las pruebas"""
        print("\n" + "="*60)
        print("INICIANDO PRUEBAS FUNCIONALES")
        print("="*60)

        if USE_EXTERNAL_SERVER:
            # Verificar que el servidor externo esté disponible
            print(f"Usando servidor externo en puerto {TEST_PORT}")
            if not TestHelpers.is_port_open(TEST_HOST, TEST_PORT):
                raise RuntimeError(f"External server not running on port {TEST_PORT}")
            print("✓ Servidor externo detectado")
        else:
            cls.server_process = subprocess.Popen(
                [sys.executable, 'server_main.py', '-p', str(TEST_PORT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(SERVER_STARTUP_TIME)

            if not TestHelpers.is_port_open(TEST_HOST, TEST_PORT):
                cls.tearDownClass()
                raise RuntimeError("Server failed to start")

    @classmethod
    def tearDownClass(cls):
        """Detiene el servidor después de las pruebas"""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
    
    def test_01_happy_path_get(self):
        """Prueba el camino feliz para la acción GET"""
        print("\n→ Test: Camino feliz - GET")
        
        # Primero crear un item
        set_data = {
            'UUID': 'test-uuid',
            'ACTION': 'set',
            'ID': 'test-get-item',
            'cp': '3260',
            'CUIT': '30-70925411-8',
            'domicilio': '25 de Mayo 385',
            'localidad': 'Concepción del Uruguay'
        }
        TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, set_data)
        
        # Ahora hacer GET
        get_data = {
            'UUID': 'test-uuid',
            'ACTION': 'get',
            'ID': 'test-get-item'
        }
        
        response = TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, get_data)
        
        self.assertIsNotNone(response, "GET response is None")
        self.assertIn('data', response, "GET response missing 'data' field")
        self.assertEqual(
            response['data'].get('cp'), '3260',
            "GET returned incorrect data"
        )
        
        print("  ✓ GET ejecutado correctamente")
    
    def test_02_happy_path_set(self):
        """Prueba el camino feliz para la acción SET"""
        print("\n→ Test: Camino feliz - SET")
        
        set_data = {
            'UUID': 'test-uuid',
            'ACTION': 'set',
            'ID': 'test-set-item',
            'cp': '1234',
            'CUIT': '30-12345678-9',
            'telefono': '011-1234-5678'
        }
        
        response = TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, set_data)
        
        self.assertIsNotNone(response, "SET response is None")
        self.assertIn('data', response, "SET response missing 'data' field")
        self.assertEqual(
            response['data'].get('telefono'), '011-1234-5678',
            "SET didn't save data correctly"
        )
        
        print("  ✓ SET ejecutado correctamente")
    
    def test_03_happy_path_list(self):
        """Prueba el camino feliz para la acción LIST"""
        print("\n→ Test: Camino feliz - LIST")
        
        list_data = {
            'UUID': 'test-uuid',
            'ACTION': 'list'
        }
        
        response = TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, list_data)
        
        self.assertIsNotNone(response, "LIST response is None")
        self.assertIn('data', response, "LIST response missing 'data' field")
        self.assertIsInstance(
            response['data'], list,
            "LIST didn't return a list"
        )
        
        print("  ✓ LIST ejecutado correctamente")
    
    def test_04_malformed_arguments(self):
        """Prueba con argumentos malformados"""
        print("\n→ Test: Argumentos malformados")
        
        # JSON inválido
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((TEST_HOST, TEST_PORT))
        
        sock.sendall(b'invalid json\n')
        response = sock.recv(4096)
        sock.close()
        
        self.assertIn(b'error', response.lower(), "Server didn't handle invalid JSON")
        
        print("  ✓ Manejo correcto de JSON inválido")
    
    def test_05_missing_required_data(self):
        """Prueba con datos mínimos faltantes"""
        print("\n→ Test: Datos requeridos faltantes")
        
        # GET sin ID
        get_without_id = {
            'UUID': 'test-uuid',
            'ACTION': 'get'
        }
        
        response = TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, get_without_id)
        
        self.assertIsNotNone(response, "No response for GET without ID")
        self.assertIn('error', response, "GET without ID should return error")
        
        print("  ✓ Manejo correcto de datos faltantes")
    
    def test_06_server_down_handling(self):
        """Prueba manejo cuando el servidor está caído"""
        print("\n→ Test: Manejo de servidor caído")
        
        # Crear archivo temporal para el cliente
        client_data = {
            'UUID': 'test-uuid',
            'ACTION': 'get',
            'ID': 'test-item'
        }
        input_file = TestHelpers.create_temp_json(client_data)
        
        # Intentar conectar a puerto inexistente
        result = subprocess.run(
            [sys.executable, 'singleton_client.py',
             '-i', input_file, '-p', '55555'],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0, "Client should fail with server down")
        
        os.unlink(input_file)
        
        print("  ✓ Manejo correcto de servidor no disponible")
    
    def test_07_duplicate_server(self):
        """Prueba levantar dos servidores en el mismo puerto"""
        print("\n→ Test: Servidor duplicado")

        if USE_EXTERNAL_SERVER:
            # Con servidor externo, intentar levantar otro en el mismo puerto
            second_server = subprocess.Popen(
                [sys.executable, 'server_main.py', '-p', str(TEST_PORT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Esperar y verificar que falle
            return_code = second_server.wait(timeout=5)

            self.assertNotEqual(return_code, 0, "Second server should fail to start")
        else:
            # Ya hay un servidor en los tests, intentar uno más
            second_server = subprocess.Popen(
                [sys.executable, 'server_main.py', '-p', str(TEST_PORT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Esperar y verificar que falle
            return_code = second_server.wait(timeout=5)

            self.assertNotEqual(return_code, 0, "Second server should fail to start")

        print("  ✓ Prevención correcta de servidor duplicado")

class TestDynamoDBIntegration(unittest.TestCase):
    """Pruebas de integración con DynamoDB"""
    
    @classmethod
    def setUpClass(cls):
        """Configura la conexión a DynamoDB"""
        print("\n" + "="*60)
        print("INICIANDO PRUEBAS DE INTEGRACIÓN CON DYNAMODB")
        print("="*60)
        
        try:
            cls.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            cls.corporate_data_table = cls.dynamodb.Table('CorporateData')
            cls.corporate_log_table = cls.dynamodb.Table('CorporateLog')
        except Exception as e:
            print(f"  ⚠ No se puede conectar a DynamoDB: {e}")
            cls.dynamodb = None
    
    @unittest.skipIf(not os.environ.get('AWS_ACCESS_KEY_ID'), 
                     "AWS credentials not configured")
    def test_01_verify_tables_exist(self):
        """Verifica que las tablas existan en DynamoDB"""
        print("\n→ Test: Verificación de tablas DynamoDB")
        
        if not self.dynamodb:
            self.skipTest("DynamoDB connection not available")
        
        try:
            # Verificar CorporateData
            self.corporate_data_table.table_status
            print("  ✓ Tabla CorporateData existe")
            
            # Verificar CorporateLog
            self.corporate_log_table.table_status
            print("  ✓ Tabla CorporateLog existe")
            
        except ClientError as e:
            self.fail(f"Table verification failed: {e}")
    
    @unittest.skipIf(not os.environ.get('AWS_ACCESS_KEY_ID'),
                     "AWS credentials not configured")
    def test_02_verify_log_entries(self):
        """Verifica que se creen entradas en CorporateLog"""
        print("\n→ Test: Verificación de logs en DynamoDB")

        if not self.dynamodb:
            self.skipTest("DynamoDB connection not available")

        # Contar logs antes
        response = self.corporate_log_table.scan()
        logs_before = len(response.get('Items', []))

        # Hacer una operación en el servidor (externo o de prueba)
        TestHelpers.send_tcp_request(TEST_HOST, TEST_PORT, {
            'UUID': 'test-log-uuid',
            'ACTION': 'get',
            'ID': 'test-item'
        })

        # Esperar un momento para que se procese
        time.sleep(1)

        # Contar logs después
        response = self.corporate_log_table.scan()
        logs_after = len(response.get('Items', []))

        self.assertGreater(
            logs_after, logs_before,
            "No log entries created in CorporateLog"
        )

        print("  ✓ Logs creados correctamente en DynamoDB")

def run_tests():
    """Ejecuta todas las pruebas"""
    
    print("\n" + "="*60)
    print(" SUITE DE PRUEBAS AUTOMATIZADAS")
    print(" Sistema SingletonProxyObserver")
    print("="*60)
    
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar pruebas en orden
    suite.addTests(loader.loadTestsFromTestCase(TestServerPatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionalRequirements))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamoDBIntegration))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*60)
    print(" RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"  Pruebas ejecutadas: {result.testsRun}")
    print(f"  ✓ Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ✗ Fallos: {len(result.failures)}")
    print(f"  ⚠ Errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n  🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    else:
        print("\n  ❌ Algunas pruebas fallaron. Revise los detalles arriba.")
    
    print("="*60 + "\n")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())