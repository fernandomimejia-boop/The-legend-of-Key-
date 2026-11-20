"""
Archivo central - Aventura Algorítmica (Checkpoint 2)
La Leyenda de Zelda: El Ascenso de Vaati

Integra en una partida jugable las cuatro estructuras del proyecto:
    - inventario.py -> Lista   (Checkpoint 1): objetos de Link.
    - historial.py  -> Pila    (LIFO): acciones de Link y deshacer (backtracking).
    - eventos.py    -> Cola    (FIFO, deque): eventos del mapa y turnos de combate.
    - mazmorra.py   -> Recursividad: generación del Palacio de los Vientos.

Decisiones de diseño (documentadas también en el README):
    1. Eventos al deshacer: el evento procesado al entrar a una sala SE PIERDE
       (no vuelve a la cola). En la lógica del juego, lo que ocurrió en Hyrule
       ya ocurrió; deshacer devuelve a Link a la sala anterior, pero no revive
       al enemigo ni repone la trampa. Así la cola sigue siendo FIFO pura
       (solo append para encolar y popleft para desencolar).
    2. Recoger objetos también se registra en el historial. Si la última acción
       fue "Recoger", deshacer devuelve el objeto al cofre (sale del inventario)
       y Link se queda en la sala; un segundo deshacer revierte el movimiento.
       Esto respeta el orden LIFO: se deshace siempre lo más reciente.
    3. Ocarina del Viento (deshacer_multiples, Guía 5): deshace varias acciones
       de una vez y aplica el efecto de cada una en orden LIFO, así que Link
       termina en la sala desde la que hizo el movimiento más antiguo deshecho.
    4. Explorar la sala (procesar_multiples_eventos, Guía 6): Link se queda en
       la sala y enfrenta los siguientes 'n' eventos de la cola en orden FIFO.
    5. Usar un objeto (usar_objeto, Checkpoint 1): se registra en el historial.
       Deshacerlo no cambia la sala ni el inventario, porque usar un objeto no
       lo consume.
"""

import sys
from collections import deque

import inventario
import historial
import eventos
import mazmorra


# ----------------------------------------------------------------------
# Constantes del menú
# ----------------------------------------------------------------------

OPCION_MOVERSE = 1
OPCION_INVENTARIO = 2
OPCION_USAR = 3
OPCION_DESHACER = 4
OPCION_OCARINA = 5
OPCION_HISTORIAL = 6
OPCION_EXPLORAR = 7
OPCION_TURNOS = 8
OPCION_SALIR = 9

# Objetos con los que Link empieza la aventura (lore del Checkpoint 1)
OBJETOS_INICIALES = ["Espada Minish", "Pluma de Roc"]

# ROBUSTEZ: en Windows, si la salida se redirige a un archivo (por ejemplo,
# "python main.py > evidencia.txt") o la consola no usa UTF-8, imprimir
# emojis o tildes lanza UnicodeEncodeError. Se fuerza UTF-8 y, si algún
# carácter no se puede mostrar, se reemplaza en lugar de cerrar el juego.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


# ----------------------------------------------------------------------
# Funciones de apoyo de main.py
# ----------------------------------------------------------------------

def leer_entrada(mensaje):
    """
    Lee texto del usuario sin que el programa se caiga.
    ROBUSTEZ: si el usuario presiona Ctrl+C o la entrada se termina (EOF),
    input() lanzaría KeyboardInterrupt/EOFError en CADA llamada; devolver None
    provocaría un ciclo infinito. Por eso se cierra la partida de forma
    ordenada con SystemExit(0): sin traceback y sin código de error.
    """
    try:
        return input(mensaje)
    except (EOFError, KeyboardInterrupt):
        print("\n[!] La conexión con la Trifuerza se interrumpió. Link guarda su progreso y descansa.")
        raise SystemExit(0)


