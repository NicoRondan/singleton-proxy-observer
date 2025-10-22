#!/usr/bin/env python3
"""
Script para crear las tablas necesarias en DynamoDB
Ejecutar una sola vez antes de usar el sistema
"""

import boto3
import sys
import time
from botocore.exceptions import ClientError

# Configuración
AWS_REGION = 'us-east-1'
DYNAMODB_ENDPOINT = None  # None para AWS real, 'http://localhost:8000' para local

def create_tables():
    """Crea las tablas CorporateData y CorporateLog en DynamoDB"""
    
    print("="*60)
    print(" CONFIGURACIÓN DE TABLAS DYNAMODB")
    print("="*60)
    
    # Conectar a DynamoDB
    try:
        if DYNAMODB_ENDPOINT:
            print(f"Conectando a DynamoDB local en {DYNAMODB_ENDPOINT}")
            dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION,
                endpoint_url=DYNAMODB_ENDPOINT
            )
        else:
            print(f"Conectando a AWS DynamoDB en región {AWS_REGION}")
            dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION
            )
    except Exception as e:
        print(f"❌ Error conectando a DynamoDB: {e}")
        print("\nVerifique sus credenciales AWS:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - AWS_REGION")
        sys.exit(1)
    
    # Definición de tablas
    tables_config = [
        {
            'name': 'CorporateData',
            'description': 'Tabla para datos corporativos centralizados',
            'key_schema': [
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            'attribute_definitions': [
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'  # String
                }
            ]
        },
        {
            'name': 'CorporateLog',
            'description': 'Tabla para registro de auditoría',
            'key_schema': [
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            'attribute_definitions': [
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'  # String
                }
            ]
        }
    ]
    
    # Crear cada tabla
    for table_config in tables_config:
        table_name = table_config['name']
        print(f"\n📋 Procesando tabla: {table_name}")
        print(f"   {table_config['description']}")
        
        try:
            # Verificar si la tabla ya existe
            existing_tables = dynamodb.tables.all()
            table_exists = any(t.name == table_name for t in existing_tables)
            
            if table_exists:
                print(f"   ⚠️  La tabla {table_name} ya existe")
                table = dynamodb.Table(table_name)
                print(f"   ℹ️  Estado: {table.table_status}")
                print(f"   ℹ️  Items: {table.item_count}")
            else:
                # Crear la tabla
                print(f"   🔄 Creando tabla {table_name}...")
                
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=table_config['key_schema'],
                    AttributeDefinitions=table_config['attribute_definitions'],
                    BillingMode='PAY_PER_REQUEST'  # On-demand billing
                )
                
                # Esperar a que la tabla esté activa
                print(f"   ⏳ Esperando activación...")
                table.meta.client.get_waiter('table_exists').wait(
                    TableName=table_name,
                    WaiterConfig={
                        'Delay': 2,
                        'MaxAttempts': 30
                    }
                )
                
                # Refrescar información de la tabla
                table.reload()
                print(f"   ✅ Tabla {table_name} creada exitosamente")
                print(f"   ℹ️  Estado: {table.table_status}")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceInUseException':
                print(f"   ⚠️  La tabla {table_name} ya existe")
            else:
                print(f"   ❌ Error creando tabla {table_name}: {e}")
                sys.exit(1)
        except Exception as e:
            print(f"   ❌ Error inesperado con tabla {table_name}: {e}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print(" RESUMEN")
    print("="*60)
    
    # Mostrar resumen de tablas
    try:
        tables = list(dynamodb.tables.all())
        print(f"\n✅ Tablas disponibles en DynamoDB:")
        for table in tables:
            if table.name in ['CorporateData', 'CorporateLog']:
                print(f"   - {table.name}")
                print(f"     • Estado: {table.table_status}")
                print(f"     • Items: {table.item_count}")
                print(f"     • ARN: {table.table_arn}")
    except Exception as e:
        print(f"❌ Error obteniendo lista de tablas: {e}")
    
    print("\n✅ Configuración completada exitosamente")
    print("   Puede ejecutar el servidor con: python server_main.py")
    print("="*60)

def insert_sample_data():
    """Inserta datos de ejemplo en CorporateData"""
    
    print("\n📝 Insertando datos de ejemplo...")
    
    try:
        if DYNAMODB_ENDPOINT:
            dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION,
                endpoint_url=DYNAMODB_ENDPOINT
            )
        else:
            dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION
            )
        
        table = dynamodb.Table('CorporateData')
        
        # Datos de ejemplo
        sample_data = [
            {
                'id': 'UADER-FCyT-IS2',
                'cp': '3260',
                'CUIT': '30-70925411-8',
                'domicilio': '25 de Mayo 385-1P',
                'idreq': '473',
                'idSeq': '1146',
                'localidad': 'Concepción del Uruguay',
                'provincia': 'Entre Rios',
                'sede': 'FCyT',
                'seqID': '23',
                'telefono': '03442 43-1442',
                'web': 'http://www.uader.edu.ar'
            },
            {
                'id': 'EMPRESA-EJEMPLO',
                'cp': '1000',
                'CUIT': '30-12345678-9',
                'domicilio': 'Av. Corrientes 1234',
                'localidad': 'Buenos Aires',
                'provincia': 'Buenos Aires',
                'telefono': '011-4555-1234',
                'web': 'http://www.ejemplo.com'
            }
        ]
        
        for item in sample_data:
            table.put_item(Item=item)
            print(f"   ✅ Insertado: {item['id']}")
        
        print("   ✅ Datos de ejemplo insertados correctamente")
        
    except Exception as e:
        print(f"   ⚠️  Error insertando datos de ejemplo: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Configurar tablas DynamoDB para el sistema'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help='Usar DynamoDB local en lugar de AWS'
    )
    parser.add_argument(
        '--sample-data',
        action='store_true',
        help='Insertar datos de ejemplo'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='Región AWS (default: us-east-1)'
    )
    
    args = parser.parse_args()
    
    if args.local:
        DYNAMODB_ENDPOINT = 'http://localhost:8000'
    
    AWS_REGION = args.region
    
    # Crear tablas
    create_tables()
    
    # Insertar datos de ejemplo si se solicita
    if args.sample_data:
        insert_sample_data()
    
    print("\n✨ ¡Listo para usar!")