# La Leyenda de Zelda: El Ascenso de Vaati
### Aventura Algorítmica · Checkpoint 2: Pilas, Colas y Recursividad

> Link debe adentrarse en el **Palacio de los Vientos**, una mazmorra que cambia de forma en cada partida, enfrentar a los secuaces de Vaati en orden de llegada y usar el poder del tiempo para deshacer sus pasos cuando el camino se vuelve peligroso.

---

## Aportes del equipo

* **Alejandro Esperanza:** Diseñó e implementó `historial.py` (pila con `append`/`pop`), incluidas las adaptaciones de la Guía 5 `deshacer_multiples` y `contar_acciones_de_tipo`, y la validación del historial vacío.
* **Jonathan Delgado:** Implementó `eventos.py` con `collections.deque`: la cola de eventos del mapa, el sistema de turnos circular (`simular_turnos`) y `procesar_multiples_eventos`, con sus casos límite.
* **Fernando Mejía:** Desarrolló `mazmorra.py`: la función recursiva `generar_mazmorra`, el marcado de salas profundas, la ramificación variable, el cálculo de profundidad real, el conteo por nivel y la impresión del árbol.
* **Arturo Guardado:** Integró los módulos en `main.py` (menú, backtracking, recolección de tesoros), validó todas las entradas del usuario, ejecutó las pruebas de casos límite y redactó este README junto con la evidencia de ejecución.

---

## Cómo ejecutar el juego

**Requisitos:** Python 3.8 o superior. No se necesitan librerías externas (`collections` y `random` son parte de la biblioteca estándar).

```bash
python main.py
```

Cada módulo también puede ejecutarse por separado (`python historial.py`, `python eventos.py`, `python mazmorra.py`) para ver una demostración de sus funciones y casos límite.

### Estructura del proyecto (Guía 1)

```
Aventura-Algoritmica/
├── main.py          # Archivo central: menú, bucle de juego e integración
├── inventario.py    # Checkpoint 1: inventario con listas
├── historial.py     # Pila (LIFO): historial de acciones y deshacer
├── eventos.py       # Cola (FIFO con deque): eventos del mapa y turnos
├── mazmorra.py      # Recursividad: generación del Palacio de los Vientos
├── arboles.py       # Exposición de árboles: misiones, decisión del Moblin y torneo
├── README.md
└── docs/
    ├── diagrama_flujo_usar_objeto.png
    ├── pseudocodigo_usar_objeto.txt
    └── evidencia_partida.txt   # Texto de la consola de una partida completa
```

Las funciones no se copian en `main.py`: se importan desde cada módulo, y cada una lleva su docstring.

### Base del Checkpoint 1

El inventario con listas sigue funcionando y sus tres funciones se usan dentro de la partida:

* `agregar_objeto` (`append`, O(1)): Link empieza con la **Espada Minish** y la **Pluma de Roc**, y recibe los objetos de las salas marcadas.
* `usar_objeto` (búsqueda lineal con `in`, O(n)): opción 3 del menú, **Usar un objeto**.
* `soltar_objeto` (`remove`, O(n)): devuelve un objeto a su cofre cuando se deshace una recolección.

El pseudocódigo y el diagrama de flujo de `usar_objeto` están en `docs/`.

---

## 1. Historial de acciones (Pila / LIFO) — `historial.py`

### Mecánica implementada

El **Libro de Crónicas de Hyrule** registra cada acción importante de Link: moverse de sala, recoger un objeto y usar un objeto. Cada acción se guarda como un diccionario:

```python
{"tipo": "Moverse", "desde": "Pasillo de los Ecos", "hacia": "Torre del Remolino", ...}
{"tipo": "Recoger", "objeto": "Botas de Pegaso", "sala": "Mina de Cristal [COFRE: Botas de Pegaso]"}
{"tipo": "Usar", "objeto": "Pluma de Roc"}
```

Guardar el origen (`desde`) es lo que permite el **backtracking real**: al deshacer un movimiento, Link vuelve físicamente a la sala anterior.

| Función | Qué hace | Operación clave | Complejidad |
|---|---|---|---|
| `registrar_accion` | Apila una acción en la cima | `append()` | O(1) amortizado |
| `deshacer_ultima_accion` | Saca y devuelve la acción más reciente | `pop()` | O(1) |
| `ver_ultima_accion` | Consulta la cima sin sacarla | `historial[-1]` | O(1) |
| `mostrar_historial_completo` | Imprime de la cima a la base | recorrido inverso | O(n) |
| `deshacer_multiples` *(Guía 5)* | "Ocarina del Viento": deshace `n` acciones (**opción 5 del menú**) | `pop()` × n | O(k), k = mín(n, tamaño) |
| `contar_acciones_de_tipo` *(Guía 5)* | Cuenta acciones de un tipo (**opción 6 del menú**: movimientos, recolecciones y usos) | recorrido | O(n) |

