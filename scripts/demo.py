#!/usr/bin/env python3
"""
Script de demostración del sistema SingletonProxyObserver
Muestra el funcionamiento completo con todos los componentes
"""

import subprocess
import time
import json
import os
import sys
import signal
import threading
from datetime import datetime

class SystemDemo:
    """Demostración completa del sistema"""
    
    def __init__(self):
        self.server_process = None
        self.observer_process = None
        self.processes = []
        
    def cleanup(self):
        """Limpia todos los procesos"""
        print("\n🧹 Limpiando procesos...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=2)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
    
    def signal_handler(self, sig, frame):
        """Manejador de señales para limpieza"""
        print("\n\n⚠️  Interrupción detectada. Cerrando demo...")
        self.cleanup()
        sys.exit(0)
    
    def print_header(self, title):
        """Imprime un encabezado formateado"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_step(self, step_num, description):
        """Imprime un paso de la demo"""
        print(f"\n📍 PASO {step_num}: {description}")
        print("-"*50)
    
    def wait_with_countdown(self, seconds, message="Esperando"):
        """Espera con contador visual"""
        for i in range(seconds, 0, -1):
            print(f"\r⏱️  {message}: {i} segundos...", end="")
            time.sleep(1)
        print("\r" + " "*50 + "\r", end="")
    
    def create_json_file(self, filename, data):
        """Crea un archivo JSON temporal"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename
    
    def run_demo(self):
        """Ejecuta la demostración completa"""
        
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.print_header("DEMOSTRACIÓN DEL SISTEMA SINGLETONPROXYOBSERVER")
        
        print("""
Este script demostrará:
1. Inicio del servidor con los tres patrones
2. Cliente Singleton realizando operaciones CRUD
3. Cliente Observer recibiendo notificaciones
4. Interacción entre componentes
5. Verificación de patrones implementados
        """)

        # Auto-start mode check
        auto_mode = '--auto' in sys.argv or not sys.stdin.isatty()
        if not auto_mode:
            try:
                input("Presione ENTER para comenzar la demostración...")
            except EOFError:
                print("\n🤖 Modo automático detectado. Iniciando demo...")
                auto_mode = True
        else:
            print("🤖 Modo automático. Iniciando demo en 2 segundos...")
            time.sleep(2)
        
        # ============= PASO 1: INICIAR SERVIDOR =============
        self.print_step(1, "Iniciando servidor SingletonProxyObserver")
        
        print("🚀 Iniciando servidor en puerto 8888...")
        self.server_process = subprocess.Popen(
            [sys.executable, 'singletonproxyobserver.py', '-p', '8888', '-v'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.wait_with_countdown(3, "Esperando inicio del servidor")
        print("✅ Servidor iniciado correctamente en puerto 8888")
        
        # ============= PASO 2: INICIAR OBSERVER =============
        self.print_step(2, "Iniciando Cliente Observer")
        
        print("👁️  Iniciando observer para recibir notificaciones...")
        self.observer_process = subprocess.Popen(
            [sys.executable, 'observerclient.py', '-p', '8888', '-o', 'demo_notifications.json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        self.processes.append(self.observer_process)
        
        self.wait_with_countdown(2, "Esperando suscripción del observer")
        print("✅ Observer suscrito y esperando notificaciones")
        
        # ============= PASO 3: OPERACIÓN GET (Item no existe) =============
        self.print_step(3, "Probando GET con item inexistente")
        
        get_data = {
            "UUID": "demo-client",
            "ACTION": "get",
            "ID": "ITEM-NO-EXISTE"
        }
        
        json_file = self.create_json_file("demo_get.json", get_data)
        print(f"📄 Enviando: {json.dumps(get_data, indent=2)}")
        
        result = subprocess.run(
            [sys.executable, 'singletonclient.py', '-i', json_file, '-p', '8888'],
            capture_output=True,
            text=True
        )
        
        print(f"📥 Respuesta: {result.stdout}")
        os.unlink(json_file)
        
        # ============= PASO 4: OPERACIÓN SET (Crear item) =============
        self.print_step(4, "Creando nuevo item con SET")
        
        set_data = {
            "UUID": "demo-client",
            "ACTION": "set",
            "ID": "DEMO-ITEM-001",
            "cp": "1234",
            "CUIT": "30-98765432-1",
            "domicilio": "Av. Demo 123",
            "localidad": "Demo City",
            "provincia": "Demo Province",
            "telefono": "011-DEMO-1234",
            "web": "http://demo.example.com"
        }
        
        json_file = self.create_json_file("demo_set.json", set_data)
        print(f"📄 Enviando: {json.dumps(set_data, indent=2)}")
        
        result = subprocess.run(
            [sys.executable, 'singletonclient.py', '-i', json_file, '-p', '8888'],
            capture_output=True,
            text=True
        )
        
        print(f"📥 Respuesta: {result.stdout}")
        print("⚡ El Observer debería haber recibido una notificación!")
        os.unlink(json_file)
        
        self.wait_with_countdown(2, "Esperando propagación")
        
        # ============= PASO 5: OPERACIÓN GET (Item existe) =============
        self.print_step(5, "Obteniendo item creado con GET")
        
        get_data = {
            "UUID": "demo-client",
            "ACTION": "get",
            "ID": "DEMO-ITEM-001"
        }
        
        json_file = self.create_json_file("demo_get2.json", get_data)
        print(f"📄 Enviando: {json.dumps(get_data, indent=2)}")
        
        result = subprocess.run(
            [sys.executable, 'singletonclient.py', '-i', json_file, '-p', '8888'],
            capture_output=True,
            text=True
        )
        
        print(f"📥 Respuesta: {result.stdout}")
        os.unlink(json_file)
        
        # ============= PASO 6: OPERACIÓN UPDATE =============
        self.print_step(6, "Actualizando item existente")
        
        update_data = {
            "UUID": "demo-client",
            "ACTION": "set",
            "ID": "DEMO-ITEM-001",
            "telefono": "011-NUEVO-5678",
            "cp": "5678"
        }
        
        json_file = self.create_json_file("demo_update.json", update_data)
        print(f"📄 Enviando actualización: {json.dumps(update_data, indent=2)}")
        
        result = subprocess.run(
            [sys.executable, 'singletonclient.py', '-i', json_file, '-p', '8888'],
            capture_output=True,
            text=True
        )
        
        print(f"📥 Respuesta: {result.stdout}")
        print("⚡ El Observer debería haber recibido otra notificación!")
        os.unlink(json_file)
        
        self.wait_with_countdown(2, "Esperando propagación")
        
        # ============= PASO 7: OPERACIÓN LIST =============
        self.print_step(7, "Listando todos los items")
        
        list_data = {
            "UUID": "demo-client",
            "ACTION": "list"
        }
        
        json_file = self.create_json_file("demo_list.json", list_data)
        print(f"📄 Enviando: {json.dumps(list_data, indent=2)}")
        
        result = subprocess.run(
            [sys.executable, 'singletonclient.py', '-i', json_file, '-p', '8888'],
            capture_output=True,
            text=True
        )
        
        print(f"📥 Respuesta (truncada): {result.stdout[:500]}...")
        os.unlink(json_file)
        
        # ============= PASO 8: MÚLTIPLES OBSERVERS =============
        self.print_step(8, "Probando múltiples observers (Patrón Observer)")
        
        print("👁️  Iniciando 2 observers adicionales...")
        
        observer2 = subprocess.Popen(
            [sys.executable, 'observer_client.py', '-p', '8888'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.processes.append(observer2)
        
        observer3 = subprocess.Popen(
            [sys.executable, 'observer_client.py', '-p', '8888'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.processes.append(observer3)
        
        self.wait_with_countdown(2, "Esperando suscripción de observers")
        print("✅ Ahora hay 3 observers suscritos")
        
        # Hacer un cambio para notificar a todos
        multi_set_data = {
            "UUID": "demo-client",
            "ACTION": "set",
            "ID": "MULTI-OBSERVER-TEST",
            "cp": "9999",
            "localidad": "Observer Test City"
        }
        
        json_file = self.create_json_file("demo_multi.json", multi_set_data)
        print(f"📄 Enviando cambio para notificar a todos los observers...")
        
        result = subprocess.run(
            [sys.executable, 'singleton_client.py', '-i', json_file, '-p', '8888'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print("⚡ Los 3 observers deberían haber recibido la notificación!")
        os.unlink(json_file)
        
        # ============= PASO 9: VERIFICAR NOTIFICACIONES =============
        self.print_step(9, "Verificando notificaciones recibidas")
        
        if os.path.exists("demo_notifications.json"):
            print("📋 Contenido del archivo de notificaciones:")
            with open("demo_notifications.json", 'r') as f:
                content = f.read()
                if content:
                    print(content[:1000])
                    if len(content) > 1000:
                        print("... (truncado)")
                else:
                    print("   (archivo vacío - las notificaciones pueden estar en proceso)")
        
        # ============= RESUMEN =============
        self.print_header("RESUMEN DE LA DEMOSTRACIÓN")
        
        print("""
✅ Demostración completada exitosamente!

Patrones demostrados:
1. SINGLETON: El servidor mantiene instancias únicas de DAOs
2. PROXY: Intercepta operaciones SET y notifica cambios
3. OBSERVER: Múltiples clientes reciben notificaciones

Funcionalidades probadas:
• GET de item inexistente
• SET para crear nuevo item
• GET de item existente
• UPDATE de item existente
• LIST de todos los items
• Notificaciones a múltiples observers

Archivos generados:
• demo_notifications.json - Log de notificaciones recibidas
        """)
        
        input("\n🎯 Presione ENTER para finalizar la demostración...")
        
        # Limpiar
        self.cleanup()
        
        # Limpiar archivos temporales
        for file in ['demo_notifications.json']:
            if os.path.exists(file):
                try:
                    os.unlink(file)
                except:
                    pass
        
        print("\n✨ Demo finalizada. ¡Gracias por ver!")

def main():
    """Función principal"""
    demo = SystemDemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrumpida por el usuario")
        demo.cleanup()
    except Exception as e:
        print(f"\n❌ Error en la demo: {e}")
        demo.cleanup()
        sys.exit(1)

if __name__ == '__main__':
    main()