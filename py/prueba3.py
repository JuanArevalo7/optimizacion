from ortools.linear_solver import pywraplp

def solve_fase_3_ortools():
    # ----------------------------------------------------------------------
    # 1. DEFINICIÓN DE CONJUNTOS Y DATOS (Mini-Problema de Prueba)
    # ----------------------------------------------------------------------

    # Conjuntos
    I = ['P1']        
    J = ['S_Alta', 'S_Baja'] 
    T = ['Q1']       
    K = [1, 2]       

    # Parámetros
    D = {'P1': {'Q1': 40}}  
    Cap = {'S_Alta': {'Q1': 100}, 'S_Baja': {'Q1': 100}} 
    L = {1: 0, 2: 40}
    U = {1: 39.99, 2: 100}
    
    # Costo Unitario C[i][j][k][t]
    C = {
        'P1': {
            'S_Alta': {1: {'Q1': 10.00}, 2: {'Q1': 7.50}},
            'S_Baja': {1: {'Q1': 12.00}, 2: {'Q1': 9.50}}
        }
    }
    
    # Penalización de Riesgo por Proveedor [j]
    Pen_Riesgo = {'S_Alta': 3.00, 'S_Baja': 0.10} 

    # ----------------------------------------------------------------------
    # 2. CREACIÓN DEL SOLVER Y VARIABLES
    # ----------------------------------------------------------------------
    
    # Usamos el solver CBC para problemas MIP
    solver = pywraplp.Solver.CreateSolver('CBC')
    if not solver:
        return

    infinity = solver.infinity()

    # Variables de Cantidad por Tramo (Continua)
    X_k = {}
    for i in I:
        for j in J:
            for k in K:
                for t in T:
                    X_k[(i, j, k, t)] = solver.NumVar(0, infinity, f'X_k_{i}_{j}_{k}_{t}')

    # Variable Binaria de Selección de Tramo
    Y = {}
    for i in I:
        for j in J:
            for k in K:
                for t in T:
                    Y[(i, j, k, t)] = solver.BoolVar(f'Y_{i}_{j}_{k}_{t}')

    # Variable Agregada para Demanda/Riesgo (X_total[i][j][t])
    X_total = {}
    for i in I:
        for j in J:
            for t in T:
                X_total[(i, j, t)] = solver.NumVar(0, infinity, f'X_total_{i}_{j}_{t}')

    # ----------------------------------------------------------------------
    # 3. RESTRICCIONES
    # ----------------------------------------------------------------------

    # A. Acople de Tramos: X_total == Suma(X_k)
    for i in I:
        for j in J:
            for t in T:
                solver.Add(X_total[(i, j, t)] == solver.Sum(X_k[(i, j, k, t)] for k in K),
                           name=f"Acople_{i}_{j}_{t}")

    # 1. Satisfacción de la Demanda: Suma(X_total para j) == D[i][t]
    for i in I:
        for t in T:
            solver.Add(solver.Sum(X_total[(i, j, t)] for j in J) == D[i][t],
                       name=f"Demanda_{i}_{t}")

    # 2. Capacidad de Suministro: Suma(X_total para i) <= Cap[j][t]
    for j in J:
        for t in T:
            solver.Add(solver.Sum(X_total[(i, j, t)] for i in I) <= Cap[j][t],
                       name=f"Capacidad_{j}_{t}")

    # 3. Lógica de Descuento (Límite Superior): X_k <= U[k] * Y
    for i in I:
        for j in J:
            for k in K:
                for t in T:
                    solver.Add(X_k[(i, j, k, t)] <= U[k] * Y[(i, j, k, t)],
                               name=f"Desc_U_{i}_{j}_{k}_{t}")

    # 4. Lógica de Descuento (Límite Inferior): X_k >= L[k] * Y
    for i in I:
        for j in J:
            for k in K:
                for t in T:
                    solver.Add(X_k[(i, j, k, t)] >= L[k] * Y[(i, j, k, t)],
                               name=f"Desc_L_{i}_{j}_{k}_{t}")

    # 5. Exclusividad del Tramo: Suma(Y para k) <= 1
    for i in I:
        for j in J:
            for t in T:
                solver.Add(solver.Sum(Y[(i, j, k, t)] for k in K) <= 1,
                           name=f"Exclusividad_{i}_{j}_{t}")

    # ----------------------------------------------------------------------
    # 4. FUNCIÓN OBJETIVO
    # ----------------------------------------------------------------------
    
    # Término de Costo de Compra (Descuento)
    costo_compra = solver.Sum(C[i][j][k][t] * X_k[(i, j, k, t)] for i in I for j in J for k in K for t in T)

    # Término de Penalización por Riesgo
    costo_riesgo = solver.Sum(Pen_Riesgo[j] * X_total[(i, j, t)] for i in I for j in J for t in T)

    # F.O. = Costo de Compra + Costo de Riesgo
    solver.Minimize(costo_compra + costo_riesgo)

    # ----------------------------------------------------------------------
    # 5. RESOLUCIÓN E IMPRESIÓN
    # ----------------------------------------------------------------------

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print(f"Estado de la Solución: ÓPTIMO")
        print(f"Resultado de la Función Objetivo (Costo Total Esperado): ${solver.Objective().Value():.2f}\n")
        
        print("--- DETALLE DE COMPRAS ---")
        for j in J:
            compra_total = X_total[('P1', j, 'Q1')].solution_value()
            if compra_total > 1e-6: # Ignoramos valores cercanos a cero
                costo_compra_base = solver.Objective().Value() - costo_riesgo.solution_value()
                costo_riesgo_j = Pen_Riesgo[j] * compra_total

                print(f"Proveedor: {j}")
                print(f"  Unidades Compradas: {compra_total:.2f}")
                print(f"  Penalización por Riesgo ({Pen_Riesgo[j]:.2f}/unidad): ${costo_riesgo_j:.2f}")
                print(f"  Tramo Activado Y: {1 if Y[('P1', j, 2, 'Q1')].solution_value() > 0.5 else 0}")

    elif status == pywraplp.Solver.INFEASIBLE:
        print("El problema es infactible.")
    else:
        print("El problema no se resolvió al óptimo.")

# Ejecutar la función
solve_fase_3_ortools()