### ¿Por qué una pila (LIFO)?

Deshacer consiste, por definición, en revertir **primero lo último que se hizo**. Si Link camina Entrada → Pasillo → Torre, la única forma coherente de retroceder es Torre → Pasillo → Entrada: el orden inverso exacto en que avanzó. Una pila garantiza ese comportamiento por su propia estructura, porque el último elemento que entra es el primero que sale. Es el mismo principio que usan el botón "Atrás" del navegador o Ctrl+Z en un editor.

Con una cola (FIFO) se desharía la acción más antigua (volver a la entrada desde cualquier punto), lo que rompería la coherencia del recorrido.

### Complejidad

La cima de la pila es el **final de la lista** de Python:

* **Apilar con `append()` es O(1) amortizado:** la lista reserva memoria extra, así que agregar al final casi nunca requiere mover elementos.
* **Desapilar con `pop()` (sin índice) es O(1):** quitar el último elemento no obliga a desplazar a ningún otro.

Por eso en el módulo **nunca se usan `pop(0)` ni `insert(0, x)`**: ambas operan sobre el inicio de la lista y desplazan todos los elementos, con costo O(n).

### Fragmento de código relevante

```python
def deshacer_ultima_accion(historial):
    """
    Desapila y devuelve la acción más reciente (la cima de la pila).
    LIFO: pop() sin índice extrae el último elemento añadido.
    Complejidad: O(1).
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
```

---

## 2. Eventos y turnos (Cola / FIFO con `deque`) — `eventos.py`

### Mecánica implementada

1. **Cola de eventos del mapa:** al iniciar la partida se encolan 8 eventos temáticos (un Moblin que bloquea el paso, rupias ocultas, una trampa de pinchos, Keese, un Octorok, un Chuchu Rojo, una Gran Hada y la risa de Vaati). **Cada vez que Link se mueve, se procesa el siguiente evento** con `popleft()`.
2. **Sistema de turnos de combate:** Link, un Moblin y un Octorok forman una cola circular. El participante del frente actúa (`popleft()`) y vuelve a formarse al final (`append()`), de modo que todos actúan en orden y la ronda puede repetirse indefinidamente (Round Robin).

| Función | Qué hace | Complejidad |
|---|---|---|
| `inicializar_cola_eventos` | Convierte la lista de eventos en una `deque`, validando cada uno | O(n) |
| `encolar_evento` | Agrega un evento al final | O(1) |
| `procesar_siguiente_evento` | Saca y narra el evento del frente | O(1) |
| `simular_turnos` *(Guía 6)* | Una ronda completa con `popleft()` + `append()` (**opción 8 del menú**) | O(k), k = participantes |
| `procesar_multiples_eventos` *(Guía 6)* | Procesa `n` eventos seguidos, se detiene si la cola se vacía (**opción 7 del menú**) | O(mín(n, tamaño)) |
| `mostrar_cola_eventos` | Muestra los eventos pendientes sin modificar la cola (antes de explorar, opción 7) | O(n) |

### ¿Por qué una cola (FIFO)?

* **Eventos del mapa:** los eventos representan lo que el destino de Hyrule tiene preparado para Link, en un orden narrativo definido. Deben ocurrir **en el mismo orden en que se programaron**: lo primero que se encola es lo primero que sucede. Eso es exactamente FIFO.
* **Turnos de batalla:** un combate justo exige que nadie actúe dos veces antes de que los demás hayan actuado. Al sacar al participante del frente y devolverlo al final, la cola reparte los turnos de forma equitativa y cíclica, sin necesidad de contadores ni índices.

### Complejidad: `deque.popleft()` O(1) frente a `list.pop(0)` O(n)

Esta es la razón por la que el módulo usa **obligatoriamente `collections.deque`**:

* **`list.pop(0)` es O(n).** Una lista de Python guarda sus elementos en un bloque **contiguo** de memoria. Al eliminar el primer elemento queda un hueco al inicio, y Python debe desplazar **todos** los elementos restantes una posición a la izquierda. Con 1,000 eventos, cada extracción mueve hasta 999 referencias; vaciar la cola completa costaría O(n²).
* **`deque.popleft()` es O(1).** Una `deque` (*double-ended queue*) está implementada como una lista **doblemente enlazada de bloques**, con referencias directas a ambos extremos. Quitar el primer elemento solo actualiza el puntero del extremo izquierdo; ningún otro dato se mueve en memoria.

