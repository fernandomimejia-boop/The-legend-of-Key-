"""
Módulo de misiones - Checkpoint 3 (Aventura Algorítmica)
La Leyenda de Zelda: El Ascenso de Vaati

ÁRBOL de misiones del Palacio de los Vientos. Cada misión depende de la que
está arriba (su padre): solo se puede completar cuando el padre ya está
completado. Es la evolución del árbol que presentamos en la exposición de
árboles (exposicion/arboles.py), ahora conectado a la partida:

    Entrar al Palacio de los Vientos                      (raíz)
    ├── Explorar 3 salas                    +10 rupias, abre el atajo del viento
    │   └── Cartografiar 6 salas            +20 rupias
    ├── Abrir el primer cofre               +15 rupias
    │   └── Reunir 3 tesoros                +30 rupias, abre la puerta del jefe
    │       └── Derrotar a Vaati            +100 rupias, Hyrule se salva
    └── Vencer a 2 secuaces de Vaati        +20 rupias, abre el atajo de la tropa
        └── Recibir la bendición de la Gran Hada   +10 rupias

¿Cómo se completa una misión?
    Cada misión tiene una CONDICIÓN (indicador, cantidad), por ejemplo
    ("salas_visitadas", 3). Después de cada acción, main.py arma los
    indicadores con el diccionario de estado y llama a revisar_misiones():
    toda misión DISPONIBLE cuya condición se cumple se completa sola.

¿Qué efecto tiene en la partida?
    La recompensa en rupias y, en algunas misiones, abrir una puerta sellada
    del grafo: BFS y DFS encuentran rutas nuevas en cuanto se abre.

Recorridos que usa el juego (todos recursivos o con cola):
    preorden ............ mostrar el árbol con sangría (menú de misiones)
    por niveles (BFS) ... listar las misiones disponibles por etapa
    postorden ........... sumar las recompensas de cada rama (ganadas y pendientes)

Complejidad: los recorridos, buscar, revisar y las disponibles son O(n),
con n = número de misiones; agregar_hijo es O(1).
"""

from collections import deque


class Nodo:
    """
    Una misión del árbol.

    Atributos:
        nombre     -> nombre único de la misión.
        recompensa -> rupias que da al completarse.
        condicion  -> tupla (indicador, cantidad) que la completa, o None
                      si se completa a mano.
        puerta     -> clave (tupla) de la puerta que abre, o None.
        hijos      -> misiones que dependen de esta.
        completada -> True cuando Link la completó.
    """

    def __init__(self, nombre, recompensa=0, condicion=None, puerta=None):
        """Crea una misión sin hijos y sin completar. Complejidad: O(1)."""
        self.nombre = nombre
        self.recompensa = recompensa
        self.condicion = condicion
        self.puerta = puerta
        self.hijos = []
        self.completada = False


def agregar_hijo(padre, hijo):
    """Agrega 'hijo' como misión que depende de 'padre'. Complejidad: O(1)."""
    padre.hijos.append(hijo)
    return hijo


def construir_arbol_misiones(tesoros_necesarios=3):
    """
    Construye el árbol de misiones del palacio.
    'tesoros_necesarios' se ajusta a la cantidad de cofres que tenga la
    mazmorra generada, para que la misión siempre se pueda cumplir.
    Las puertas que abre cada misión las asigna main.py con asignar_puerta(),
    porque dependen del mapa generado.
    Complejidad: O(n). Retorna la raíz.
    """
    raiz = Nodo("Entrar al Palacio de los Vientos", 0, ("salas_visitadas", 1))

    explorar = agregar_hijo(raiz, Nodo("Explorar 3 salas", 10, ("salas_visitadas", 3)))
    agregar_hijo(explorar, Nodo("Cartografiar 6 salas", 20, ("salas_visitadas", 6)))

    cofre = agregar_hijo(raiz, Nodo("Abrir el primer cofre", 15, ("tesoros_recogidos", 1)))
    reunir = agregar_hijo(cofre, Nodo(f"Reunir {tesoros_necesarios} tesoros", 30,
                                      ("tesoros_recogidos", tesoros_necesarios)))
    agregar_hijo(reunir, Nodo("Derrotar a Vaati", 100, ("jefe_derrotado", 1)))

    secuaces = agregar_hijo(raiz, Nodo("Vencer a 2 secuaces de Vaati", 20, ("enemigos_vencidos", 2)))
    agregar_hijo(secuaces, Nodo("Recibir la bendición de la Gran Hada", 10, ("hadas", 1)))

    return raiz


