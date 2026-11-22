"""
Módulo de estado del mundo - Checkpoint 3 (Aventura Algorítmica)
La Leyenda de Zelda: El Ascenso de Vaati

Guarda en DICCIONARIOS todo lo que cambia mientras se juega y que el juego
necesita consultar rápido:

    estado = {
        "salas": {                                   # clave: nombre de la sala (texto único)
            "Entrada del Palacio de los Vientos": {"visitada": True,  "tesoro": None,  "recogido": False},
            "Mina de Cristal [COFRE: Botas de Pegaso]": {"visitada": False, "tesoro": "Botas de Pegaso", "recogido": False},
            ...
        },
        "puertas_selladas": {                        # clave: TUPLA ordenada (sala_a, sala_b)
            ("Cripta de los Caballeros", "Puente de las Nubes [JEFE VAATI]"): "Reunir 3 tesoros",
            ...
        },
        "eventos": {"enemigo": 2, "rupias": 1, ...}, # clave: tipo de evento (texto)
        "rupias": 35,
    }

¿Por qué un diccionario?
    En cada movimiento el juego pregunta "¿esta sala ya se visitó?", "¿esta
    puerta está sellada?", "¿cuántos enemigos venció Link?". Con un
    diccionario cada consulta es O(1) en promedio (tabla hash); con una lista
    habría que recorrerla buscando la sala: O(n).

¿Por qué esas claves?
    - Sala: su nombre es único en la mazmorra (el generador nunca repite
      nombres), así que es una clave natural.
    - Puerta: una TUPLA ordenada (a, b). Es inmutable, así que puede ser
      clave (una lista no podría: no es "hasheable"), y al ordenarla la
      puerta A-B y la puerta B-A son la misma clave.

Operaciones del diccionario que usa el juego:
    consulta ........ .get()  (obtener_sala, motivo_sello, contar_eventos)
    actualización ... marcar_visitada, marcar_tesoro, sumar_rupias
    inserción ....... sellar_puerta, registrar_evento (tipo nuevo)
    eliminación ..... abrir_puerta (pop de la puerta sellada)
    funciones propias de resumen y filtro:
                      salas_visitadas, tesoros_pendientes,
                      contar_tesoros_recogidos, resumen_estado
"""


# ----------------------------------------------------------------------
# Creación
# ----------------------------------------------------------------------

def crear_estado(salas, tesoros_por_sala, sala_inicial):
    """
    Crea el diccionario del estado del mundo.

    Parámetros:
        salas             -> lista con los nombres de todas las salas.
        tesoros_por_sala  -> diccionario {sala: objeto} con las salas que
                             tienen un tesoro (cofre o jefe).
        sala_inicial      -> sala donde empieza Link (se marca visitada).

    Complejidad: O(S), donde S es el número de salas (una inserción O(1)
    por sala).
    """
    estado = {
        "salas": {},
        "puertas_selladas": {},
        "eventos": {},
        "rupias": 0,
    }
    for sala in salas:
        estado["salas"][sala] = {                      # INSERCIÓN
            "visitada": False,
            "tesoro": tesoros_por_sala.get(sala),      # CONSULTA con .get(): None si no hay
            "recogido": False,
        }
    marcar_visitada(estado, sala_inicial)
    return estado


def clave_puerta(sala_a, sala_b):
    """
    Construye la clave de una puerta: una TUPLA ordenada, para que A-B y
    B-A sean la misma puerta. Complejidad: O(1).
    """
    return tuple(sorted((sala_a, sala_b)))


# ----------------------------------------------------------------------
# Salas
# ----------------------------------------------------------------------

def obtener_sala(estado, sala):
    """
    CONSULTA segura del estado de una sala con .get(). Si la sala no existe
    retorna None (nunca lanza KeyError). Complejidad: O(1) promedio.
    """
    return estado["salas"].get(sala)


