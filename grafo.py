"""
Módulo de grafos - Checkpoint 3 (Aventura Algorítmica)
La Leyenda de Zelda: El Ascenso de Vaati

Implementación GENÉRICA y reutilizable de un grafo con lista de adyacencia.
No depende de la mazmorra: sirve para cualquier conjunto de elementos
relacionados (salas, ciudades, personajes...). En el juego se usa para el
Palacio de los Vientos, y la autoprueba del final la usa con otro mapa
(las regiones de Hyrule) para mostrar que es reutilizable.

Representación (lista de adyacencia con un diccionario):
    self._adyacencia = {
        "Entrada del Palacio": ["Pasillo de los Ecos", "Santuario Minish"],
        "Pasillo de los Ecos": ["Entrada del Palacio"],
        ...
    }
    - Clave: el vértice (cualquier valor inmutable, normalmente un texto).
    - Valor: la lista de sus vecinos.

¿Por qué lista de adyacencia y no matriz?
    Una mazmorra tiene pocas puertas por sala (grafo disperso). La lista de
    adyacencia ocupa O(V + E) de memoria, mientras que una matriz ocupa
    O(V^2) aunque casi todas sus celdas estén vacías. Además, recorrer los
    vecinos de una sala cuesta O(grado) y no O(V).

Aristas bloqueadas:
    BFS, DFS y las rutas reciben un conjunto opcional de aristas bloqueadas
    (tuplas (a, b)). Así el MISMO grafo sirve para preguntar "¿por dónde se
    puede pasar AHORA?" sin borrar aristas: en el juego, las puertas selladas
    viven en el diccionario de estado y se pasan aquí como bloqueadas.

Complejidad (V = vértices, E = aristas):
    agregar_vertice / agregar_arista ........ O(1) promedio
    vecinos(v) .............................. O(1) para obtener la lista
    BFS, DFS, ruta_mas_corta, alcanzables ... O(V + E)
    componentes_conexas ..................... O(V + E)
"""

from collections import deque


