"""
arboles.py - Exposición: árboles, árboles de decisión y dependencias
Aventura Algorítmica · La Leyenda de Zelda: El Ascenso de Vaati

Contenido:
    1. Árbol de misiones de Link (clase Nodo) con sus dependencias:
       una misión solo se desbloquea cuando se completa la misión padre.
    2. Árbol de decisión del Moblin guardián del Palacio de los Vientos.
    3. Caso de la vida real: un torneo de tenis de eliminación directa
       (árbol binario) con sus tres recorridos: preorden, inorden y postorden.

Todos los recorridos están escritos con RECURSIVIDAD (Semana 7).
Solo usa Python estándar: no hay que instalar nada ni usar internet.

Cómo ejecutarlo:
    python arboles.py               -> demo con pausas (Enter para avanzar)
    python arboles.py --sin-pausas  -> demo completa de corrido

Notación de complejidad:
    n = cantidad de nodos del árbol
    h = altura del árbol (aristas del camino más largo de la raíz a una hoja)
"""

import sys

# Evita errores al imprimir tildes o símbolos en consolas de Windows
# o cuando la salida se redirige a un archivo.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


# ======================================================================
# PARTE 1 · ÁRBOL DE MISIONES (dependencias)
# ======================================================================

class Nodo:
    """
    Una misión del árbol de misiones de Link.

    Atributos:
        nombre     -> nombre de la misión (texto).
        hijos      -> lista de misiones que dependen de esta.
        completada -> True si Link ya la completó.

    Cada misión tiene UN SOLO padre: por eso la estructura es un árbol
    (un grafo conexo y sin ciclos), no un grafo general.
    """

    def __init__(self, nombre):
        self.nombre = nombre
        self.hijos = []
        self.completada = False


def agregar_hijo(padre, hijo):
    """
    Conecta 'hijo' como misión que depende de 'padre'.

    Complejidad: O(1), porque append() agrega al final de la lista de
    hijos sin recorrer el árbol.

    Retorna el hijo, para poder encadenar la construcción del árbol.
    """
    padre.hijos.append(hijo)
    return hijo


def estado_de(nodo, padre_completado):
    """
    Devuelve el estado de una misión como texto:
        "completada" -> Link ya la hizo.
        "disponible" -> no está hecha, pero su padre sí (o es la raíz).
        "bloqueada"  -> su padre todavía no está completado.
    Complejidad: O(1).
    """
    if nodo.completada:
        return "completada"
    if padre_completado:
        return "disponible"
    return "bloqueada"


def imprimir_preorden(nodo, nivel=0, padre_completado=True):
    """
    Imprime el árbol en PREORDEN con sangría según el nivel.

    Preorden = primero la raíz, luego cada hijo de izquierda a derecha.
    Es exactamente un recorrido en profundidad (DFS): baja por una rama
    hasta la hoja antes de pasar a la rama hermana.

    Caso base: una hoja no tiene hijos, así que el ciclo no hace llamadas.
    Caso recursivo: se imprime la misión y se llama para cada hijo con
    nivel + 1.

    Complejidad: O(n), porque cada misión se imprime exactamente una vez.
    """
    sangria = "    " * nivel
    estado = estado_de(nodo, padre_completado)
    print(f"{sangria}[{estado:^10}] {nodo.nombre}")
    for hijo in nodo.hijos:
        imprimir_preorden(hijo, nivel + 1, nodo.completada)


def altura(nodo):
    """
    Calcula la altura del árbol: cuántas aristas tiene el camino más
    largo desde este nodo hasta una hoja.

    Caso base: una hoja tiene altura 0.
    Caso recursivo: 1 + la mayor altura entre sus hijos.

    Complejidad: O(n), porque hay que visitar todos los nodos para saber
    cuál es la rama más larga.
    """
    if len(nodo.hijos) == 0:
        return 0
    return 1 + max(altura(hijo) for hijo in nodo.hijos)


def contar_hojas(nodo):
    """
    Cuenta las hojas: las misiones que no desbloquean ninguna otra.

    Caso base: si el nodo no tiene hijos, es una hoja y cuenta 1.
    Caso recursivo: la suma de las hojas de cada hijo.

    Complejidad: O(n), se visita cada nodo una vez.
    """
    if len(nodo.hijos) == 0:
        return 1
    return sum(contar_hojas(hijo) for hijo in nodo.hijos)


