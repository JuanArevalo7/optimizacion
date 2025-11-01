from ortools.linear_solver import pywraplp

# --- Datos ---
I = ["Item1", "Item2"]
J = ["ProvA", "ProvB", "ProvC"]
T = ["Q1", "Q2"]

D = {("Item1","Q1"):100, ("Item1","Q2"):120,
     ("Item2","Q1"):50,  ("Item2","Q2"):60}

Cap = {("ProvA","Q1"):80,  ("ProvA","Q2"):100,
       ("ProvB","Q1"):90,  ("ProvB","Q2"):90,
       ("ProvC","Q1"):150, ("ProvC","Q2"):150}

C = {
  ("Item1","ProvA","Q1"):10.0, ("Item1","ProvA","Q2"):10.5,
  ("Item1","ProvB","Q1"):9.5,  ("Item1","ProvB","Q2"):9.8,
  ("Item1","ProvC","Q1"):11.0, ("Item1","ProvC","Q2"):11.2,
  ("Item2","ProvA","Q1"):22.0, ("Item2","ProvA","Q2"):23.0,
  ("Item2","ProvB","Q1"):21.5, ("Item2","ProvB","Q2"):22.5,
  ("Item2","ProvC","Q1"):24.0, ("Item2","ProvC","Q2"):25.0
}

# --- Crear solver ---
solver = pywraplp.Solver.CreateSolver("GLOP")  # LP continuo

# --- Variables ---
X = {}
for i in I:
    for j in J:
        for t in T:
            X[i,j,t] = solver.NumVar(0, solver.infinity(), f"X_{i}_{j}_{t}")

# --- Función objetivo ---
objective = solver.Sum(C[i,j,t] * X[i,j,t] for i in I for j in J for t in T)
solver.Minimize(objective)

# --- Restricción de demanda ---
for i in I:
    for t in T:
        solver.Add(solver.Sum(X[i,j,t] for j in J) == D[i,t])

# --- Restricción de capacidad ---
for j in J:
    for t in T:
        solver.Add(solver.Sum(X[i,j,t] for i in I) <= Cap[j,t])

# --- Resolver ---
status = solver.Solve()

# --- Resultados ---
if status == pywraplp.Solver.OPTIMAL:
    print("✅ Solución óptima encontrada\n")
    print(f"Costo total mínimo = {solver.Objective().Value():.2f}\n")

    print("Asignaciones (todas las variables):")
    print(f"{'Item':<8}{'Proveedor':<8}{'Periodo':<6}{'Cantidad':>10}")
    print("-" * 35)
    for i in I:
        for j in J:
            for t in T:
                val = X[i,j,t].solution_value()
                print(f"{i:<8}{j:<8}{t:<6}{val:>10.2f}")
else:
    print("⚠️ No se encontró solución óptima.")