def leer_opcion_numerica(mensaje, minimo, maximo):
    """
    Pide un número entero y valida que esté en el rango [minimo, maximo].

    ROBUSTEZ (casos límite de cualquier menú):
        - Texto o símbolos  -> int() lanza ValueError, se captura con try/except.
        - Entrada vacía     -> también ValueError.
        - 0, negativos o fuera de rango -> se valida el rango explícitamente.
    Retorna el número válido, o None si la entrada no es válida
    (quien llama decide hacer 'continue').
    """
    texto = leer_entrada(mensaje)
    if texto is None:
        return None

    try:
        numero = int(texto.strip())
    except ValueError:
        print(f"[!] '{texto.strip()}' no es una opción válida. "
              f"Las runas de Hyrule solo aceptan números del {minimo} al {maximo}.")
        return None

    if numero < minimo or numero > maximo:
        print(f"[!] Opción fuera de rango. Elige un número del {minimo} al {maximo}.")
        return None

    return numero


def mostrar_encabezado():
    """Imprime la portada temática del juego."""
    print("==================================================")
    print("     LA LEYENDA DE ZELDA: EL ASCENSO DE VAATI     ")
    print("        Aventura Algorítmica - Checkpoint 2       ")
    print("==================================================")
    print("Héroe: Link | Antagonista: Vaati | Región: Hyrule\n")


def mostrar_menu(sala_actual):
    """Muestra la ubicación de Link y las opciones del menú principal."""
    print("\n--------------------------------------------------")
    print(f"📍 Link está en: {sala_actual}")
    print("--------------------------------------------------")
    print("1. Moverse a otra sala")
    print("2. Ver inventario")
    print("3. Usar un objeto")
    print("4. Deshacer última acción")
    print("5. Tocar la Ocarina del Viento (deshacer varias acciones)")
    print("6. Ver historial completo")
    print("7. Explorar la sala (resolver varios eventos)")
    print("8. Simular turnos de batalla")
    print("9. Salir del juego")


def mostrar_inventario(mochila):
    """
    Muestra el inventario de Link (Checkpoint 1: lista).
    Maneja el caso de inventario vacío.
    """
    print("\n============ BOLSA DE OBJETOS DE LINK ============")
    if len(mochila) == 0:
        print("  La bolsa está vacía. Explora las salas marcadas para encontrar tesoros.")
    else:
        for i, objeto in enumerate(mochila, start=1):
            print(f"  {i}. {objeto}")
    print("==================================================")


def intentar_recoger_tesoro(sala, mochila, cronicas, tesoros_recogidos):
    """
    INTEGRACIÓN (d): si la sala está marcada como sala profunda ([JEFE VAATI]
    o [COFRE: ...]), Link obtiene su objeto, que entra al inventario del
    Checkpoint 1 y se registra en el historial como acción "Recoger".

    Nota: el generador marca las salas con "[JEFE VAATI]" y "[COFRE: objeto]",
    por eso se usa mazmorra.es_sala_marcada() en lugar de buscar el texto
    literal "[JEFE]" o "[COFRE]".

    Un tesoro solo puede recogerse una vez (conjunto tesoros_recogidos).
    """
    if not mazmorra.es_sala_marcada(sala):
        return

    if sala in tesoros_recogidos:
        print("[i] El cofre de esta sala ya está abierto. Aquí no queda nada más.")
        return

    objeto = mazmorra.obtener_objeto_de_sala(sala)
    if objeto is None:
        return

    if "[JEFE VAATI]" in sala:
        print("\n🌀 ¡Vaati aparece envuelto en un torbellino oscuro!")
        print("⚔️  Link resiste el viento y lo derrota con la Espada Minish.")
        print(f"✨ Vaati deja caer el {objeto}.")
    else:
        print("\n🎁 ¡Da-da-da-daaa! Link abre un cofre antiguo.")

    inventario.agregar_objeto(mochila, objeto)                 # Checkpoint 1: lista
    tesoros_recogidos.add(sala)
    historial.registrar_accion(cronicas, {"tipo": "Recoger",   # Pila: append
                                          "objeto": objeto,
                                          "sala": sala})