def marcar_visitada(estado, sala):
    """
    ACTUALIZACIÓN: marca una sala como visitada.
    Retorna True si es la primera visita, False si ya estaba visitada o si
    la sala no existe. Complejidad: O(1) promedio.
    """
    datos = obtener_sala(estado, sala)
    if datos is None:
        print(f"[!] La sala '{sala}' no existe en el estado del mundo.")
        return False
    if datos["visitada"]:
        return False
    datos["visitada"] = True
    return True


def marcar_tesoro(estado, sala, recogido):
    """
    ACTUALIZACIÓN: marca el tesoro de una sala como recogido (True) o
    devuelto a su cofre (False, al deshacer).
    Retorna True si cambió algo. Complejidad: O(1) promedio.
    """
    datos = obtener_sala(estado, sala)
    if datos is None or datos["tesoro"] is None:
        return False
    if datos["recogido"] == recogido:
        return False
    datos["recogido"] = recogido
    return True


def tesoro_disponible(estado, sala):
    """
    Indica si en la sala hay un tesoro que todavía no se ha recogido.
    Complejidad: O(1) promedio.
    """
    datos = obtener_sala(estado, sala)
    return datos is not None and datos["tesoro"] is not None and not datos["recogido"]


# ----------------------------------------------------------------------
# Puertas selladas
# ----------------------------------------------------------------------

def sellar_puerta(estado, sala_a, sala_b, mision):
    """
    INSERCIÓN: sella la puerta entre dos salas hasta completar 'mision'.
    Complejidad: O(1) promedio.
    """
    estado["puertas_selladas"][clave_puerta(sala_a, sala_b)] = mision


def abrir_puerta(estado, sala_a, sala_b):
    """
    ELIMINACIÓN: quita la puerta del diccionario de puertas selladas con
    pop(clave, None), que no falla si la puerta ya estaba abierta.
    Retorna True si la puerta estaba sellada y se abrió.
    Complejidad: O(1) promedio.
    """
    return estado["puertas_selladas"].pop(clave_puerta(sala_a, sala_b), None) is not None


def motivo_sello(estado, sala_a, sala_b):
    """
    CONSULTA con .get(): retorna la misión que abre la puerta, o None si
    la puerta no está sellada. Complejidad: O(1) promedio.
    """
    return estado["puertas_selladas"].get(clave_puerta(sala_a, sala_b))


def aristas_bloqueadas(estado):
    """
    Retorna el conjunto de puertas selladas como tuplas, listo para pasarlo
    al Grafo (BFS, DFS y rutas lo respetan). Complejidad: O(P), P = puertas.
    """
    return set(estado["puertas_selladas"].keys())


# ----------------------------------------------------------------------
# Eventos y rupias
# ----------------------------------------------------------------------

def registrar_evento(estado, tipo):
    """
    INSERCIÓN o ACTUALIZACIÓN: suma 1 al contador del tipo de evento. Si el
    tipo aparece por primera vez, .get(tipo, 0) evita el KeyError y la
    asignación lo inserta. Complejidad: O(1) promedio.
    """
    estado["eventos"][tipo] = estado["eventos"].get(tipo, 0) + 1


def contar_eventos(estado, tipo):
    """CONSULTA con .get(): cuántos eventos de ese tipo vivió Link. O(1)."""
    return estado["eventos"].get(tipo, 0)


def sumar_rupias(estado, cantidad):
    """ACTUALIZACIÓN: suma rupias al monedero de Link. Complejidad: O(1)."""
    estado["rupias"] = estado.get("rupias", 0) + cantidad


# ----------------------------------------------------------------------
# Funciones propias de resumen y filtro
# ----------------------------------------------------------------------

def salas_visitadas(estado):
    """
    FILTRO: lista de las salas que Link ya visitó.
    Complejidad: O(S), porque revisa cada sala una vez.
    """
    return [sala for sala, datos in estado["salas"].items() if datos["visitada"]]


def tesoros_pendientes(estado):
    """
    FILTRO: diccionario {sala: objeto} con los tesoros que siguen en sus
    cofres. Complejidad: O(S).
    """
    return {sala: datos["tesoro"] for sala, datos in estado["salas"].items()
            if datos["tesoro"] is not None and not datos["recogido"]}