def obtener_hojas(nodo, resultado=None):
    """
    Devuelve la lista con los NOMBRES de las hojas, en preorden.
    Complejidad: O(n), se visita cada nodo una vez.
    """
    if resultado is None:
        resultado = []
    if len(nodo.hijos) == 0:
        resultado.append(nodo.nombre)
    for hijo in nodo.hijos:
        obtener_hojas(hijo, resultado)
    return resultado


def contar_nodos(nodo):
    """
    Cuenta todas las misiones del árbol (n).
    Caso base: un nodo sin hijos cuenta 1. Caso recursivo: 1 + nodos de cada hijo.
    Complejidad: O(n).
    """
    return 1 + sum(contar_nodos(hijo) for hijo in nodo.hijos)


def misiones_disponibles(nodo, padre_completado=True, resultado=None):
    """
    Devuelve las misiones DISPONIBLES: las que no están completadas y
    cuyo padre sí lo está. La raíz no tiene padre, así que está
    disponible mientras no se complete.

    Se recorre el árbol en preorden y se pasa a cada hijo si su padre
    está completado (parámetro padre_completado).

    Complejidad: O(n), porque se revisa cada misión una vez.
    """
    if resultado is None:
        resultado = []
    if not nodo.completada and padre_completado:
        resultado.append(nodo.nombre)
    for hijo in nodo.hijos:
        misiones_disponibles(hijo, nodo.completada, resultado)
    return resultado


def buscar_mision(nodo, nombre, padre=None):
    """
    Busca una misión por nombre y devuelve la tupla (mision, padre).
    Si no existe, devuelve (None, None). La comparación ignora
    mayúsculas y espacios sobrantes.

    Complejidad: O(n) en el peor caso, porque la misión puede ser la
    última del recorrido o no existir.
    """
    if nodo.nombre.strip().lower() == nombre.strip().lower():
        return nodo, padre
    for hijo in nodo.hijos:
        encontrada, su_padre = buscar_mision(hijo, nombre, nodo)
        if encontrada is not None:
            return encontrada, su_padre
    return None, None


def completar_mision(raiz, nombre):
    """
    Marca una misión como completada, SOLO si está desbloqueada.

    Reglas (dependencias):
        - Si la misión no existe: mensaje de error.
        - Si ya estaba completada: mensaje de aviso.
        - Si su padre no está completado: está BLOQUEADA y no se permite.
        - Si se completa: se muestran las misiones que se desbloquearon.

    Complejidad: O(n). Buscar la misión cuesta O(n) y calcular las
    disponibles antes y después también cuesta O(n); O(n) + O(n) = O(n).

    Retorna True si se completó, False si no se pudo.
    """
    if not isinstance(nombre, str) or nombre.strip() == "":
        print("  [!] Escribe el nombre de una misión.")
        return False

    mision, padre = buscar_mision(raiz, nombre)

    if mision is None:
        print(f"  [!] La misión '{nombre}' no existe en las crónicas de Hyrule.")
        return False

    if mision.completada:
        print(f"  [!] '{mision.nombre}' ya estaba completada.")
        return False

    if padre is not None and not padre.completada:
        print(f"  [X] '{mision.nombre}' está BLOQUEADA.")
        print(f"      Ezlo: \"Primero debes completar '{padre.nombre}'.\"")
        return False

    antes = misiones_disponibles(raiz)
    mision.completada = True
    despues = misiones_disponibles(raiz)
    nuevas = [m for m in despues if m not in antes]

    print(f"  [OK] ¡Misión completada: {mision.nombre}!")
    if nuevas:
        print("       Se desbloquearon:")
        for nueva in nuevas:
            print(f"         -> {nueva}")
    else:
        print("       No se desbloqueó nada nuevo: era una hoja del árbol.")
    return True


