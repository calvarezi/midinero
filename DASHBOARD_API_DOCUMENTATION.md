# Dashboard API - Documentación

Guía completa de uso de los endpoints de análisis financiero.

## Autenticación

Todos los endpoints requieren autenticación JWT:

```http
Authorization: Bearer <access_token>
```

## Endpoints Disponibles

### 1. Resumen General (Overview)

Obtiene un resumen completo de la situación financiera del usuario.

**Endpoint:** `GET /api/finances/dashboard/overview/`

**Query Parameters:**
- `start_date` (opcional): Fecha inicial en formato YYYY-MM-DD
- `end_date` (opcional): Fecha final en formato YYYY-MM-DD

**Ejemplo de Request:**

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/overview/?start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Bearer <token>"
```

**Ejemplo de Response:**

```json
{
  "status": "success",
  "message": "Resumen financiero obtenido correctamente",
  "data": {
    "total_income": 5000.00,
    "total_expense": 3200.00,
    "balance": 1800.00,
    "savings_rate": 36.00,
    "avg_income": 2500.00,
    "avg_expense": 533.33,
    "transaction_count": 15,
    "income_count": 2,
    "expense_count": 13,
    "max_expense": 800.00,
    "min_expense": 50.00,
    "period": {
      "start_date": "2025-01-01",
      "end_date": "2025-01-31"
    }
  }
}
```

---

### 2. Tendencias Mensuales

Analiza ingresos y gastos mes a mes.

**Endpoint:** `GET /api/finances/dashboard/trends/`

**Query Parameters:**
- `months` (opcional): Número de meses a analizar (1-36, default: 12)

**Ejemplo de Request:**

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/trends/?months=6" \
  -H "Authorization: Bearer <token>"
```

**Ejemplo de Response:**

```json
{
  "status": "success",
  "message": "Tendencias de los últimos 6 meses obtenidas correctamente",
  "data": [
    {
      "month": "2024-08",
      "month_name": "August 2024",
      "total_income": 4500.00,
      "total_expense": 2800.00,
      "balance": 1700.00,
      "transaction_count": 23
    },
    {
      "month": "2024-09",
      "month_name": "September 2024",
      "total_income": 4800.00,
      "total_expense": 3100.00,
      "balance": 1700.00,
      "transaction_count": 28
    }
  ]
}
```

**Casos de uso:**
- Gráficos de líneas para visualizar tendencias
- Comparar ingresos vs gastos por mes
- Identificar meses con mayor/menor ahorro

---

### 3. Desglose por Categorías

Analiza la distribución de gastos o ingresos por categoría.

**Endpoint:** `GET /api/finances/dashboard/categories/`

**Query Parameters:**
- `category_type` (opcional): 'income' o 'expense'
- `start_date` (opcional): Fecha inicial YYYY-MM-DD
- `end_date` (opcional): Fecha final YYYY-MM-DD

**Ejemplo de Request:**

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/categories/?category_type=expense" \
  -H "Authorization: Bearer <token>"
```

**Ejemplo de Response:**

```json
{
  "status": "success",
  "message": "Desglose por categorías obtenido correctamente",
  "data": [
    {
      "category_id": 5,
      "category_name": "Alimentación",
      "category_type": "expense",
      "total": 1200.00,
      "percentage": 37.50,
      "transaction_count": 15,
      "average": 80.00
    },
    {
      "category_id": 8,
      "category_name": "Transporte",
      "category_type": "expense",
      "total": 800.00,
      "percentage": 25.00,
      "transaction_count": 10,
      "average": 80.00
    }
  ]
}
```

**Casos de uso:**
- Gráficos de torta/dona para visualizar distribución
- Identificar categorías con mayor gasto
- Optimizar presupuestos por categoría

---

### 4. Patrones de Gasto

Identifica patrones de comportamiento financiero.

**Endpoint:** `GET /api/finances/dashboard/patterns/`

**Query Parameters:**
- `days` (opcional): Número de días a analizar (7-365, default: 90)

**Ejemplo de Request:**

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/patterns/?days=30" \
  -H "Authorization: Bearer <token>"
```

**Ejemplo de Response:**

```json
{
  "status": "success",
  "message": "Patrones de gasto de los últimos 30 días obtenidos correctamente",
  "data": {
    "daily_pattern": [
      {
        "day": "Monday",
        "total": 450.00,
        "count": 8,
        "average": 56.25
      },
      {
        "day": "Friday",
        "total": 680.00,
        "count": 12,
        "average": 56.67
      }
    ],
    "most_frequent_category": "Alimentación",
    "most_frequent_count": 25,
    "average_daily_spending": 106.67,
    "analysis_period_days": 30
  }
}
```

**Casos de uso:**
- Identificar días con mayor gasto
- Detectar hábitos de consumo
- Planificar mejor el presupuesto semanal

---

### 5. Predicción de Gastos