def accion_moverse(mapa, sala_actual, cola_eventos, cronicas, mochila, tesoros_recogidos):
    """
    Opción 1. Muestra las salas conectadas, valida la elección y mueve a Link.

    INTEGRACIÓN:
        (a) Registra el movimiento en el historial con {'desde', 'hacia'}.
        (b) Actualiza la sala actual (se retorna la nueva sala).
        (c) Dispara el siguiente evento de la cola (popleft).
        (d) Si la sala está marcada, Link recoge su objeto.

    ROBUSTEZ: valida por índice que la sala elegida exista entre las opciones
    presentadas y, además, que exista la conexión en el mapa.

    Retorna la sala donde queda Link (la misma si el movimiento no se hizo).
    """
    conectadas = mazmorra.obtener_salas_conectadas(mapa, sala_actual)

    if len(conectadas) == 0:
        print("[!] No hay puertas en esta sala. Link no puede avanzar.")
        return sala_actual

    print("\n🚪 Puertas disponibles:")
    for i, sala in enumerate(conectadas, start=1):
        print(f"  {i}) {sala}")
    opcion_quedarse = len(conectadas) + 1
    print(f"  {opcion_quedarse}) Quedarse en esta sala")

    # ROBUSTEZ: validación por rango de índices (evita que lista[-1] o un índice
    # fuera de rango seleccionen una sala que no fue presentada)
    eleccion = leer_opcion_numerica("Elige una sala: ", 1, opcion_quedarse)
    if eleccion is None:
        print("[i] Link duda frente a las puertas y se queda donde está.")
        return sala_actual

    if eleccion == opcion_quedarse:
        print("[i] Link decide no moverse por ahora.")
        return sala_actual

    destino = conectadas[eleccion - 1]

    # ROBUSTEZ: doble verificación de que la conexión existe en el grafo
    if not mazmorra.existe_conexion(mapa, sala_actual, destino):
        print(f"[!] No hay un camino directo hacia '{destino}'.")
        return sala_actual

    # (a) Registrar el movimiento en la pila (backtracking real con 'desde'/'hacia')
    movimiento = {
        "tipo": "Moverse",
        "desde": sala_actual,
        "hacia": destino,
        "detalle": f"de '{sala_actual}' a '{destino}'",
    }
    historial.registrar_accion(cronicas, movimiento)

    # (b) Actualizar la ubicación de Link
    print(f"\n🏃 Link se mueve a: {destino}")
    sala_actual = destino

    # (c) Cada movimiento dispara el siguiente evento de la cola (FIFO, popleft)
    evento = eventos.procesar_siguiente_evento(cola_eventos)
    if evento is not None:
        movimiento["evento"] = evento   # Se guarda solo como referencia; al deshacer se pierde

    # (d) Si la sala está marcada, Link obtiene un objeto para el inventario
    intentar_recoger_tesoro(sala_actual, mochila, cronicas, tesoros_recogidos)

    return sala_actual


