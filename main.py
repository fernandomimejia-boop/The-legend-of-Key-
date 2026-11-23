"""
Archivo central - Aventura Algorítmica (Checkpoint 3)
La Leyenda de Zelda: El Ascenso de Vaati

Integra en una partida jugable todas las estructuras del proyecto:
    - inventario.py -> Lista      (Checkpoint 1): objetos de Link.
    - historial.py  -> Pila       (LIFO): acciones de Link y deshacer (backtracking).
    - eventos.py    -> Cola       (FIFO, deque): eventos del mapa y turnos de combate.
    - mazmorra.py   -> Recursividad: genera el Palacio de los Vientos (un árbol).
    - grafo.py      -> Grafo      (lista de adyacencia): el palacio con atajos,
                                   BFS para rutas y DFS para zonas alcanzables.
    - misiones.py   -> Árbol      de misiones que dependen de la anterior.
    - estado.py     -> Diccionario con el estado del mundo.

CÓMO TRABAJAN JUNTAS (Checkpoint 3):
    1. Link se mueve por las aristas del GRAFO. Las puertas selladas viven en
       el DICCIONARIO de estado (clave = tupla de dos salas) y el grafo las
       recibe como aristas bloqueadas: no se puede cruzar una puerta sellada.
    2. Cada acción actualiza el DICCIONARIO: salas visitadas, tesoros,
       eventos vividos y rupias.
    3. Después de cada acción, el ÁRBOL de misiones revisa esos números: si
       una misión disponible cumple su condición, se completa sola, da rupias
       y puede ABRIR una puerta (se elimina del diccionario).
    4. Al abrirse una puerta, BFS encuentra rutas nuevas (los atajos crean
       ciclos y caminos más cortos) y DFS deja de ver zonas aisladas.

Decisiones de diseño (documentadas también en el README):
    1. Eventos al deshacer: el evento procesado SE PIERDE (no vuelve a la cola).
    2. Recoger también se registra en el historial; deshacerlo devuelve el
       objeto a su cofre (inventario y diccionario de estado).
    3. Ocarina del Viento: deshace varias acciones en orden LIFO.
    4. Explorar la sala: procesa varios eventos seguidos en orden FIFO.
    5. Usar un objeto se registra en el historial; deshacerlo no lo consume.
    6. Estado del mundo al deshacer (Checkpoint 3): deshacer revierte la
       POSICIÓN de Link y los TESOROS recogidos, pero no lo que Link ya
       descubrió: las salas siguen visitadas, los eventos vividos siguen
       contados y las misiones completadas (con sus rupias y sus puertas
       abiertas) no se pierden.
"""

import sys
from collections import deque

import inventario
import historial
import eventos
import mazmorra
import misiones
import estado as mundo


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
OPCION_RUTA = 9
OPCION_MAPA = 10
OPCION_MISIONES = 11
OPCION_ESTADO = 12
OPCION_SALIR = 13

# Objetos con los que Link empieza la aventura (lore del Checkpoint 1)
OBJETOS_INICIALES = ["Espada Minish", "Pluma de Roc"]

# Rupias que da un evento de rupias
RUPIAS_POR_EVENTO = 20

# ROBUSTEZ: en Windows, si la salida se redirige a un archivo o la consola no
# usa UTF-8, imprimir emojis o tildes lanza UnicodeEncodeError.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


# ----------------------------------------------------------------------
# Entrada robusta
# ----------------------------------------------------------------------

def leer_entrada(mensaje):
    """
    Lee texto del usuario sin que el programa se caiga.
    ROBUSTEZ: con Ctrl+C o fin de la entrada (EOF) se cierra la partida de
    forma ordenada con SystemExit(0), sin traceback y sin ciclo infinito.
    """
    try:
        return input(mensaje)
    except (EOFError, KeyboardInterrupt):
        print("\n[!] La conexión con la Trifuerza se interrumpió. Link guarda su progreso y descansa.")
        raise SystemExit(0)


def leer_opcion_numerica(mensaje, minimo, maximo):
    """
    Pide un número entero y valida que esté en el rango [minimo, maximo].
    ROBUSTEZ: texto, símbolos, entrada vacía, 0, negativos y números fuera de
    rango muestran un mensaje y retornan None (quien llama hace 'continue').
    """
    texto = leer_entrada(mensaje)
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


