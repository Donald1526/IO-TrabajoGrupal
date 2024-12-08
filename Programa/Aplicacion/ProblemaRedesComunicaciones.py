import tkinter as tk
from tkinter import messagebox
import numpy as np
import random
import matplotlib.pyplot as plt

# Parámetros globales iniciales
n_hormigas = 10
n_iteraciones = 50
feromona_inicial = 0.1
alpha = 1
beta = 3
evaporacion = 0.5
q0 = 0.9
phi = 0.1

# Variables globales para matriz y radio de cobertura
matriz_entrada = None
radio_cobertura = None
grid_entries = []


# Función para generar la matriz editable
def crear_grid():
    try:
        n = int(entry_size.get())
        if n <= 0:
            raise ValueError("El tamaño debe ser positivo.")
        
        # Limpiar el frame_grid antes de crear la nueva grid
        for widget in frame_grid.winfo_children():
            widget.destroy()

        global grid_entries
        grid_entries = []
        for i in range(n):
            row_entries = []
            for j in range(n):
                entry = tk.Entry(frame_grid, width=5, justify="center")
                entry.insert(0, "0")  # Rellenar con ceros por defecto
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            grid_entries.append(row_entries)

        # Mostrar el campo para el radio de cobertura y el botón de ejecución
        label_radio.grid(row=0, column=0, sticky="w")
        entry_radio.grid(row=0, column=1, sticky="w")
        btn_ejecutar.grid(row=1, column=0, columnspan=2, pady=10)

    except ValueError as e:
        messagebox.showerror("Error", f"Entrada inválida: {e}")


# Función para guardar la matriz y ejecutar el algoritmo
def ejecutar_algoritmo():
    try:
        # Leer la matriz de entrada
        n = len(grid_entries)
        global matriz_entrada, radio_cobertura
        matriz_entrada = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                valor = grid_entries[i][j].get()
                matriz_entrada[i, j] = int(valor) if valor else 0

        # Leer el radio de cobertura
        radio_cobertura = int(entry_radio.get())
        if radio_cobertura <= 0:
            raise ValueError("El radio de cobertura debe ser positivo.")

        # Generar matriz de cobertura y ubicaciones candidatas
        matriz_cobertura, ubicaciones_candidatas = generar_matriz_cobertura(matriz_entrada, radio_cobertura)

        # Verificar si hay ubicaciones candidatas
        if len(ubicaciones_candidatas) == 0:
            raise ValueError("No hay ubicaciones candidatas en la matriz de entrada.")

        # Inicializar feromonas y heurística
        feromonas = np.full(len(ubicaciones_candidatas), feromona_inicial)
        heuristica = np.ones(len(ubicaciones_candidatas))  # Suponiendo heurística uniforme

        # Ejecutar el algoritmo de colonia de hormigas
        mejor_solucion, mejor_costo, mejor_matriz_cubierta = colonia_de_hormigas(
            matriz_cobertura, feromonas, heuristica, ubicaciones_candidatas
        )

        # Generar la matriz de salida
        matriz_salida = matriz_entrada.copy()
        for i, seleccion in enumerate(mejor_solucion):
            if seleccion == 1:
                fila, columna = ubicaciones_candidatas[i]
                matriz_salida[fila, columna] = 3  # Marcamos las ubicaciones elegidas

        # Mostrar resultados en un cuadro de diálogo
        matriz_salida_str = "\n".join([" ".join(map(str, row)) for row in matriz_salida.astype(int)])
        messagebox.showinfo(
            "Resultados",
            f"Mejor Costo: {mejor_costo}\n\nMatriz de Salida:\n{matriz_salida_str}"
        )

    except ValueError as e:
        messagebox.showerror("Error", f"Error en los datos: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")