def contar_tesoros_recogidos(estado):
    """RESUMEN: cuántos tesoros ha recogido Link. Complejidad: O(S)."""
    return sum(1 for datos in estado["salas"].values() if datos["recogido"])


def contar_cofres(estado, objeto_jefe):
    """
    RESUMEN: cuántos cofres hay en la mazmorra (tesoros que no son el del
    jefe). Complejidad: O(S).
    """
    return sum(1 for datos in estado["salas"].values()
               if datos["tesoro"] is not None and datos["tesoro"] != objeto_jefe)


def resumen_estado(estado):
    """
    RESUMEN: diccionario corto con los números clave de la partida, que
    usan el menú y las misiones. Complejidad: O(S).
    """
    total = len(estado["salas"])
    visitadas = len(salas_visitadas(estado))
    return {
        "salas_visitadas": visitadas,
        "salas_totales": total,
        "tesoros_recogidos": contar_tesoros_recogidos(estado),
        "tesoros_pendientes": len(tesoros_pendientes(estado)),
        "puertas_selladas": len(estado["puertas_selladas"]),
        "enemigos_vencidos": contar_eventos(estado, "enemigo"),
        "rupias": estado.get("rupias", 0),
    }


def mostrar_estado(estado):
    """
    Imprime el estado del mundo para el menú del juego.
    Complejidad: O(S + P).
    """
    r = resumen_estado(estado)
    print("\n=============== ESTADO DEL MUNDO ===============")
    print(f"  Salas visitadas:   {r['salas_visitadas']} de {r['salas_totales']}")
    print(f"  Tesoros recogidos: {r['tesoros_recogidos']} | En sus cofres: {r['tesoros_pendientes']}")
    print(f"  Enemigos vencidos: {r['enemigos_vencidos']}")
    print(f"  Rupias:            {r['rupias']}")
    if estado["puertas_selladas"]:
        print("  Puertas selladas:")
        for (a, b), mision in estado["puertas_selladas"].items():
            print(f"    - {a} <-> {b}  (se abre con: {mision})")
    else:
        print("  Puertas selladas:  ninguna, el viento de Vaati se disipó.")
    if estado["eventos"]:
        detalle = ", ".join(f"{tipo}: {n}" for tipo, n in estado["eventos"].items())
        print(f"  Eventos vividos:   {detalle}")
    print("================================================")


# ----------------------------------------------------------------------
# Autoprueba
# ----------------------------------------------------------------------

if __name__ == "__main__":
    est = crear_estado(["Entrada", "Pasillo", "Cripta [COFRE: Botas de Pegaso]"],
                       {"Cripta [COFRE: Botas de Pegaso]": "Botas de Pegaso"}, "Entrada")
    sellar_puerta(est, "Pasillo", "Cripta [COFRE: Botas de Pegaso]", "Explorar 3 salas")
    print("Consulta con .get():", obtener_sala(est, "Pasillo"))
    print("Sala inexistente:", obtener_sala(est, "Sala Fantasma"))
    print("Primera visita al pasillo:", marcar_visitada(est, "Pasillo"))
    print("Visita repetida:", marcar_visitada(est, "Pasillo"))
    print("Motivo del sello (orden invertido):", motivo_sello(est, "Cripta [COFRE: Botas de Pegaso]", "Pasillo"))
    print("Abrir puerta:", abrir_puerta(est, "Pasillo", "Cripta [COFRE: Botas de Pegaso]"))
    print("Abrirla otra vez:", abrir_puerta(est, "Pasillo", "Cripta [COFRE: Botas de Pegaso]"))
    registrar_evento(est, "enemigo")
    registrar_evento(est, "enemigo")
    sumar_rupias(est, 20)
    print("Recoger tesoro:", marcar_tesoro(est, "Cripta [COFRE: Botas de Pegaso]", True))
    print("Recogerlo otra vez:", marcar_tesoro(est, "Cripta [COFRE: Botas de Pegaso]", True))
    print("Salas visitadas:", salas_visitadas(est))
    print("Tesoros pendientes:", tesoros_pendientes(est))
    mostrar_estado(est)
