"""
Módulo de historial - Checkpoint 2 (Aventura Algorítmica)
La Leyenda de Zelda: El Ascenso de Vaati

Implementa el "Libro de Crónicas de Hyrule": un historial de las acciones
de Link usando una PILA (Stack) construida sobre una lista nativa de Python.

Principio LIFO (Last In, First Out):
    - La CIMA de la pila es el final de la lista (historial[-1]).
    - Apilar   -> historial.append(accion)   O(1) amortizado
    - Desapilar -> historial.pop()           O(1)
    - Consultar la cima -> historial[-1]     O(1)

Nunca se usa pop(0) ni insert(0, x), porque ambas operan sobre el inicio
de la lista y obligan a desplazar todos los elementos: O(n).

Formato recomendado para las acciones (permite el backtracking en main.py):
    {"tipo": "Moverse", "desde": "Pasillo de los Ecos", "hacia": "Torre del Remolino"}
    {"tipo": "Recoger", "objeto": "Espada Minish", "sala": "Santuario Minish"}
También se aceptan acciones como texto simple, por ejemplo "Atacar: Chuchu".
"""


# ----------------------------------------------------------------------
# Funciones auxiliares (privadas)
# ----------------------------------------------------------------------

def _es_historial_valido(historial):
    """
    Verifica que el historial sea una lista de Python.
    Evita que el programa se caiga si por error se pasa None u otro tipo.
    Complejidad: O(1).
    """
    if not isinstance(historial, list):
        print("[!] El Libro de Crónicas de Hyrule está dañado: el historial no es una lista válida.")
        return False
    return True


def _texto_accion(accion):
    """
    Convierte una acción (dict o str) en un texto legible para la consola.
    No modifica la pila; solo sirve para mostrar y buscar acciones.
    Complejidad: O(1) (depende solo del tamaño de la acción, no del historial).
    """
    if isinstance(accion, dict):
        tipo = str(accion.get("tipo", "Acción desconocida"))
        if "desde" in accion and "hacia" in accion:
            return f"{tipo}: de '{accion['desde']}' a '{accion['hacia']}'"
        if "objeto" in accion:
            sala = accion.get("sala")
            if sala:
                return f"{tipo}: '{accion['objeto']}' en '{sala}'"
            return f"{tipo}: '{accion['objeto']}'"
        if "detalle" in accion:
            return f"{tipo}: {accion['detalle']}"
        return tipo
    return str(accion)


# ----------------------------------------------------------------------
# Funciones obligatorias de la pila
# ----------------------------------------------------------------------

def registrar_accion(historial, accion):
    """
    Apila una nueva acción de Link en la cima del historial.

    LIFO: append() coloca la acción al final de la lista, que es la cima
    de la pila; así la acción más reciente siempre será la primera en salir.

    Complejidad: O(1) amortizado, porque append() no desplaza elementos.

    Retorna True si la acción se registró, False si no era válida.
    """
    if not _es_historial_valido(historial):
        return False

    if accion is None or (isinstance(accion, str) and accion.strip() == ""):
        print("[!] Las crónicas de Hyrule no pueden registrar una acción vacía.")
        return False

    if isinstance(accion, dict) and not accion.get("tipo"):
        print("[!] La acción no tiene 'tipo'. Las crónicas necesitan saber qué hizo Link.")
        return False

    historial.append(accion)
    print(f"[📜] El Libro de Crónicas de Hyrule registra: {_texto_accion(accion)}")
    return True


def deshacer_ultima_accion(historial):
    """
    Desapila y devuelve la acción más reciente (la cima de la pila).

    LIFO: pop() sin índice extrae el último elemento añadido, es decir,
    la última acción que hizo Link. Es exactamente lo que significa "deshacer".

    Caso límite: si el historial está vacío, NO se llama a pop() (lanzaría
    IndexError). Se muestra un mensaje y se retorna None.

    Complejidad: O(1), porque pop() en el final de la lista no desplaza elementos.

    Retorna la acción deshecha, o None si no había nada que deshacer.
    """
    if not _es_historial_valido(historial):
        return None

    if len(historial) == 0:
        print("[!] Las arenas del tiempo están quietas: no hay movimientos que deshacer. "
              "El historial está vacío.")
        return None

    accion = historial.pop()
    print(f"[⏳] El tiempo retrocede en Hyrule... Deshaces: {_texto_accion(accion)}")
    return accion


def ver_ultima_accion(historial, mostrar=True):
    """
    Consulta la acción en la cima de la pila SIN sacarla (operación peek).

    LIFO: historial[-1] es la cima, es decir, la acción que saldría primero
    si se deshiciera. La pila no se modifica.

    Caso límite: en Python lista[-1] sobre una lista vacía lanza IndexError,
    por eso se valida antes que el historial tenga elementos.

    Complejidad: O(1), acceso directo por índice.

    Parámetro mostrar: si es True, imprime la acción en consola.
    Retorna la última acción, o None si el historial está vacío.
    """
    if not _es_historial_valido(historial):
        return None

    if len(historial) == 0:
        if mostrar:
            print("[!] El Libro de Crónicas está en blanco: Link aún no ha realizado ninguna acción.")
        return None

    ultima = historial[-1]
    if mostrar:
        print(f"[🔎] Última acción de Link: {_texto_accion(ultima)}")
    return ultima


