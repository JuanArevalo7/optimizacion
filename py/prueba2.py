from ortools.linear_solver import pywraplp

# --- Conjuntos ---
I = ["Item1", "Item2"]
J = ["ProvA", "ProvB", "ProvC"]
T = ["Q1", "Q2"]
K = [1, 2, 3]

# --- Parámetros ---
D = {("Item1","Q1"):100, ("Item1","Q2"):120,
     ("Item2","Q1"):50,  ("Item2","Q2"):60}

Cap = {("ProvA","Q1"):80,  ("ProvA","Q2"):100,
       ("ProvB","Q1"):90,  ("ProvB","Q2"):90,
       ("ProvC","Q1"):150, ("ProvC","Q2"):150}

L = {1:0, 2:50, 3:100}
U = {1:49.99, 2:99.99, 3:500}

# C[i][j][k][t]
C = {
# Item1
("Item1","ProvA",1,"Q1"):10.0, ("Item1","ProvA",1,"Q2"):10.5,
("Item1","ProvA",2,"Q1"):9.5,  ("Item1","ProvA",2,"Q2"):10.0,
("Item1","ProvA",3,"Q1"):9.0,  ("Item1","ProvA",3,"Q2"):9.5,

("Item1","ProvB",1,"Q1"):9.5,  ("Item1","ProvB",1,"Q2"):9.8,
("Item1","ProvB",2,"Q1"):9.0,  ("Item1","ProvB",2,"Q2"):9.3,
("Item1","ProvB",3,"Q1"):8.5,  ("Item1","ProvB",3,"Q2"):8.8,

("Item1","ProvC",1,"Q1"):11.0, ("Item1","ProvC",1,"Q2"):11.2,
("Item1","ProvC",2,"Q1"):10.5, ("Item1","ProvC",2,"Q2"):10.7,
("Item1","ProvC",3,"Q1"):10.0, ("Item1","ProvC",3,"Q2"):10.2,

# Item2
("Item2","ProvA",1,"Q1"):22.0, ("Item2","ProvA",1,"Q2"):23.0,
("Item2","ProvA",2,"Q1"):21.0, ("Item2","ProvA",2,"Q2"):22.0,
("Item2","ProvA",3,"Q1"):20.0, ("Item2","ProvA",3,"Q2"):21.0,

("Item2","ProvB",1,"Q1"):21.5, ("Item2","ProvB",1,"Q2"):22.5,
("Item2","ProvB",2,"Q1"):20.5, ("Item2","ProvB",2,"Q2"):21.5,
("Item2","ProvB",3,"Q1"):19.5, ("Item2","ProvB",3,"Q2"):20.5,

("Item2","ProvC",1,"Q1"):24.0, ("Item2","ProvC",1,"Q2"):25.0,
("Item2","ProvC",2,"Q1"):23.0, ("Item2","ProvC",2,"Q2"):24.0,
("Item2","ProvC",3,"Q1"):22.0, ("Item2","ProvC",3,"Q2"):23.0
}

# --- Crear solver MIP (CBC) ---
solver = pywraplp.Solver.CreateSolver("CBC")

# --- Variables ---
X = {}          # X[i,j,t]  total
Xk = {}         # X[i,j,k,t]
Y = {}          # Y[i,j,k,t] binaria

for i in I:
    for j in J:
        for t in T:
            X[i,j,t] = solver.NumVar(0, solver.infinity(), f"X_{i}_{j}_{t}")
            for k in K:
                Xk[i,j,k,t] = solver.NumVar(0, solver.infinity(), f"X_{i}_{j}_{k}_{t}")
                Y[i,j,k,t]  = solver.BoolVar(f"Y_{i}_{j}_{k}_{t}")

# --- Función objetivo ---
solver.Minimize(
    solver.Sum(C[i,j,k,t]*Xk[i,j,k,t] for i in I for j in J for k in K for t in T)
)

# --- Restricciones ---

# A. Acople de tramos
for i in I:
    for j in J:
        for t in T:
            solver.Add(solver.Sum(Xk[i,j,k,t] for k in K) == X[i,j,t])

# 1. Satisfacción de la demanda
for i in I:
    for t in T:
        solver.Add(solver.Sum(X[i,j,t] for j in J) == D[i,t])

# 2. Capacidad de proveedor
for j in J:
    for t in T:
        solver.Add(solver.Sum(X[i,j,t] for i in I) <= Cap[j,t])

# 3 y 4. Lógica de descuento
for i in I:
    for j in J:
        for t in T:
            for k in K:
                solver.Add(Xk[i,j,k,t] <= U[k]*Y[i,j,k,t])
                solver.Add(Xk[i,j,k,t] >= L[k]*Y[i,j,k,t])

# 5. Exclusividad de tramo
for i in I:
    for j in J:
        for t in T:
            solver.Add(solver.Sum(Y[i,j,k,t] for k in K) <= 1)

# --- Resolver ---
status = solver.Solve()

# --- Resultados ---
if status == pywraplp.Solver.OPTIMAL:
    print("✅ Solución óptima encontrada\n")
    print(f"Costo total mínimo = {solver.Objective().Value():.2f}\n")

    print(f"{'Item':<6}{'Prov':<6}{'Per':<4}{'Tramo':<6}{'Xk':>10}{'Y':>6}")
    print("-"*45)
    for i in I:
        for j in J:
            for t in T:
                for k in K:
                    print(f"{i:<6}{j:<6}{t:<4}{k:<6}{Xk[i,j,k,t].solution_value():>10.2f}{int(Y[i,j,k,t].solution_value()):>6}")
else:
    print("⚠️ No se encontró solución óptima.")