def construir_arbol_misiones():
    """
    Construye el árbol de misiones de "El Ascenso de Vaati".
    11 misiones, altura 4 (5 niveles: del 0 al 4) y 4 hojas.

    Coherente con main.py: al rescatar a Ezlo, Link recibe la Espada Minish
    y la Pluma de Roc; las misiones siguientes las templan y las dominan.
    El Elemento del Viento no aparece aquí porque se obtiene al derrotar a
    Vaati en la sala del jefe de la mazmorra.

        Rescatar a Ezlo en el Bosque Minish                (raíz, nivel 0)
        ├── Templar la Espada Minish con Melari             (nivel 1)
        │   ├── Obtener el Elemento de la Tierra            (nivel 2, hoja)
        │   └── Obtener el Elemento del Fuego               (nivel 2)
        │       └── Obtener el Elemento del Agua            (nivel 3, hoja)
        ├── Dominar la Pluma de Roc                         (nivel 1)
        │   └── Cruzar el Puente de las Nubes               (nivel 2)
        │       └── Entrar al Palacio de los Vientos        (nivel 3)
        │           └── Derrotar a Vaati                    (nivel 4, hoja)
        └── Visitar la Fuente de las Hadas                  (nivel 1)
            └── Recibir la Jarra Mágica                     (nivel 2, hoja)

    Complejidad: O(n), una llamada O(1) a agregar_hijo por cada misión.
    Retorna la raíz del árbol.
    """
    raiz = Nodo("Rescatar a Ezlo en el Bosque Minish")

    espada = agregar_hijo(raiz, Nodo("Templar la Espada Minish con Melari"))
    agregar_hijo(espada, Nodo("Obtener el Elemento de la Tierra"))
    fuego = agregar_hijo(espada, Nodo("Obtener el Elemento del Fuego"))
    agregar_hijo(fuego, Nodo("Obtener el Elemento del Agua"))

    pluma = agregar_hijo(raiz, Nodo("Dominar la Pluma de Roc"))
    puente = agregar_hijo(pluma, Nodo("Cruzar el Puente de las Nubes"))
    palacio = agregar_hijo(puente, Nodo("Entrar al Palacio de los Vientos"))
    agregar_hijo(palacio, Nodo("Derrotar a Vaati"))

    hadas = agregar_hijo(raiz, Nodo("Visitar la Fuente de las Hadas"))
    agregar_hijo(hadas, Nodo("Recibir la Jarra Mágica"))

    return raiz


# ======================================================================
# PARTE 2 · ÁRBOL DE DECISIÓN DEL MOBLIN
# ======================================================================

class NodoDecision:
    """
    Nodo del árbol de decisión.

    - Nodo interno (pregunta): guarda la pregunta y dos hijos, 'si' y 'no'.
      'clave' es el dato de la situación que responde la pregunta; si hay
      'umbral', la respuesta es Sí cuando el valor es MENOR que el umbral
      (por ejemplo, vida < 30). Si no hay umbral, el valor es True o False.
    - Hoja (decisión): guarda solo el texto de la decisión.
    """

    def __init__(self, pregunta=None, clave=None, umbral=None,
                 si=None, no=None, decision=None):
        self.pregunta = pregunta
        self.clave = clave
        self.umbral = umbral
        self.si = si
        self.no = no
        self.decision = decision

    def es_hoja(self):
        """Retorna True si el nodo es una decisión (hoja). Complejidad: O(1)."""
        return self.decision is not None


def pregunta(texto, clave, si, no, umbral=None):
    """Crea un nodo interno con una pregunta y sus dos hijos. Complejidad: O(1)."""
    return NodoDecision(pregunta=texto, clave=clave, umbral=umbral, si=si, no=no)


def decision(texto):
    """Crea una hoja con una decisión. Complejidad: O(1)."""
    return NodoDecision(decision=texto)


def responder(nodo, situacion):
    """
    Responde la pregunta de un nodo interno con los datos de la situación.
    Si falta el dato o no es válido, avisa y responde "No" para que el
    programa no se caiga.
    Complejidad: O(1), es una consulta a un diccionario.
    """
    if nodo.clave not in situacion:
        print(f"    [!] La situación no dice '{nodo.clave}'; el Moblin asume que No.")
        return False

    valor = situacion[nodo.clave]

    if nodo.umbral is not None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            print(f"    [!] '{nodo.clave}' debe ser un número; el Moblin asume que No.")
            return False
        return valor < nodo.umbral

    return bool(valor)


