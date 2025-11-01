/*********************************************
 * OPL 22.1.2.0 Model
 * Author: jnare
 * Creation Date: 1/11/2025 at 10:50:41 a. m.
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
//  VARIABLES
dvar float+ X_k[I][J][K][T]; 
dvar boolean Y[I][J][K][T]; 
dvar float+ X_total[I][J][T];

// FUNCIÓN OBJETIVO
minimize sum(i in I, j in J, k in K, t in T) C[i][j][k][t] * X_k[i][j][k][t];
// E. RESTRICCIONES
subject to {  
	forall(i in I, j in J, t in T) X_total[i][j][t] == sum(k in K) X_k[i][j][k][t];
  // 1. Satisfacción de la Demanda: X_total debe cubrir la demanda D[i][t]
  forall(i in I, t in T) sum(j in J) X_total[i][j][t] == D[i][t];
  // 2. Capacidad de Suministro: X_total <= Cap[j][t]
  forall(j in J, t in T) sum(i in I) X_total[i][j][t] <= Cap[j][t];
  // 3. Lógica de Descuento (Límite Superior): X_k <= U[k] * Y[k]
  forall(i in I, j in J, k in K, t in T) X_k[i][j][k][t] <= U[k] * Y[i][j][k][t];
  // 4. Lógica de Descuento (Límite Inferior): X_k >= L[k] * Y[k] (FUERZA VOLUMEN)
  forall(i in I, j in J, k in K, t in T)  X_k[i][j][k][t] >= L[k] * Y[i][j][k][t];
  // 5. Exclusividad del Tramo: Solo se activa un tramo Y[k] por compra
  forall(i in I, j in J, t in T) sum(k in K) Y[i][j][k][t] <= 1;
}