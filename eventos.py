"""
Módulo de eventos y turnos - Checkpoint 2 (Aventura Algorítmica)
La Leyenda de Zelda: El Ascenso de Vaati

Implementa dos mecánicas basadas en una COLA (Queue - FIFO: First In, First Out):
    1. La cola de eventos de Hyrule: rupias, trampas, cofres y enemigos que
       aparecen en el orden en que fueron encolados al iniciar la partida.
    2. El sistema de turnos de combate: Link y los secuaces de Vaati actúan
       por orden y, al terminar, vuelven a formarse al final de la fila.

¿Por qué collections.deque y no una lista normal?
    Una lista de Python guarda sus elementos en un bloque contiguo de memoria.
    Al ejecutar list.pop(0) se elimina el primer elemento y TODOS los demás
    deben desplazarse una posición hacia la izquierda para cerrar el hueco:
    eso cuesta O(n), y en una cola que se vacía elemento por elemento el costo
    total crece a O(n^2).

    collections.deque (double-ended queue) está implementada como una lista
    doblemente enlazada de bloques. Mantiene referencias directas a ambos
    extremos, así que quitar el primer elemento con popleft() solo mueve un
    puntero: O(1), sin desplazar nada en memoria.

Operaciones principales de la cola:
    - Encolar    -> cola.append(x)    O(1)
    - Desencolar -> cola.popleft()    O(1)
    - Consultar el frente -> cola[0]  O(1)
    - Tamaño     -> len(cola)         O(1)

Nunca se usa list.pop(0) en este módulo.
"""

from collections import deque


# ----------------------------------------------------------------------
# Funciones auxiliares (privadas)
# ----------------------------------------------------------------------

def _es_cola_valida(cola):
    """
    Verifica que la estructura recibida sea una collections.deque.
    Evita que el programa se caiga si se pasa una lista, None u otro tipo.
    Complejidad: O(1).
    """
    if not isinstance(cola, deque):
        print("[!] La magia de Hyrule falla: la estructura recibida no es una cola (deque) válida.")
        return False
    return True


def _validar_entero_positivo(n, contexto):
    """
    Convierte 'n' a entero positivo. Acepta enteros o texto numérico (por si
    viene de input()). Rechaza booleanos, decimales, texto no numérico, 0 y
    negativos. Retorna el entero o None si no es válido.
    Complejidad: O(1).
    """
    if isinstance(n, bool) or not isinstance(n, (int, str)):
        print(f"[!] {contexto}: debes indicar un número entero.")
        return None
    try:
        n = int(n)
    except ValueError:
        print(f"[!] {contexto}: '{n}' no es un número entero válido.")
        return None
    if n <= 0:
        print(f"[!] {contexto}: el número debe ser mayor que 0.")
        return None
    return n


def _narrar_evento(evento):
    """
    Genera una narración inmersiva según el tipo de evento, buscando palabras
    clave en el texto (rupia, trampa, cofre, moblin, keese, etc.).
    No modifica la cola.
    Complejidad: O(1) respecto al tamaño de la cola.
    """
    texto = evento.lower()
    if "rupia" in texto:
        return f"💎 ¡Tintineo de rupias! {evento}."
    if "trampa" in texto or "pinchos" in texto or "foso" in texto:
        return f"⚠️  ¡Cuidado, Link! {evento}. Saltas justo a tiempo con la Pluma de Roc."
    if "cofre" in texto:
        return f"🎁 ¡Da-da-da-daaa! {evento}."
    if "moblin" in texto or "keese" in texto or "octorok" in texto or "chuchu" in texto or "darknut" in texto:
        return f"⚔️  ¡Un secuaz de Vaati aparece! {evento}. Desenvainas la Espada Minish."
    if "vaati" in texto:
        return f"🌀 Un viento oscuro recorre la sala... {evento}."
    if "hada" in texto or "corazón" in texto or "corazon" in texto:
        return f"✨ Una luz cálida te rodea. {evento}."
    return f"📯 {evento}."


def tipo_de_evento(evento):
    """
    Clasifica un evento para el estado del mundo (Checkpoint 3):
    "enemigo", "rupias", "trampa", "hada", "vaati" u "otro".
    El diccionario de estado cuenta cuántos eventos de cada tipo vivió Link,
    y esos conteos completan misiones (por ejemplo, vencer a 2 secuaces).
    Complejidad: O(1) respecto al tamaño de la cola.
    """
    if not isinstance(evento, str):
        return "otro"
    texto = evento.lower()
    if any(e in texto for e in ("moblin", "keese", "octorok", "chuchu", "darknut")):
        return "enemigo"
    if "rupia" in texto:
        return "rupias"
    if "trampa" in texto or "pinchos" in texto:
        return "trampa"
    if "hada" in texto:
        return "hada"
    if "vaati" in texto:
        return "vaati"
    return "otro"