# ----------------------------------------------------------------------
# Pantallas
# ----------------------------------------------------------------------

def mostrar_encabezado():
    """Imprime la portada temática del juego."""
    print("==================================================")
    print("     LA LEYENDA DE ZELDA: EL ASCENSO DE VAATI     ")
    print("        Aventura Algorítmica - Checkpoint 3       ")
    print("==================================================")
    print("Héroe: Link | Antagonista: Vaati | Región: Hyrule\n")


def mostrar_menu(partida):
    """Muestra la ubicación, las rupias y las opciones del menú principal."""
    print("\n--------------------------------------------------")
    print(f"📍 Link está en: {partida['sala']}")
    print(f"💎 Rupias: {partida['estado']['rupias']}")
    print("--------------------------------------------------")
    print(" 1. Moverse a otra sala")
    print(" 2. Ver inventario")
    print(" 3. Usar un objeto")
    print(" 4. Deshacer última acción")
    print(" 5. Tocar la Ocarina del Viento (deshacer varias acciones)")
    print(" 6. Ver historial completo")
    print(" 7. Explorar la sala (resolver varios eventos)")
    print(" 8. Simular turnos de batalla")
    print(" 9. Buscar la ruta más corta a una sala (BFS)")
    print("10. Ver salas alcanzables y zonas aisladas (DFS)")
    print("11. Ver árbol de misiones")
    print("12. Ver estado del mundo")
    print("13. Salir del juego")


def mostrar_inventario(mochila):
    """Muestra el inventario de Link (Checkpoint 1: lista)."""
    print("\n============ BOLSA DE OBJETOS DE LINK ============")
    if len(mochila) == 0:
        print("  La bolsa está vacía. Explora las salas marcadas para encontrar tesoros.")
    else:
        for i, objeto in enumerate(mochila, start=1):
            print(f"  {i}. {objeto}")
    print("==================================================")


def elegir_sala(partida, mensaje):
    """
    Muestra todas las salas numeradas y pide una por número.
    ROBUSTEZ: solo acepta índices de las salas mostradas; cualquier otra
    entrada retorna None. Así nunca se consulta una sala que no existe.
    """
    salas = partida["grafo"].vertices()
    print()
    for i, sala in enumerate(salas, start=1):
        marca = "  <- Link está aquí" if sala == partida["sala"] else ""
        print(f"  {i:>2}) {sala}{marca}")
    eleccion = leer_opcion_numerica(mensaje, 1, len(salas))
    if eleccion is None:
        return None
    return salas[eleccion - 1]


# ----------------------------------------------------------------------
# Integración: estado del mundo, eventos y misiones
# ----------------------------------------------------------------------

def indicadores(partida):
    """
    Arma los números que revisan las misiones a partir del DICCIONARIO de
    estado (resumen_estado + conteos de eventos + jefe derrotado).
    Complejidad: O(S), S = salas.
    """
    est = partida["estado"]
    datos = mundo.resumen_estado(est)
    datos["hadas"] = mundo.contar_eventos(est, "hada")
    jefe = mundo.obtener_sala(est, partida["jefe"]) if partida["jefe"] else None
    datos["jefe_derrotado"] = 1 if jefe and jefe["visitada"] else 0
    return datos


def revisar_misiones(partida):
    """
    INTEGRACIÓN ÁRBOL -> DICCIONARIO -> GRAFO:
    completa las misiones disponibles cuya condición ya se cumple; cada una
    da rupias (diccionario) y puede abrir una puerta sellada (se elimina del
    diccionario, y el grafo deja de tratarla como bloqueada).
    """
    completadas = misiones.revisar_misiones(partida["misiones"], indicadores(partida))
    for mision in completadas:
        print(f"\n🏆 ¡Misión completada: {mision.nombre}!")
        if mision.recompensa:
            mundo.sumar_rupias(partida["estado"], mision.recompensa)
            print(f"   +{mision.recompensa} rupias (total: {partida['estado']['rupias']})")
        if mision.puerta and mundo.abrir_puerta(partida["estado"], *mision.puerta):
            a, b = mision.puerta
            print(f"   🌬️  El viento de Vaati se disipa: se abre la puerta {a} <-> {b}.")
        if mision.nombre == "Derrotar a Vaati":
            print("\n✨ ¡Vaati ha sido derrotado! El Palacio de los Vientos vuelve a la calma.")
            print("   Hyrule está a salvo. Puedes seguir explorando o salir del juego.")
        disponibles = [m.nombre for m in misiones.misiones_disponibles(partida["misiones"])]
        hijas = [h.nombre for h in mision.hijos if h.nombre in disponibles]
        if hijas:
            print(f"   Nuevas misiones disponibles: {', '.join(hijas)}")


