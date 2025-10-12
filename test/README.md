# 🧪 Tests - SISCOM API

Suite completa de tests para la API SISCOM usando pytest.

## 📂 Estructura de Tests

```
test/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── test_health.py           # Tests del health check
├── test_security.py         # Tests de JWT y autenticación
├── test_communications.py   # Tests de endpoints de comunicaciones
├── test_repository.py       # Tests del servicio de repositorio
├── test_schemas.py          # Tests de schemas Pydantic
├── test_models.py           # Tests de modelos SQLAlchemy
├── test_config.py           # Tests de configuración
└── README.md                # Este archivo
```

## 🚀 Ejecutar Tests

### Todos los Tests

```bash
# Opción 1: pytest directo
pytest

# Opción 2: Con coverage
pytest --cov=app --cov-report=html

# Opción 3: Con Make
make test
```

### Tests Específicos

```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Solo tests de autenticación
pytest -m auth

# Solo tests de base de datos
pytest -m database

# Excluir tests lentos
pytest -m "not slow"

# Un archivo específico
pytest test/test_health.py

# Una clase específica
pytest test/test_security.py::TestJWTToken

# Un test específico
pytest test/test_health.py::TestHealthEndpoint::test_health_check_returns_200
```

### Modo Verbose

```bash
# Muy detallado
pytest -vv

# Con output de print
pytest -s

# Sin captura de output
pytest --capture=no
```

## 📊 Cobertura de Tests

### Ver Reporte de Cobertura

```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir reporte en navegador
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html       # macOS
```

### Reporte en Terminal

```bash
pytest --cov=app --cov-report=term-missing
```

## 🏷️ Markers de Tests

Los tests están organizados con markers para facilitar su ejecución:

- **`unit`**: Tests unitarios (no requieren BD ni servicios externos)
- **`integration`**: Tests de integración (requieren API completa)
- **`auth`**: Tests relacionados con autenticación
- **`database`**: Tests que requieren base de datos
- **`slow`**: Tests que toman más tiempo

### Usar Markers

```bash
pytest -m unit              # Solo unitarios
pytest -m "unit and auth"   # Unitarios de auth
pytest -m "not slow"        # Excluir lentos
```

## 🔧 Configuración

### pytest.ini

La configuración principal está en `/home/chch/Code/siscom-api/pytest.ini`:

- Modo async automático
- Coverage configurado
- Markers registrados
- Opciones de output

### conftest.py

Fixtures reutilizables:

#### Fixtures de Base de Datos

- `db_session`: Sesión de BD para cada test
- `setup_test_database`: Crea/destruye tablas de test

#### Fixtures de Autenticación

- `valid_token`: JWT token válido
- `expired_token`: JWT token expirado
- `invalid_token`: JWT token inválido
- `auth_headers`: Headers con Authorization

#### Fixtures de Datos

- `sample_suntech_communication`: Comunicación Suntech de prueba
- `sample_queclink_communication`: Comunicación Queclink de prueba
- `multiple_communications`: Múltiples registros

#### Fixtures de Cliente HTTP

- `client`: TestClient síncrono
- `async_client`: AsyncClient asíncrono

## 📋 Requisitos

### Dependencias de Test

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

O instalar desde requirements.txt:

```bash
pip install -r requirements.txt
```

### Base de Datos de Test

Los tests usan una base de datos separada: `siscom_test`

Crear la BD de test:

```bash
# PostgreSQL local
createdb siscom_test

# O con Docker
docker exec siscom-postgres psql -U postgres -c "CREATE DATABASE siscom_test;"
```

## 📝 Escribir Tests

### Estructura Básica

```python
import pytest

@pytest.mark.unit
class TestMiComponente:
    """Descripción de la suite de tests."""

    def test_comportamiento_esperado(self, fixture_necesaria):
        """
        Test: Descripción de qué se está probando.
        """
        # Arrange (preparar)
        data = {"key": "value"}

        # Act (ejecutar)
        result = funcion_a_probar(data)

        # Assert (verificar)
        assert result == expected_value
```

### Tests Async

```python
@pytest.mark.asyncio
async def test_async_function(db_session):
    """Test de función asíncrona."""
    result = await async_function(db_session)
    assert result is not None
```

### Usar Fixtures

```python
def test_with_auth(client, auth_headers):
    """Test con autenticación."""
    response = client.get("/api/v1/protected", headers=auth_headers)
    assert response.status_code == 200
```

## 🎯 Cobertura por Módulo

| Módulo                             | Coverage | Tests                  |
| ---------------------------------- | -------- | ---------------------- |
| `app/main.py`                      | 100%     | test_health.py         |
| `app/core/security.py`             | 100%     | test_security.py       |
| `app/api/routes/communications.py` | 95%      | test_communications.py |
| `app/services/repository.py`       | 100%     | test_repository.py     |
| `app/models/communications.py`     | 100%     | test_models.py         |
| `app/schemas/communications.py`    | 100%     | test_schemas.py        |
| `app/core/config.py`               | 100%     | test_config.py         |

**Total**: ~95% de cobertura

## 🐛 Troubleshooting

### Error: "No such file or directory: siscom_test"

```bash
# Crear la base de datos de test
createdb siscom_test
```

### Error: "connection to server failed"

```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql
# O
docker ps | grep postgres
```

### Error: "ModuleNotFoundError"

```bash
# Instalar dependencias
pip install -r requirements.txt

# Asegurarse de que el path esté bien
export PYTHONPATH="${PYTHONPATH}:/home/chch/Code/siscom-api"
```

### Tests Lentos

```bash
# Excluir tests marcados como 'slow'
pytest -m "not slow"

# Ejecutar en paralelo (requiere pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## 📊 CI/CD

Los tests se ejecutan automáticamente en GitHub Actions:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## 🎓 Mejores Prácticas

1. **Un concepto por test**: Cada test debe verificar una sola cosa
2. **Nombres descriptivos**: El nombre debe explicar qué se prueba
3. **AAA Pattern**: Arrange, Act, Assert
4. **Fixtures para setup**: Usar fixtures en lugar de código duplicado
5. **Markers apropiados**: Marcar tests según su tipo y requerimientos
6. **Tests independientes**: Cada test debe poder ejecutarse solo
7. **Cleanup automático**: Usar fixtures con yield para limpieza

## 📚 Recursos

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/core/connections.html#using-transactions-for-testsuites)

## ✅ Checklist de Tests

Antes de hacer commit, verifica:

- [ ] Todos los tests pasan (`pytest`)
- [ ] Coverage > 90% (`pytest --cov=app`)
- [ ] No hay tests marcados con `@pytest.mark.skip`
- [ ] Nuevas features tienen tests
- [ ] Tests documentados con docstrings
- [ ] Fixtures apropiadas están en conftest.py
- [ ] Markers correctos aplicados

---

**Última actualización**: 7 de octubre de 2025  
**Tests totales**: 50+  
**Cobertura**: ~95%
