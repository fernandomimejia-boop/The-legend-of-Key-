"""
Módulo de mazmorra - Checkpoint 2 (Aventura Algorítmica)
La Leyenda de Zelda: El Ascenso de Vaati

Genera el Palacio de los Vientos, la fortaleza de Vaati, usando RECURSIVIDAD.

Representación del mapa (grafo de adyacencia):
    mapa = {
        "Entrada del Palacio de los Vientos": ["Pasillo de los Ecos", "Santuario Minish"],
        "Pasillo de los Ecos": ["Entrada del Palacio de los Vientos", "Cripta de los Caballeros [COFRE: Botas de Pegaso]"],
        ...
    }
    - La clave es el nombre de la sala.
    - El valor es la lista de salas conectadas (incluye la sala de la que se
      vino, para que el mapa sea jugable en ambos sentidos).

¿Por qué recursividad?
    Una mazmorra es una estructura jerárquica (un árbol): cada sala es, a su vez,
    la "entrada" de una mazmorra más pequeña. Generar una sala y luego pedir
    que se genere el resto desde cada puerta es exactamente la definición de
    un problema recursivo: el mismo procedimiento se repite sobre un
    subproblema más pequeño (un nivel más profundo) hasta llegar a un caso
    base que se resuelve sin más llamadas.

Adaptaciones de la Guía 7 incluidas:
    1. Marcar las salas más profundas (dentro del caso base) con [JEFE VAATI]
       o [COFRE: objeto].
    2. Ramificación variable con random (1, 2 o 3 puertas por sala).
    3. (Extra) Calcular la profundidad real alcanzada.
    4. (Extra) Contar las salas por nivel.
"""

import random


# ----------------------------------------------------------------------
# Datos del mundo de Hyrule
# ----------------------------------------------------------------------

SALA_INICIAL = "Entrada del Palacio de los Vientos"

NOMBRES_SALAS = [
    "Pasillo de los Ecos",
    "Santuario Minish",
    "Galería de los Vientos",
    "Cámara de las Antorchas",
    "Puente de las Nubes",
    "Sala de los Espejos",
    "Cripta de los Caballeros",
    "Biblioteca Hyliana",
    "Jardín de los Picori",
    "Bóveda de las Rupias",
    "Torre del Remolino",
    "Fuente de las Hadas",
    "Forja de Melari",
    "Caverna de los Keese",
    "Patio de los Moblins",
    "Escalinata Celeste",
    "Salón del Trono Olvidado",
    "Mina de Cristal",
    "Observatorio de Hyrule",
    "Acueducto Sumergido",
    "Atrio del Viento Gélido",
    "Laberinto de Raíces",
    "Capilla del Elemento",
    "Mirador del Gran Tornado",
    "Archivo de los Sabios",
]

OBJETOS_TESORO = [
    "Boomerang Mágico",
    "Botas de Pegaso",
    "Brazalete de Fuerza",
    "Jarra Mágica",
    "Bastón de Pacci",
    "Capa de Roc",
    "Llave del Jefe",
    "Fragmento de Corazón",
]

MARCADOR_JEFE = "[JEFE VAATI]"
OBJETO_JEFE = "Elemento del Viento"
PREFIJO_COFRE = "[COFRE: "


# ----------------------------------------------------------------------
# Funciones auxiliares (privadas)
# ----------------------------------------------------------------------

def _marcar_sala_profunda(mapa, sala, sala_padre, estado):
    """
    Concatena un marcador al nombre de una sala del nivel más profundo.
    La primera sala profunda que se genera recibe al jefe Vaati; las demás
    reciben un cofre con un objeto distinto.

    Como el nombre de la sala es la clave del diccionario, el renombre se
    hace en dos lugares:
        1. Se mueve la entrada del diccionario a la nueva clave.
        2. Se reemplaza el nombre viejo en la lista de conexiones del padre.

    Complejidad: O(b), donde b es el número de conexiones del padre
    (por la búsqueda con index()).

    Retorna el nuevo nombre de la sala.
    """
    if not estado["jefe_colocado"]:
        marcador = MARCADOR_JEFE
        estado["jefe_colocado"] = True
    else:
        if estado["objetos"]:
            objeto = estado["objetos"].pop()
        else:
            objeto = "Bolsa de 50 Rupias"
        marcador = f"{PREFIJO_COFRE}{objeto}]"

    nuevo_nombre = f"{sala} {marcador}"
    mapa[nuevo_nombre] = mapa.pop(sala)

    if sala_padre is not None and sala_padre in mapa:
        indice = mapa[sala_padre].index(sala)
        mapa[sala_padre][indice] = nuevo_nombre

    return nuevo_nombre