def aplicar_evento(partida, evento):
    """
    INTEGRACIÓN COLA -> DICCIONARIO: cada evento procesado se cuenta en el
    estado del mundo por su tipo, y los de rupias suman rupias.
    """
    if evento is None:
        return
    tipo = eventos.tipo_de_evento(evento)
    mundo.registrar_evento(partida["estado"], tipo)
    if tipo == "rupias":
        mundo.sumar_rupias(partida["estado"], RUPIAS_POR_EVENTO)
        print(f"   +{RUPIAS_POR_EVENTO} rupias (total: {partida['estado']['rupias']})")
    elif tipo == "enemigo":
        print(f"   Link vence al enemigo. Secuaces vencidos: "
              f"{mundo.contar_eventos(partida['estado'], 'enemigo')}")


def intentar_recoger_tesoro(partida):
    """
    Si la sala actual tiene un tesoro sin recoger (según el DICCIONARIO),
    Link lo obtiene: entra al inventario (lista), se marca en el estado y se
    registra en el historial (pila) como "Recoger".
    ROBUSTEZ: un tesoro ya recogido no se puede recoger otra vez.
    """
    sala = partida["sala"]
    datos = mundo.obtener_sala(partida["estado"], sala)
    if datos is None or datos["tesoro"] is None:
        return
    if datos["recogido"]:
        print("[i] El cofre de esta sala ya está abierto. Aquí no queda nada más.")
        return

    objeto = datos["tesoro"]
    vaati, _ = misiones.buscar_mision(partida["misiones"], "Derrotar a Vaati")
    if mazmorra.MARCADOR_JEFE in sala and vaati is not None and vaati.completada:
        print(f"\n✨ Link recoge el {objeto} que Vaati dejó al ser derrotado.")
    elif mazmorra.MARCADOR_JEFE in sala:
        print("\n🌀 ¡Vaati aparece envuelto en un torbellino oscuro!")
        print("⚔️  Link resiste el viento y lo derrota con la Espada Minish.")
        print(f"✨ Vaati deja caer el {objeto}.")
    else:
        print("\n🎁 ¡Da-da-da-daaa! Link abre un cofre antiguo.")

    inventario.agregar_objeto(partida["mochila"], objeto)          # Lista
    mundo.marcar_tesoro(partida["estado"], sala, True)              # Diccionario
    historial.registrar_accion(partida["cronicas"], {"tipo": "Recoger",   # Pila
                                                     "objeto": objeto, "sala": sala})


# ----------------------------------------------------------------------
# Acciones del menú
# ----------------------------------------------------------------------

