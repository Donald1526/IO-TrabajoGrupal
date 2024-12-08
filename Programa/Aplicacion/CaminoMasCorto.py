import tkinter as tk
from tkinter import messagebox
import numpy as np
import random
import matplotlib.pyplot as plt

# Variables globales
L = 0  # Dimensión de la matriz
V = None  # Matriz de visibilidad
tau = None  # Vector de feromonas

# Parámetros del algoritmo de colonia de hormigas
tau_inicial = 0.1  # Feromona inicial
ro = 0.01  # Factor de evaporación
nh = 50  # Número de hormigas de la colonia
N = 50  # Número de iteraciones
pi = 0  # Nodo inicial (predeterminado)
pf = 5  # Nodo final (predeterminado)
mejora = []  # Lista para guardar el mejor costo en cada iteración

def insertar_datos():
    global grid_entries
    try:
        A = np.array([
            [0, 4, np.inf, np.inf, np.inf, 100],  # Desde el nodo 0
            [np.inf, 0, 7, np.inf, np.inf, np.inf],  # Desde el nodo 1
            [np.inf, 8, 0, 18, 9, np.inf],  # Desde el nodo 2
            [1, np.inf, np.inf, 0, 12, 8],  # Desde el nodo 3
            [np.inf, np.inf, 3, 11, 0, np.inf],  # Desde el nodo 4
            [np.inf, np.inf, 6, np.inf, np.inf, 0]  # Desde el nodo 5
        ])

        # Validar tamaño del grid
        if len(A) != len(grid_entries) or len(A[0]) != len(grid_entries[0]):
            messagebox.showerror("Error", "El tamaño del grid no coincide con la matriz A.")
            return

        # Insertar los valores de la matriz A en el grid
        for i in range(len(A)):
            for j in range(len(A[i])):
                value = "" if A[i, j] == np.inf else A[i, j]
                grid_entries[i][j].delete(0, tk.END)
                grid_entries[i][j].insert(0, value)
    except Exception as e:
        messagebox.showerror("Error", f"Error al insertar datos: {e}")

# Clase Hormiga
class Hormiga:
    def __init__(self, pi, pf):
        self.pi = pi
        self.pf = pf
        self.Camino = [pi]

    def sig_nodo(self, n):
        global V, tau
        P = V * tau
        P[n, self.Camino[-1]] = 0  # Impide volver al nodo anterior
        P = P[n, :] / np.sum(P[n, :])  # Vector de probabilidades
        indice = np.array(range(L))
        c = P > 0
        P = P[c]
        indice = indice[c]

        for i in range(1, len(P)):
            P[i] += P[i - 1]

        u = random.random()
        for i, prob in enumerate(P):
            if u <= prob:
                y = indice[i]
                break

        self.Camino.append(y)

    def trayectoria(self):
        global L
        run = 0
        while run < L - 1:
            self.sig_nodo(self.Camino[-1])
            if self.Camino[-1] == self.pf:
                break
            run += 1

    def apor_fero(self, i, j):
        C = self.Camino
        return 1 if (i, j) in zip(C[:-1], C[1:]) else 0

    def costo(self):
        global matriz
        C = self.Camino
        if C[-1] != self.pf:
            return np.inf
        return sum(matriz[C[t], C[t + 1]] for t in range(len(C) - 1))


