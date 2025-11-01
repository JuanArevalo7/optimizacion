/*********************************************
 * OPL 22.1.2.0 Model
 * Author: jnare
 * Creation Date: 31/10/2025 at 10:42:46 a.�m.
 *********************************************/
{string} T=...;
{string} I=...;
{string} J=...;
//parametros
float D[I][T] = ...;
float Cap[J][T] = ...;
float C[I][J][T] = ...;
//variable
dvar float+ X[I][J][T];
//restricciones
minimize sum(i in I, j in J, t in T) C[i][j][t] * X[i][j][t];
subject to {
  forall(i in I, t in T) sum(j in J) X[i][j][t] == D[i][t];
  forall(j in J, t in T) sum(i in I) X[i][j][t] <= Cap[j][t];
}