# ----------------------------------------------------------------------
# Funciones obligatorias de la cola de eventos
# ----------------------------------------------------------------------

def inicializar_cola_eventos(lista_eventos):
    """
    Recibe una lista normal de eventos (strings) y retorna una deque con ellos,
    respetando el orden original: el primer evento de la lista será el primero
    en procesarse (FIFO).

    Casos límite:
        - Si no se recibe una lista o tupla, se retorna una deque vacía.
        - Se descartan los eventos que no sean texto o que estén vacíos.

    Complejidad: O(n), se recorre cada evento una vez para validarlo y
    encolarlo con append() (O(1) cada uno).
    """
    cola = deque()

    if not isinstance(lista_eventos, (list, tuple)):
        print("[!] Los mapas de Hyrule están en blanco: no se recibió una lista de eventos válida.")
        return cola

    descartados = 0
    for evento in lista_eventos:
        if isinstance(evento, str) and evento.strip() != "":
            cola.append(evento.strip())
        else:
            descartados += 1

    if descartados > 0:
        print(f"[!] Se descartaron {descartados} evento(s) inválido(s) al preparar la mazmorra.")

    print(f"[🗺️ ] El destino de Hyrule está escrito: {len(cola)} evento(s) aguardan a Link.")
    return cola


def encolar_evento(cola_eventos, evento):
    """
    Agrega un nuevo evento al FINAL de la cola, para que se procese después
    de todos los que ya estaban esperando (FIFO).

    Complejidad: O(1), append() en una deque solo enlaza el nuevo elemento
    en el extremo derecho.

    Retorna True si el evento se encoló, False si no era válido.
    """
    if not _es_cola_valida(cola_eventos):
        return False
    if not isinstance(evento, str) or evento.strip() == "":
        print("[!] No se puede encolar un evento vacío en las tierras de Hyrule.")
        return False

    cola_eventos.append(evento.strip())
    return True


def procesar_siguiente_evento(cola_eventos):
    """
    Extrae, narra y devuelve el siguiente evento de la cola (el más antiguo).

    FIFO: popleft() retira el elemento del FRENTE de la cola, es decir, el que
    llegó primero. Así los eventos ocurren en el mismo orden en que se
    encolaron al iniciar la partida.

    ¿Por qué deque.popleft() y no list.pop(0)?
        - list.pop(0) es O(n): al quitar el primer elemento de una lista,
          Python debe desplazar todos los elementos restantes una posición
          en memoria para mantener el bloque contiguo.
        - deque.popleft() es O(1): la deque mantiene un puntero al extremo
          izquierdo; quitar el primer elemento solo actualiza ese puntero,
          sin mover ningún otro dato.
        Como cada movimiento de Link dispara un popleft(), usar deque mantiene
        el juego eficiente sin importar cuántos eventos tenga el mapa.

    Caso límite: si la cola está vacía, NO se llama a popleft() (lanzaría
    IndexError). Se informa que la sala está despejada y se retorna None.

    Complejidad: O(1).
    """
    if not _es_cola_valida(cola_eventos):
        return None

    if len(cola_eventos) == 0:
        print("[🍃] La sala está despejada. Solo se escucha el viento de Hyrule... "
              "No quedan eventos por procesar.")
        return None

    evento = cola_eventos.popleft()
    print(f"[Evento] {_narrar_evento(evento)} (quedan {len(cola_eventos)} evento(s))")
    return evento


# ----------------------------------------------------------------------
# Adaptaciones de la Guía 6
# ----------------------------------------------------------------------

def simular_turnos(participantes):
    """
    Simula UNA ronda completa de combate: cada participante actúa exactamente
    una vez, en orden de llegada.

    FIFO cíclico (Round Robin):
        1. popleft() saca al participante que está al frente: es su turno.
        2. Ese participante actúa (ataca).
        3. append() lo vuelve a formar al final de la cola.
    Tras una ronda de len(participantes) turnos, la cola queda en el mismo
    orden inicial, lista para la siguiente ronda.

    Casos límite:
        - Si no es una deque, se muestra un mensaje y no se simula nada.
        - Si hay menos de 3 participantes, se avisa y no se simula.

    Complejidad: O(k), donde k es el número de participantes; cada
    popleft() y cada append() son O(1).

    Retorna una lista con el orden en que actuaron los participantes.
    """
    if not _es_cola_valida(participantes):
        return []

    if len(participantes) < 3:
        print(f"[!] El combate necesita al menos 3 participantes; solo hay {len(participantes)}.")
        return []

    acciones_por_nombre = {
        "link": "blande la Espada Minish con un giro de espada",
        "moblin": "embiste con su lanza",
        "octorok": "escupe una roca",
        "keese": "revolotea y muerde",
        "chuchu": "se lanza saltando",
        "darknut": "golpea con su espadón",
        "vaati": "lanza una ráfaga de viento oscuro",
    }

    orden_de_accion = []
    total = len(participantes)

    print("\n============ RONDA DE COMBATE ============")
    print(f"Orden de la cola: {' -> '.join(str(p) for p in participantes)}")

    for turno in range(1, total + 1):
        actual = participantes.popleft()           # O(1): sale del frente
        nombre = str(actual)
        accion = "ataca con todas sus fuerzas"
        for clave, descripcion in acciones_por_nombre.items():
            if clave in nombre.lower():
                accion = descripcion
                break
        print(f"  Turno {turno}: {nombre} {accion}.")
        orden_de_accion.append(nombre)
        participantes.append(actual)               # O(1): vuelve al final

    print(f"Fin de la ronda. Próximo en actuar: {participantes[0]}")
    print("==========================================\n")
    return orden_de_accion