def accion_moverse(partida):
    """
    Opción 1. Muestra las puertas de la sala según el GRAFO y mueve a Link.

    INTEGRACIÓN:
        (a) Las puertas selladas (diccionario) se muestran pero no se cruzan.
        (b) El movimiento se apila en el historial con {'desde', 'hacia'}.
        (c) Dispara el siguiente evento de la cola y lo cuenta en el estado.
        (d) Marca la sala como visitada y recoge su tesoro si tiene.
        (e) Revisa las misiones, que pueden abrir puertas nuevas.

    ROBUSTEZ: solo se aceptan las puertas mostradas, y una puerta sellada es
    una acción no permitida: se avisa y Link no se mueve.
    """
    sala_actual = partida["sala"]
    puertas = partida["grafo"].vecinos(sala_actual)
    if not puertas:
        print("[!] No hay puertas en esta sala. Link no puede avanzar.")
        return

    print("\n🚪 Puertas de la sala:")
    for i, sala in enumerate(puertas, start=1):
        mision = mundo.motivo_sello(partida["estado"], sala_actual, sala)
        datos = mundo.obtener_sala(partida["estado"], sala)
        marcas = []
        if mision:
            marcas.append(f"sellada: se abre con '{mision}'")
        if datos and datos["visitada"]:
            marcas.append("visitada")
        texto = f"  ({', '.join(marcas)})" if marcas else ""
        print(f"  {i}) {sala}{texto}")
    opcion_quedarse = len(puertas) + 1
    print(f"  {opcion_quedarse}) Quedarse en esta sala")

    eleccion = leer_opcion_numerica("Elige una puerta: ", 1, opcion_quedarse)
    if eleccion is None:
        print("[i] Link duda frente a las puertas y se queda donde está.")
        return
    if eleccion == opcion_quedarse:
        print("[i] Link decide no moverse por ahora.")
        return

    destino = puertas[eleccion - 1]

    # (a) Acción no permitida: la puerta sigue sellada
    mision = mundo.motivo_sello(partida["estado"], sala_actual, destino)
    if mision:
        print(f"[X] Un muro de viento sella la puerta hacia '{destino}'.")
        print(f"    Ezlo: \"Se abrirá cuando completes la misión '{mision}'.\"")
        return

    # (b) Historial (pila)
    historial.registrar_accion(partida["cronicas"], {
        "tipo": "Moverse", "desde": sala_actual, "hacia": destino,
        "detalle": f"de '{sala_actual}' a '{destino}'",
    })
    print(f"\n🏃 Link se mueve a: {destino}")
    partida["sala"] = destino

    # (c) Evento (cola) -> estado (diccionario)
    aplicar_evento(partida, eventos.procesar_siguiente_evento(partida["cola"]))

    # (d) Estado del mundo y tesoro
    if mundo.marcar_visitada(partida["estado"], destino):
        visitadas = len(mundo.salas_visitadas(partida["estado"]))
        print(f"   🗺️  Sala nueva descubierta ({visitadas} de {partida['grafo'].num_vertices()}).")
    intentar_recoger_tesoro(partida)

    # (e) Misiones (árbol)
    revisar_misiones(partida)


def revertir_accion(partida, accion):
    """
    Aplica el efecto de UNA acción que ya salió de la pila (deshacer y
    Ocarina). Decisión del Checkpoint 3: se revierten la posición y los
    tesoros; las salas visitadas, los eventos y las misiones completadas se
    conservan.
    """
    if not isinstance(accion, dict):
        print("[i] La acción deshecha no implicaba moverse. Link sigue en la misma sala.")
        return
    tipo = accion.get("tipo")

    if tipo == "Moverse":
        anterior = accion.get("desde")
        if anterior is None or not partida["grafo"].existe_vertice(anterior):
            print("[!] Las crónicas no indican de dónde venía Link. Se queda en su sala.")
            return
        partida["sala"] = anterior
        print(f"[⏪] Un remolino arrastra a Link de vuelta a: {anterior}")
        print("     (El evento ya ocurrió y la sala sigue descubierta en el mapa.)")
        return

    if tipo == "Recoger":
        objeto = accion.get("objeto")
        if objeto in partida["mochila"]:
            inventario.soltar_objeto(partida["mochila"], objeto)   # Lista: remove()
        mundo.marcar_tesoro(partida["estado"], accion.get("sala"), False)  # Diccionario
        print(f"[⏪] El {objeto} regresa a su cofre. Link sigue en: {partida['sala']}")
        print("     (Las misiones ya completadas y sus recompensas se conservan.)")
        return

    if tipo == "Usar":
        print(f"[⏪] El efecto de {accion.get('objeto')} se desvanece. "
              "El objeto sigue en la bolsa de Link.")
        return

    print("[i] Acción deshecha. Link permanece en su sala.")


def accion_deshacer(partida):
    """
    Opción 4. Deshace la última acción con pop() (LIFO).
    ROBUSTEZ: historial vacío -> deshacer_ultima_accion() avisa y retorna
    None; Link no se mueve.
    """
    accion = historial.deshacer_ultima_accion(partida["cronicas"])
    if accion is None:
        return
    revertir_accion(partida, accion)
    if isinstance(accion, dict) and accion.get("tipo") == "Recoger":
        print("     Deshaz de nuevo si quieres volver a la sala anterior.")