Predice gastos futuros basándose en histórico.

**Endpoint:** `GET /api/finances/dashboard/prediction/`

**Query Parameters:**
- `months_to_analyze` (opcional): Meses históricos (3-12, default: 6)

**Ejemplo de Request:**

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/prediction/" \
  -H "Authorization: Bearer <token>"
```

**Ejemplo de Response:**

```json
{
  "status": "success",
  "message": "Predicción de gastos obtenida correctamente",
  "data": {
    "predicted_total": 3150.00,
    "category_predictions": [
      {
        "category_id": 5,
        "category_name": "Alimentación",
        "predicted_amount": 1100.00
      },
      {
        "category_id": 8,
        "category_name": "Transporte",
        "predicted_amount": 750.00
      }
    ],
    "trend": "increasing",
    "trend_percentage": 8.50,
    "confidence": "medium",
    "based_on_months": 6
  }
}
```

**Interpretación de tendencias:**
- `increasing`: Gastos están aumentando
- `decreasing`: Gastos están disminuyendo
- `stable`: Gastos se mantienen constantes

**Casos de uso:**
- Planificación financiera a futuro
- Ajustar presupuestos proactivamente
- Alertas tempranas de sobregasto

---

### 6. Salud de Presupuestos

Evalúa el estado actual de los presupuestos configurados.

**Endpoint:** `GET /api/finances/dashboard/budget-health/`

**Query Parameters:**
- `month` (opcional): Mes a evaluar YYYY-MM-DD (default: mes actual)

**Ejemplo de Request:**

```bash
curl -X GET "http://localhost:8000/api/finances/dashboard/budget-health/?month=2025-01-01" \
  -H "Authorization: Bearer <token>"
```

**Ejemplo de Response:**

```json
{
  "status": "success",
  "message": "Estado de presupuestos obtenido correctamente",
  "data": {
    "month": "2025-01",
    "overall_status": "warning",
    "overall_percentage": 82.50,
    "total_budget": 5000.00,
    "total_spent": 4125.00,
    "total_remaining": 875.00,
    "has_budgets": true,
    "budgets": [
      {
        "category_name": "Alimentación",
        "limit": 1500.00,
        "spent": 1450.00,
        "remaining": 50.00,
        "percentage": 96.67,
        "status": "warning"
      },
      {
        "category_name": "Entretenimiento",
        "limit": 500.00,
        "spent": 600.00,
        "remaining": -100.00,
        "percentage": 120.00,
        "status": "exceeded"
      }
    ]
  }
}
```

**Estados de presupuesto:**
- `healthy`: Menos del 80% usado
- `warning`: Entre 80% y 100%
- `exceeded`: Más del 100%
- `critical`: Overall status cuando múltiples presupuestos están excedidos

**Casos de uso:**
- Dashboard de salud financiera
- Alertas automáticas
- Visualización de progreso de presupuestos

---

## Manejo de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "status": "error",
  "message": "Descripción del error",
  "errors": {
    "field_name": ["Detalle del error"]
  }
}
```

### Códigos de Estado HTTP

- `200 OK`: Request exitoso
- `400 Bad Request`: Parámetros inválidos
- `401 Unauthorized`: Token inválido o ausente
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

---

## Ejemplos de Integración

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/finances"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Obtener resumen
response = requests.get(
    f"{BASE_URL}/dashboard/overview/",
    headers=headers,
    params={"start_date": "2025-01-01", "end_date": "2025-01-31"}
)

data = response.json()
print(f"Balance: ${data['data']['balance']}")
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000/api/finances";
const TOKEN = "your_access_token";

async function getOverview() {
  const response = await fetch(
    `${BASE_URL}/dashboard/overview/`,
    {
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
        "Content-Type": "application/json"
      }
    }
  );
  
  const data = await response.json();
  console.log(`Balance: $${data.data.balance}`);
}
```

---

## Mejores Prácticas

1. **Caché de datos**: Cachea respuestas del dashboard por períodos cortos (5-10 min)

2. **Paginación**: Para datos históricos extensos, considera limitar el rango de fechas

3. **Rate limiting**: Implementa límites para evitar sobrecarga del servidor

4. **Manejo de errores**: Siempre valida las respuestas y maneja errores apropiadamente

5. **Optimización**: Usa los filtros de fecha para reducir la cantidad de datos procesados

---

## Testing

Para ejecutar los tests del dashboard:

```bash
python manage.py test finances.tests.test_dashboard
```

Para tests específicos:

```bash
python manage.py test finances.tests.test_dashboard.DashboardOverviewTests
```

---

## Roadmap de Mejoras Futuras

- Exportación de reportes en PDF
- Comparación entre períodos
- Alertas configurables
- Machine Learning para predicciones más precisas
- Integración con instituciones bancarias
- Análisis de cashflow
- Recomendaciones personalizadas de ahorro