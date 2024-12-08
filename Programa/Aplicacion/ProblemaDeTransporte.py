import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt

# Parámetros del algoritmo de colonia de hormigas
tau_inicial = 0.1  # Feromona inicial
alpha = 1  # Peso de la feromona
beta = 2  # Peso de la heurística
evaporacion = 0.5  # Tasa de evaporación
n_hormigas = 10  # Número de hormigas
n_iteraciones = 100  # Número de iteraciones

costos = None
demandas = None
ofertas = None
tau = None
heuristica = None


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


def colonia_de_hormigas():
    global tau, heuristica
    mejor_costo_global = float("inf")
    mejor_asignacion_global = None
    costos_mejor_iteracion = []

    tau = np.full(costos.shape, tau_inicial)
    heuristica = 1 / (costos + 1e-9)  # Evitar división por cero

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


def actualizar_feromonas(hormigas):
    global tau
    # Evaporación de feromonas
    tau *= (1 - evaporacion)
    for hormiga in hormigas:
        for i in range(costos.shape[0]):
            for j in range(costos.shape[1]):
                if hormiga.asignacion[i, j] > 0:
                    tau[i, j] += 1 / hormiga.costo_total  # Incremento proporcional al costo inverso


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
        global costos, ofertas, demandas
        # Leer la matriz de costos
        n = len(grid_entries)
        costos = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                valor = grid_entries[i][j].get()
                costos[i, j] = float(valor) if valor else float("inf")

        # Leer ofertas y demandas
        ofertas = list(map(int, entry_ofertas.get().split(",")))
        demandas = list(map(int, entry_demandas.get().split(",")))

        if len(ofertas) != n or len(demandas) != n:
            raise ValueError("La cantidad de ofertas y demandas debe coincidir con el tamaño de la matriz.")

        mejor_asignacion, mejor_costo, costos_iteraciones = colonia_de_hormigas()

        # Mostrar resultados
        messagebox.showinfo("Resultados", f"Mejor Costo: {mejor_costo}\nAsignación:\n{mejor_asignacion}")
        plt.plot(costos_iteraciones)
        plt.title("Convergencia del costo")
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
