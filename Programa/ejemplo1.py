import numpy as np
import random
import matplotlib.pyplot as plt

# Representa un grafo dirigido con pesos.
A = np.array([
    [0, 4, np.inf, np.inf, np.inf, 100],  # Desde el nodo 0
    [np.inf, 0, 7, np.inf, np.inf, np.inf],  # Desde el nodo 1
    [np.inf, 8, 0, 18, 9, np.inf],  # Desde el nodo 2
    [1, np.inf, np.inf, 0, 12, 8],  # Desde el nodo 3
    [np.inf, np.inf, 3, 11, 0, np.inf],  # Desde el nodo 4
    [np.inf, np.inf, 6, np.inf, np.inf, 0]  # Desde el nodo 5
])


L = len(A)  # Dimensión de A.

# Matriz de visibilidad
V = np.zeros((L, L))
for i in range(L):
    for j in range(L):
        if A[i, j] != 0:
            V[i, j] = 1 / A[i, j]

tau_inicial = 0.1  # Feromona inicial.
tau = tau_inicial * np.ones((L, L))  # Vector de feromonas.
ro = 0.01  # Factor de evaporación.
nh = 50  # Número de hormigas de la colonia.
N = 50  # Número de iteraciones.
pi = 0  # Punto inicial.
pf = 5  # Punto final.

mejora = []  # Lista que guarda el mejor costo en cada iteración.

# Clase Hormiga
class Hormiga:
    def __init__(self, pi, pf):
        self.pi = pi
        self.pf = pf
        self.Camino = [pi]

    def sig_nodo(self, n):
        P = V * tau
        P[n, self.Camino[-1]] = 0  # Impide volver al nodo anterior.
        P = P[n, :] / np.sum(P[n, :])  # Vector de probabilidades.
        indice = np.array(range(L))
        c = P > 0
        P = P[c]
        indice = indice[c]

        for i in range(1, len(P)):
            P[i] = P[i] + P[i - 1]

        u = random.random()
        if 0 <= u <= P[0]:
            y = indice[0]
        else:
            for i in range(1, len(P)):
                if P[i - 1] < u <= P[i]:
                    y = indice[i]

        self.Camino.append(y)

    def trayectoria(self):
        run = 0
        while run < L - 1:
            self.sig_nodo(self.Camino[-1])
            if self.Camino[-1] == self.pf:
                break
            run += 1

    def apor_fero(self, i, j):
        C = self.Camino
        y = 0
        for t in range(len(C) - 1):
            if (i, j) == (C[t], C[t + 1]):
                y = 1
        return y

    def costo(self):
        C = self.Camino
        if C[-1] != self.pf:
            return np.inf
        return sum(A[C[t], C[t + 1]] for t in range(len(C) - 1))

def main():
    global tau
    d = 0
    while d < N:
        Colonia = [Hormiga(pi, pf) for _ in range(nh)]

        for hormiga in Colonia:
            hormiga.trayectoria()

        for hormiga in Colonia:
            hormiga.costo()

        for i in range(L):
            for j in range(L):
                for hormiga in Colonia:
                    tau[i, j] = (1 - ro) * tau[i, j] + hormiga.apor_fero(i, j) * 1 / (hormiga.costo() ** 4)

        # Cálculo del menor costo en esta iteración
        M_C = [hormiga.costo() for hormiga in Colonia]
        mejora.append(np.min(M_C))

        d += 1

    # Cálculos finales y gráficos
    Costos = [hormiga.costo() for hormiga in Colonia]
    indice = np.argsort(Costos)
    Mejor_Costo = Costos[indice[0]]
    Mejor_Camino = np.array(Colonia[indice[0]].Camino) + 1

    print("El mejor individuo es:", Mejor_Camino)
    print("Su costo es:", Mejor_Costo)

    mejora.append(Mejor_Costo)
    plt.plot(mejora)
    plt.title("Evolución del algoritmo", fontweight="bold", fontsize=14)
    plt.xlabel("Generación", fontweight="bold", fontsize=12)
    plt.ylabel("Mejor costo", fontweight="bold", fontsize=12)
    plt.xlim(0, N)
    plt.show()

# Ejecutamos el programa
if __name__ == "__main__":
    main()
