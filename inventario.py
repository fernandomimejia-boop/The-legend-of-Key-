"""
Módulo de inventario - Checkpoint 1
Maneja los objetos del héroe usando estructuras de datos tipo Lista.
"""

def agregar_objeto(inventario, objeto):
    """
    Agrega un objeto al final de la lista del inventario.
    Complejidad: O(1)
    """
    inventario.append(objeto)
    print(f"[*] Has obtenido: {objeto}")

def usar_objeto(inventario, objeto):
    """
    Busca y usa un objeto si existe en la lista.
    Complejidad: O(n) por la búsqueda lineal con 'in'.
    """
    if objeto in inventario:
        print(f"[*] Has usado: {objeto}. Ezlo exclama: ¡El poder de los Picori fluye por la Espada Minish!")
    else:
        print(f"[!] No puedes usar '{objeto}'. Ezlo te recuerda que no está en tu bolsa.")

def soltar_objeto(inventario, objeto):
    """
    Elimina la primera aparición del objeto en el inventario.
    Complejidad: O(n) por la búsqueda y el reacomodo de elementos.
    """
    if objeto in inventario:
        inventario.remove(objeto)
        print(f"[*] Has soltado: {objeto}")
    else:
        print(f"[!] No puedes soltar '{objeto}' porque no está en tu inventario.")