# modelo_optimizacion.py - Construye, resuelve (CBC) y valida el modelo 0-1 contra las cotas analiticas.

import pulp

from datos import (
    nombres, c, a, b,
    B_nominal, H_nominal, J_critico,
)
from cotas_analiticas import (
    heuristica_greedy_dual, cota_superior_LP,
)

# 1. Construccion del modelo: devuelve (modelo, lista de variables binarias x_j).
def construir_modelo(c, a, b, B, H, J_crit, nombres):
    n = len(c)
    J = range(n)

    modelo = pulp.LpProblem("Priorizacion_Mantenimiento", pulp.LpMaximize)
    x = [
        pulp.LpVariable(f"x_{nombres[j]}", cat="Binary")
        for j in J
    ]
    modelo += pulp.lpSum(c[j] * x[j] for j in J), "Prioridad_agregada"
    modelo += (
        pulp.lpSum(a[j] * x[j] for j in J) <= B,
        "R1_presupuesto"
    )
    modelo += (
        pulp.lpSum(b[j] * x[j] for j in J) <= H,
        "R2_horas"
    )
    for j in J_crit:
        modelo += (
            x[j] == 1,
            f"R3_critico_{nombres[j]}"
        )
    return modelo, x

# 2. Resolucion con CBC: devuelve dict con estado, z_optimo, x_estrella, seleccionados, gasto y horas.
def resolver_modelo(modelo, x, c, a, b, nombres):
    modelo.solve(pulp.PULP_CBC_CMD(msg=False))
    estado = pulp.LpStatus[modelo.status]
    z_optimo = pulp.value(modelo.objective)
    x_estrella = [int(round(x[j].value())) for j in range(len(x))]
    seleccionados = [j for j, v in enumerate(x_estrella) if v == 1]
    gasto = sum(a[j] for j in seleccionados)
    horas = sum(b[j] for j in seleccionados)

    return {
        "estado": estado,
        "z_optimo": z_optimo,
        "x_estrella": x_estrella,
        "seleccionados": seleccionados,
        "gasto": gasto,
        "horas": horas,
    }

# 3. Validacion: comprueba que z* cae en la banda [z_greedy, CS2].
def validar_contra_cotas(z_optimo, c, a, b, B, H, J_crit):
    _, _, _, z_greedy = heuristica_greedy_dual(
        c, a, b, B, H, J_crit, criterio="coste"
    )
    CS2_R1 = cota_superior_LP(c, a, B, J_crit)
    CS2_R2 = cota_superior_LP(c, b, H, J_crit)
    CS2 = min(CS2_R1, CS2_R2)

    en_banda = (z_greedy - 1e-6) <= z_optimo <= (CS2 + 1e-6)  # tolerancia 1e-6 frente a redondeo

    return {
        "z_greedy": z_greedy,
        "CS2_R1": CS2_R1,
        "CS2_R2": CS2_R2,
        "CS2": CS2,
        "z_optimo": z_optimo,
        "en_banda": en_banda,
        "gap_absoluto_inferior": z_optimo - z_greedy,
        "gap_absoluto_superior": CS2 - z_optimo,
    }

# 4. Comparativa detallada greedy vs optimo (interseccion, exclusivos de cada plan y cifras agregadas).
def comparar_greedy_vs_optimo(sol, c, a, b, B, H, J_crit, nombres):
    sel_greedy, gasto_greedy, horas_greedy, z_greedy = heuristica_greedy_dual(
        c, a, b, B, H, J_crit, criterio="coste"
    )
    set_greedy = set(sel_greedy)
    set_optimo = set(sol["seleccionados"])

    interseccion = sorted(set_greedy & set_optimo)
    solo_greedy = sorted(set_greedy - set_optimo)
    solo_optimo = sorted(set_optimo - set_greedy)
    def detalle(j):
        return {
            "j": j,
            "nombre": nombres[j],
            "c": float(c[j]),
            "a": int(a[j]),
            "b": float(b[j]),
            "c_sobre_a": float(c[j] / a[j]),
            "c_sobre_b": float(c[j] / b[j]),
        }

    return {
        "z_greedy": z_greedy,
        "z_optimo": sol["z_optimo"],
        "gasto_greedy": gasto_greedy,
        "gasto_optimo": sol["gasto"],
        "horas_greedy": horas_greedy,
        "horas_optimo": sol["horas"],
        "n_greedy": len(sel_greedy),
        "n_optimo": len(sol["seleccionados"]),
        "interseccion": [detalle(j) for j in interseccion],
        "solo_greedy": [detalle(j) for j in solo_greedy],
        "solo_optimo": [detalle(j) for j in solo_optimo],
    }