def decidir(nodo, situacion, mostrar=False):
    """
    Baja desde la raíz hasta una hoja y devuelve la decisión del Moblin.

    Caso base: el nodo es una hoja, así que se devuelve su decisión.
    Caso recursivo: se responde la pregunta y se baja al hijo 'si' o 'no'.

    En cada nivel se hace UNA sola pregunta y se descarta la otra rama
    completa, por eso no se visita todo el árbol.

    Complejidad: O(h), donde h es la altura del árbol de decisión: como
    máximo se hacen h preguntas.

    Si mostrar=True, imprime cada pregunta y su respuesta.
    """
    if nodo.es_hoja():
        return nodo.decision

    respuesta = responder(nodo, situacion)
    if mostrar:
        print(f"    {nodo.pregunta} -> {'Sí' if respuesta else 'No'}")

    siguiente = nodo.si if respuesta else nodo.no
    return decidir(siguiente, situacion, mostrar)


def imprimir_arbol_decision(nodo, nivel=0, etiqueta=""):
    """
    Imprime el árbol de decisión en preorden con sangría.
    Las preguntas llevan '?' y las decisiones llevan '=>'.
    Complejidad: O(n), cada nodo se imprime una vez.
    """
    sangria = "    " * nivel
    if nodo.es_hoja():
        print(f"{sangria}{etiqueta}=> {nodo.decision}")
        return
    print(f"{sangria}{etiqueta}{nodo.pregunta}")
    imprimir_arbol_decision(nodo.si, nivel + 1, "[Sí] ")
    imprimir_arbol_decision(nodo.no, nivel + 1, "[No] ")


def altura_decision(nodo):
    """
    Altura del árbol de decisión = número MÁXIMO de preguntas que el
    Moblin hace antes de decidir.
    Caso base: una hoja tiene altura 0. Caso recursivo: 1 + la mayor de sus dos ramas.
    Complejidad: O(n), se visitan todos los nodos.
    """
    if nodo.es_hoja():
        return 0
    return 1 + max(altura_decision(nodo.si), altura_decision(nodo.no))


def construir_arbol_moblin():
    """
    Construye el árbol de decisión del Moblin guardián del Palacio de
    los Vientos: 4 preguntas y 5 decisiones posibles, altura 3.

        ¿Link está cerca?
        ├── Sí: ¿Tengo poca vida? (vida < 30)
        │   ├── Sí: ¿Hay otro Moblin cerca?
        │   │   ├── Sí => Tocar el cuerno y pedir ayuda a la tropa
        │   │   └── No => Huir hacia la Caverna de los Keese
        │   └── No => Embestir a Link con la lanza
        └── No: ¿Escuché un ruido?
            ├── Sí => Ir a investigar el ruido
            └── No => Patrullar el Patio de los Moblins

    Complejidad: O(1): el árbol tiene un tamaño fijo.
    Retorna la raíz del árbol.
    """
    return pregunta(
        "¿Link está cerca?", "jugador_cerca",
        si=pregunta(
            "¿Tengo poca vida? (vida < 30)", "vida", umbral=30,
            si=pregunta(
                "¿Hay otro Moblin cerca?", "aliados_cerca",
                si=decision("Tocar el cuerno y pedir ayuda a la tropa"),
                no=decision("Huir hacia la Caverna de los Keese"),
            ),
            no=decision("Embestir a Link con la lanza"),
        ),
        no=pregunta(
            "¿Escuché un ruido?", "escucho_ruido",
            si=decision("Ir a investigar el ruido"),
            no=decision("Patrullar el Patio de los Moblins"),
        ),
    )


# ======================================================================
# PARTE 3 · CASO REAL: TORNEO DE ELIMINACIÓN DIRECTA
# ======================================================================

