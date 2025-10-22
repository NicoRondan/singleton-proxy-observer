# 📂 Ejemplos de Uso
## SingletonProxyObserver - Ejemplos Prácticos

Esta carpeta contiene ejemplos listos para usar con el sistema.

---

## 📝 Archivos JSON de Entrada

### `input_get.json` - Obtener un registro

**Uso:**
```bash
python singletonclient.py -i=examples/input_get.json
```

**Descripción:** Recupera el registro con ID especificado de la tabla CorporateData.

---

### `input_set.json` - Crear/Actualizar registro

**Uso:**
```bash
python singletonclient.py -i=examples/input_set.json
```

**Descripción:** Crea o actualiza el registro especificado.

⚠️ **Importante:** Esta acción dispara notificaciones a todos los observers suscritos.

---

### `input_list.json` - Listar todos los registros

**Uso:**
```bash
python singletonclient.py -i=examples/input_list.json
```

**Descripción:** Retorna todos los registros de la tabla CorporateData.

---

## 🎬 Scripts de Demostración

### `demo_observer.sh` - Demo del Patrón Observer

```bash
./examples/demo_observer.sh
```

**Cómo probarlo:**
1. Ejecutar el script en Terminal 1
2. En Terminal 2, hacer un SET:
   ```bash
   python singletonclient.py -i=examples/input_set.json
   ```
3. Ver la notificación en Terminal 1

---