| Operación | `list` | `deque` |
|---|---|---|
| Encolar al final | `append()` → O(1) | `append()` → O(1) |
| Desencolar del frente | `pop(0)` → **O(n)** | `popleft()` → **O(1)** |

Como **cada movimiento de Link dispara un `popleft()`**, usar `deque` mantiene el costo de cada turno constante sin importar cuántos eventos tenga el mapa.

### Fragmento de código relevante

```python
from collections import deque

def procesar_siguiente_evento(cola_eventos):
    """
    Extrae, narra y devuelve el siguiente evento (el más antiguo).
    FIFO: popleft() retira el elemento del frente en O(1), a diferencia de
    list.pop(0), que es O(n) porque desplaza todos los elementos en memoria.
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
```

---

## 3. Generación de mazmorra (Recursividad) — `mazmorra.py`

### Mecánica implementada

Al iniciar la partida se genera el **Palacio de los Vientos**, la fortaleza de Vaati, como un **grafo de adyacencia** (diccionario): la clave es el nombre de la sala y el valor es la lista de salas conectadas. Las conexiones son bidireccionales, por lo que Link puede caminar en ambos sentidos.

Adaptaciones de la Guía 7 implementadas:

1. **Marcar las salas más profundas:** al llegar al caso base de profundidad máxima, se concatena al nombre un marcador: la primera sala profunda recibe **`[JEFE VAATI]`** y las demás **`[COFRE: objeto]`**.
2. **Ramificación variable:** con `random.randint(1, 3)` cada sala abre 1, 2 o 3 puertas, así que **cada partida genera una mazmorra distinta**.
3. **Calcular la profundidad real alcanzada:** `calcular_profundidad_real()` (también recursiva).
4. **Contar las salas por nivel:** `contar_salas_por_nivel()` (también recursiva).

La función `crear_mazmorra()` llama a la función recursiva y **garantiza los mínimos del checkpoint** (al menos 7 salas, profundidad real ≥ 2 y un jefe colocado). Si un intento aleatorio genera una mazmorra demasiado pequeña, se vuelve a generar; como respaldo final, se fuerza una ramificación mínima de 2, que asegura 1 + 2 + 4 = 7 salas.

### ¿Por qué recursividad?

Una mazmorra es una estructura **jerárquica**: cada puerta conduce a una sala que es, a su vez, la entrada de una mazmorra más pequeña. Generar una sala y luego "pedir que se genere el resto" desde cada una de sus puertas es aplicar el **mismo procedimiento a un subproblema más pequeño**: la definición de un problema recursivo. Hacerlo con ciclos obligaría a manejar a mano una pila de salas pendientes; la recursión usa la pila de llamadas de Python para eso, y el código queda más corto y fiel a la forma del árbol.

* **Caso base** (la función retorna sin volver a llamarse):
  * **a)** `profundidad_actual == profundidad_maxima`: la sala está en el nivel más profundo. Aquí se le concatena el marcador `[JEFE VAATI]` o `[COFRE: ...]` y no se abren más puertas.
  * **b)** Se alcanzó el límite de salas o no quedan nombres disponibles: la sala queda como callejón sin salida.
* **Caso recursivo:** se elige al azar cuántas puertas abre la sala (1 a 3); por cada puerta se toma un nombre nuevo, se conecta y se llama a `generar_mazmorra(...)` con `profundidad_actual + 1`. Cada llamada se acerca al caso base porque la profundidad siempre aumenta y los nombres disponibles siempre disminuyen, lo que garantiza que la recursión termina.

### Complejidad

Sea **b** el factor de ramificación (máximo 3) y **d** la profundidad máxima:

* **Temporal: O(b^d).** En el peor caso se crean 1 + b + b² + … + b^d salas, serie dominada por b^d (además, acotada por `limite_salas`).
* **Espacial: O(b^d)** para el diccionario con todas las salas, más **O(d)** para la pila de llamadas, porque el recorrido es en profundidad y solo hay una llamada activa por nivel.

### Árbol de la mazmorra (partida de la evidencia)

Como la ramificación es aleatoria, cada partida produce un árbol distinto. Este es el árbol que `imprimir_arbol_mazmorra()` mostró en la partida registrada en `docs/evidencia_partida.txt` (12 salas, profundidad 3):

