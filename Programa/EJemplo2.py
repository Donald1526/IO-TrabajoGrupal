import numpy as np
import random
import matplotlib.pyplot as plt

# Parámetros del problema
origenes = ["A", "B", "C"]  # Orígenes
destinos = ["X", "Y", "Z"]  # Destinos
costos = np.array([  # Matriz de costos de transporte
    [4, 3, 2],
    [5, 8, 6],
    [7, 4, 3]
])
demandas = [30, 40, 50]  # Demanda en los destinos
ofertas = [40, 50, 30]   # Oferta en los orígenes

# Parámetros del algoritmo de colonia de hormigas
tau_inicial = 0.1  # Feromona inicial
alpha = 1  # Peso de la feromona
beta = 2  # Peso de la heurística
evaporacion = 0.5  # Tasa de evaporación
n_hormigas = 10  # Número de hormigas
n_iteraciones = 100  # Número de iteraciones

# Inicialización de las feromonas
tau = tau_inicial * np.ones_like(costos)

# Función heurística: 1/costo (mayor probabilidad para menores costos)
heuristica = 1 / costos

# Clase Hormiga
class Hormiga:
    def __init__(self):
        self.asignacion = np.zeros_like(costos)
        self.ofertas_restantes = ofertas.copy()
        self.demandas_restantes = demandas.copy()
        self.costo_total = 0

    def construir_solucion(self):
        global heuristica, tau
        while sum(self.demandas_restantes) > 0:
            # Probabilidades para elegir origen-destino
            probabilidades = (tau ** alpha) * (heuristica ** beta)
            probabilidades /= np.sum(probabilidades)

            # Seleccionar un origen-destino basado en probabilidades
            indices_origen, indices_destino = np.unravel_index(
                np.random.choice(probabilidades.size, p=probabilidades.ravel()), probabilidades.shape
            )
            origen, destino = indices_origen, indices_destino

            # Cantidad a transportar
            cantidad = min(self.ofertas_restantes[origen], self.demandas_restantes[destino])

            # Actualizar la asignación, ofertas y demandas
            self.asignacion[origen, destino] += cantidad
            self.ofertas_restantes[origen] -= cantidad
            self.demandas_restantes[destino] -= cantidad
            self.costo_total += cantidad * costos[origen, destino]

# Función para actualizar feromonas
def actualizar_feromonas(hormigas):
    global tau
    # Evaporación de feromonas
    tau *= (1 - evaporacion)
    for hormiga in hormigas:
        for i in range(costos.shape[0]):
            for j in range(costos.shape[1]):
                if hormiga.asignacion[i, j] > 0:
                    tau[i, j] += 1 / hormiga.costo_total  # Incremento proporcional al costo inverso

# Algoritmo principal
def colonia_de_hormigas():
    mejor_costo_global = float("inf")
    mejor_asignacion_global = None
    costos_mejor_iteracion = []

    for iteracion in range(n_iteraciones):
        hormigas = [Hormiga() for _ in range(n_hormigas)]

        # Cada hormiga construye una solución
        for hormiga in hormigas:
            hormiga.construir_solucion()

        # Buscar la mejor solución de esta iteración
        mejor_hormiga = min(hormigas, key=lambda h: h.costo_total)
        if mejor_hormiga.costo_total < mejor_costo_global:
            mejor_costo_global = mejor_hormiga.costo_total
            mejor_asignacion_global = mejor_hormiga.asignacion

        # Actualizar feromonas
        actualizar_feromonas(hormigas)

        # Guardar el mejor costo de esta iteración
        costos_mejor_iteracion.append(mejor_costo_global)

    return mejor_asignacion_global, mejor_costo_global, costos_mejor_iteracion

# Ejecutar el algoritmo
mejor_asignacion, mejor_costo, costos_iteraciones = colonia_de_hormigas()

# Mostrar resultados
print("Mejor Asignación:")
print(mejor_asignacion)
print(f"Costo Total: {mejor_costo}")

# Graficar la evolución del costo
plt.plot(costos_iteraciones)
plt.title("Evolución del Costo en ACO")
plt.xlabel("Iteraciones")
plt.ylabel("Costo")
plt.show()
