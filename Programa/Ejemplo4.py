import numpy as np
import random

# Parámetros del problema
nodos = ['A', 'B', 'C', 'D', 'E']  # Los 5 nodos
distancias = {  # Distancias entre los nodos (distancia entre A y B es 10, etc.)
    ('A', 'B'): 20, ('B', 'A'): 20,
    ('A', 'C'): 24, ('C', 'A'): 24,
    ('A', 'D'): 17, ('D', 'A'): 17,
    ('A', 'E'): 14, ('E', 'A'): 14,
    ('B', 'C'): 13, ('C', 'B'): 13,
    ('B', 'D'): 9,  ('D', 'B'): 9,
    ('B', 'E'): 15, ('E', 'B'): 15,
    ('C', 'D'): 12, ('D', 'C'): 12,
    ('C', 'E'): 22, ('E', 'C'): 22,
    ('D', 'E'): 18, ('E', 'D'): 18,
    ('A', 'A'): 0   # Distancia de 'A' a 'A' es 0
}

# Parámetros del algoritmo ACO
n_hormigas = 10
n_iteraciones = 1000
alpha = 1  # Intensidad de la feromona
beta = 2   # Influencia de la distancia
rho = 0.5  # Evaporación de feromonas
Q = 100    # Constante de feromonas

# Inicialización de la feromona
feromona = {arista: 1.0 for arista in distancias}  # Feromona inicial en todas las aristas

# Función para calcular la distancia total de una ruta
def calcular_distancia(ruta):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        distancia_total += distancias[(ruta[i], ruta[i+1])]
    distancia_total += distancias[(ruta[-1], ruta[0])]  # Vuelve al nodo inicial
    return distancia_total

# Función para seleccionar el siguiente nodo a visitar
def seleccionar_siguiente_nodo(nodo_actual, nodos_visitados, feromona, distancias):
    candidatos = [nodo for nodo in nodos if nodo not in nodos_visitados]
    probabilidades = []

    # Calcular las probabilidades para cada candidato
    for candidato in candidatos:
        arista = (nodo_actual, candidato) if (nodo_actual, candidato) in distancias else (candidato, nodo_actual)
        probabilidad = (feromona[arista] ** alpha) * ((1.0 / distancias[arista]) ** beta)
        probabilidades.append(probabilidad)

    # Normalización
    suma_probabilidades = sum(probabilidades)
    probabilidades = [p / suma_probabilidades for p in probabilidades]

    # Selección del siguiente nodo por ruleta
    return random.choices(candidatos, weights=probabilidades, k=1)[0]

# Función para actualizar las feromonas después de cada iteración
def actualizar_feromonas(feromona, rutas, distancias, rho, Q):
    # Evaporación de feromonas
    for arista in feromona:
        feromona[arista] *= (1 - rho)
    
    # Depósito de nuevas feromonas
    for ruta in rutas:
        distancia_total = calcular_distancia(ruta)
        for i in range(len(ruta) - 1):
            arista = (ruta[i], ruta[i+1]) if (ruta[i], ruta[i+1]) in distancias else (ruta[i+1], ruta[i])
            feromona[arista] += Q / distancia_total
        arista = (ruta[-1], ruta[0]) if (ruta[-1], ruta[0]) in distancias else (ruta[0], ruta[-1])
        feromona[arista] += Q / distancia_total

# Función para resolver el TSP con el algoritmo ACO
def resolver_tsp(nodos, distancias, n_hormigas, n_iteraciones, alpha, beta, rho, Q):
    mejor_ruta = None
    mejor_distancia = float('inf')

    for _ in range(n_iteraciones):
        rutas = []
        for _ in range(n_hormigas):
            ruta = []
            nodo_actual = 'A'  # Aseguramos que todas las hormigas comiencen en "A"
            ruta.append(nodo_actual)
            nodos_visitados = set([nodo_actual])
            while len(ruta) < len(nodos):
                siguiente_nodo = seleccionar_siguiente_nodo(nodo_actual, nodos_visitados, feromona, distancias)
                ruta.append(siguiente_nodo)
                nodos_visitados.add(siguiente_nodo)
                nodo_actual = siguiente_nodo
            ruta.append('A')  # Aseguramos que la ruta termine en "A"
            rutas.append(ruta)

        # Actualizar feromonas
        actualizar_feromonas(feromona, rutas, distancias, rho, Q)

        # Encontrar la mejor ruta de esta iteración
        for ruta in rutas:
            distancia = calcular_distancia(ruta)
            if distancia < mejor_distancia:
                mejor_ruta = ruta
                mejor_distancia = distancia

    return mejor_ruta, mejor_distancia

# Ejecutar el algoritmo
mejor_ruta, mejor_distancia = resolver_tsp(nodos, distancias, n_hormigas, n_iteraciones, alpha, beta, rho, Q)

# Resultados
print("Mejor ruta encontrada:", mejor_ruta)
print("Distancia total de la mejor ruta:", mejor_distancia)