```
=============== MAPA DEL PALACIO DE LOS VIENTOS ===============
🏰 Entrada del Palacio de los Vientos  (nivel 0)
├── Galería de los Vientos  (nivel 1)
│   └── Cripta de los Caballeros  (nivel 2)
│       ├── Puente de las Nubes [JEFE VAATI]  (nivel 3)
│       └── Bóveda de las Rupias [COFRE: Fragmento de Corazón]  (nivel 3)
├── Biblioteca Hyliana  (nivel 1)
│   └── Escalinata Celeste  (nivel 2)
│       ├── Pasillo de los Ecos [COFRE: Boomerang Mágico]  (nivel 3)
│       └── Santuario Minish [COFRE: Brazalete de Fuerza]  (nivel 3)
└── Cámara de las Antorchas  (nivel 1)
    └── Torre del Remolino  (nivel 2)
        └── Jardín de los Picori [COFRE: Llave del Jefe]  (nivel 3)
---------------------------------------------------------------
Total de salas: 12 | Profundidad real: 3
  Nivel 0: 1 sala(s)
  Nivel 1: 3 sala(s)
  Nivel 2: 3 sala(s)
  Nivel 3: 5 sala(s)
Salas marcadas (jefe o cofre): 5
===============================================================
```

Se observa la **ramificación variable** (la Entrada abre 3 puertas, la Galería de los Vientos solo 1, la Cripta de los Caballeros 2) y que **solo las salas del nivel más profundo** llevan marcador.

### Fragmento de código relevante

```python
def generar_mazmorra(mapa, sala_actual, sala_padre, profundidad_actual,
                     profundidad_maxima, nombres_disponibles, estado,
                     limite_salas=15, rama_min=1, rama_max=3):
    # Registrar la sala y su conexión de regreso
    mapa[sala_actual] = []
    if sala_padre is not None:
        mapa[sala_actual].append(sala_padre)

    # CASO BASE (a): nivel más profundo -> se marca con jefe o cofre
    if profundidad_actual >= profundidad_maxima:
        _marcar_sala_profunda(mapa, sala_actual, sala_padre, estado)
        return mapa

    # CASO BASE (b): sin espacio o sin nombres disponibles
    if len(mapa) >= limite_salas or len(nombres_disponibles) == 0:
        return mapa

    # CASO RECURSIVO: ramificación variable (1, 2 o 3 puertas)
    numero_puertas = random.randint(rama_min, rama_max)
    for _ in range(numero_puertas):
        if len(mapa) >= limite_salas or len(nombres_disponibles) == 0:
            break
        nueva_sala = nombres_disponibles.pop()
        mapa[sala_actual].append(nueva_sala)
        generar_mazmorra(mapa, nueva_sala, sala_actual, profundidad_actual + 1,
                         profundidad_maxima, nombres_disponibles, estado,
                         limite_salas, rama_min, rama_max)
    return mapa
```

---

## 4. Integración y toma de decisiones — `main.py`

### Cómo interactúan las estructuras

`main.py` importa los cuatro módulos y ejecuta un menú dentro de un ciclo `while True`:

```
1. Moverse a otra sala
2. Ver inventario
3. Usar un objeto
4. Deshacer última acción
5. Tocar la Ocarina del Viento (deshacer varias acciones)
6. Ver historial completo
7. Explorar la sala (resolver varios eventos)
8. Simular turnos de batalla
9. Salir del juego
```

Cada función pedida por las guías se puede ver funcionando dentro de la partida:

| Opción | Función que se llama | Estructura |
|---|---|---|
| 1. Moverse | `historial.registrar_accion`, `eventos.procesar_siguiente_evento`, `inventario.agregar_objeto` | Pila + Cola + Lista |
| 2. Ver inventario | recorrido de la lista del inventario | Lista |
| 3. Usar un objeto | `inventario.usar_objeto` + `historial.registrar_accion` | Lista + Pila |
| 4. Deshacer | `historial.deshacer_ultima_accion` | Pila (`pop`) |
| 5. Ocarina del Viento | `historial.deshacer_multiples` *(Guía 5)* | Pila (`pop` × n) |
| 6. Historial | `mostrar_historial_completo`, `ver_ultima_accion`, `contar_acciones_de_tipo` *(Guía 5)* | Pila |
| 7. Explorar la sala | `eventos.mostrar_cola_eventos`, `eventos.procesar_multiples_eventos` *(Guía 6)* | Cola (`popleft` × n) |
| 8. Turnos de batalla | `eventos.simular_turnos` *(Guía 6)* | Cola circular |