# 5. Ejecucion directa
if __name__ == "__main__":

    print("Modelo de optimizacion 0-1 en PuLP")
    print("-" * 60)
    print(f"Solver utilizado: CBC (via PuLP {pulp.__version__}).")
    print(f"Parametros nominales: B = {B_nominal:,} euros, H = {H_nominal} h.")
    print(f"Activos criticos forzados: "
          f"{[nombres[j] for j in J_critico]}.")

    modelo, x = construir_modelo(
        c, a, b, B_nominal, H_nominal, J_critico, nombres
    )
    print(f"\nVariables del modelo: {len(modelo.variables())}.")
    print(f"Restricciones del modelo: {len(modelo.constraints)}.")
    for nombre_r in modelo.constraints:
        print(f"  - {nombre_r}")

    print(f"\nResolucion y solucion optima")
    print("-" * 60)
    sol = resolver_modelo(modelo, x, c, a, b, nombres)
    print(f"Estado del solver: {sol['estado']}.")
    print(f"Valor optimo z*:   {sol['z_optimo']:.4f}.")
    print(f"Activos elegidos:  {len(sol['seleccionados'])} de 20.")
    print(f"Lista: {sorted([nombres[j] for j in sol['seleccionados']])}.")
    print(f"Gasto: {sol['gasto']:>8,.0f} euros "
          f"({100 * sol['gasto'] / B_nominal:.1f}% de B).")
    print(f"Horas: {sol['horas']:>8.1f} h "
          f"({100 * sol['horas'] / H_nominal:.1f}% de H).")

    print(f"\nValidacion contra las cotas analiticas")
    print("-" * 60)
    val = validar_contra_cotas(
        sol["z_optimo"], c, a, b, B_nominal, H_nominal, J_critico
    )
    print(f"  Cota inferior z_greedy : {val['z_greedy']:.4f}")
    print(f"  Optimo entero z*       : {val['z_optimo']:.4f}")
    print(f"  Cota superior CS2      : {val['CS2']:.4f}")
    veredicto = "si" if val["en_banda"] else "no"
    print(f"\n  El optimo entero esta dentro de la banda: {veredicto}.")
    print(f"  Mejora respecto al greedy : "
          f"+{val['gap_absoluto_inferior']:.4f} "
          f"({100 * val['gap_absoluto_inferior'] / val['z_greedy']:.2f}%).")
    print(f"  Distancia a la cota CS2   : "
          f"-{val['gap_absoluto_superior']:.4f} "
          f"({100 * val['gap_absoluto_superior'] / val['CS2']:.2f}%).")

    print(f"\nComparativa greedy vs optimo")
    print("-" * 60)
    comp = comparar_greedy_vs_optimo(
        sol, c, a, b, B_nominal, H_nominal, J_critico, nombres
    )
    print(f"  Greedy: {comp['n_greedy']} activos, z = {comp['z_greedy']:.4f}, "
          f"gasto = {comp['gasto_greedy']:,} euros, horas = {comp['horas_greedy']:.1f} h.")
    print(f"  Optimo: {comp['n_optimo']} activos, z = {comp['z_optimo']:.4f}, "
          f"gasto = {comp['gasto_optimo']:,} euros, horas = {comp['horas_optimo']:.1f} h.")

    print(f"\n  Interseccion (en ambos planes): "
          f"{len(comp['interseccion'])} activos.")
    print(f"    {[d['nombre'] for d in comp['interseccion']]}")

    print(f"\n  Solo en el greedy ({len(comp['solo_greedy'])} activos, "
          f"descartados por el optimo):")
    print(f"    {'Nombre':<12} {'c_j':>8} {'a_j (eur)':>10} "
          f"{'b_j (h)':>8} {'c/a':>9} {'c/b':>7}")
    for d in comp['solo_greedy']:
        print(f"    {d['nombre']:<12} {d['c']:>8.4f} {d['a']:>10,} "
              f"{d['b']:>8.1f} {d['c_sobre_a']*1000:>9.4f} "
              f"{d['c_sobre_b']:>7.4f}")

    print(f"\n  Solo en el optimo ({len(comp['solo_optimo'])} activos, "
          f"incorporados frente al greedy):")
    print(f"    {'Nombre':<12} {'c_j':>8} {'a_j (eur)':>10} "
          f"{'b_j (h)':>8} {'c/a':>9} {'c/b':>7}")
    for d in comp['solo_optimo']:
        print(f"    {d['nombre']:<12} {d['c']:>8.4f} {d['a']:>10,} "
              f"{d['b']:>8.1f} {d['c_sobre_a']*1000:>9.4f} "
              f"{d['c_sobre_b']:>7.4f}")
    print(f"\n  Nota: c/a expresado en miles (c_j / a_j x 1000) para legibilidad.")
