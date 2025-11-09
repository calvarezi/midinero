# Guía de Implementación - Dashboard Financiero

## Pasos de Instalación

### 1. Crear los archivos nuevos

Crea los siguientes archivos en tu proyecto:

```
finances/
├── services/
│   └── analytics_service.py          # Servicio de análisis
├── serializers_dashboard.py          # Serializers del dashboard
├── views_dashboard.py                # Views del dashboard
└── tests/
    └── test_dashboard.py              # Tests del dashboard
```

### 2. Actualizar archivos existentes

Reemplaza el contenido de:
- `finances/urls.py` con la versión actualizada

### 3. Verificar importaciones

Asegúrate de que estos paquetes estén instalados:

```bash
pip install djangorestframework
pip install drf-spectacular
pip install django-filter
```

### 4. Aplicar configuración

No se requieren migraciones nuevas ya que usamos los modelos existentes.

### 5. Reiniciar el servidor

```bash
python manage.py runserver
```

---

## Verificación de Funcionamiento

### Test 1: Resumen General

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/overview/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Respuesta esperada: JSON con total_income, total_expense, balance

### Test 2: Tendencias

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/trends/?months=6" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Respuesta esperada: Array con datos mensuales

### Test 3: Categorías

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/categories/?category_type=expense" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Respuesta esperada: Array con desglose por categoría

---

## Ejecución de Tests

```bash
# Todos los tests del dashboard
python manage.py test finances.tests.test_dashboard

# Test específico
python manage.py test finances.tests.test_dashboard.DashboardOverviewTests

# Con verbosidad
python manage.py test finances.tests.test_dashboard -v 2
```

---

## Documentación en Swagger

Los endpoints se documentan automáticamente en:

```
http://localhost:8000/api/docs/swagger/
```

Busca la sección "Dashboard" en la interfaz de Swagger UI.

---

## Casos de Uso Comunes

### Caso 1: Dashboard principal del usuario

```python
# Obtener resumen del mes actual
overview = requests.get(
    f"{BASE_URL}/dashboard/overview/",
    headers=headers,
    params={
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    }
)

# Obtener tendencias de últimos 6 meses
trends = requests.get(
    f"{BASE_URL}/dashboard/trends/",
    headers=headers,
    params={"months": 6}
)

# Obtener salud de presupuestos
budget_health = requests.get(
    f"{BASE_URL}/dashboard/budget-health/",
    headers=headers
)
```

### Caso 2: Análisis de gastos

```python
# Desglose de gastos por categoría
categories = requests.get(
    f"{BASE_URL}/dashboard/categories/",
    headers=headers,
    params={"category_type": "expense"}
)

# Patrones de gasto últimos 90 días
patterns = requests.get(
    f"{BASE_URL}/dashboard/patterns/",
    headers=headers,
    params={"days": 90}
)
```

### Caso 3: Planificación financiera

```python
# Predicción de gastos
prediction = requests.get(
    f"{BASE_URL}/dashboard/prediction/",
    headers=headers,
    params={"months_to_analyze": 6}
)

# Evaluar salud financiera
health = requests.get(
    f"{BASE_URL}/dashboard/budget-health/",
    headers=headers
)
```

---

## Solución de Problemas

### Error: Module not found

```bash
# Verifica que el archivo exista
ls finances/services/analytics_service.py

# Verifica que __init__.py exista en services/
touch finances/services/__init__.py
```

### Error: Import circular

Si ves errores de import circular:
1. Verifica que no estés importando Transaction dentro de Transaction
2. Los imports deben estar al inicio del archivo o dentro de métodos

### Error: 404 Not Found

Verifica que las URLs estén registradas:

```python
# En finances/urls.py
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
```

### Error: Authentication required

Asegúrate de enviar el token JWT:

```bash
# Primero obtén el token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Luego úsalo en las requests
curl -H "Authorization: Bearer <token>" ...
```

---

## Optimizaciones Recomendadas

### 1. Caché con Redis

```python
from django.core.cache import cache

def get_overview_cached(user, start_date, end_date):
    cache_key = f"overview_{user.id}_{start_date}_{end_date}"
    data = cache.get(cache_key)
    
    if not data:
        data = FinancialAnalyticsService.get_overview(
            user, start_date, end_date
        )
        cache.set(cache_key, data, timeout=300)  # 5 minutos
    
    return data
```

### 2. Índices de base de datos

Agrega estos índices en una migración:

```python
class Migration(migrations.Migration):
    operations = [
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'date', 'category'], name='trans_user_date_cat_idx')
        ),
    ]
```

### 3. Paginación para datos extensos

```python
from rest_framework.pagination import PageNumberPagination

class LargePagination(PageNumberPagination):
    page_size = 100
    max_page_size = 500
```

---

## Métricas y Monitoreo

### Endpoints a monitorear

1. Tiempo de respuesta (debe ser < 500ms)
2. Tasa de errores (debe ser < 1%)
3. Uso de memoria en análisis

### Logging recomendado

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Overview requested by user {user.id}")
logger.error(f"Error in trends: {str(e)}")
```

---

## Próximos Pasos

1. Implementar caché con Redis
2. Agregar exportación de reportes en PDF
3. Crear gráficos automáticos con Chart.js
4. Implementar alertas proactivas
5. Machine Learning para predicciones