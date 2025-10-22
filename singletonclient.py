#!/usr/bin/env python3
"""
SingletonClient - Cliente para operaciones CRUD sobre CorporateData
Trabajo Práctico Final Integrador - IS2

Uso:
    python singletonclient.py -i=input.json [-o=output.json] [-v]

Formato de input.json:
    {
        "UUID": "XXXXXXXXXXXXXXXXXXXXXXX",
        "ID": "ZZZZZZZZZZZZZZZZZZZZZZZ",
        "ACTION": "get|set|list",
        ... campos adicionales para SET ...
    }
"""

import sys
import argparse
import json
import logging
from pathlib import Path

# Agregar src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from singleton_proxy_observer.clients.singleton_client import SingletonClient


def load_input_file(input_path: str) -> dict:
    """
    Carga y valida el archivo JSON de entrada

    Args:
        input_path: Ruta al archivo de entrada

    Returns:
        Diccionario con los datos del archivo
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validar campos requeridos básicos
        if 'ACTION' not in data:
            raise ValueError("El archivo debe contener el campo 'ACTION'")

        action = data['ACTION'].lower()
        if action not in ['get', 'set', 'list']:
            raise ValueError(f"ACTION inválida: {action}. Debe ser: get, set, o list")

        # Validar ID para get y set
        if action in ['get', 'set'] and 'ID' not in data:
            raise ValueError(f"La acción '{action}' requiere el campo 'ID'")

        return data

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{input_path}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: El archivo '{input_path}' no es un JSON válido")
        print(f"   Detalle: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
        sys.exit(1)


def save_output(data: dict, output_path: str = None):
    """
    Guarda o muestra la respuesta

    Args:
        data: Datos a guardar/mostrar
        output_path: Ruta opcional del archivo de salida
    """
    output_json = json.dumps(data, indent=2, ensure_ascii=False)

    # Siempre mostrar en stdout
    print("\n" + "="*60)
    print("RESPUESTA DEL SERVIDOR")
    print("="*60)
    print(output_json)
    print("="*60 + "\n")

    # Guardar en archivo si se especificó
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"✅ Respuesta guardada en: {output_path}")
        except Exception as e:
            print(f"⚠️  Error al guardar archivo de salida: {e}")


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description='Cliente Singleton para operaciones sobre CorporateData',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # GET - Obtener un registro
  python singletonclient.py -i=examples/input_get.json

  # SET - Modificar/crear un registro
  python singletonclient.py -i=examples/input_set.json -o=output.json

  # LIST - Listar todos los registros
  python singletonclient.py -i=examples/input_list.json -v

Formato de input.json para GET:
  {
    "ID": "UADER-FCyT-IS2",
    "ACTION": "get"
  }

Formato de input.json para SET:
  {
    "ID": "UADER-FCyT-IS2",
    "ACTION": "set",
    "cp": "3260",
    "CUIT": "30-70925411-8",
    "domicilio": "25 de Mayo 385-1P",
    "localidad": "Concepción del Uruguay",
    "provincia": "Entre Rios",
    "sede": "FCyT",
    "telefono": "03442 43-1442",
    "web": "http://www.uader.edu.ar"
  }

Formato de input.json para LIST:
  {
    "ACTION": "list"
  }
        """
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Archivo JSON de entrada con la solicitud (requerido)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Archivo JSON de salida para guardar la respuesta (opcional)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose - muestra logs detallados'
    )

    parser.add_argument(
        '-s', '--server',
        default='localhost',
        help='Hostname del servidor (default: localhost)'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8080,
        help='Puerto del servidor (default: 8080)'
    )

    args = parser.parse_args()

    # Cargar datos de entrada
    input_data = load_input_file(args.input)

    # Crear cliente
    client = SingletonClient(
        host=args.server,
        port=args.port,
        verbose=args.verbose
    )

    # Determinar la acción
    action = input_data['ACTION'].lower()

    try:
        # Ejecutar acción
        if action == 'get':
            item_id = input_data['ID']
            if args.verbose:
                print(f"📥 Ejecutando GET para ID: {item_id}")
            response = client.get(item_id)

        elif action == 'set':
            item_id = input_data['ID']
            # Extraer campos de datos (todos excepto UUID, ID, ACTION)
            data_fields = {k: v for k, v in input_data.items()
                          if k not in ['UUID', 'ID', 'ACTION']}
            if args.verbose:
                print(f"📝 Ejecutando SET para ID: {item_id}")
                print(f"   Campos: {list(data_fields.keys())}")
            response = client.set(item_id, data_fields)

        elif action == 'list':
            if args.verbose:
                print("📋 Ejecutando LIST")
            response = client.list_all()

        # Verificar respuesta
        if response is None:
            print("❌ Error: No se recibió respuesta del servidor")
            print("   Verifique que el servidor esté ejecutándose")
            sys.exit(1)

        if 'error' in response:
            print(f"❌ Error del servidor: {response['error']}")
            sys.exit(1)

        # Guardar/mostrar resultado
        save_output(response, args.output)

        print("✅ Operación completada exitosamente")

    except ConnectionRefusedError:
        print(f"❌ Error: No se pudo conectar al servidor en {args.server}:{args.port}")
        print("   Asegúrese de que el servidor esté ejecutándose")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
