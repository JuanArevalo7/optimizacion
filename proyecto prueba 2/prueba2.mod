/*********************************************
 * OPL 22.1.2.0 Model
 * Author: jnare
 * Creation Date: 31/10/2025 at 11:33:05 a.�m.
 *********************************************/
{string} I = ...; 
{string} J = ...; 
{string} T = ...; 
{int} K = ...;  
//PARAMETROS
float D[I][T] = ...;        
float Cap[J][T] = ...;      
float L[K] = ...;          
float U[K] = ...;           
float C[I][J][K][T] = ...;   
// C. VARIABLES DE DECISIÓN
// Cantidad asignada al tramo de descuento k.
dvar float+ X_k[I][J][K][T]; 
dvar boolean Y[I][J][K][T]; 
dvar float+ X_total[I][J][T];
// D. FUNCIÓN OBJETIVO
// ----------------------------------------------------------------------------
// Minimizar el costo total basado en los costos por tramo.
minimize
  sum(i in I, j in J, k in K, t in T) C[i][j][k][t] * X_k[i][j][k][t];

// ----------------------------------------------------------------------------
// E. RESTRICCIONES
// ----------------------------------------------------------------------------
subject to {
  
  // Definición de X_total[i][j][t] como una expresión (Acople de Tramos)
  // X_total es la suma de todas las cantidades por tramo.
  forall(i in I, j in J, t in T)
    ct_acople:
      X_total[i][j][t] == sum(k in K) X_k[i][j][k][t];

  // 1. Satisfacción de la Demanda: Ahora usa la variable X_total
  forall(i in I, t in T)
    ct_demanda:
      sum(j in J) X_total[i][j][t] == D[i][t];

  // 2. Capacidad de Suministro: También usa X_total
  forall(j in J, t in T)
    ct_capacidad:
      sum(i in I) X_total[i][j][t] <= Cap[j][t];

  // 3. Lógica de Descuento (Límite Superior): Big-M con U[k].
  // Si Y=0, X_k debe ser 0.
  forall(i in I, j in J, k in K, t in T)
    ct_logica_desc_U:
      X_k[i][j][k][t] <= U[k] * Y[i][j][k][t];

  // 4. Lógica de Descuento (Límite Inferior): Fuerza el volumen mínimo si el tramo es elegido.
  // Si Y=1, X_k debe ser >= L[k].
  forall(i in I, j in J, k in K, t in T)
    ct_logica_desc_L:
      X_k[i][j][k][t] >= L[k] * Y[i][j][k][t];

  // 5. Exclusividad del Tramo: Solo se puede activar un tramo k por compra (i, j, t).
  forall(i in I, j in J, t in T)
    ct_exclusividad_k:
      sum(k in K) Y[i][j][k][t] <= 1;
}