def revertir_accion(accion, sala_actual, mochila, tesoros_recogidos):
    """
    Aplica en el juego el efecto de UNA acción que ya salió de la pila.
    La usan tanto el deshacer simple como la Ocarina del Viento.

    - Moverse: BACKTRACKING real, Link vuelve a la sala 'desde'.
    - Recoger: el objeto sale del inventario y vuelve a su cofre; Link se
      queda en la sala.
    - Usar: usar un objeto no lo consume, así que solo se informa.

    Retorna la sala donde queda Link.
    """
    if not isinstance(accion, dict):
        print("[i] La acción deshecha no implicaba moverse. Link sigue en la misma sala.")
        return sala_actual

    tipo = accion.get("tipo")

    if tipo == "Moverse":
        sala_anterior = accion.get("desde")
        if sala_anterior is None:
            print("[!] Las crónicas no indican de dónde venía Link. Se queda en su sala.")
            return sala_actual
        print(f"[⏪] Un remolino arrastra a Link de vuelta a: {sala_anterior}")
        print("     (El evento de la sala que dejaste ya ocurrió y no regresa a la cola.)")
        return sala_anterior

    if tipo == "Recoger":
        objeto = accion.get("objeto")
        sala_tesoro = accion.get("sala")
        if objeto in mochila:
            inventario.soltar_objeto(mochila, objeto)        # Checkpoint 1: remove()
        tesoros_recogidos.discard(sala_tesoro)
        print(f"[⏪] El {objeto} regresa a su cofre. Link sigue en: {sala_actual}")
        return sala_actual

    if tipo == "Usar":
        print(f"[⏪] El efecto de {accion.get('objeto')} se desvanece. "
              "El objeto sigue en la bolsa de Link.")
        return sala_actual

    print("[i] Acción deshecha. Link permanece en su sala.")
    return sala_actual


def accion_deshacer(sala_actual, cronicas, mochila, tesoros_recogidos):
    """
    Opción 4. Deshace la última acción con pop() (LIFO) y aplica su efecto.
    Si el historial está vacío, historial.deshacer_ultima_accion() muestra
    el mensaje y retorna None; main.py no cambia de sala.
    Retorna la sala donde queda Link.
    """
    accion = historial.deshacer_ultima_accion(cronicas)

    # ROBUSTEZ: historial vacío -> None, Link se queda donde está
    if accion is None:
        return sala_actual

    sala_actual = revertir_accion(accion, sala_actual, mochila, tesoros_recogidos)
    if isinstance(accion, dict) and accion.get("tipo") == "Recoger":
        print("     Deshaz de nuevo si quieres volver a la sala anterior.")
    return sala_actual


def accion_ocarina(sala_actual, cronicas, mochila, tesoros_recogidos):
    """
    Opción 5. INTEGRACIÓN de la Guía 5: historial.deshacer_multiples().

    Link toca la Ocarina del Viento para deshacer varias acciones de una vez.
    deshacer_multiples() hace pop() 'n' veces y devuelve las acciones en el
    orden en que salieron (de la más reciente a la más antigua). main.py
    aplica el efecto de cada una en ese mismo orden (LIFO), así que, si se
    deshacen varios movimientos, Link termina en la sala desde la que hizo
    el movimiento más antiguo de los deshechos.

    ROBUSTEZ:
        - Historial vacío: deshacer_multiples() avisa y retorna [], Link no se mueve.
        - Cantidad inválida (texto, 0, negativos o mayor que el historial):
          se rechaza con leer_opcion_numerica y no se deshace nada.

    Retorna la sala donde queda Link.
    """
    if len(cronicas) == 0:
        historial.deshacer_multiples(cronicas, 1)   # Delega el mensaje de historial vacío
        return sala_actual

    n = leer_opcion_numerica(f"¿Cuántas acciones quieres deshacer? (1 a {len(cronicas)}): ",
                             1, len(cronicas))
    if n is None:
        print("[i] Link baja la Ocarina sin tocar la melodía. Nada cambia.")
        return sala_actual

    deshechas = historial.deshacer_multiples(cronicas, n)   # pop() x n
    for accion in deshechas:
        sala_actual = revertir_accion(accion, sala_actual, mochila, tesoros_recogidos)

    print(f"[🎶] Cuando el remolino se calma, Link está en: {sala_actual}")
    return sala_actual


