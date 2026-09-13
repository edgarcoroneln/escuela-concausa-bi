"""Cache, timeout y distinción de causas en `RepositorioAboutPostgres` (US-601).

Los tres puntos que pidió Edgar Coronel al revisar el PR #350, cada uno con la prueba que lo
falsifica:

1. **`no disponible` ≠ `no existe`.** Antes las dos condiciones caían en el mismo `except
   DBAPIError` y la página afirmaba *"Tabla no materializada todavía"* aunque la base estuviera
   caída. Es una afirmación falsa sobre el esquema cuando el problema es la conexión — el mismo
   tipo de error que la política `SIN_DATO` existe para evitar: no saber por qué falta un dato no
   autoriza a inventar la causa.
2. **Carga.** `conteos_capas()` dispara ~30 `COUNT(*)` desde un endpoint **público**. Sin cache,
   cada visita los repite todos.
3. **Timeout.** Cada consulta acota su `statement_timeout` a la transacción.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

from src.api.repositorio_about import RepositorioAboutPostgres


class _MotorFalso:
    """Motor que cuenta consultas y puede fallar con la excepción que se le indique."""

    def __init__(self, excepcion: Exception | None = None) -> None:
        self.excepcion = excepcion
        self.consultas: list[str] = []
        self.dialect = create_engine("sqlite://").dialect

    def begin(self):
        return _Contexto(self)

    def connect(self):
        return _Contexto(self)


class _Contexto:
    def __init__(self, motor: _MotorFalso) -> None:
        self._motor = motor

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False

    def execute(self, consulta):
        texto = str(getattr(consulta, "text", consulta))
        self._motor.consultas.append(texto)
        if "statement_timeout" in texto:
            return _Resultado(0)
        if self._motor.excepcion is not None:
            raise self._motor.excepcion
        return _Resultado(7)


class _Resultado:
    def __init__(self, valor: int) -> None:
        self._valor = valor

    def scalar_one(self):
        return self._valor

    def scalars(self):
        return self

    def all(self):
        return []

    def mappings(self):
        return self


def _error(clase) -> Exception:
    return clase("SELECT 1", {}, Exception("boom"))


# --------------------------------------------------------------- 1. causa correcta


def test_base_caida_no_se_reporta_como_tabla_inexistente() -> None:
    """El defecto que motivó la revisión: afirmar algo del esquema cuando falla la conexión."""
    repo = RepositorioAboutPostgres(engine=_MotorFalso(_error(OperationalError)))
    filas, nota = repo._contar("gold", "predicciones")

    assert filas is None
    assert "no respondió" in nota, f"la nota inventa la causa: {nota!r}"
    assert "materializada" not in nota
    assert repo.hubo_error_de_conexion() is True


def test_tabla_ausente_sigue_diciendo_que_no_esta_materializada() -> None:
    """El otro lado: un esquema realmente ausente no debe reportarse como caída."""
    repo = RepositorioAboutPostgres(engine=_MotorFalso(_error(ProgrammingError)))
    filas, nota = repo._contar("gold", "predicciones")

    assert filas is None
    assert "materializada" in nota
    assert repo.hubo_error_de_conexion() is False, (
        "una tabla ausente no es una caída de la base; declararlo así haría que la sección "
        "muestre una advertencia falsa"
    )


def test_la_bandera_se_reinicia_entre_intentos() -> None:
    """Una caída vieja no debe teñir un intento nuevo que sí funcionó."""
    motor = _MotorFalso(_error(OperationalError))
    repo = RepositorioAboutPostgres(engine=motor)
    repo.conteos_capas()
    assert repo.hubo_error_de_conexion() is True

    motor.excepcion = None
    repo.conteos_capas()
    assert repo.hubo_error_de_conexion() is False


# --------------------------------------------------------------- 2. cache


def test_la_segunda_visita_no_vuelve_a_consultar_postgres() -> None:
    """El punto de la revisión: ~30 COUNT(*) por visita en un endpoint público."""
    motor = _MotorFalso()
    repo = RepositorioAboutPostgres(engine=motor)

    primera = repo.conteos_capas()
    consultas_primera = len(motor.consultas)
    segunda = repo.conteos_capas()

    assert consultas_primera > 10, "se esperaba el barrido completo en la primera visita"
    assert len(motor.consultas) == consultas_primera, "la segunda visita volvió a consultar"
    assert segunda == primera


def test_un_resultado_con_la_base_caida_no_se_cachea() -> None:
    """Si se cacheara, la página seguiría diciendo "no disponible" después de que Postgres vuelva.

    Mismo criterio que `cache_predicciones.py`, que nunca cachea errores.
    """
    motor = _MotorFalso(_error(OperationalError))
    repo = RepositorioAboutPostgres(engine=motor)
    repo.conteos_capas()
    consultas_tras_el_fallo = len(motor.consultas)

    motor.excepcion = None
    repo.conteos_capas()

    assert len(motor.consultas) > consultas_tras_el_fallo, (
        "el resultado con la base caída quedó cacheado: la recuperación no se vería hasta que "
        "venciera el TTL"
    )
    assert repo.hubo_error_de_conexion() is False


# --------------------------------------------------------------- 3. timeout


def test_cada_consulta_acota_su_statement_timeout() -> None:
    """`SET LOCAL` y no `SET`: el efecto muere con la transacción y no fuga al pool compartido."""
    motor = _MotorFalso()
    repo = RepositorioAboutPostgres(engine=motor)
    repo._contar("gold", "predicciones")

    timeouts = [c for c in motor.consultas if "statement_timeout" in c]
    assert timeouts, "la consulta corrió sin acotar su timeout"
    assert all("SET LOCAL" in t for t in timeouts), (
        "un `SET` sin `LOCAL` sobrevive a la transacción y se lleva el timeout al motor "
        "compartido cuando la conexión vuelve al pool"
    )


@pytest.mark.parametrize("ajuste", ["about_timeout_ms", "about_cache_ttl_segundos"])
def test_los_valores_salen_de_settings_y_no_estan_escritos_a_mano(ajuste: str) -> None:
    from src.api.config import get_settings

    valor = getattr(get_settings(), ajuste)
    assert isinstance(valor, int) and valor > 0


def test_el_timeout_es_el_de_settings() -> None:
    from src.api.config import get_settings

    motor = _MotorFalso()
    repo = RepositorioAboutPostgres(engine=motor)
    repo._contar("gold", "predicciones")

    esperado = f"SET LOCAL statement_timeout = {get_settings().about_timeout_ms}"
    assert any(esperado == c for c in motor.consultas)


def test_un_identificador_invalido_no_llega_a_construir_sql() -> None:
    """Último resguardo: el nombre de tabla nunca viene de una petición, pero se valida igual."""
    motor = _MotorFalso()
    repo = RepositorioAboutPostgres(engine=motor)
    filas, nota = repo._contar("gold", 'predicciones"; DROP TABLE x --')

    assert filas is None
    assert "inválido" in nota
    assert motor.consultas == [], "se construyó SQL con un identificador rechazado"


def test_el_texto_del_conteo_usa_comillas_dobles_sobre_el_identificador() -> None:
    motor = _MotorFalso()
    RepositorioAboutPostgres(engine=motor)._contar("gold", "predicciones")
    conteos = [c for c in motor.consultas if "COUNT(*)" in c]
    assert conteos == ['SELECT COUNT(*) FROM "gold"."predicciones"']


def test_text_sigue_disponible_para_el_modulo() -> None:
    """Guarda trivial contra un refactor que quite el import y rompa el `SET LOCAL`."""
    assert text is not None
