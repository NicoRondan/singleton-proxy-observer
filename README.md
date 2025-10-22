# 🚀 Guía Rápida de Uso
## Sistema SingletonProxyObserver - UADER FCyT IS2

Esta guía te permite comenzar a usar el sistema en menos de 5 minutos.

---

## 📋 Pre-requisitos

1. Python 3.7 o superior
2. Paquetes instalados: `pip install -r requirements.txt`
3. Credenciales AWS configuradas (o usar DynamoDB local)

---

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Iniciar el Servidor

```bash
# Opción 1: Script simple
./scripts/run_server.sh

# Opción 2: Comando directo
python singletonproxyobserver.py

# Opción 3: Puerto personalizado y verbose
python singletonproxyobserver.py -p 9000 -v
```

**Salida esperada:**
```
============================================================
 SERVIDOR SINGLETON-PROXY-OBSERVER
============================================================
✅ Servidor iniciado exitosamente
📡 Escuchando en puerto: 8080
```

---

### 2️⃣ Ejecutar Operaciones CRUD

#### 📥 GET - Obtener un registro

```bash
python singletonclient.py -i=examples/input_get.json
```

**Input (`examples/input_get.json`):**
```json
{
  "ID": "UADER-FCyT-IS2",
  "ACTION": "get"
}
```

**Output:**
```json
{
  "action": "get",
  "data": {
    "id": "UADER-FCyT-IS2",
    "cp": "3260",
    "CUIT": "30-70925411-8",
    ...
  }
}
```

---

#### 📝 SET - Crear/Modificar un registro

```bash
python singletonclient.py -i=examples/input_set.json -o=output.json
```

**Input (`examples/input_set.json`):**
```json
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
```

**Output:**
```json
{
  "action": "set",
  "data": {
    "id": "UADER-FCyT-IS2",
    "cp": "3260",
    ...
  }
}
```

---

#### 📋 LIST - Listar todos los registros

```bash
python singletonclient.py -i=examples/input_list.json
```

**Input (`examples/input_list.json`):**
```json
{
  "ACTION": "list"
}
```

**Output:**
```json
{
  "action": "list",
  "data": [
    {"id": "UADER-FCyT-IS2", ...},
    {"id": "otro-registro", ...}
  ]
}
```

---

### 3️⃣ Recibir Notificaciones en Tiempo Real

#### 👂 Suscribirse como Observer

```bash
# Terminal 1: Iniciar observer
python observerclient.py -v

# Terminal 2: Hacer un cambio
python singletonclient.py -i=examples/input_set.json
```

**El Terminal 1 recibirá:**
```
[2024-10-22T03:45:12.123456] Notification received:
{
  "action": "update",
  "item_id": "UADER-FCyT-IS2",
  "data": {
    "id": "UADER-FCyT-IS2",
    "cp": "3260",
    ...
  },
  "timestamp": "2024-10-22T03:45:12.123456"
}
--------------------------------------------------
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Monitoreo en Tiempo Real

**Escenario:** Múltiples clientes observando cambios

```bash
# Terminal 1: Observer 1
python observerclient.py -o=observer1.json

# Terminal 2: Observer 2
python observerclient.py -o=observer2.json

# Terminal 3: Hacer cambios
python singletonclient.py -i=examples/input_set.json
```

**Resultado:** Ambos observers reciben la notificación simultáneamente ✅

---

### Caso 2: Actualización Masiva

**Escenario:** Actualizar múltiples registros

```bash
# Crear input_set_1.json, input_set_2.json, ...
for file in examples/input_set_*.json; do
    python singletonclient.py -i=$file
    echo "✅ Procesado: $file"
done
```

---

### Caso 3: Servidor en Máquina Remota

**Escenario:** Cliente y servidor en diferentes hosts

```bash
# En servidor (192.168.1.100)
python singletonproxyobserver.py -p 8080

# En cliente
python singletonclient.py -s=192.168.1.100 -p=8080 -i=input.json
python observerclient.py -s=192.168.1.100 -p=8080
```

---

## 🔧 Opciones Avanzadas

### Servidor

```bash
# Puerto personalizado
python singletonproxyobserver.py -p 9000

# Modo verbose (logs detallados)
python singletonproxyobserver.py -v

# Ambos
python singletonproxyobserver.py -p 9000 -v
```

### SingletonClient

```bash
# Especificar servidor y puerto
python singletonclient.py -i=input.json -s=192.168.1.100 -p=9000

# Guardar output en archivo
python singletonclient.py -i=input.json -o=resultado.json

# Modo verbose
python singletonclient.py -i=input.json -v
```

### ObserverClient

```bash
# Servidor remoto
python observerclient.py -s=192.168.1.100 -p=9000

# Guardar notificaciones
python observerclient.py -o=notificaciones.json

# Intervalo de reconexión personalizado
python observerclient.py -r=60  # Reintentar cada 60 segundos

# Modo verbose
python observerclient.py -v
```

---

## 🧪 Pruebas Automatizadas

```bash
# 1. Iniciar servidor
python singletonproxyobserver.py

# 2. En otra terminal, ejecutar tests
cd src
python test_suite.py
```

**Resultado esperado:**
```
============================================================
 RESUMEN DE PRUEBAS
============================================================
  Pruebas ejecutadas: 12
  ✓ Exitosas: 12
  ✗ Fallos: 0

  🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
============================================================
```

---

## 🐛 Solución de Problemas

### Problema: "ConnectionRefusedError"

**Causa:** El servidor no está ejecutándose

**Solución:**
```bash
# Verificar que el servidor esté corriendo
python singletonproxyobserver.py
```

---

### Problema: "Port already in use"

**Causa:** El puerto 8080 está ocupado

**Solución 1:** Usar otro puerto
```bash
python singletonproxyobserver.py -p 9000
```

**Solución 2:** Matar proceso en puerto 8080
```bash
# Linux/Mac
lsof -ti:8080 | xargs kill -9

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

### Problema: "ModuleNotFoundError"

**Causa:** Paquetes no instalados

**Solución:**
```bash
pip install -r requirements.txt
```

---

## 📚 Más Información

- **Documentación completa:** Ver `README.md`
- **API Reference:** Ver `docs/API.md`
- **Como empezar:** Ver `COMO_EMPEZAR.md`
- **Arquitectura:** Ver `docs/diagrams/uml_diagrams.mermaid`

---

## 🎓 Patrones de Diseño Implementados

Este sistema demuestra 3 patrones de diseño:

### 1️⃣ **Singleton**
- Solo una instancia de conexión a DynamoDB
- Solo una instancia de cada DAO
- Ahorra recursos y garantiza consistencia

### 2️⃣ **Proxy**
- Intercepta operaciones SET
- Agrega notificaciones automáticas
- Transparente para el cliente

### 3️⃣ **Observer**
- Clientes se suscriben
- Reciben notificaciones automáticas
- Sin necesidad de polling

---

## ✅ Checklist de Verificación

- [ ] Servidor inicia sin errores
- [ ] GET retorna datos correctamente
- [ ] SET actualiza y notifica observers
- [ ] LIST retorna todos los registros
- [ ] Observer recibe notificaciones en tiempo real
- [ ] Tests automatizados pasan (12/12)
- [ ] Logs de auditoría se crean en CorporateLog

---

## 🆘 Ayuda

Si encuentras problemas:

1. Revisa esta guía
2. Consulta `README.md` para detalles técnicos
3. Ejecuta en modo verbose (`-v`) para ver logs detallados
4. Verifica credenciales AWS
5. Revisa que las tablas DynamoDB existan

---

**🎉 ¡Listo! Ya puedes usar el sistema completo.**