def procesar_multiples_eventos(cola_eventos, n):
    """
    Procesa 'n' eventos consecutivos en orden de llegada usando popleft().

    FIFO: en cada iteración se retira el evento del frente, por lo que los
    eventos salen exactamente en el orden en que fueron encolados.

    Casos límite:
        - n no es un entero, es 0 o negativo: mensaje y lista vacía.
        - La cola ya está vacía: mensaje y lista vacía.
        - La cola se vacía antes de completar los 'n' eventos: se detiene
          el bucle sin error y se informa cuántos se procesaron.

    Complejidad: O(k), donde k = mínimo entre n y el tamaño de la cola,
    porque cada popleft() es O(1).

    Retorna una lista con los eventos procesados, en orden de llegada.
    """
    if not _es_cola_valida(cola_eventos):
        return []

    n = _validar_entero_positivo(n, "La cola de eventos de Hyrule")
    if n is None:
        return []

    if len(cola_eventos) == 0:
        print("[🍃] No hay eventos que procesar: Hyrule está en calma por ahora.")
        return []

    print(f"[⏩] Link avanza decidido por la mazmorra... procesando hasta {n} evento(s).")
    procesados = []
    for _ in range(n):
        if len(cola_eventos) == 0:
            print(f"[!] La cola se vació antes de tiempo: solo se procesaron "
                  f"{len(procesados)} de {n} evento(s).")
            break
        evento = cola_eventos.popleft()
        procesados.append(evento)
        print(f"  [Evento {len(procesados)}] {_narrar_evento(evento)}")

    print(f"[✔] Eventos procesados: {len(procesados)}. Quedan en la cola: {len(cola_eventos)}.")
    return procesados


def mostrar_cola_eventos(cola_eventos):
    """
    Muestra los eventos pendientes desde el FRENTE (el próximo en ocurrir)
    hasta el FINAL (el último en ocurrir), sin modificar la cola.

    Complejidad: O(n), se recorre cada evento una vez (solo lectura).
    """
    if not _es_cola_valida(cola_eventos):
        return

    print("\n======== EVENTOS PENDIENTES EN HYRULE ========")
    if len(cola_eventos) == 0:
        print("  No quedan eventos: la mazmorra está en silencio.")
    else:
        for posicion, evento in enumerate(cola_eventos, start=1):
            marca = "  <- frente (próximo)" if posicion == 1 else ""
            print(f"  {posicion}. {evento}{marca}")
    print("==============================================\n")


# ----------------------------------------------------------------------
# Prueba rápida del módulo (solo se ejecuta si se corre este archivo directamente)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("--- Inicializando eventos del mapa ---")
    eventos = inicializar_cola_eventos([
        "Un Moblin te bloquea el paso en el puente",
        "Encuentras 20 rupias rojas entre la hierba",
        "",                                   # caso límite: evento vacío
        "Una trampa de pinchos se activa bajo tus pies",
        "Una bandada de Keese desciende del techo",
        "Encuentras un cofre con un Fragmento de Corazón",
        42,                                   # caso límite: no es texto
    ])
    mostrar_cola_eventos(eventos)

    print("--- Procesando eventos uno por uno ---")
    procesar_siguiente_evento(eventos)
    procesar_siguiente_evento(eventos)

    print("\n--- Procesando múltiples eventos ---")
    procesar_multiples_eventos(eventos, "abc")   # caso límite: texto
    procesar_multiples_eventos(eventos, 0)       # caso límite: cero
    procesar_multiples_eventos(eventos, -2)      # caso límite: negativo
    procesar_multiples_eventos(eventos, 10)      # caso límite: más de los que hay

    print("\n--- Cola vacía ---")
    procesar_siguiente_evento(eventos)           # caso límite: cola vacía

    print("\n--- Sistema de turnos ---")
    combatientes = deque(["Link", "Moblin", "Octorok"])
    simular_turnos(combatientes)
    simular_turnos(deque(["Link", "Keese"]))     # caso límite: menos de 3
    simular_turnos(["Link", "Moblin", "Octorok"])  # caso límite: lista, no deque