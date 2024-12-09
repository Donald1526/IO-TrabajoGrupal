import numpy as np

# Parámetros del algoritmo
n_hormigas = 10
n_iteraciones = 50
feromona_inicial = 0.1
alpha = 1
beta = 3
evaporacion = 0.5
q0 = 0.9
phi = 0.1

# Radio de cobertura como variable externa
radio_cobertura = 2

# Matriz de entrada (2: ubicaciones candidatas, 0: no candidato)
matriz_entrada = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 0, 0, 2],
    [0, 0, 2, 0, 0, 0, 2, 2, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
])

# Generar la matriz de cobertura
def generar_matriz_cobertura(matriz_entrada, radio_cobertura):
    n_filas, n_columnas = matriz_entrada.shape
    matriz_cobertura = np.zeros_like(matriz_entrada)

    ubicaciones_candidatas = np.argwhere(matriz_entrada == 2)

    for fila, columna in ubicaciones_candidatas:
        for i in range(max(0, fila - radio_cobertura), min(n_filas, fila + radio_cobertura + 1)):
            for j in range(max(0, columna - radio_cobertura), min(n_columnas, columna + radio_cobertura + 1)):
                matriz_cobertura[i, j] = 1

    return matriz_cobertura, ubicaciones_candidatas

# Inicialización de feromonas y heurística
matriz_cobertura, ubicaciones_candidatas = generar_matriz_cobertura(matriz_entrada, radio_cobertura)
feromonas = np.full(len(ubicaciones_candidatas), feromona_inicial)
heuristica = np.sum(matriz_cobertura, axis=(0, 1))

class Hormiga:
    def __init__(self):
        self.solucion = np.zeros(len(ubicaciones_candidatas), dtype=int)
        self.matriz_cubierta = np.zeros_like(matriz_entrada)
        self.costo = 0

    def construir_solucion(self):
        global feromonas, heuristica
        celdas_por_cubrir = matriz_cobertura.copy()

        while np.any(celdas_por_cubrir > 0):
            # Calcular probabilidad de elegir cada ubicación
            probabilidades = (feromonas ** alpha) * (heuristica ** beta)
            probabilidades /= np.sum(probabilidades)

            if np.random.rand() < q0:
                # Selección determinística
                indice = np.argmax(probabilidades)
            else:
                # Selección probabilística
                indice = np.random.choice(len(ubicaciones_candidatas), p=probabilidades)

            # Añadir antena en la ubicación seleccionada
            self.solucion[indice] = 1
            fila, columna = ubicaciones_candidatas[indice]

            for i in range(max(0, fila - radio_cobertura), min(matriz_entrada.shape[0], fila + radio_cobertura + 1)):
                for j in range(max(0, columna - radio_cobertura), min(matriz_entrada.shape[1], columna + radio_cobertura + 1)):
                    celdas_por_cubrir[i, j] = 0
                    self.matriz_cubierta[i, j] = 1

            # Actualización local de feromonas
            feromonas[indice] = (1 - phi) * feromonas[indice] + phi * feromona_inicial

        self.costo = np.sum(self.solucion)

def actualizar_feromonas_global(mejor_solucion, mejor_costo):
    global feromonas
    feromonas *= (1 - evaporacion)
    for i, antena in enumerate(mejor_solucion):
        if antena == 1:
            feromonas[i] += 1 / mejor_costo

def colonia_de_hormigas():
    mejor_costo_global = float('inf')
    mejor_solucion_global = None
    mejor_matriz_cubierta = None

    for iteracion in range(n_iteraciones):
        hormigas = [Hormiga() for _ in range(n_hormigas)]

        # Cada hormiga construye una solución
        for hormiga in hormigas:
            hormiga.construir_solucion()

        # Encontrar la mejor solución de esta iteración
        mejor_hormiga = min(hormigas, key=lambda h: h.costo)
        if mejor_hormiga.costo < mejor_costo_global:
            mejor_costo_global = mejor_hormiga.costo
            mejor_solucion_global = mejor_hormiga.solucion
            mejor_matriz_cubierta = mejor_hormiga.matriz_cubierta

        # Actualizar feromonas globalmente
        actualizar_feromonas_global(mejor_solucion_global, mejor_costo_global)

    return mejor_solucion_global, mejor_costo_global, mejor_matriz_cubierta

# Ejecutar el algoritmo
mejor_solucion, mejor_costo, mejor_matriz_cubierta = colonia_de_hormigas()

# Generar la matriz de salida
matriz_salida = matriz_entrada.copy()
for i, seleccion in enumerate(mejor_solucion):
    if seleccion == 1:
        fila, columna = ubicaciones_candidatas[i]
        matriz_salida[fila, columna] = 3  # Marcamos las ubicaciones elegidas

# Imprimir resultados
print("Matriz de salida:")
print(matriz_salida)