# ----------------------------------------------------------------------
# Recorridos
# ----------------------------------------------------------------------

def estado_de(nodo, padre_completado):
    """Texto del estado de una misión: completada, disponible o bloqueada. O(1)."""
    if nodo.completada:
        return "completada"
    return "disponible" if padre_completado else "bloqueada"


def imprimir_preorden(nodo, nivel=0, padre_completado=True):
    """
    PREORDEN (raíz y luego cada hijo): imprime el árbol con sangría según el
    nivel, su estado y su recompensa. Es un DFS sobre el árbol.
    Caso base: una hoja (el ciclo no hace llamadas).
    Complejidad: O(n), cada misión se imprime una vez.
    """
    sangria = "    " * nivel
    estado = estado_de(nodo, padre_completado)
    extra = f" (+{nodo.recompensa} rupias)" if nodo.recompensa else ""
    print(f"  {sangria}[{estado:^10}] {nodo.nombre}{extra}")
    for hijo in nodo.hijos:
        imprimir_preorden(hijo, nivel + 1, nodo.completada)


def recorrido_por_niveles(raiz):
    """
    Recorrido POR NIVELES (BFS sobre el árbol) con una cola deque.
    Retorna una lista de niveles; cada nivel es una lista de tuplas
    (nodo, padre_completado). El juego lo usa para mostrar las misiones
    disponibles agrupadas por etapa.
    Complejidad: O(n).
    """
    niveles = []
    cola = deque([(raiz, 0, True)])
    while cola:
        nodo, nivel, padre_completado = cola.popleft()
        if nivel == len(niveles):
            niveles.append([])
        niveles[nivel].append((nodo, padre_completado))
        for hijo in nodo.hijos:
            cola.append((hijo, nivel + 1, nodo.completada))
    return niveles


def recompensa_rama(nodo, obtenidas=False):
    """
    POSTORDEN: primero suma las recompensas de los hijos y al final la del
    nodo. Con obtenidas=True suma solo las misiones completadas; con False,
    solo las que faltan.
    Caso base: una hoja devuelve su propia recompensa (o 0).
    Complejidad: O(n) para la rama.
    """
    total = 0
    for hijo in nodo.hijos:
        total += recompensa_rama(hijo, obtenidas)
    if nodo.completada == obtenidas:
        total += nodo.recompensa
    return total


def altura(nodo):
    """Altura del árbol: aristas del camino más largo a una hoja. O(n)."""
    if not nodo.hijos:
        return 0
    return 1 + max(altura(hijo) for hijo in nodo.hijos)


def contar_misiones(nodo):
    """Número total de misiones (n). Complejidad: O(n)."""
    return 1 + sum(contar_misiones(hijo) for hijo in nodo.hijos)


def contar_completadas(nodo):
    """Número de misiones completadas. Complejidad: O(n)."""
    return int(nodo.completada) + sum(contar_completadas(h) for h in nodo.hijos)


# ----------------------------------------------------------------------
# Búsqueda y dependencias
# ----------------------------------------------------------------------

def buscar_mision(nodo, nombre, padre=None):
    """
    Busca una misión por nombre (sin distinguir mayúsculas) y retorna la
    tupla (mision, padre), o (None, None) si no existe.
    Complejidad: O(n) en el peor caso.
    """
    if not isinstance(nombre, str):
        return None, None
    if nodo.nombre.strip().lower() == nombre.strip().lower():
        return nodo, padre
    for hijo in nodo.hijos:
        encontrada, su_padre = buscar_mision(hijo, nombre, nodo)
        if encontrada is not None:
            return encontrada, su_padre
    return None, None


def asignar_puerta(raiz, nombre, puerta):
    """
    Indica qué puerta (clave tupla) abre una misión al completarse.
    Retorna True si la misión existe. Complejidad: O(n).
    """
    mision, _ = buscar_mision(raiz, nombre)
    if mision is None:
        print(f"[!] No existe la misión '{nombre}'.")
        return False
    mision.puerta = puerta
    return True


def misiones_disponibles(nodo, padre_completado=True, resultado=None):
    """
    Misiones DISPONIBLES: no completadas y con el padre completado (la raíz
    está disponible desde el inicio). Retorna la lista de nodos en preorden.
    Complejidad: O(n).
    """
    if resultado is None:
        resultado = []
    if not nodo.completada and padre_completado:
        resultado.append(nodo)
    for hijo in nodo.hijos:
        misiones_disponibles(hijo, nodo.completada, resultado)
    return resultado


