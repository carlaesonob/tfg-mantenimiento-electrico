# cotas_analiticas.py - Cotas analiticas del optimo del problema 0-1 (validan despues el resultado de PuLP).

import numpy as np
import pulp

from datos import (
    nombres, c, a, b,
    B_nominal, H_nominal, J_critico,
)

# 1. Validacion cruzada de la solucion minima (solo criticos): cumple_B, cumple_H, gasto, horas.
def comprobar_factibilidad_critico(J_crit, B, H, a, b):
    gasto = sum(a[j] for j in J_crit)
    horas = sum(b[j] for j in J_crit)
    return (gasto <= B), (horas <= H), gasto, horas

# 2. Heuristica greedy dual (cota inferior): fuerza criticos, ordena el resto por c/a o c/b e incorpora si cabe.
def heuristica_greedy_dual(c, a, b, B, H, J_crit, criterio="coste"):
    seleccionados = list(J_crit)
    gasto = sum(a[j] for j in J_crit)
    horas = sum(b[j] for j in J_crit)

    restantes = [j for j in range(len(c)) if j not in J_crit]
    if criterio == "coste":
        restantes.sort(key=lambda j: -c[j] / a[j])
    else:
        restantes.sort(key=lambda j: -c[j] / b[j])

    for j in restantes:
        if (gasto + a[j] <= B) and (horas + b[j] <= H):
            seleccionados.append(j)
            gasto += a[j]
            horas += b[j]

    valor = sum(c[j] for j in seleccionados)
    return seleccionados, gasto, horas, valor

# 3. Relajacion LP de Dantzig con una sola restriccion (cota superior conservadora).
def cota_superior_LP(c, recurso, capacidad, J_crit):
    x = np.zeros(len(c))
    consumo = 0.0
    for j in J_crit:
        x[j] = 1
        consumo += recurso[j]

    restantes = [j for j in range(len(c)) if j not in J_crit]
    restantes.sort(key=lambda j: -c[j] / recurso[j])

    for j in restantes:
        if consumo + recurso[j] <= capacidad:
            x[j] = 1
            consumo += recurso[j]
        else:
            fraccion = (capacidad - consumo) / recurso[j]
            x[j] = fraccion
            break

    return float(c @ x)

# 4. Relajacion LP completa con R1 y R2 simultaneas y criticos forzados (cota superior ajustada).
def cota_superior_LP_completa(c, a, b, B, H, J_crit, nombres):
    n = len(c)
    J = range(n)

    modelo = pulp.LpProblem("Relajacion_LP_completa", pulp.LpMaximize)
    x = [
        pulp.LpVariable(f"x_{nombres[j]}", lowBound=0, upBound=1,
                        cat="Continuous")
        for j in J
    ]

    modelo += pulp.lpSum(c[j] * x[j] for j in J), "Prioridad_agregada"
    modelo += pulp.lpSum(a[j] * x[j] for j in J) <= B, "R1_presupuesto"
    modelo += pulp.lpSum(b[j] * x[j] for j in J) <= H, "R2_horas"
    for j in J_crit:
        modelo += x[j] == 1, f"R3_critico_{nombres[j]}"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))
    return float(pulp.value(modelo.objective))

# 5. Ejecucion directa
if __name__ == "__main__":

    print("Validacion cruzada de los parametros nominales")
    print("-" * 60)
    cumple_B, cumple_H, gasto_c, horas_c = comprobar_factibilidad_critico(
        J_critico, B_nominal, H_nominal, a, b
    )
    print("Solucion minima (solo criticos):")
    estado_B = "cabe" if cumple_B else "no cabe"
    estado_H = "cabe" if cumple_H else "no cabe"
    print(f"  Gasto: {gasto_c:>8,.0f} euros de {B_nominal:,} ({estado_B}).")
    print(f"  Horas: {horas_c:>8.1f} h de {H_nominal} h ({estado_H}).")

    sel, gasto_g, horas_g, z_greedy = heuristica_greedy_dual(
        c, a, b, B_nominal, H_nominal, J_critico, criterio="coste"
    )
    print(f"\nHeuristica greedy por c_j/a_j (R1 + R2 + R3):")
    print(f"  Activos seleccionados: {len(sel)} de 20.")
    print(f"  Lista: {sorted([nombres[j] for j in sel])}.")
    print(f"  Gasto: {gasto_g:>8,.0f} euros ({100 * gasto_g / B_nominal:.1f}% de B).")
    print(f"  Horas: {horas_g:>8.1f} h ({100 * horas_g / H_nominal:.1f}% de H).")
    print(f"  z_greedy = {z_greedy:.4f}.")

    print(f"\nCotas del optimo entero z*")
    print("-" * 60)
    CS1 = c.sum()
    CS2_R1 = cota_superior_LP(c, a, B_nominal, J_critico)
    CS2_R2 = cota_superior_LP(c, b, H_nominal, J_critico)
    CS2 = min(CS2_R1, CS2_R2)
    CS3 = cota_superior_LP_completa(
        c, a, b, B_nominal, H_nominal, J_critico, nombres
    )

    print(f"  CS1 (suma de c_j, no factible)        : {CS1:.4f}")
    print(f"  CS2_R1 (relajacion LP solo con R1)    : {CS2_R1:.4f}")
    print(f"  CS2_R2 (relajacion LP solo con R2)    : {CS2_R2:.4f}")
    print(f"  CS2 efectiva = min(CS2_R1, CS2_R2)    : {CS2:.4f}")
    print(f"  CS3 (relajacion LP completa, R1+R2+R3): {CS3:.4f}")
    print(f"  Cota inferior (heuristica greedy)     : {z_greedy:.4f}")
    print(f"\n  Banda conservadora: {z_greedy:.4f} <= z* <= {CS2:.4f}.")
    print(f"  Banda ajustada    : {z_greedy:.4f} <= z* <= {CS3:.4f}.")
    print(f"  Mejora de la cota superior: "
          f"{CS2 - CS3:.4f} ({100 * (CS2 - CS3) / CS2:.2f}%).")
    print(f"  Cobertura de riesgo: "
          f"{100 * z_greedy / c.sum():.1f}% <= cob <= {100 * CS3 / c.sum():.1f}%.")