def accion_ocarina(partida):
    """
    Opción 5. historial.deshacer_multiples() (Guía 5): pop() 'n' veces y
    aplica cada acción en orden LIFO.
    ROBUSTEZ: historial vacío o cantidad inválida -> mensaje, nada cambia.
    """
    cronicas = partida["cronicas"]
    if len(cronicas) == 0:
        historial.deshacer_multiples(cronicas, 1)
        return
    n = leer_opcion_numerica(f"¿Cuántas acciones quieres deshacer? (1 a {len(cronicas)}): ",
                             1, len(cronicas))
    if n is None:
        print("[i] Link baja la Ocarina sin tocar la melodía. Nada cambia.")
        return
    for accion in historial.deshacer_multiples(cronicas, n):
        revertir_accion(partida, accion)
    print(f"[🎶] Cuando el remolino se calma, Link está en: {partida['sala']}")


def accion_usar_objeto(partida):
    """
    Opción 3. inventario.usar_objeto() (Checkpoint 1) + registro en la pila.
    ROBUSTEZ: bolsa vacía u opción inválida -> mensaje, nada se registra.
    """
    mochila = partida["mochila"]
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
    inventario.usar_objeto(mochila, objeto)
    historial.registrar_accion(partida["cronicas"], {"tipo": "Usar", "objeto": objeto})


def accion_explorar(partida):
    """
    Opción 7. eventos.procesar_multiples_eventos() (Guía 6): 'n' eventos en
    orden FIFO; cada uno se cuenta en el estado y puede completar misiones.
    ROBUSTEZ: cola vacía o cantidad inválida -> mensaje, nada se procesa.
    """
    cola = partida["cola"]
    if len(cola) == 0:
        eventos.procesar_multiples_eventos(cola, 1)
        return
    eventos.mostrar_cola_eventos(cola)
    n = leer_opcion_numerica(f"¿Cuántos eventos quieres enfrentar? (1 a {len(cola)}): ", 1, len(cola))
    if n is None:
        print("[i] Link prefiere no tentar a la suerte y sigue en guardia.")
        return
    for evento in eventos.procesar_multiples_eventos(cola, n):
        aplicar_evento(partida, evento)
    revisar_misiones(partida)


def accion_ver_historial(partida):
    """Opción 6. Pila de la cima a la base, cima sin sacarla y conteos por tipo."""
    cronicas = partida["cronicas"]
    historial.mostrar_historial_completo(cronicas)
    historial.ver_ultima_accion(cronicas)
    if len(cronicas) > 0:
        for tipo in ("Moverse", "Recoger", "Usar"):
            historial.contar_acciones_de_tipo(cronicas, tipo)


def accion_ruta(partida):
    """
    Opción 9. BFS: ruta con MENOS SALTOS desde la sala de Link hasta la sala
    elegida, respetando las puertas selladas del diccionario.

    - Compara con la ruta por el árbol original (sin atajos) para mostrar
      que los atajos crean caminos alternativos más cortos.
    - Si no hay ruta posible, busca la ruta ignorando los sellos y dice qué
      misión hay que completar para abrir el camino.
    ROBUSTEZ: sala inválida, la misma sala o ruta inexistente -> mensaje.
    """
    destino = elegir_sala(partida, "¿A qué sala quieres llegar? ")
    if destino is None:
        print("[i] Ezlo guarda el mapa.")
        return
    origen = partida["sala"]
    if destino == origen:
        print("[i] Link ya está en esa sala.")
        return

    bloqueadas = mundo.aristas_bloqueadas(partida["estado"])
    ruta = partida["grafo"].ruta_mas_corta(origen, destino, bloqueadas)

    if ruta is None:
        print(f"\n[X] Ahora mismo no hay ruta hacia '{destino}'.")
        sin_sellos = partida["grafo"].ruta_mas_corta(origen, destino)
        if sin_sellos is None:
            print("    Esa sala no está conectada con ninguna puerta.")
            return
        for a, b in zip(sin_sellos, sin_sellos[1:]):
            mision = mundo.motivo_sello(partida["estado"], a, b)
            if mision:
                print(f"    La bloquea la puerta {a} <-> {b}: se abre con '{mision}'.")
        return

    print(f"\n🧭 Ruta más corta (BFS): {len(ruta) - 1} salto(s)")
    for paso, sala in enumerate(ruta):
        print(f"    {paso}. {sala}")
    arbol = partida["grafo_arbol"].ruta_mas_corta(origen, destino)
    if arbol is not None and len(arbol) > len(ruta):
        print(f"    ¡Un atajo ahorra {len(arbol) - len(ruta)} salto(s)! "
              f"Por el árbol original serían {len(arbol) - 1}.")