def accion_usar_objeto(mochila, cronicas):
    """
    Opción 3. INTEGRACIÓN del Checkpoint 1: inventario.usar_objeto().

    Muestra los objetos de la bolsa, el jugador elige uno por número y se
    llama a usar_objeto() (búsqueda lineal O(n) con 'in'). Si el objeto se
    usó, la acción "Usar" se apila en el historial con append().

    ROBUSTEZ: bolsa vacía, texto, 0, negativos y números fuera de rango se
    manejan con un mensaje y sin cerrar el programa.
    """
    if len(mochila) == 0:
        print("[!] La bolsa de Link está vacía: no hay nada que usar.")
        return

    print("\n🎒 ¿Qué objeto quieres usar?")
    for i, objeto in enumerate(mochila, start=1):
        print(f"  {i}) {objeto}")
    opcion_cancelar = len(mochila) + 1
    print(f"  {opcion_cancelar}) Cancelar")

    eleccion = leer_opcion_numerica("Elige un objeto: ", 1, opcion_cancelar)
    if eleccion is None or eleccion == opcion_cancelar:
        print("[i] Link guarda sus objetos y sigue adelante.")
        return

    objeto = mochila[eleccion - 1]
    inventario.usar_objeto(mochila, objeto)                    # Checkpoint 1: búsqueda O(n)
    historial.registrar_accion(cronicas, {"tipo": "Usar",      # Pila: append
                                          "objeto": objeto})


def accion_explorar(cola_eventos):
    """
    Opción 7. INTEGRACIÓN de la Guía 6: eventos.procesar_multiples_eventos().

    Link se queda en la sala y explora a fondo: los siguientes 'n' eventos de
    la cola llegan a él en orden de llegada (popleft() 'n' veces, FIFO).
    Antes se muestran los eventos pendientes con mostrar_cola_eventos().

    ROBUSTEZ:
        - Cola vacía: procesar_multiples_eventos() avisa que Hyrule está en
          calma y retorna [], sin error.
        - Cantidad inválida (texto, 0, negativos o mayor que la cola): se
          rechaza y no se procesa nada.
    """
    if len(cola_eventos) == 0:
        eventos.procesar_multiples_eventos(cola_eventos, 1)   # Delega el mensaje de cola vacía
        return

    eventos.mostrar_cola_eventos(cola_eventos)
    n = leer_opcion_numerica(f"¿Cuántos eventos quieres enfrentar? (1 a {len(cola_eventos)}): ",
                             1, len(cola_eventos))
    if n is None:
        print("[i] Link prefiere no tentar a la suerte y sigue en guardia.")
        return

    eventos.procesar_multiples_eventos(cola_eventos, n)        # popleft() x n


def accion_ver_historial(cronicas):
    """
    Opción 6. Muestra la pila de la cima a la base, consulta la última
    acción sin sacarla (ver_ultima_accion) y resume con contar_acciones_de_tipo
    (adaptación de la Guía 5).
    """
    historial.mostrar_historial_completo(cronicas)
    historial.ver_ultima_accion(cronicas)          # Consultar la cima sin sacarla (peek)
    if len(cronicas) > 0:
        historial.contar_acciones_de_tipo(cronicas, "Moverse")
        historial.contar_acciones_de_tipo(cronicas, "Recoger")
        historial.contar_acciones_de_tipo(cronicas, "Usar")


# ----------------------------------------------------------------------
# Partida principal
# ----------------------------------------------------------------------

