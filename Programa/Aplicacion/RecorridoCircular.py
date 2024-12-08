import tkinter as tk
from tkinter import messagebox, simpledialog
import numpy as np
import random

# Parámetros iniciales del ACO
n_hormigas = 10
n_iteraciones = 100
alpha = 1
beta = 2
rho = 0.5
Q = 100
feromona = {}

# Funciones del algoritmo
def calcular_distancia(ruta, distancias):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        distancia_total += distancias[(ruta[i], ruta[i + 1])]
    distancia_total += distancias[(ruta[-1], ruta[0])]  # Vuelve al nodo inicial
    return distancia_total


def seleccionar_siguiente_nodo(nodo_actual, nodos_visitados, feromona, distancias, nodos):
    candidatos = [nodo for nodo in nodos if nodo not in nodos_visitados]
    probabilidades = []

    for candidato in candidatos:
        arista = (nodo_actual, candidato) if (nodo_actual, candidato) in distancias else (candidato, nodo_actual)
        probabilidad = (feromona[arista] ** alpha) * ((1.0 / distancias[arista]) ** beta)
        probabilidades.append(probabilidad)

    suma_probabilidades = sum(probabilidades)
    probabilidades = [p / suma_probabilidades for p in probabilidades]

    return random.choices(candidatos, weights=probabilidades, k=1)[0]


def actualizar_feromonas(feromona, rutas, distancias, rho, Q):
    for arista in feromona:
        feromona[arista] *= (1 - rho)

    for ruta in rutas:
        distancia_total = calcular_distancia(ruta, distancias)
        for i in range(len(ruta) - 1):
            arista = (ruta[i], ruta[i + 1]) if (ruta[i], ruta[i + 1]) in distancias else (ruta[i + 1], ruta[i])
            feromona[arista] += Q / distancia_total
        arista = (ruta[-1], ruta[0]) if (ruta[-1], ruta[0]) in distancias else (ruta[0], ruta[-1])
        feromona[arista] += Q / distancia_total


def resolver_tsp(nodos, distancias, n_hormigas, n_iteraciones, alpha, beta, rho, Q):
    mejor_ruta = None
    mejor_distancia = float("inf")

    for _ in range(n_iteraciones):
        rutas = []
        for _ in range(n_hormigas):
            ruta = []
            nodo_actual = nodos[0]
            ruta.append(nodo_actual)
            nodos_visitados = set([nodo_actual])
            while len(ruta) < len(nodos):
                siguiente_nodo = seleccionar_siguiente_nodo(nodo_actual, nodos_visitados, feromona, distancias, nodos)
                ruta.append(siguiente_nodo)
                nodos_visitados.add(siguiente_nodo)
                nodo_actual = siguiente_nodo
            ruta.append(nodos[0])
            rutas.append(ruta)

        actualizar_feromonas(feromona, rutas, distancias, rho, Q)

        for ruta in rutas:
            distancia = calcular_distancia(ruta, distancias)
            if distancia < mejor_distancia:
                mejor_ruta = ruta
                mejor_distancia = distancia

    return mejor_ruta, mejor_distancia

# Interfaz gráfica
def agregar_nodo():
    nodo = simpledialog.askstring("Agregar Nodo", "Ingrese el nombre del nodo:")
    if nodo and nodo not in nodos:
        nodos.append(nodo)
        actualizar_lista_nodos()


def agregar_distancia():
    if len(nodos) < 2:
        messagebox.showerror("Error", "Agregue al menos dos nodos primero.")
        return
    nodo1 = simpledialog.askstring("Nodo 1", "Ingrese el primer nodo:")
    nodo2 = simpledialog.askstring("Nodo 2", "Ingrese el segundo nodo:")
    if nodo1 not in nodos or nodo2 not in nodos:
        messagebox.showerror("Error", "Ambos nodos deben existir.")
        return
    distancia = simpledialog.askinteger("Distancia", f"Ingrese la distancia entre {nodo1} y {nodo2}:")
    if distancia is not None and distancia > 0:
        distancias[(nodo1, nodo2)] = distancia
        distancias[(nodo2, nodo1)] = distancia
        actualizar_lista_distancias()


def cargar_datos_predeterminados():
    global nodos, distancias, feromona
    nodos.extend(['A', 'B', 'C', 'D', 'E'])
    distancias.update({
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
        ('A', 'A'): 0
    })
    feromona = {arista: 1.0 for arista in distancias}
    actualizar_lista_nodos()
    actualizar_lista_distancias()


def ejecutar_aco():
    if len(nodos) < 2 or not distancias:
        messagebox.showerror("Error", "Agregue nodos y distancias primero.")
        return

    global feromona
    feromona = {arista: 1.0 for arista in distancias}

    mejor_ruta, mejor_distancia = resolver_tsp(nodos, distancias, n_hormigas, n_iteraciones, alpha, beta, rho, Q)

    messagebox.showinfo("Resultado", f"Mejor Ruta: {' -> '.join(mejor_ruta)}\nDistancia Total: {mejor_distancia}")


def actualizar_lista_nodos():
    lista_nodos.delete(0, tk.END)
    for nodo in nodos:
        lista_nodos.insert(tk.END, nodo)


def actualizar_lista_distancias():
    lista_distancias.delete(0, tk.END)
    for (nodo1, nodo2), distancia in distancias.items():
        lista_distancias.insert(tk.END, f"{nodo1} - {nodo2}: {distancia}")


# Variables globales para la interfaz
nodos = []
distancias = {}

# Crear la ventana principal
root = tk.Tk()
root.title("ACO para TSP")

frame_nodos = tk.Frame(root)
frame_nodos.pack(pady=10)

btn_agregar_nodo = tk.Button(frame_nodos, text="Agregar Nodo", command=agregar_nodo)
btn_agregar_nodo.pack(side=tk.LEFT, padx=5)

btn_agregar_distancia = tk.Button(frame_nodos, text="Agregar Distancia", command=agregar_distancia)
btn_agregar_distancia.pack(side=tk.LEFT, padx=5)

btn_cargar_predeterminados = tk.Button(frame_nodos, text="Cargar Datos Predeterminados", command=cargar_datos_predeterminados)
btn_cargar_predeterminados.pack(side=tk.LEFT, padx=5)

frame_listas = tk.Frame(root)
frame_listas.pack(pady=10)

lista_nodos = tk.Listbox(frame_listas, height=10, width=20)
lista_nodos.pack(side=tk.LEFT, padx=5)

lista_distancias = tk.Listbox(frame_listas, height=10, width=40)
lista_distancias.pack(side=tk.LEFT, padx=5)

btn_ejecutar = tk.Button(root, text="Ejecutar ACO", command=ejecutar_aco)
btn_ejecutar.pack(pady=10)

root.mainloop()