def mostrar_historial_completo(historial):
    """
    Imprime todas las acciones desde la MÁS RECIENTE (cima) hasta la
    MÁS ANTIGUA (base), sin modificar la pila.

    LIFO: se recorre la lista de atrás hacia adelante con índices, que es
    el mismo orden en que saldrían las acciones al desapilarlas con pop().

    Complejidad: O(n), se visita cada acción una vez.
    """
    if not _es_historial_valido(historial):
        return

    print("\n========== LIBRO DE CRÓNICAS DE HYRULE ==========")

    if len(historial) == 0:
        print("  Las páginas están en blanco. La aventura de Link aún no comienza.")
        print("=================================================\n")
        return

    total = len(historial)
    posicion = 1
    for i in range(total - 1, -1, -1):
        etiqueta = ""
        if i == total - 1:
            etiqueta = "  <- cima (más reciente)"
        elif i == 0:
            etiqueta = "  <- base (más antigua)"
        print(f"  {posicion}. {_texto_accion(historial[i])}{etiqueta}")
        posicion += 1

    print(f"  Total de acciones registradas: {total}")
    print("=================================================\n")


# ----------------------------------------------------------------------
# Adaptaciones de la Guía 5
# ----------------------------------------------------------------------

def deshacer_multiples(historial, n):
    """
    Usa el poder de la Ocarina del Viento para deshacer las últimas 'n'
    acciones de una sola vez: un remolino arrastra a Link hacia atrás.

    LIFO: se ejecuta pop() 'n' veces; cada pop() saca la cima actual, así
    que las acciones se deshacen de la más reciente a la más antigua.

    Casos límite:
        - n no es un número entero (texto, decimal, booleano): mensaje y [].
        - n <= 0: mensaje y [].
        - historial vacío: mensaje y [].
        - n mayor que el número de acciones: se deshacen solo las que existen.

    Complejidad: O(k), donde k = mínimo entre n y el tamaño del historial,
    porque cada pop() es O(1).

    Retorna una lista con las acciones deshechas, en el orden en que salieron
    (la primera es la más reciente).
    """
    if not _es_historial_valido(historial):
        return []

    # Validar que n sea un entero (se acepta texto como "3" por si viene de input())
    if isinstance(n, bool) or not isinstance(n, (int, str)):
        print("[!] La Ocarina del Viento no entiende esa melodía: indica un número entero de acciones.")
        return []
    try:
        n = int(n)
    except ValueError:
        print("[!] La Ocarina del Viento no entiende esa melodía: indica un número entero de acciones.")
        return []

    if n <= 0:
        print("[!] La Ocarina del Viento solo puede deshacer un número positivo de acciones.")
        return []

    if len(historial) == 0:
        print("[!] Tocas la Ocarina del Viento, pero no hay acciones que deshacer: el historial está vacío.")
        return []

    if n > len(historial):
        print(f"[!] Solo hay {len(historial)} acción(es) en las crónicas. "
              f"El remolino retrocederá hasta el inicio de la aventura.")
        n = len(historial)

    print(f"[🎶] Link toca la Ocarina del Viento... ¡un remolino deshace {n} acción(es)!")
    deshechas = []
    for _ in range(n):
        accion = historial.pop()
        deshechas.append(accion)
        print(f"     - Deshecho: {_texto_accion(accion)}")

    return deshechas


def contar_acciones_de_tipo(historial, palabra_clave):
    """
    Recorre la pila y cuenta cuántas acciones contienen la palabra clave
    (por ejemplo "Moverse", "Atacar" o "Recoger"). No distingue mayúsculas.

    LIFO: el recorrido es de solo lectura; no se apila ni desapila nada,
    por lo que el orden y el contenido de la pila se conservan intactos.

    Complejidad: O(n), se revisa cada acción del historial una vez.

    Retorna el número de coincidencias (0 si no hay o si la entrada es inválida).
    """
    if not _es_historial_valido(historial):
        return 0

    if not isinstance(palabra_clave, str) or palabra_clave.strip() == "":
        print("[!] Debes indicar qué tipo de acción buscar en las crónicas (por ejemplo, 'Moverse').")
        return 0

    clave = palabra_clave.strip().lower()
    contador = 0
    for accion in historial:
        if isinstance(accion, dict):
            texto = str(accion.get("tipo", "")).lower()
        else:
            texto = str(accion).lower()
        if clave in texto:
            contador += 1

    print(f"[📊] Según las crónicas, Link ha realizado '{palabra_clave.strip()}' {contador} vez/veces.")
    return contador


# ----------------------------------------------------------------------
# Prueba rápida del módulo (solo se ejecuta si se corre este archivo directamente)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    cronicas = []

    print("--- Prueba de casos límite con historial vacío ---")
    deshacer_ultima_accion(cronicas)
    ver_ultima_accion(cronicas)
    deshacer_multiples(cronicas, 2)
    mostrar_historial_completo(cronicas)

    print("\n--- Registrando acciones de Link ---")
    registrar_accion(cronicas, {"tipo": "Moverse", "desde": "Pueblo de Hyrule", "hacia": "Bosque Minish"})
    registrar_accion(cronicas, {"tipo": "Recoger", "objeto": "Pluma de Roc", "sala": "Bosque Minish"})
    registrar_accion(cronicas, {"tipo": "Moverse", "desde": "Bosque Minish", "hacia": "Cueva de las Llamas"})
    registrar_accion(cronicas, "Atacar: Chuchu Rojo")
    registrar_accion(cronicas, "")      # caso límite: acción vacía
    registrar_accion(cronicas, None)    # caso límite: acción nula

    mostrar_historial_completo(cronicas)
    ver_ultima_accion(cronicas)
    contar_acciones_de_tipo(cronicas, "moverse")
    contar_acciones_de_tipo(cronicas, "")  # caso límite

    print("\n--- Deshaciendo acciones ---")
    deshacer_ultima_accion(cronicas)
    deshacer_multiples(cronicas, "abc")  # caso límite: texto
    deshacer_multiples(cronicas, -1)     # caso límite: negativo
    deshacer_multiples(cronicas, 10)     # caso límite: más de las que hay

    mostrar_historial_completo(cronicas)