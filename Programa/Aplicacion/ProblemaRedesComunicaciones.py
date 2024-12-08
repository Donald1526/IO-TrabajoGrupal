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
matriz_salida=None
grid_entries = []
def mostrar_mapa_bits(matriz_resultado):
    try:
        # Validar que la matriz esté definida
        if matriz_resultado is None:
            raise ValueError("La matriz de salida no está disponible. Ejecute el algoritmo primero.")

        # Tamaño del grid y de los píxeles
        n_filas, n_columnas = matriz_resultado.shape
        pixel_size = 20  # Tamaño de cada píxel

        # Crear ventana para el mapa de bits
        ventana_mapa = tk.Toplevel(root)
        ventana_mapa.title("Mapa de Bits")

        # Crear Canvas para dibujar
        canvas = tk.Canvas(ventana_mapa, width=n_columnas * pixel_size, height=n_filas * pixel_size)
        canvas.pack()

        # Dibujar cada píxel
        for i in range(n_filas):
            for j in range(n_columnas):
                color = "white"  # Blanco para 0
                if matriz_resultado[i, j] == 2:
                    color = "orange"  # Naranja para 2
                elif matriz_resultado[i, j] == 3:
                    color = "yellow"  # Amarillo para 3

                # Dibujar un rectángulo con el color correspondiente
                x1, y1 = j * pixel_size, i * pixel_size
                x2, y2 = x1 + pixel_size, y1 + pixel_size
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"Error al mostrar el mapa de bits: {e}")


def insertar_datos():
    global grid_entries, matriz_entrada, radio_cobertura
    try:
        radio_cobertura = 2  # Definir el radio de cobertura
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

        # Regenerar el grid si no coincide con el tamaño de la matriz
        n = matriz_entrada.shape[0]
        if len(grid_entries) != n or len(grid_entries[0]) != n:
            entry_size.delete(0, tk.END)
            entry_size.insert(0, str(n))
            crear_grid()

        # Insertar los valores en el grid
        for i in range(len(grid_entries)):
            for j in range(len(grid_entries[i])):
                grid_entries[i][j].delete(0, tk.END)
                grid_entries[i][j].insert(0, str(int(matriz_entrada[i, j])))

        # Prellenar el campo de radio de cobertura
        entry_radio.delete(0, tk.END)
        entry_radio.insert(0, str(radio_cobertura))

    except Exception as e:
        messagebox.showerror("Error", f"Error al insertar datos: {e}")



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


def ejecutar_algoritmo():
    global matriz_entrada, radio_cobertura, matriz_salida
    try:
        # Leer la matriz de entrada
        n = len(grid_entries)
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
        matriz_salida = matriz_entrada.copy()  # Asignar globalmente
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
btn_insertar = tk.Button(root, text="Insertar Datos", command=insertar_datos)
btn_insertar.pack(pady=10)
btn_mostrar_mapa = tk.Button(root, text="Mostrar Mapa de Bits", command=lambda: mostrar_mapa_bits(matriz_salida))
btn_mostrar_mapa.pack(pady=10)

frame_grid = tk.Frame(root)
frame_grid.pack(pady=10)

frame_control = tk.Frame(root)
frame_control.pack(pady=10)

label_radio = tk.Label(frame_control, text="Radio de cobertura:")
entry_radio = tk.Entry(frame_control, width=5)
btn_ejecutar = tk.Button(frame_control, text="Ejecutar", command=ejecutar_algoritmo)

root.mainloop()