def construir_torneo():
    """
    Construye un torneo de TENIS de eliminación directa de 4 jugadores
    como árbol BINARIO (reutiliza la clase Nodo; cada partido tiene 2 hijos):

                          Final
                    /               \\
             Semifinal 1         Semifinal 2
             /        \\           /        \\
         Alcaraz     Sinner    Djokovic     Zverev

    - Hojas: los jugadores. Nodos internos: los partidos.
    - Relación padre-hijo: el ganador de un hijo juega en el partido padre.
    - Pregunta que responde: ¿quién es el campeón y cómo llegó?
    Complejidad: O(1): el torneo tiene un tamaño fijo.
    """
    final = Nodo("Final")
    semi1 = agregar_hijo(final, Nodo("Semifinal 1"))
    semi2 = agregar_hijo(final, Nodo("Semifinal 2"))
    agregar_hijo(semi1, Nodo("Alcaraz"))
    agregar_hijo(semi1, Nodo("Sinner"))
    agregar_hijo(semi2, Nodo("Djokovic"))
    agregar_hijo(semi2, Nodo("Zverev"))
    return final


def preorden(nodo, resultado=None):
    """
    Preorden: RAÍZ, luego cada hijo de izquierda a derecha. Es DFS.
    Complejidad: O(n).
    """
    if resultado is None:
        resultado = []
    resultado.append(nodo.nombre)
    for hijo in nodo.hijos:
        preorden(hijo, resultado)
    return resultado


def inorden(nodo, resultado=None):
    """
    Inorden: hijo IZQUIERDO, RAÍZ, hijo DERECHO.
    Solo está bien definido en árboles BINARIOS (máximo 2 hijos), por eso
    se usa con el torneo y no con el árbol de misiones.
    Complejidad: O(n).
    """
    if resultado is None:
        resultado = []
    if len(nodo.hijos) > 0:
        inorden(nodo.hijos[0], resultado)
    resultado.append(nodo.nombre)
    if len(nodo.hijos) > 1:
        inorden(nodo.hijos[1], resultado)
    return resultado


def postorden(nodo, resultado=None):
    """
    Postorden: primero TODOS los hijos y al final la RAÍZ.
    En el torneo es el orden real de juego: no se puede jugar la final
    antes de las semifinales (los hijos van antes que el padre).
    Complejidad: O(n).
    """
    if resultado is None:
        resultado = []
    for hijo in nodo.hijos:
        postorden(hijo, resultado)
    resultado.append(nodo.nombre)
    return resultado


# ======================================================================
# DEMO Y MODO DEFENSA
# ======================================================================

PAUSAR = "--sin-pausas" not in sys.argv


def pausa():
    """
    Espera a que el expositor presione Enter para pasar al siguiente
    bloque. No hace nada con --sin-pausas o si la entrada se termina.
    """
    if not PAUSAR:
        return
    try:
        input("\n   (Enter para continuar) ")
    except (EOFError, KeyboardInterrupt):
        print()


def titulo(texto):
    """Imprime el encabezado de un bloque de la exposición."""
    print("\n" + "=" * 66)
    print(f"  {texto}")
    print("=" * 66)


def leer_texto(mensaje):
    """
    Lee texto del usuario. Retorna None si la entrada se termina o se
    presiona Ctrl+C, para salir del modo defensa sin error.
    """
    try:
        return input(mensaje).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def leer_si_no(mensaje):
    """
    Pide una respuesta s/n hasta que sea válida.
    Retorna True (sí), False (no) o None si la entrada se termina.
    """
    while True:
        texto = leer_texto(mensaje)
        if texto is None:
            return None
        if texto.lower() in ("s", "si", "sí"):
            return True
        if texto.lower() == "n" or texto.lower() == "no":
            return False
        print("    [!] Responde con 's' o 'n'.")


def leer_entero(mensaje, minimo, maximo):
    """
    Pide un entero en el rango [minimo, maximo] hasta que sea válido.
    Maneja texto, decimales, negativos y números fuera de rango.
    Retorna el número o None si la entrada se termina.
    """
    while True:
        texto = leer_texto(mensaje)
        if texto is None:
            return None
        try:
            numero = int(texto)
        except ValueError:
            print(f"    [!] '{texto}' no es un número entero.")
            continue
        if numero < minimo or numero > maximo:
            print(f"    [!] Debe estar entre {minimo} y {maximo}.")
            continue
        return numero