def accion_mapa(partida):
    """
    Opción 10. DFS: salas que Link puede alcanzar desde donde está sin cruzar
    puertas selladas, y ZONAS AISLADAS (componentes conexas del grafo con las
    puertas selladas cerradas).
    """
    bloqueadas = mundo.aristas_bloqueadas(partida["estado"])
    orden = partida["grafo"].dfs(partida["sala"], bloqueadas)
    print(f"\n🗺️  Exploración en profundidad (DFS) desde {partida['sala']}:")
    for sala in orden:
        datos = mundo.obtener_sala(partida["estado"], sala)
        marcas = []
        if datos and datos["visitada"]:
            marcas.append("visitada")
        if datos and datos["tesoro"] and not datos["recogido"]:
            marcas.append(f"tesoro: {datos['tesoro']}")
        texto = f"  ({', '.join(marcas)})" if marcas else ""
        print(f"    - {sala}{texto}")
    print(f"  Alcanzables ahora: {len(orden)} de {partida['grafo'].num_vertices()} salas.")

    aisladas = [zona for zona in partida["grafo"].componentes_conexas(bloqueadas)
                if partida["sala"] not in zona]
    if aisladas:
        print("  Zonas aisladas por puertas selladas:")
        for zona in aisladas:
            print(f"    - {', '.join(zona)}")
    else:
        print("  No hay zonas aisladas: todo el palacio está conectado.")


def accion_salir(partida):
    """Opción 13. Resumen final de la partida."""
    info = indicadores(partida)
    print("\n==================================================")
    print("  Link guarda la Espada Minish y descansa.")
    print(f"  Salas descubiertas: {info['salas_visitadas']} de {info['salas_totales']}")
    print(f"  Misiones completadas: {misiones.contar_completadas(partida['misiones'])}"
          f" de {misiones.contar_misiones(partida['misiones'])}")
    print(f"  Rupias: {info['rupias']} | Objetos en la bolsa: {len(partida['mochila'])}")
    if info["jefe_derrotado"]:
        print("  ¡Vaati ha sido derrotado! Hyrule vuelve a estar en paz.")
    else:
        print("  Vaati sigue acechando... Hyrule espera tu regreso.")
    print("==================================================")


# ----------------------------------------------------------------------
# Preparación de la partida
# ----------------------------------------------------------------------