class Grafo:
    """
    Grafo con lista de adyacencia. Puede ser dirigido o no dirigido.

    Ejemplo:
        g = Grafo()
        g.agregar_arista("A", "B")
        g.ruta_mas_corta("A", "B")   # -> ["A", "B"]
    """

    def __init__(self, dirigido=False):
        """Crea un grafo vacío. Complejidad: O(1)."""
        self.dirigido = dirigido
        self._adyacencia = {}

    # ------------------------------------------------------------------
    # Construcción y consulta
    # ------------------------------------------------------------------

    def agregar_vertice(self, vertice):
        """
        Agrega un vértice sin vecinos. Si ya existía, no hace nada.
        Complejidad: O(1) promedio (inserción en diccionario).
        Retorna True si lo agregó, False si ya existía.
        """
        if vertice in self._adyacencia:
            return False
        self._adyacencia[vertice] = []
        return True

    def agregar_arista(self, a, b):
        """
        Conecta a con b (y b con a si el grafo no es dirigido). Crea los
        vértices si no existían. No duplica aristas ni permite lazos (a == b).
        Complejidad: O(grado), por la revisión de duplicados.
        Retorna True si agregó la arista, False si ya existía o era un lazo.
        """
        if a == b:
            return False
        self.agregar_vertice(a)
        self.agregar_vertice(b)
        if b in self._adyacencia[a]:
            return False
        self._adyacencia[a].append(b)
        if not self.dirigido:
            self._adyacencia[b].append(a)
        return True

    def eliminar_arista(self, a, b):
        """
        Quita la arista entre a y b. Si no existe, no falla.
        Complejidad: O(grado). Retorna True si la quitó.
        """
        if not self.existe_arista(a, b):
            return False
        self._adyacencia[a].remove(b)
        if not self.dirigido and a in self._adyacencia.get(b, []):
            self._adyacencia[b].remove(a)
        return True

    def existe_vertice(self, vertice):
        """Indica si el vértice está en el grafo. Complejidad: O(1) promedio."""
        return vertice in self._adyacencia

    def existe_arista(self, a, b):
        """Indica si hay arista de a hacia b. Complejidad: O(grado)."""
        return b in self._adyacencia.get(a, [])

    def vecinos(self, vertice):
        """
        Retorna una COPIA de la lista de vecinos. Si el vértice no existe,
        retorna una lista vacía en lugar de lanzar KeyError.
        Complejidad: O(grado), por la copia.
        """
        return list(self._adyacencia.get(vertice, []))

    def vertices(self):
        """Retorna la lista de vértices. Complejidad: O(V)."""
        return list(self._adyacencia.keys())

    def num_vertices(self):
        """Cantidad de vértices. Complejidad: O(1)."""
        return len(self._adyacencia)

    def num_aristas(self):
        """
        Cantidad de aristas (en un grafo no dirigido, cada puerta cuenta
        una sola vez). Complejidad: O(V).
        """
        total = sum(len(v) for v in self._adyacencia.values())
        return total if self.dirigido else total // 2

    def como_diccionario(self):
        """
        Retorna una copia de la lista de adyacencia como diccionario.
        Complejidad: O(V + E).
        """
        return {v: list(vec) for v, vec in self._adyacencia.items()}

    # ------------------------------------------------------------------
    # Ayuda para aristas bloqueadas
    # ------------------------------------------------------------------

    def _bloqueada(self, a, b, bloqueadas):
        """
        Indica si la arista a-b está bloqueada. En un grafo no dirigido se
        revisan los dos sentidos. Complejidad: O(1) promedio (conjunto).
        """
        if not bloqueadas:
            return False
        if (a, b) in bloqueadas:
            return True
        return (not self.dirigido) and (b, a) in bloqueadas

    # ------------------------------------------------------------------
    # BFS: búsqueda por anchura
    # ------------------------------------------------------------------

    def bfs(self, origen, bloqueadas=None):
        """
        Recorre el grafo POR NIVELES desde 'origen' usando una cola (deque):
        primero los vecinos directos, luego los vecinos de los vecinos...

        Retorna la lista de vértices en el orden en que se visitaron, o una
        lista vacía si el origen no existe.

        Complejidad: O(V + E): cada vértice entra a la cola una sola vez y
        cada arista se revisa una vez (dos en no dirigido).
        """
        if origen not in self._adyacencia:
            return []
        visitados = {origen}
        orden = []
        cola = deque([origen])
        while cola:
            actual = cola.popleft()
            orden.append(actual)
            for vecino in self._adyacencia[actual]:
                if vecino not in visitados and not self._bloqueada(actual, vecino, bloqueadas):
                    visitados.add(vecino)
                    cola.append(vecino)
        return orden

    def ruta_mas_corta(self, origen, destino, bloqueadas=None):
        """
        Encuentra la ruta con MENOS SALTOS de 'origen' a 'destino' con BFS.

        BFS garantiza la ruta más corta en número de aristas porque explora
        por niveles: la primera vez que llega al destino lo hace por el
        camino con menos saltos. Se guarda el "padre" de cada vértice y al
        final se reconstruye la ruta de atrás hacia adelante.

        Retorna la lista de vértices de la ruta, o None si no hay ruta
        (vértices inexistentes o destino inalcanzable).

        Complejidad: O(V + E).
        """
        if origen not in self._adyacencia or destino not in self._adyacencia:
            return None
        if origen == destino:
            return [origen]
        padre = {origen: None}
        cola = deque([origen])
        while cola:
            actual = cola.popleft()
            for vecino in self._adyacencia[actual]:
                if vecino in padre or self._bloqueada(actual, vecino, bloqueadas):
                    continue
                padre[vecino] = actual
                if vecino == destino:
                    ruta = [destino]
                    while padre[ruta[-1]] is not None:
                        ruta.append(padre[ruta[-1]])
                    ruta.reverse()
                    return ruta
                cola.append(vecino)
        return None

    # ------------------------------------------------------------------
    # DFS: búsqueda en profundidad
    # ------------------------------------------------------------------

    def dfs(self, origen, bloqueadas=None):
        """
        Recorre el grafo EN PROFUNDIDAD desde 'origen' (recursivo): baja por
        un camino hasta que no puede seguir y solo entonces retrocede.

        Caso base: un vértice sin vecinos nuevos (ya visitados o bloqueados).
        Caso recursivo: visitar cada vecino no visitado.

        Retorna la lista de vértices en orden de visita ([] si no existe).

        Complejidad: O(V + E) en tiempo y O(V) en la pila de llamadas.
        """
        if origen not in self._adyacencia:
            return []
        visitados = set()
        orden = []
        self._dfs_recursivo(origen, visitados, orden, bloqueadas)
        return orden

    def _dfs_recursivo(self, actual, visitados, orden, bloqueadas):
        """Paso recursivo del DFS. Complejidad total: O(V + E)."""
        visitados.add(actual)
        orden.append(actual)
        for vecino in self._adyacencia[actual]:
            if vecino not in visitados and not self._bloqueada(actual, vecino, bloqueadas):
                self._dfs_recursivo(vecino, visitados, orden, bloqueadas)

    def alcanzables(self, origen, bloqueadas=None):
        """
        Conjunto de vértices a los que se puede llegar desde 'origen' sin
        cruzar aristas bloqueadas. Usa DFS.
        Complejidad: O(V + E).
        """
        return set(self.dfs(origen, bloqueadas))

    def componentes_conexas(self, bloqueadas=None):
        """
        Divide el grafo en ZONAS AISLADAS: grupos de vértices conectados
        entre sí pero no con el resto (respetando las aristas bloqueadas).
        Lanza un DFS desde cada vértice que aún no pertenece a una zona.

        Pensado para grafos no dirigidos. Retorna una lista de listas.
        Complejidad: O(V + E), porque cada vértice se visita una sola vez.
        """
        visitados = set()
        componentes = []
        for vertice in self._adyacencia:
            if vertice not in visitados:
                orden = []
                self._dfs_recursivo(vertice, visitados, orden, bloqueadas)
                componentes.append(orden)
        return componentes

    def __repr__(self):
        """Texto corto para depurar. Complejidad: O(V)."""
        tipo = "dirigido" if self.dirigido else "no dirigido"
        return f"Grafo({tipo}, {self.num_vertices()} vértices, {self.num_aristas()} aristas)"