def crear_grid():
    global grid_entries
    try:
        # Leer el tamaño del grid
        n = int(entry_size.get())
        if n <= 0:
            raise ValueError("El tamaño debe ser un número positivo.")

        # Desactivar el campo de texto y el botón
        entry_size.config(state="disabled")
        btn_crear.config(state="disabled")
        btn_insertar = tk.Button(frame_control, text="Insertar Datos A", command=insertar_datos)
        btn_insertar.grid(row=3, column=0, columnspan=2, pady=5)

        # Limpiar el frame_grid antes de crear el nuevo grid
        for widget in frame_grid.winfo_children():
            widget.destroy()

        # Crear el grid dinámico dentro del frame
        grid_entries = []
        for i in range(n):
            row_entries = []
            for j in range(n):
                entry = tk.Entry(frame_grid, width=5, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            grid_entries.append(row_entries)

        # Crear campos adicionales y botón "Ejecutar"
        tk.Label(frame_control, text="Nodo Inicial:").grid(row=0, column=0, pady=5)
        global entry_inicio
        entry_inicio = tk.Entry(frame_control, width=10)
        entry_inicio.grid(row=0, column=1, pady=5)

        tk.Label(frame_control, text="Nodo Final:").grid(row=1, column=0, pady=5)
        global entry_final
        entry_final = tk.Entry(frame_control, width=10)
        entry_final.grid(row=1, column=1, pady=5)

        boton_ejecutar = tk.Button(frame_control, text="Ejecutar", command=guardar_matriz)
        boton_ejecutar.grid(row=2, column=0, columnspan=2, pady=10)

    except ValueError as e:
        messagebox.showerror("Error", f"Entrada inválida: {e}")


def guardar_matriz():
    global L, V, tau, matriz  # Variables globales
    try:
        # Leer los datos del grid
        n = len(grid_entries)  # Tamaño del grid
        matriz = np.zeros((n, n))  # Crear una matriz vacía

        for i in range(n):
            for j in range(n):
                valor = grid_entries[i][j].get()
                matriz[i, j] = np.inf if valor == "" else float(valor)  # Asignar infinito si está vacío

        # Leer nodos inicial y final
        global pi, pf
        pi = int(entry_inicio.get()) 
        pf = int(entry_final.get()) 

        # Calcular L y V
        L = len(matriz)
        V = np.zeros((L, L))
        for i in range(L):
            for j in range(L):
                if matriz[i, j] != 0 and matriz[i, j] != np.inf:
                    V[i, j] = 1 / matriz[i, j]

        # Inicializar tau
        tau = tau_inicial * np.ones((L, L))

        # Ejecutar el algoritmo
        ejecutar_algoritmo()

    except ValueError as e:
        messagebox.showerror("Error", f"Error al guardar datos: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")


def ejecutar_algoritmo():
    global tau, mejora
    d = 0
    while d < N:
        # Construir la colonia
        Colonia = [Hormiga(pi, pf) for _ in range(nh)]

        # Calcular la trayectoria de cada hormiga
        for hormiga in Colonia:
            hormiga.trayectoria()

        # Calcular el costo de cada hormiga
        for hormiga in Colonia:
            hormiga.costo()

        # Actualización de la feromona
        for i in range(L):
            for j in range(L):
                for hormiga in Colonia:
                    tau[i, j] = (1 - ro) * tau[i, j] + hormiga.apor_fero(i, j) * 1 / (hormiga.costo() ** 4)

        # Cálculo del menor costo en esta iteración
        M_C = [hormiga.costo() for hormiga in Colonia]
        mejora.append(np.min(M_C))
        d += 1

    # Resultados finales
    Costos = [hormiga.costo() for hormiga in Colonia]
    indice = np.argsort(Costos)
    Mejor_Costo = Costos[indice[0]]
    Mejor_Camino = np.array(Colonia[indice[0]].Camino) + 1

    print("El mejor individuo es:", Mejor_Camino)
    print("Su costo es:", Mejor_Costo)
    # Mostrar los resultados en un messagebox
    resultado = f"El mejor individuo es: {Mejor_Camino}\nSu costo es: {Mejor_Costo}"
    messagebox.showinfo("Resultados", resultado)


    mejora.append(Mejor_Costo)
    plt.plot(mejora)
    plt.title("Evolución del algoritmo", fontweight="bold", fontsize=14)
    plt.xlabel("Generación", fontweight="bold", fontsize=12)
    plt.ylabel("Mejor costo", fontweight="bold", fontsize=12)
    plt.xlim(0, N)
    plt.show()


# Crear ventana principal
root = tk.Tk()
root.title("Generador de Grid Dinámico")

# Configurar tamaño inicial de la ventana
root.geometry("800x600")

# Campo de texto para ingresar el tamaño del grid
label_size = tk.Label(root, text="Tamaño del grid:")
label_size.pack(pady=5)

entry_size = tk.Entry(root, width=10, justify="center")
entry_size.pack(pady=5)

# Botón para crear el grid
btn_crear = tk.Button(root, text="Crear Grid", command=crear_grid)
btn_crear.pack(pady=10)

# Frame donde se colocará el grid
frame_grid = tk.Frame(root)
frame_grid.pack(pady=10)

# Frame donde se colocarán los campos de control
frame_control = tk.Frame(root)
frame_control.pack(pady=10)

# Ejecutar el bucle principal
root.mainloop()