def completar_mision(raiz, nombre):
    """
    Completa una misión SOLO si está desbloqueada.
    Casos límite: misión inexistente, ya completada o bloqueada -> mensaje
    y None, sin cerrar el programa.
    Complejidad: O(n), por la búsqueda.
    Retorna el nodo completado, o None si no se pudo.
    """
    mision, padre = buscar_mision(raiz, nombre)
    if mision is None:
        print(f"  [!] La misión '{nombre}' no existe en las crónicas de Hyrule.")
        return None
    if mision.completada:
        print(f"  [!] '{mision.nombre}' ya estaba completada.")
        return None
    if padre is not None and not padre.completada:
        print(f"  [X] '{mision.nombre}' está bloqueada: primero completa '{padre.nombre}'.")
        return None
    mision.completada = True
    return mision


def condicion_cumplida(mision, indicadores):
    """
    Revisa si se cumple la condición de una misión con los indicadores del
    estado del mundo (diccionario). Usa .get() por si falta un indicador.
    Complejidad: O(1).
    """
    if mision.condicion is None:
        return False
    indicador, cantidad = mision.condicion
    return indicadores.get(indicador, 0) >= cantidad


def revisar_misiones(raiz, indicadores):
    """
    Completa automáticamente toda misión disponible cuya condición ya se
    cumple. Repite mientras haya cambios, porque completar una misión puede
    desbloquear a su hija y su condición quizá ya se cumplía (cascada).

    Retorna la lista de misiones completadas en esta revisión.
    Complejidad: O(n · k), con k = misiones completadas en la cascada
    (k ≤ n, y en la práctica 0, 1 o 2).
    """
    completadas = []
    hubo_cambio = True
    while hubo_cambio:
        hubo_cambio = False
        for mision in misiones_disponibles(raiz):
            if condicion_cumplida(mision, indicadores):
                mision.completada = True
                completadas.append(mision)
                hubo_cambio = True
    return completadas


# ----------------------------------------------------------------------
# Vista para el menú
# ----------------------------------------------------------------------

def mostrar_misiones(raiz, indicadores=None):
    """
    Muestra el árbol con los tres recorridos que usa el juego:
        - preorden: el árbol con sangría y el estado de cada misión;
        - por niveles: las misiones disponibles agrupadas por etapa, con
          el progreso de su condición;
        - postorden: las rupias ganadas y las pendientes de cada rama.
    Complejidad: O(n).
    """
    indicadores = indicadores or {}
    print("\n=============== MISIONES DEL PALACIO ===============")
    imprimir_preorden(raiz)
    print(f"\n  Completadas: {contar_completadas(raiz)} de {contar_misiones(raiz)}"
          f" | Altura del árbol: {altura(raiz)}")

    print("\n  Disponibles por etapa (recorrido por niveles):")
    hay = False
    for numero, nivel in enumerate(recorrido_por_niveles(raiz)):
        disponibles = [n for n, padre_ok in nivel if not n.completada and padre_ok]
        for mision in disponibles:
            hay = True
            progreso = ""
            if mision.condicion:
                ind, cant = mision.condicion
                progreso = f"  [{min(indicadores.get(ind, 0), cant)}/{cant}]"
            print(f"    Etapa {numero}: {mision.nombre}{progreso}")
    if not hay:
        print("    Ninguna: ¡Link completó todas las misiones!")

    print("\n  Rupias por rama (postorden):")
    for rama in raiz.hijos:
        print(f"    {rama.nombre}: ganadas {recompensa_rama(rama, True)},"
              f" pendientes {recompensa_rama(rama, False)}")
    print("====================================================")


# ----------------------------------------------------------------------
# Autoprueba
# ----------------------------------------------------------------------

if __name__ == "__main__":
    arbol = construir_arbol_misiones(3)
    ind = {"salas_visitadas": 4, "tesoros_recogidos": 1}
    print("Completadas:", [m.nombre for m in revisar_misiones(arbol, ind)])
    mostrar_misiones(arbol, ind)
    print("\n--- Casos límite ---")
    completar_mision(arbol, "Misión que no existe")
    completar_mision(arbol, "Explorar 3 salas")
    completar_mision(arbol, "Derrotar a Vaati")
    print("Sin cambios nuevos:", revisar_misiones(arbol, ind))