def modo_defensa(misiones, moblin):
    """
    Menú opcional para la ronda de preguntas: permite probar EN VIVO
    una situación nueva del Moblin, agregar una misión nueva y ver cómo
    cambia el recorrido, o completar una misión.
    Toda entrada inválida muestra un mensaje y vuelve a preguntar.
    """
    while True:
        print("\n----------------- MODO DEFENSA -----------------")
        print("1. Probar una situación nueva con el Moblin")
        print("2. Agregar una misión nueva y ver el recorrido")
        print("3. Completar una misión")
        print("4. Ver misiones disponibles")
        print("5. Salir")
        opcion = leer_entero("Opción: ", 1, 5)

        if opcion is None or opcion == 5:
            print("\nEzlo: \"¡Buen trabajo, Link! Hyrule está en buenas manos.\"")
            return

        if opcion == 1:
            cerca = leer_si_no("  ¿Link está cerca? (s/n): ")
            if cerca is None:
                return
            vida = leer_entero("  Vida del Moblin (0 a 100): ", 0, 100)
            if vida is None:
                return
            aliados = leer_si_no("  ¿Hay otro Moblin cerca? (s/n): ")
            if aliados is None:
                return
            ruido = leer_si_no("  ¿Escuchó un ruido? (s/n): ")
            if ruido is None:
                return
            situacion = {"jugador_cerca": cerca, "vida": vida,
                         "aliados_cerca": aliados, "escucho_ruido": ruido}
            print(f"\n  Situación: {situacion}")
            print(f"  Decisión: {decidir(moblin, situacion, mostrar=True)}")

        elif opcion == 2:
            padre_nombre = leer_texto("  Nombre de la misión padre: ")
            if padre_nombre is None:
                return
            padre, _ = buscar_mision(misiones, padre_nombre)
            if padre is None:
                print(f"    [!] La misión '{padre_nombre}' no existe.")
                continue
            nueva = leer_texto("  Nombre de la misión nueva: ")
            if nueva is None:
                return
            if nueva == "":
                print("    [!] La misión necesita un nombre.")
                continue
            if buscar_mision(misiones, nueva)[0] is not None:
                print("    [!] Ya existe una misión con ese nombre.")
                continue
            agregar_hijo(padre, Nodo(nueva))
            print("\n  Árbol en preorden:")
            imprimir_preorden(misiones)
            print(f"\n  Altura: {altura(misiones)} | Hojas: {contar_hojas(misiones)}"
                  f" | Misiones: {contar_nodos(misiones)}")

        elif opcion == 3:
            nombre = leer_texto("  Nombre de la misión a completar: ")
            if nombre is None:
                return
            completar_mision(misiones, nombre)

        elif opcion == 4:
            print("  Misiones disponibles:")
            for m in misiones_disponibles(misiones):
                print(f"    - {m}")


