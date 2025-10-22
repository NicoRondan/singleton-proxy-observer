# 🧪 Tests - Suite de Pruebas Automatizadas

Este directorio contiene los tests automatizados del sistema SingletonProxyObserver.

---

## 📄 Archivos

### `test_suite.py`
Suite completa de pruebas que verifica:

1. **Patrones de Diseño (3 tests)**
   - ✅ Singleton: Verifica instancias únicas
   - ✅ Proxy: Verifica interceptación y notificación
   - ✅ Observer: Verifica notificaciones a múltiples clientes

2. **Funcionalidad (7 tests)**
   - ✅ Caminos felices: GET, SET, LIST
   - ✅ Manejo de errores: JSON inválido, datos faltantes
   - ✅ Casos edge: servidor caído, puerto duplicado

3. **Integración DynamoDB (2 tests - opcionales)**
   - Verificación de tablas
   - Verificación de logs de auditoría

**Total: 12 tests**

---

## 🚀 Cómo Ejecutar

### Método 1: Con servidor en puerto 8080
```bash
# Terminal 1: Iniciar servidor
python singletonproxyobserver.py

# Terminal 2: Ejecutar tests
python tests/test_suite.py
```

### Método 2: Desde el directorio tests
```bash
cd tests
python test_suite.py
```

### Método 3: Con pytest (recomendado)
```bash
pytest tests/test_suite.py -v
```

---

## 📊 Resultado Esperado

```
============================================================
 RESUMEN DE PRUEBAS
============================================================
  Pruebas ejecutadas: 12
  ✓ Exitosas: 12
  ✗ Fallos: 0
  ⚠ Errores: 0

  🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
============================================================
```

---

## 🔧 Configuración

Los tests están configurados para:
- **Puerto del servidor:** 8080 (configurable en `TEST_PORT`)
- **Modo:** Usa servidor externo (configurable en `USE_EXTERNAL_SERVER`)
- **Timeout:** 5 segundos por operación

Para modificar la configuración, editar las constantes en `test_suite.py`:
```python
TEST_PORT = 8080
TEST_HOST = 'localhost'
USE_EXTERNAL_SERVER = True
```

---

## 📝 Agregar Nuevos Tests

Para agregar nuevos tests:

1. Crear una nueva función en una de las clases:
   - `TestServerPatterns`: Tests de patrones de diseño
   - `TestFunctionalRequirements`: Tests funcionales
   - `TestDynamoDBIntegration`: Tests de integración con AWS

2. Seguir la convención de nombres: `test_XX_descripcion`

3. Usar los helpers disponibles:
   ```python
   TestHelpers.send_tcp_request(host, port, data)
   TestHelpers.is_port_open(host, port)
   ```

### Ejemplo:
```python
def test_08_custom_validation(self):
    """Prueba validación personalizada"""
    print("\n→ Test: Validación personalizada")

    # Tu código de test aquí
    response = TestHelpers.send_tcp_request(...)
    self.assertIsNotNone(response)

    print("  ✓ Test personalizado pasado")
```

---

## 🐛 Troubleshooting

### Error: "ConnectionRefusedError"
**Problema:** El servidor no está ejecutándose
**Solución:**
```bash
python singletonproxyobserver.py
```

### Error: "Port already in use"
**Problema:** El puerto 8080 está ocupado
**Solución:**
```bash
# Opción 1: Matar proceso en puerto 8080
lsof -ti:8080 | xargs kill -9

# Opción 2: Usar otro puerto (modificar TEST_PORT en test_suite.py)
```

### Tests fallan con "Module not found"
**Problema:** El paquete no está instalado
**Solución:**
```bash
pip install -e .
```

---

## 📚 Recursos Adicionales

- **Documentación de unittest:** https://docs.python.org/3/library/unittest.html
- **Documentación de pytest:** https://docs.pytest.org/
- **Guía del proyecto:** Ver `../README.md`

---

**Última actualización:** Octubre 2024
