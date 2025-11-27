from ortools.linear_solver import pywraplp

def solve_fase_3_escalada_ortools():
    # ----------------------------------------------------------------------
    # 1. DEFINICIÓN DE CONJUNTOS Y DATOS (Fase 3.2 Escalandada)
    # ----------------------------------------------------------------------

    I = ['Item1', 'Item2']
    J = ['ProvA', 'ProvB', 'ProvC']
    T = ['Q1', 'Q2']
    K = [1, 2, 3]

    # Demandas
    D = {'Item1': {'Q1': 100, 'Q2': 120}, 'Item2': {'Q1': 50, 'Q2': 60}}

    # Capacidades
    Cap = {'ProvA': {'Q1': 80, 'Q2': 100}, 'ProvB': {'Q1': 90, 'Q2': 90}, 'ProvC': {'Q1': 150, 'Q2': 150}}

    # Límites de Volumen
    L = {1: 0, 2: 50, 3: 100}
    U = {1: 49.99, 2: 99.99, 3: 500} # 500 actúa como Big M

    # Penalización de Riesgo por Proveedor [j]
    # ProvB (1.20) es el más riesgoso, ProvC (0.10) el más seguro.
    Pen_Riesgo = {'ProvA': 0.30, 'ProvB': 1.20, 'ProvC': 0.10} 

    # Costo Unitario C[i][j][k][t] (Solo mostramos la estructura, asumiendo los datos cargados)
    C = {
        'Item1': {
            'ProvA': {1: {'Q1': 10.0, 'Q2': 10.5}, 2: {'Q1': 9.5, 'Q2': 10.0}, 3: {'Q1': 9.0, 'Q2': 9.5}},
            'ProvB': {1: {'Q1': 9.5, 'Q2': 9.8}, 2: {'Q1': 9.0, 'Q2': 9.3}, 3: {'Q1': 8.5, 'Q2': 8.8}},
            'ProvC': {1: {'Q1': 11.0, 'Q2': 11.2}, 2: {'Q1': 10.5, 'Q2': 10.7}, 3: {'Q1': 10.0, 'Q2': 10.2}}
        },
        'Item2': {
            'ProvA': {1: {'Q1': 22.0, 'Q2': 23.0}, 2: {'Q1': 21.0, 'Q2': 22.0}, 3: {'Q1': 20.0, 'Q2': 21.0}},
            'ProvB': {1: {'Q1': 21.5, 'Q2': 22.5}, 2: {'Q1': 20.5, 'Q2': 21.5}, 3: {'Q1': 19.5, 'Q2': 20.5}},
            'ProvC': {1: {'Q1': 24.0, 'Q2': 25.0}, 2: {'Q1': 23.0, 'Q2': 24.0}, 3: {'Q1': 22.0, 'Q2': 23.0}}
        }
    }

    # ----------------------------------------------------------------------
    # 2. CREACIÓN DEL SOLVER Y VARIABLES (Mismo código que antes)
    # ----------------------------------------------------------------------
    
    solver = pywraplp.Solver.CreateSolver('CBC')
    if not solver: return
    infinity = solver.infinity()

    # Variables de Decisión
    X_k = {}
    Y = {}
    for i in I:
        for j in J:
            for k in K:
                for t in T:
                    X_k[(i, j, k, t)] = solver.NumVar(0, infinity, f'X_k_{i}_{j}_{k}_{t}')
                    Y[(i, j, k, t)] = solver.BoolVar(f'Y_{i}_{j}_{k}_{t}')

    X_total = {}
    for i in I:
        for j in J:
            for t in T:
                X_total[(i, j, t)] = solver.NumVar(0, infinity, f'X_total_{i}_{j}_{t}')

    # ----------------------------------------------------------------------
    # 3. RESTRICCIONES (Se mantienen igual a la Fase 2)
    # ----------------------------------------------------------------------

    # Acople de Tramos
    for i in I:
        for j in J:
            for t in T:
                solver.Add(X_total[(i, j, t)] == solver.Sum(X_k[(i, j, k, t)] for k in K), name=f"Acople_{i}_{j}_{t}")

    # Demanda
    for i in I:
        for t in T:
            solver.Add(solver.Sum(X_total[(i, j, t)] for j in J) == D[i][t], name=f"Demanda_{i}_{t}")

    # Capacidad
    for j in J:
        for t in T:
            solver.Add(solver.Sum(X_total[(i, j, t)] for i in I) <= Cap[j][t], name=f"Capacidad_{j}_{t}")

    # Lógica de Descuento (U y L)
    for i in I:
        for j in J:
            for k in K:
                for t in T:
                    # U
                    solver.Add(X_k[(i, j, k, t)] <= U[k] * Y[(i, j, k, t)], name=f"Desc_U_{i}_{j}_{k}_{t}")
                    # L
                    solver.Add(X_k[(i, j, k, t)] >= L[k] * Y[(i, j, k, t)], name=f"Desc_L_{i}_{j}_{k}_{t}")

    # Exclusividad del Tramo
    for i in I:
        for j in J:
            for t in T:
                solver.Add(solver.Sum(Y[(i, j, k, t)] for k in K) <= 1, name=f"Exclusividad_{i}_{j}_{t}")

    # ----------------------------------------------------------------------
    # 4. FUNCIÓN OBJETIVO (Costo de Compra + Costo de Riesgo)
    # ----------------------------------------------------------------------
    
    costo_compra = solver.Sum(C[i][j][k][t] * X_k[(i, j, k, t)] for i in I for j in J for k in K for t in T)
    costo_riesgo = solver.Sum(Pen_Riesgo[j] * X_total[(i, j, t)] for i in I for j in J for t in T)
    
    solver.Minimize(costo_compra + costo_riesgo)

    # ----------------------------------------------------------------------
    # 5. RESOLUCIÓN E IMPRESIÓN
    # ----------------------------------------------------------------------

    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print(f"✅ Estado de la Solución: ÓPTIMO")
        final_fo = solver.Objective().Value()
        costo_riesgo_total = costo_riesgo.solution_value()
        costo_compra_final = final_fo - costo_riesgo_total

        print(f"\n--- RESULTADOS ECONÓMICOS ---")
        print(f"F.O. Final (Costo Total Esperado): ${final_fo:.2f}")
        print(f"Costo de Compra (Fase 2 + Descuento): ${costo_compra_final:.2f} (Base 4,396.00)")
        print(f"Costo de Penalización por Riesgo: ${costo_riesgo_total:.2f}")
        
        print(f"\n--- DECISIÓN DE ASIGNACIÓN (X_total) ---")
        for j in J:
            compra_j = sum(X_total[(i, j, t)].solution_value() for i in I for t in T)
            if compra_j > 1e-6:
                costo_efectivo_j = final_fo / sum(D[i][t] for i in I for t in T)
                print(f"  {j}: {compra_j:.2f} unidades asignadas.")
                
    else:
        print("El problema no se resolvió al óptimo.")

# Ejecutar la función
solve_fase_3_escalada_ortools()