# Generar matriz de cobertura
def generar_matriz_cobertura(matriz_entrada, radio_cobertura):
    n_filas, n_columnas = matriz_entrada.shape
    matriz_cobertura = np.zeros_like(matriz_entrada)

    ubicaciones_candidatas = np.argwhere(matriz_entrada == 2)

    for fila, columna in ubicaciones_candidatas:
        for i in range(max(0, fila - radio_cobertura), min(n_filas, fila + radio_cobertura + 1)):
            for j in range(max(0, columna - radio_cobertura), min(n_columnas, columna + radio_cobertura + 1)):
                matriz_cobertura[i, j] = 1

    return matriz_cobertura, ubicaciones_candidatas


# Clase Hormiga
class Hormiga:
    def __init__(self, matriz_cobertura, feromonas, heuristica, ubicaciones_candidatas):
        self.matriz_cobertura = matriz_cobertura
        self.feromonas = feromonas
        self.heuristica = heuristica
        self.ubicaciones_candidatas = ubicaciones_candidatas
        self.solucion = np.zeros(len(ubicaciones_candidatas), dtype=int)
        self.matriz_cubierta = np.zeros_like(matriz_cobertura)
        self.costo = 0

    def construir_solucion(self):
        celdas_por_cubrir = self.matriz_cobertura.copy()

        while np.any(celdas_por_cubrir > 0):
            # Calcular probabilidad de elegir cada ubicación
            probabilidades = (self.feromonas ** alpha) * (self.heuristica ** beta)
            probabilidades /= np.sum(probabilidades)

            if np.random.rand() < q0:
                # Selección determinística
                indice = np.argmax(probabilidades)
            else:
                # Selección probabilística
                indice = np.random.choice(len(self.ubicaciones_candidatas), p=probabilidades)

            # Añadir antena en la ubicación seleccionada
            self.solucion[indice] = 1
            fila, columna = self.ubicaciones_candidatas[indice]

            for i in range(max(0, fila - radio_cobertura), min(celdas_por_cubrir.shape[0], fila + radio_cobertura + 1)):
                for j in range(max(0, columna - radio_cobertura), min(celdas_por_cubrir.shape[1], columna + radio_cobertura + 1)):
                    celdas_por_cubrir[i, j] = 0
                    self.matriz_cubierta[i, j] = 1

            # Actualización local de feromonas
            self.feromonas[indice] = (1 - phi) * self.feromonas[indice] + phi * feromona_inicial

        self.costo = np.sum(self.solucion)


def actualizar_feromonas_global(mejor_solucion, mejor_costo, feromonas):
    feromonas *= (1 - evaporacion)
    for i, antena in enumerate(mejor_solucion):
        if antena == 1:
            feromonas[i] += 1 / mejor_costo


def colonia_de_hormigas(matriz_cobertura, feromonas, heuristica, ubicaciones_candidatas):
    mejor_costo_global = float('inf')
    mejor_solucion_global = None
    mejor_matriz_cubierta = None

    for _ in range(n_iteraciones):
        hormigas = [Hormiga(matriz_cobertura, feromonas, heuristica, ubicaciones_candidatas) for _ in range(n_hormigas)]

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
        actualizar_feromonas_global(mejor_solucion_global, mejor_costo_global, feromonas)

    return mejor_solucion_global, mejor_costo_global, mejor_matriz_cubierta


# Interfaz gráfica
root = tk.Tk()
root.title("ACO: Configuración de Entrada")
root.geometry("800x600")

# Configuración inicial
tk.Label(root, text="Tamaño de la matriz:").pack(pady=5)
entry_size = tk.Entry(root, width=5)
entry_size.pack(pady=5)

btn_generar = tk.Button(root, text="Generar Grid", command=crear_grid)
btn_generar.pack(pady=10)

frame_grid = tk.Frame(root)
frame_grid.pack(pady=10)

frame_control = tk.Frame(root)
frame_control.pack(pady=10)

label_radio = tk.Label(frame_control, text="Radio de cobertura:")
entry_radio = tk.Entry(frame_control, width=5)
btn_ejecutar = tk.Button(frame_control, text="Ejecutar", command=ejecutar_algoritmo)

root.mainloop()