# ----------------------------------------------------------------------
# Autoprueba: el MISMO Grafo con otro mapa (regiones de Hyrule)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    hyrule = Grafo()
    for a, b in [
        ("Pueblo de Hyrule", "Bosque Minish"),
        ("Pueblo de Hyrule", "Castillo de Hyrule"),
        ("Pueblo de Hyrule", "Lago Hylia"),
        ("Bosque Minish", "Templo de la Tierra"),
        ("Lago Hylia", "Cueva de las Llamas"),
        ("Castillo de Hyrule", "Palacio de los Vientos"),
        ("Cueva de las Llamas", "Palacio de los Vientos"),
    ]:
        hyrule.agregar_arista(a, b)
    hyrule.agregar_vertice("Isla de los Picori")   # zona aislada

    print(hyrule)
    print("BFS desde el pueblo:", hyrule.bfs("Pueblo de Hyrule"))
    print("DFS desde el pueblo:", hyrule.dfs("Pueblo de Hyrule"))
    print("Ruta al palacio:", hyrule.ruta_mas_corta("Pueblo de Hyrule", "Palacio de los Vientos"))
    bloqueo = {("Pueblo de Hyrule", "Castillo de Hyrule")}
    print("Ruta alternativa con el castillo cerrado:",
          hyrule.ruta_mas_corta("Pueblo de Hyrule", "Palacio de los Vientos", bloqueo))
    print("Zonas aisladas:", hyrule.componentes_conexas())

    print("\n--- Casos límite ---")
    print("BFS desde un lugar que no existe:", hyrule.bfs("Atlántida"))
    print("Ruta a un lugar que no existe:", hyrule.ruta_mas_corta("Pueblo de Hyrule", "Atlántida"))
    print("Ruta a una zona aislada:", hyrule.ruta_mas_corta("Pueblo de Hyrule", "Isla de los Picori"))
    print("Vecinos de un lugar que no existe:", hyrule.vecinos("Atlántida"))
    print("Arista repetida:", hyrule.agregar_arista("Pueblo de Hyrule", "Bosque Minish"))
    print("Lazo:", hyrule.agregar_arista("Lago Hylia", "Lago Hylia"))
