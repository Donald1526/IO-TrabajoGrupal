import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
import random
# Parámetros del algoritmo de colonia de hormigas
tau_inicial = 0.1  # Feromona inicial
alpha = 1  # Peso de la feromona
beta = 2  # Peso de la heurística
evaporacion = 0.5  # Tasa de evaporación
n_hormigas = 10  # Número de hormigas
n_iteraciones = 100  # Número de iteraciones

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
def generar_matriz():
    try:
        n = int(entry_size.get())
        if n <= 0:
            raise ValueError("El tamaño debe ser positivo.")
        
        # Limpiar el frame_grid antes de crear el nuevo grid
        for widget in frame_grid.winfo_children():
            widget.destroy()
        
        global grid_entries
        grid_entries = []
        for i in range(n):
            row_entries = []
            for j in range(n):
                entry = tk.Entry(frame_grid, width=5, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            grid_entries.append(row_entries)
        
        # Mostrar campos para ofertas y demandas
        label_ofertas.grid(row=0, column=0, pady=10, sticky="w")
        entry_ofertas.grid(row=0, column=1, pady=10, sticky="w")
        label_demandas.grid(row=1, column=0, pady=10, sticky="w")
        entry_demandas.grid(row=1, column=1, pady=10, sticky="w")
        btn_ejecutar.grid(row=2, column=0, columnspan=2, pady=10)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def ejecutar_aco():
    try:
        # Leer la matriz de costos
        n = len(grid_entries)
        matriz_costos = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                valor = grid_entries[i][j].get()
                matriz_costos[i, j] = float(valor) if valor else np.inf
        
        # Leer ofertas y demandas
        ofertas = list(map(int, entry_ofertas.get().split(",")))
        demandas = list(map(int, entry_demandas.get().split(",")))
        
        if len(ofertas) != n or len(demandas) != n:
            raise ValueError("La cantidad de ofertas y demandas debe coincidir con el tamaño de la matriz.")
        
        # Simulación del ACO (puedes reemplazar con tu implementación real)
        mejor_asignacion = np.zeros((n, n))
        mejor_costo = random.randint(50, 150)  # Simulación del costo mínimo
        
        # Mostrar resultados
        messagebox.showinfo("Resultados", f"Matriz:\n{matriz_costos}\n\nMejor Costo: {mejor_costo}")
        plt.plot([random.randint(50, mejor_costo) for _ in range(10)])
        plt.title("Convergencia")
        plt.xlabel("Iteraciones")
        plt.ylabel("Costo")
        plt.show()
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Crear ventana principal
root = tk.Tk()
root.title("ACO: Problema de Transporte")
root.geometry("800x600")

# Entrada de tamaño de matriz
tk.Label(root, text="Tamaño de la matriz:").pack(pady=10)
entry_size = tk.Entry(root, width=5)
entry_size.pack(pady=10)

# Botón para generar matriz
btn_generar = tk.Button(root, text="Generar Matriz", command=generar_matriz)
btn_generar.pack(pady=10)

# Frame para el grid
frame_grid = tk.Frame(root)
frame_grid.pack(pady=10)

# Frame para las ofertas y demandas
frame_control = tk.Frame(root)
frame_control.pack(pady=10)

# Campos para ofertas y demandas
label_ofertas = tk.Label(frame_control, text="Ofertas:")
entry_ofertas = tk.Entry(frame_control, width=20)
label_demandas = tk.Label(frame_control, text="Demandas:")
entry_demandas = tk.Entry(frame_control, width=20)

# Botón para ejecutar el algoritmo
btn_ejecutar = tk.Button(frame_control, text="Ejecutar ACO", command=ejecutar_aco)

# Ejecutar ventana principal
root.mainloop()