def main():
    """
    Punto de entrada del juego.

    1. Prepara la partida: genera la mazmorra con la función recursiva,
       ubica a Link en la sala inicial y crea el inventario (lista), el
       historial (pila), la cola de eventos (deque) y la cola de turnos.
    2. Ejecuta el menú dentro de un ciclo while True hasta que el jugador
       elige salir. Cada opción llama a las funciones importadas de los
       módulos; ninguna función se copia dentro de main.py.

    ROBUSTEZ: toda opción inválida (texto, 0, negativos o fuera de rango)
    muestra un mensaje y reinicia el ciclo con continue.
    """
    mostrar_encabezado()

    # ---------------- SETUP 1: mazmorra recursiva ----------------
    # crear_mazmorra() llama a la función recursiva generar_mazmorra() y
    # garantiza profundidad mínima 2 y al menos 7 salas.
    mapa = mazmorra.crear_mazmorra(profundidad_maxima=3, limite_salas=15)
    if not mapa:
        print("[!] El Palacio de los Vientos no pudo formarse. Fin de la aventura.")
        return
    mazmorra.imprimir_arbol_mazmorra(mapa)

    # ---------------- SETUP 2: sala inicial ----------------
    sala_actual = mazmorra.SALA_INICIAL

    # ---------------- SETUP 3: inventario (lista, Checkpoint 1) ----------------
    mochila_link = []
    tesoros_recogidos = set()
    print("\nEzlo te entrega el equipo de un héroe de Hyrule:")
    for objeto in OBJETOS_INICIALES:
        inventario.agregar_objeto(mochila_link, objeto)       # Checkpoint 1: append

    # ---------------- SETUP 4: historial (pila) ----------------
    cronicas = []

    # ---------------- SETUP 5: cola de eventos (deque) ----------------
    cola_eventos = eventos.inicializar_cola_eventos([
        "Un Moblin te bloquea el paso con su lanza",
        "Encuentras 20 rupias rojas ocultas en una vasija",
        "Una trampa de pinchos se activa bajo tus pies",
        "Una bandada de Keese desciende del techo",
        "Un Octorok dispara rocas desde un charco",
        "Un Chuchu Rojo brota del suelo y bloquea la puerta",
        "Una Gran Hada te restaura los corazones",
        "La risa de Vaati resuena entre los muros",
    ])

    # Participantes del sistema de turnos (cola circular, al menos 3)
    combatientes = deque(["Link", "Moblin", "Octorok"])

    print("\nEzlo te susurra: \"Link, Vaati se oculta en lo más profundo del palacio. ¡Encuéntralo!\"")

    # ---------------- BUCLE PRINCIPAL ----------------
    while True:
        mostrar_menu(sala_actual)

        # ROBUSTEZ: texto, símbolos, 0, negativos y fuera de rango -> continue
        opcion = leer_opcion_numerica("Opción: ", OPCION_MOVERSE, OPCION_SALIR)
        if opcion is None:
            continue

        if opcion == OPCION_MOVERSE:
            sala_actual = accion_moverse(mapa, sala_actual, cola_eventos,
                                         cronicas, mochila_link, tesoros_recogidos)

        elif opcion == OPCION_INVENTARIO:
            mostrar_inventario(mochila_link)

        elif opcion == OPCION_USAR:
            accion_usar_objeto(mochila_link, cronicas)

        elif opcion == OPCION_DESHACER:
            sala_actual = accion_deshacer(sala_actual, cronicas,
                                          mochila_link, tesoros_recogidos)

        elif opcion == OPCION_OCARINA:
            sala_actual = accion_ocarina(sala_actual, cronicas,
                                         mochila_link, tesoros_recogidos)

        elif opcion == OPCION_HISTORIAL:
            accion_ver_historial(cronicas)

        elif opcion == OPCION_EXPLORAR:
            accion_explorar(cola_eventos)

        elif opcion == OPCION_TURNOS:
            # Cola de turnos: popleft() para actuar y append() para volver a formarse
            eventos.simular_turnos(combatientes)

        elif opcion == OPCION_SALIR:
            print("\n==================================================")
            print("  Link guarda la Espada Minish y descansa.")
            print(f"  Objetos en la bolsa: {len(mochila_link)} | Acciones registradas: {len(cronicas)}")
            if "Elemento del Viento" in mochila_link:
                print("  ¡Vaati ha sido derrotado! Hyrule vuelve a estar en paz.")
            else:
                print("  Vaati sigue acechando... Hyrule espera tu regreso.")
            print("==================================================")
            break


if __name__ == "__main__":
    main()