**Al iniciar:** se genera la mazmorra con la función recursiva y se imprime su árbol; Link empieza en la *Entrada del Palacio de los Vientos*; se crean el inventario (lista, con la Espada Minish y la Pluma de Roc), el historial (pila), la cola de eventos (`deque`) y la cola de turnos (Link, Moblin y Octorok).

**Flujo de un movimiento (opción 1):**

```
Elegir sala conectada
      │
      ├─► historial.registrar_accion({"tipo": "Moverse", "desde": A, "hacia": B})   [PILA: append]
      ├─► sala_actual = B
      ├─► eventos.procesar_siguiente_evento(cola)                                   [COLA: popleft]
      └─► ¿La sala tiene [JEFE VAATI] o [COFRE: ...]?
              └─► inventario.agregar_objeto(mochila, objeto)                        [LISTA: append]
                  historial.registrar_accion({"tipo": "Recoger", ...})              [PILA: append]
```

* **Usar un objeto (opción 3):** el jugador elige un objeto de la bolsa por número; `inventario.usar_objeto()` lo busca con una búsqueda lineal O(n) y la acción `"Usar"` se apila en el historial.
* **Deshacer (opción 4):** `historial.deshacer_ultima_accion()` hace `pop()`. Si la acción fue un movimiento, Link vuelve a la sala `desde` (**backtracking real**). Si fue una recolección, el objeto sale del inventario y vuelve a su cofre; un segundo deshacer revierte el movimiento. Si fue un uso, el efecto se desvanece, pero el objeto sigue en la bolsa porque usarlo no lo consume. Siempre se deshace lo más reciente, respetando LIFO.
* **Ocarina del Viento (opción 5):** el jugador indica cuántas acciones deshacer y `historial.deshacer_multiples()` ejecuta `pop()` esa cantidad de veces. `main.py` aplica el efecto de cada acción en el orden en que salieron de la pila (de la más reciente a la más antigua), con la misma lógica del deshacer simple. Si se deshacen varios movimientos, Link termina en la sala desde la que hizo el movimiento más antiguo de los deshechos.
* **Historial (opción 6):** muestra la pila de la cima a la base, consulta la cima sin sacarla con `ver_ultima_accion` y usa `contar_acciones_de_tipo` para resumir cuántos movimientos, recolecciones y usos hizo Link.
* **Explorar la sala (opción 7):** Link se queda en la sala y enfrenta varios eventos seguidos. Primero `mostrar_cola_eventos()` muestra los pendientes; luego el jugador elige cuántos enfrentar y `eventos.procesar_multiples_eventos()` los saca con `popleft()` en orden de llegada (FIFO).
* **Turnos (opción 8):** `eventos.simular_turnos()` ejecuta una ronda completa con `popleft()` + `append()`.
* Cada tesoro solo puede recogerse una vez (se controla con un conjunto `tesoros_recogidos`).

### Decisión: ¿qué pasa con los eventos al deshacer un movimiento?

**El evento ya procesado se pierde: no vuelve a la cola.**

**Justificación:**

1. **Coherencia con el mundo del juego:** el poder del tiempo devuelve a Link físicamente a la sala anterior, pero lo que ocurrió en Hyrule ya ocurrió: el Moblin derrotado no revive, las rupias recogidas no reaparecen y la trampa ya se activó. Deshacer es retroceder en el **espacio** (la ubicación de Link), no en el **destino** del mapa.
2. **Pureza de la estructura FIFO:** volver a meter el evento obligaría a insertarlo al frente (`appendleft`), lo que rompería el principio de "el primero en llegar es el primero en salir" que la rúbrica evalúa. Así, la cola solo usa `append` para encolar y `popleft` para desencolar.
3. **Evita trampas de juego:** si los eventos regresaran, el jugador podría moverse y deshacer repetidamente para "reciclar" eventos favorables, como las rupias o la Gran Hada.

Como referencia, cada movimiento guarda en el historial el evento que disparó (clave `"evento"`), pero esa información no se reinyecta en la cola.

La misma regla aplica a la **Ocarina del Viento**: aunque deshaga varios movimientos de una vez, ningún evento vuelve a la cola.

### Manejo de casos límite

El programa **no se cierra con error en ningún caso**; siempre muestra un mensaje y continúa el ciclo:

| Caso límite | Dónde se maneja | Qué ocurre |
|---|---|---|
| Deshacer con historial vacío | `historial.deshacer_ultima_accion` | Verifica `len(historial) == 0` antes de `pop()`, avisa y retorna `None`; `main.py` deja a Link en su sala. |
| Procesar evento con cola vacía | `eventos.procesar_siguiente_evento` | Verifica la longitud antes de `popleft()`, informa que la sala está despejada y retorna `None`. |
| Texto o símbolos en un menú | `leer_opcion_numerica` en `main.py` | `int()` dentro de `try/except ValueError`; se muestra un mensaje y se hace `continue`. |
| `0`, negativos o fuera de rango | `leer_opcion_numerica` | Se valida el rango `[mínimo, máximo]` explícitamente antes de usar el número. |
| Sala inexistente o no conectada | `accion_moverse` + `mazmorra.existe_conexion` | Solo se aceptan índices del 1 al total de puertas mostradas (se evita que `lista[-1]` seleccione una sala), y luego se verifica la conexión en el grafo. |
| `Ctrl+C` / fin de la entrada (EOF) en un `input()` | `leer_entrada` | Captura `KeyboardInterrupt` y `EOFError` y cierra la partida de forma ordenada (`SystemExit(0)`), sin traceback y sin quedar en un ciclo infinito. |
| Consola de Windows o salida redirigida a archivo | inicio de `main.py` | `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` evita `UnicodeEncodeError` al imprimir emojis y tildes. |
| Parámetros inválidos de la mazmorra | `mazmorra.crear_mazmorra` | Valida tipo y rango de la profundidad y del límite de salas; nunca genera menos de 7 salas ni profundidad menor a 2. |
| Ocarina con historial vacío / Explorar con cola vacía | `deshacer_multiples`, `procesar_multiples_eventos` | Avisan que no hay acciones o eventos y retornan una lista vacía; Link no se mueve. |
| Cantidad inválida en la Ocarina o al Explorar | `accion_ocarina`, `accion_explorar` en `main.py` | Solo se acepta de 1 hasta el total de acciones o eventos disponibles; texto, `0`, negativos o un número mayor se rechazan y no se deshace ni se procesa nada. |
| Usar un objeto con la bolsa vacía o un número inválido | `accion_usar_objeto` en `main.py` | Avisa que la bolsa está vacía o rechaza la opción; no se registra ninguna acción. |

> **Nota técnica:** en Python, `lista[-1]` no lanza error porque cuenta desde el final. Por eso, en `main.py` se valida el rango **antes** de usar el índice `eleccion - 1`.

---

## 6. Exposición de árboles — `arboles.py`

Archivo independiente para la exposición de árboles, árboles de decisión y dependencias (base del árbol de misiones del Checkpoint 3). Se ejecuta con `python arboles.py` (o `python arboles.py --sin-pausas`) y no importa los otros módulos.

* **Árbol de misiones** (clase `Nodo`): 11 misiones, altura 4 y 4 hojas, con `agregar_hijo`, recorrido en preorden con sangría, `altura`, `contar_hojas`, `misiones_disponibles` y `completar_mision`, que no deja completar una misión bloqueada.
* **Coherencia con el juego:** al rescatar a Ezlo, Link recibe la Espada Minish y la Pluma de Roc (por eso empieza con ambas en `main.py`); las misiones siguientes son templarlas y dominarlas. La rama final, *Entrar al Palacio de los Vientos → Derrotar a Vaati*, es la mazmorra que se juega en este checkpoint.
* **Árbol de decisión del Moblin** guardián del Palacio de los Vientos: 4 preguntas y 5 decisiones, con `decidir(nodo, situacion)` en O(h).
* **Caso real:** un torneo de tenis de eliminación directa, con preorden, inorden y postorden.

## 5. Evidencia de ejecución

El archivo `docs/evidencia_partida.txt` contiene el texto de la consola de una partida completa, que muestra: la mazmorra generada, al menos 3 movimientos, al menos 2 eventos procesados, una ronda completa del sistema de turnos, un deshacer que devuelve a Link a la sala anterior, el historial en pantalla y varios casos límite manejados sin error (deshacer y Ocarina con historial vacío, y las opciones `abc`, `0` y `-2` en el menú). También muestra funcionando dentro de la partida las funciones de las guías: `usar_objeto` (Checkpoint 1), `deshacer_multiples` y `contar_acciones_de_tipo` (Guía 5), y `procesar_multiples_eventos` y `simular_turnos` (Guía 6).