def preparar_partida():
    """
    Crea todas las estructuras de la partida y las conecta:
        1. Mazmorra recursiva (árbol) -> Grafo genérico + 2 atajos (ciclos).
        2. Diccionario de estado con las salas, tesoros y puertas selladas:
           la puerta del jefe y los dos atajos empiezan sellados.
        3. Árbol de misiones; cada sello lo abre una misión.
        4. Inventario, historial, cola de eventos y cola de turnos (CP1 y CP2).
    Retorna el diccionario 'partida', o None si la mazmorra no se pudo crear.
    """
    mapa = mazmorra.crear_mazmorra(profundidad_maxima=3, limite_salas=15)
    if not mapa:
        print("[!] El Palacio de los Vientos no pudo formarse. Fin de la aventura.")
        return None
    mazmorra.imprimir_arbol_mazmorra(mapa)

    grafo_arbol = mazmorra.construir_grafo(mapa)          # el árbol tal cual
    grafo = mazmorra.construir_grafo(mapa)                # el que recibe atajos
    atajos = mazmorra.agregar_atajos(grafo, cantidad=2)
    jefe = mazmorra.sala_del_jefe(grafo)

    estado = mundo.crear_estado(grafo.vertices(), mazmorra.tesoros_por_sala(grafo),
                                mazmorra.SALA_INICIAL)
    cofres = mundo.contar_cofres(estado, mazmorra.OBJETO_JEFE)
    arbol = misiones.construir_arbol_misiones(min(3, cofres))
    nombre_reunir = f"Reunir {min(3, cofres)} tesoros"

    # Puerta del jefe: su única puerta es la que lo une con su sala padre
    if jefe:
        padre_jefe = mapa[jefe][0]
        mundo.sellar_puerta(estado, padre_jefe, jefe, nombre_reunir)
        misiones.asignar_puerta(arbol, nombre_reunir, mundo.clave_puerta(padre_jefe, jefe))

    for atajo, nombre in zip(atajos, ["Explorar 3 salas", "Vencer a 2 secuaces de Vaati"]):
        mundo.sellar_puerta(estado, atajo[0], atajo[1], nombre)
        misiones.asignar_puerta(arbol, nombre, mundo.clave_puerta(*atajo))

    mazmorra.imprimir_grafo_mazmorra(grafo, atajos, estado["puertas_selladas"])

    partida = {
        "grafo": grafo,
        "grafo_arbol": grafo_arbol,
        "jefe": jefe,
        "estado": estado,
        "misiones": arbol,
        "sala": mazmorra.SALA_INICIAL,
        "mochila": [],
        "cronicas": [],
        "cola": eventos.inicializar_cola_eventos([
            "Un Moblin te bloquea el paso con su lanza",
            "Encuentras 20 rupias rojas ocultas en una vasija",
            "Una trampa de pinchos se activa bajo tus pies",
            "Una bandada de Keese desciende del techo",
            "Un Octorok dispara rocas desde un charco",
            "Un Chuchu Rojo brota del suelo y bloquea la puerta",
            "Una Gran Hada te restaura los corazones",
            "La risa de Vaati resuena entre los muros",
        ]),
        "combatientes": deque(["Link", "Moblin", "Octorok"]),
    }

    print("\nEzlo te entrega el equipo de un héroe de Hyrule:")
    for objeto in OBJETOS_INICIALES:
        inventario.agregar_objeto(partida["mochila"], objeto)
    return partida


# ----------------------------------------------------------------------
# Partida principal
# ----------------------------------------------------------------------

def main():
    """
    Punto de entrada del juego: prepara la partida y ejecuta el menú dentro
    de un ciclo while True hasta que el jugador elige salir.
    ROBUSTEZ: toda opción inválida (texto, 0, negativos o fuera de rango)
    muestra un mensaje y reinicia el ciclo con continue.
    """
    mostrar_encabezado()
    partida = preparar_partida()
    if partida is None:
        return

    print("\nEzlo te susurra: \"Link, Vaati se oculta tras una puerta sellada por el viento.")
    print("Completa las misiones del palacio para abrirla.\"")
    revisar_misiones(partida)        # completa la raíz: Link ya entró al palacio

    acciones = {
        OPCION_MOVERSE: accion_moverse,
        OPCION_INVENTARIO: lambda p: mostrar_inventario(p["mochila"]),
        OPCION_USAR: accion_usar_objeto,
        OPCION_DESHACER: accion_deshacer,
        OPCION_OCARINA: accion_ocarina,
        OPCION_HISTORIAL: accion_ver_historial,
        OPCION_EXPLORAR: accion_explorar,
        OPCION_TURNOS: lambda p: eventos.simular_turnos(p["combatientes"]),
        OPCION_RUTA: accion_ruta,
        OPCION_MAPA: accion_mapa,
        OPCION_MISIONES: lambda p: misiones.mostrar_misiones(p["misiones"], indicadores(p)),
        OPCION_ESTADO: lambda p: mundo.mostrar_estado(p["estado"]),
    }

    while True:
        mostrar_menu(partida)
        opcion = leer_opcion_numerica("Opción: ", OPCION_MOVERSE, OPCION_SALIR)
        if opcion is None:
            continue
        if opcion == OPCION_SALIR:
            accion_salir(partida)
            break
        acciones[opcion](partida)


if __name__ == "__main__":
    main()