def main():
    """
    Demo en vivo de la exposición, en el orden de los seis bloques:
        1. Qué es un árbol: árbol de misiones, raíz, hojas y altura.
        2. Recorridos: preorden, inorden y postorden (torneo).
        3. Caso real: el torneo de tenis de eliminación directa.
        4. Árbol de decisión del Moblin con 5 situaciones distintas.
        5. Dependencias: completar dos misiones y probar una bloqueada.
        6. Complejidad: nodos visitados y preguntas máximas.
    Al final ofrece el modo defensa para la ronda de preguntas.
    """
    misiones = construir_arbol_misiones()
    moblin = construir_arbol_moblin()
    torneo = construir_torneo()

    print("\n  LA LEYENDA DE ZELDA: EL ASCENSO DE VAATI")
    print("  Exposición: árboles, árboles de decisión y dependencias")

    # ------------------------------------------------------------ Bloque 1
    titulo("BLOQUE 1 · ¿QUÉ ES UN ÁRBOL? · El árbol de misiones de Link")
    imprimir_preorden(misiones)
    print(f"\n  Raíz:    {misiones.nombre}")
    print(f"  Misiones (n): {contar_nodos(misiones)}")
    print(f"  Altura (h):   {altura(misiones)}")
    print(f"  Hojas:        {contar_hojas(misiones)} -> {', '.join(obtener_hojas(misiones))}")
    pausa()

    # ------------------------------------------------------------ Bloque 2
    titulo("BLOQUE 2 · RECORRIDOS · Torneo de tenis de 4 jugadores (binario)")
    print(f"  Preorden  (raíz, izq, der): {' -> '.join(preorden(torneo))}")
    print(f"  Inorden   (izq, raíz, der): {' -> '.join(inorden(torneo))}")
    print(f"  Postorden (izq, der, raíz): {' -> '.join(postorden(torneo))}")
    print("\n  El preorden es DFS: baja por una rama hasta la hoja antes de")
    print("  pasar a la siguiente. Así se imprimió el árbol de misiones:")
    print(f"  {' -> '.join(preorden(misiones)[:4])} -> ...")
    pausa()

    # ------------------------------------------------------------ Bloque 3
    titulo("BLOQUE 3 · CASO REAL · Torneo de tenis de eliminación directa")
    jugadores = obtener_hojas(torneo)
    partidos = [p for p in postorden(torneo) if p not in jugadores]
    print(f"  Jugadores (hojas):  {', '.join(jugadores)}")
    print(f"  Rondas (altura h):  {altura(torneo)}")
    print(f"  Orden de los partidos (postorden): {' -> '.join(partidos)}")
    print("  Los hijos se juegan antes que el padre: la final va al final.")
    print("  Wimbledon tiene 128 jugadores: log2(128) = 7 rondas.")
    pausa()

    # ------------------------------------------------------------ Bloque 4
    titulo("BLOQUE 4 · ÁRBOL DE DECISIÓN · Moblin guardián del palacio")
    imprimir_arbol_decision(moblin)

    situaciones = [
        {"jugador_cerca": True, "vida": 80, "aliados_cerca": False, "escucho_ruido": False},
        {"jugador_cerca": True, "vida": 20, "aliados_cerca": True, "escucho_ruido": False},
        {"jugador_cerca": True, "vida": 20, "aliados_cerca": False, "escucho_ruido": True},
        {"jugador_cerca": False, "vida": 90, "aliados_cerca": True, "escucho_ruido": True},
        {"jugador_cerca": False, "vida": 90, "aliados_cerca": False, "escucho_ruido": False},
    ]
    for numero, situacion in enumerate(situaciones, start=1):
        print(f"\n  Situación {numero}: {situacion}")
        print(f"  => Decisión: {decidir(moblin, situacion, mostrar=True)}")
    pausa()

    # ------------------------------------------------------------ Bloque 5
    titulo("BLOQUE 5 · DEPENDENCIAS · Completar misiones en vivo")
    print(f"  Disponibles al inicio: {misiones_disponibles(misiones)}")

    print("\n  1) Completar la raíz:")
    completar_mision(misiones, "Rescatar a Ezlo en el Bosque Minish")

    print("\n  2) Completar 'Dominar la Pluma de Roc':")
    completar_mision(misiones, "Dominar la Pluma de Roc")

    print("\n  3) Intentar 'Derrotar a Vaati' (todavía está bloqueada):")
    completar_mision(misiones, "Derrotar a Vaati")

    print("\n  4) Intentar una misión que no existe:")
    completar_mision(misiones, "Encontrar la Trifuerza")

    print("\n  Árbol actualizado:")
    imprimir_preorden(misiones)
    print(f"\n  Disponibles ahora: {misiones_disponibles(misiones)}")
    pausa()

    # ------------------------------------------------------------ Bloque 6
    titulo("BLOQUE 6 · COMPLEJIDAD")
    print(f"  Recorrido completo de misiones: visita n = {contar_nodos(misiones)} nodos -> O(n)")
    print(f"  Preguntas máximas del Moblin:   h = {altura_decision(moblin)} -> O(h)")
    print("  Si el árbol de decisión se volviera una sola fila (degenerado),")
    print("  h sería igual al número de preguntas: con 15 preguntas, el Moblin")
    print("  haría hasta 15. Si estuviera balanceado, con 16 decisiones")
    print("  bastarían h = log2(16) = 4 preguntas.")

    # ------------------------------------------------------------ Defensa
    if PAUSAR:
        if leer_si_no("\n¿Abrir el modo defensa para la ronda de preguntas? (s/n): "):
            modo_defensa(misiones, moblin)
        else:
            print("\nEzlo: \"¡Buen trabajo, Link! Hyrule está en buenas manos.\"")


if __name__ == "__main__":
    main()