def _validar_entero_en_rango(valor, minimo, maximo, nombre):
    """
    Verifica que 'valor' sea un entero (no booleano) dentro de [minimo, maximo].
    Retorna True si es válido; si no, imprime un mensaje y retorna False.
    Complejidad: O(1).
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        print(f"[!] El parámetro '{nombre}' debe ser un número entero.")
        return False
    if valor < minimo or valor > maximo:
        print(f"[!] El parámetro '{nombre}' debe estar entre {minimo} y {maximo}.")
        return False
    return True


# ----------------------------------------------------------------------
# Función recursiva principal
# ----------------------------------------------------------------------

def generar_mazmorra(mapa, sala_actual, sala_padre, profundidad_actual,
                     profundidad_maxima, nombres_disponibles, estado,
                     limite_salas=15, rama_min=1, rama_max=3):
    """
    Construye RECURSIVAMENTE el grafo de adyacencia de la mazmorra.

    Parámetros:
        mapa                -> diccionario que se va llenando {sala: [conectadas]}.
        sala_actual         -> nombre de la sala que se está creando.
        sala_padre          -> sala desde la que se llegó (None en la entrada).
        profundidad_actual  -> nivel de la sala actual (la entrada es nivel 0).
        profundidad_maxima  -> nivel en el que se detiene la generación.
        nombres_disponibles -> lista de nombres aún no usados (se consumen con pop()).
        estado              -> dict compartido: {"jefe_colocado": bool, "objetos": [...]}.
        limite_salas        -> número máximo de salas de la mazmorra.
        rama_min, rama_max  -> rango de puertas que puede abrir cada sala.

    CASO BASE (la función retorna sin volver a llamarse):
        a) profundidad_actual == profundidad_maxima: la sala está en el nivel
           más profundo. Aquí se aplica la adaptación de la Guía 7: se le
           concatena un marcador ([JEFE VAATI] o [COFRE: objeto]) y no se
           generan más puertas. Es una hoja del árbol.
        b) Se alcanzó el límite de salas o ya no quedan nombres disponibles:
           la sala queda como callejón sin salida (hoja sin marcador).

    CASO RECURSIVO:
        Si la sala no está en el nivel máximo, se decide al azar cuántas
        puertas abre (random.randint(rama_min, rama_max) -> 1, 2 o 3 caminos:
        ramificación variable). Por cada puerta se toma un nombre nuevo, se
        conecta con la sala actual y se llama a generar_mazmorra(...) con
        profundidad_actual + 1. Cada llamada se acerca al caso base porque la
        profundidad siempre aumenta y los nombres disponibles siempre disminuyen,
        lo que garantiza que la recursión termina.

    COMPLEJIDAD:
        Sea b el factor de ramificación (máximo 3) y d la profundidad máxima.
        - Temporal: O(b^d). En el peor caso cada sala abre b puertas, por lo que
          se crean 1 + b + b^2 + ... + b^d salas, una serie dominada por b^d.
          Cada sala se procesa una vez con trabajo O(b) para conectarla, así
          que el total es O(b^d) (acotado además por limite_salas).
        - Espacial: O(b^d) para guardar el diccionario con todas las salas y
          sus conexiones, más O(d) para la pila de llamadas recursivas, ya que
          en cada momento solo hay una llamada activa por nivel (recorrido en
          profundidad).

    Retorna el diccionario 'mapa' con la mazmorra construida.
    """
    # Registrar la sala actual y su conexión de regreso (mapa jugable en ambos sentidos)
    mapa[sala_actual] = []
    if sala_padre is not None:
        mapa[sala_actual].append(sala_padre)

    # ---------------- CASO BASE (a): nivel más profundo ----------------
    if profundidad_actual >= profundidad_maxima:
        _marcar_sala_profunda(mapa, sala_actual, sala_padre, estado)
        return mapa

    # ---------------- CASO BASE (b): sin espacio o sin nombres ----------------
    if len(mapa) >= limite_salas or len(nombres_disponibles) == 0:
        return mapa

    # ---------------- CASO RECURSIVO ----------------
    numero_puertas = random.randint(rama_min, rama_max)  # Ramificación variable

    for _ in range(numero_puertas):
        if len(mapa) >= limite_salas or len(nombres_disponibles) == 0:
            break

        nueva_sala = nombres_disponibles.pop()
        mapa[sala_actual].append(nueva_sala)

        generar_mazmorra(mapa, nueva_sala, sala_actual, profundidad_actual + 1,
                         profundidad_maxima, nombres_disponibles, estado,
                         limite_salas, rama_min, rama_max)

    return mapa


# ----------------------------------------------------------------------
# Adaptaciones extra de la Guía 7 (también recursivas)
# ----------------------------------------------------------------------

def calcular_profundidad_real(mapa, sala, sala_padre=None):
    """
    Calcula recursivamente la profundidad real alcanzada desde 'sala'.

    Caso base: la sala no tiene salas hijas (solo conecta con su padre),
    por lo tanto su profundidad es 0.
    Caso recursivo: 1 + la mayor profundidad entre sus salas hijas.

    Como el mapa es bidireccional, se excluye la sala padre para no volver
    hacia atrás (evita un ciclo infinito).

    Complejidad: O(n) temporal (visita cada sala una vez) y O(d) espacial
    por la pila de llamadas.
    """
    if not isinstance(mapa, dict) or sala not in mapa:
        return 0

    hijas = [s for s in mapa[sala] if s != sala_padre]
    if len(hijas) == 0:
        return 0

    return 1 + max(calcular_profundidad_real(mapa, hija, sala) for hija in hijas)


def contar_salas_por_nivel(mapa, sala, nivel=0, sala_padre=None, conteo=None):
    """
    Cuenta recursivamente cuántas salas hay en cada nivel de la mazmorra.

    Caso base: la sala no tiene hijas; solo se suma ella misma a su nivel.
    Caso recursivo: se suma la sala actual y se repite para cada hija en
    el nivel + 1.

    Complejidad: O(n) temporal y O(d) espacial por la recursión.

    Retorna un diccionario {nivel: cantidad_de_salas}.
    """
    if conteo is None:
        conteo = {}
    if not isinstance(mapa, dict) or sala not in mapa:
        return conteo

    conteo[nivel] = conteo.get(nivel, 0) + 1

    for hija in mapa[sala]:
        if hija != sala_padre:
            contar_salas_por_nivel(mapa, hija, nivel + 1, sala, conteo)

    return conteo


# ----------------------------------------------------------------------
# Función de alto nivel para main.py
# ----------------------------------------------------------------------

def crear_mazmorra(profundidad_maxima=3, limite_salas=15, semilla=None, intentos=20):
    """
    Prepara los datos y llama a la función recursiva generar_mazmorra().
    Garantiza que la mazmorra cumpla los requisitos mínimos del checkpoint:
    al menos 7 salas, profundidad real mínima de 2 y un jefe colocado.

    Como la ramificación es aleatoria, un intento podría generar una mazmorra
    demasiado pequeña (por ejemplo, si todas las salas abren solo 1 puerta).
    En ese caso se vuelve a generar. Si tras varios intentos no se cumple,
    se genera una última vez con ramificación mínima de 2, que asegura
    1 + 2 + 4 = 7 salas como mínimo con profundidad 2.

    Parámetros:
        profundidad_maxima -> entre 2 y 5.
        limite_salas       -> entre 7 y la cantidad de nombres disponibles + 1.
        semilla            -> número opcional para reproducir la misma mazmorra
                              (útil para la evidencia del checkpoint).
        intentos           -> cantidad de generaciones antes del respaldo.

    Complejidad: O(intentos * b^d) en el peor caso.

    Retorna el diccionario de la mazmorra, o un diccionario vacío si los
    parámetros son inválidos.
    """
    if not _validar_entero_en_rango(profundidad_maxima, 2, 5, "profundidad_maxima"):
        return {}
    if not _validar_entero_en_rango(limite_salas, 7, len(NOMBRES_SALAS) + 1, "limite_salas"):
        return {}
    if not _validar_entero_en_rango(intentos, 1, 1000, "intentos"):
        return {}

    if semilla is not None:
        random.seed(semilla)

    def _un_intento(rama_min):
        """
        Genera UNA mazmorra completa llamando a la función recursiva
        generar_mazmorra() con nombres y tesoros barajados al azar.
        rama_min indica el mínimo de puertas por sala (1 normal, 2 en el
        respaldo). Retorna la tupla (mapa, estado).
        Complejidad: O(b^d), la misma de la generación recursiva.
        """
        nombres = NOMBRES_SALAS[:]          # Copia para no alterar la lista original
        random.shuffle(nombres)
        objetos = OBJETOS_TESORO[:]
        random.shuffle(objetos)
        estado = {"jefe_colocado": False, "objetos": objetos}
        mapa = generar_mazmorra({}, SALA_INICIAL, None, 0, profundidad_maxima,
                                nombres, estado, limite_salas, rama_min, 3)
        return mapa, estado

    def _cumple(mapa, estado):
        """
        Verifica que la mazmorra generada cumpla los mínimos del checkpoint:
        al menos 7 salas, profundidad real de 2 o más y el jefe Vaati colocado.
        Retorna True si cumple, False si hay que volver a generarla.
        Complejidad: O(n), por el cálculo recursivo de la profundidad real.
        """
        return (len(mapa) >= 7
                and calcular_profundidad_real(mapa, SALA_INICIAL) >= 2
                and estado["jefe_colocado"])

    for _ in range(intentos):
        mapa, estado = _un_intento(rama_min=1)
        if _cumple(mapa, estado):
            break
    else:
        # Respaldo: ramificación mínima de 2 garantiza los requisitos
        mapa, estado = _un_intento(rama_min=2)

    profundidad = calcular_profundidad_real(mapa, SALA_INICIAL)
    print("[🏰] Los vientos de Vaati dan forma al Palacio de los Vientos...")
    print(f"[🏰] Mazmorra generada: {len(mapa)} salas, profundidad {profundidad}")
    return mapa


# ----------------------------------------------------------------------
# Funciones de apoyo para la partida (usadas desde main.py)
# ----------------------------------------------------------------------

def obtener_salas_conectadas(mapa, sala):
    """
    Retorna una COPIA de la lista de salas conectadas a 'sala'.
    Si el mapa o la sala no existen, retorna una lista vacía (sin error).
    Complejidad: O(b), por la copia de la lista de conexiones.
    """
    if not isinstance(mapa, dict) or sala not in mapa:
        print(f"[!] La sala '{sala}' no existe en el Palacio de los Vientos.")
        return []
    return list(mapa[sala])


def existe_conexion(mapa, origen, destino):
    """
    Verifica si hay una puerta directa entre 'origen' y 'destino'.
    Sirve para validar el caso límite de moverse a una sala que no existe
    o que no está conectada.
    Complejidad: O(b), búsqueda en la lista de conexiones del origen.
    """
    if not isinstance(mapa, dict) or origen not in mapa or destino not in mapa:
        return False
    return destino in mapa[origen]


def es_sala_marcada(sala):
    """
    Indica si la sala tiene un marcador de sala profunda (jefe o cofre).
    Complejidad: O(m), donde m es la longitud del nombre.
    """
    if not isinstance(sala, str):
        return False
    return MARCADOR_JEFE in sala or PREFIJO_COFRE in sala


def obtener_objeto_de_sala(sala):
    """
    Retorna el objeto que se puede recoger en una sala marcada:
        - Sala del jefe  -> "Elemento del Viento".
        - Sala con cofre -> el objeto escrito en su marcador.
    Si la sala no está marcada, retorna None.
    Complejidad: O(m), donde m es la longitud del nombre.
    """
    if not es_sala_marcada(sala):
        return None
    if MARCADOR_JEFE in sala:
        return OBJETO_JEFE
    inicio = sala.index(PREFIJO_COFRE) + len(PREFIJO_COFRE)
    fin = sala.find("]", inicio)
    if fin == -1:
        return None
    return sala[inicio:fin]


# ----------------------------------------------------------------------
# Visualización del árbol (para la evidencia y el README)
# ----------------------------------------------------------------------

def _imprimir_rama(mapa, sala, sala_padre, prefijo, es_ultima, nivel):
    """
    Función auxiliar recursiva que dibuja una sala y sus hijas con sangría.
    Excluye a la sala padre para no imprimir el camino de regreso.
    Complejidad: O(n) en total, cada sala se imprime una vez.
    """
    conector = "└── " if es_ultima else "├── "
    print(f"{prefijo}{conector}{sala}  (nivel {nivel})")

    hijas = [s for s in mapa.get(sala, []) if s != sala_padre]
    nuevo_prefijo = prefijo + ("    " if es_ultima else "│   ")
    for i, hija in enumerate(hijas):
        _imprimir_rama(mapa, hija, sala, nuevo_prefijo, i == len(hijas) - 1, nivel + 1)


def imprimir_arbol_mazmorra(mapa, sala_inicial=SALA_INICIAL):
    """
    Muestra la mazmorra como un árbol con sangrías, desde la sala inicial
    hasta las salas más profundas, junto con un resumen por niveles.

    Ejemplo de salida:
        🏰 Entrada del Palacio de los Vientos  (nivel 0)
        ├── Pasillo de los Ecos  (nivel 1)
        │   └── Cripta de los Caballeros [JEFE VAATI]  (nivel 2)
        └── Santuario Minish  (nivel 1)
            └── ...

    Complejidad: O(n), cada sala se visita una sola vez.
    """
    if not isinstance(mapa, dict) or len(mapa) == 0:
        print("[!] No hay mazmorra que mostrar: el Palacio de los Vientos aún no se ha formado.")
        return
    if sala_inicial not in mapa:
        print(f"[!] La sala inicial '{sala_inicial}' no existe en el mapa.")
        return

    print("\n=============== MAPA DEL PALACIO DE LOS VIENTOS ===============")
    print(f"🏰 {sala_inicial}  (nivel 0)")

    hijas = list(mapa[sala_inicial])
    for i, hija in enumerate(hijas):
        _imprimir_rama(mapa, hija, sala_inicial, "", i == len(hijas) - 1, 1)

    conteo = contar_salas_por_nivel(mapa, sala_inicial)
    profundidad = calcular_profundidad_real(mapa, sala_inicial)
    marcadas = [s for s in mapa if es_sala_marcada(s)]

    print("---------------------------------------------------------------")
    print(f"Total de salas: {len(mapa)} | Profundidad real: {profundidad}")
    for nivel in sorted(conteo):
        print(f"  Nivel {nivel}: {conteo[nivel]} sala(s)")
    print(f"Salas marcadas (jefe o cofre): {len(marcadas)}")
    print("===============================================================\n")


# ----------------------------------------------------------------------
# Prueba rápida del módulo (solo se ejecuta si se corre este archivo directamente)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("--- Generando la mazmorra ---")
    mazmorra = crear_mazmorra(profundidad_maxima=3, limite_salas=15)
    imprimir_arbol_mazmorra(mazmorra)

    print("--- Salas conectadas a la entrada ---")
    print(obtener_salas_conectadas(mazmorra, SALA_INICIAL))

    print("\n--- Salas marcadas y sus objetos ---")
    for sala in mazmorra:
        if es_sala_marcada(sala):
            print(f"  {sala} -> objeto: {obtener_objeto_de_sala(sala)}")

    print("\n--- Casos límite ---")
    obtener_salas_conectadas(mazmorra, "Sala Inexistente")
    print("¿Conexión válida con una sala inexistente?",
          existe_conexion(mazmorra, SALA_INICIAL, "Sala Inexistente"))
    print("Objeto en sala sin marcar:", obtener_objeto_de_sala(SALA_INICIAL))
    crear_mazmorra(profundidad_maxima=1)        # profundidad menor a 2
    crear_mazmorra(profundidad_maxima="tres")   # tipo inválido
    crear_mazmorra(limite_salas=3)              # menos de 7 salas
    imprimir_arbol_mazmorra({})                 # mapa vacío