# Optimizing Preventive Maintenance Under Budget Constraints

**An interactive decision tool that decides where to spend a limited maintenance budget to cover the most risk.**

When you have more assets that need maintenance than budget and crew hours to maintain them, which ones do you fix first? This project turns that question into a quantitative model and an interactive dashboard, so the trade-off can be made with data instead of intuition.

Built as my final-year engineering thesis (graded **9.2/10, Distinction**). The case study uses an electrical distribution network, but the underlying problem — allocating scarce resources to maximize impact under hard constraints — is general.

**[▶ Try the live dashboard](https://mantenimiento-electrico-tfg-carlaeb.streamlit.app)** · [Read the approach](#approach)

---

## The problem

Maintenance teams routinely face more work than resources: a long list of assets, each with a different probability of failing, a different cost of failing, and a different cost and time to fix. The budget and the available crew hours only cover a fraction of them. Picking the wrong subset wastes money and leaves the highest-risk assets unattended.

The goal: **select the set of assets to maintain that covers the maximum possible risk, without exceeding the budget or the available hours.**

## Approach

The tool combines two operations-research techniques:

1. **Scoring the priorities (AHP).** Each asset is scored on four criteria — failure probability, failure impact, intervention cost, and intervention time. The criteria are weighted using the Analytic Hierarchy Process, which turns expert judgment into consistent numeric weights (with a built-in consistency check so the judgments can't contradict each other).

2. **Choosing the optimal plan (0-1 optimization).** A binary integer program then picks the combination of assets that maximizes total covered risk while respecting the budget and crew-hour limits. It's solved exactly, not approximated.

To make sure the result can be trusted, the optimal plan is **validated against analytical bounds** (a lower bound from a greedy heuristic, an upper bound from the linear relaxation) and stress-tested with a **sensitivity analysis** — confirming the recommended plan stays stable under reasonable changes in budget, hours, and weights.

## What it does

- Computes the **optimal maintenance plan** for a given budget and crew-hour limit.
- Lets the user **change the constraints and instantly see how the plan shifts** — turning a one-off study into a tool anyone can use without writing code.
- Flags when input data is getting stale, so decisions aren't made on outdated numbers.

## Tech stack

Python · Streamlit · PuLP + CBC (optimization) · Plotly · pandas · NumPy

## Run it locally

```bash
pip install -r requirements.txt
streamlit run Plan_de_mantenimiento.py
```

## Code structure

| File | Purpose |
|------|---------|
| `Plan_de_mantenimiento.py` | Main dashboard (Streamlit) |
| `pages/1_Inputs.py` | Asset inventory view |
| `datos.py` | Case-study data + model parameters |
| `modelo_optimizacion.py` | Model build & solve (PuLP) |
| `cotas_analiticas.py` | Analytical bounds for validation |

---

## Case study details

The model is demonstrated on a simulated urban distribution network of 20 assets (transformers, MV lines, switchgear, fuses, LV lines), dimensioned according to Spanish low-voltage regulation (REBT, ITC-BT-10) and distributor standards (E-Redes, Iberdrola). A demo mode (`?demo=1` in the URL) simulates different asset ages to illustrate the data-freshness warnings.

**Author:** Carla Esono Ballesteros · Connected Industry Engineering 4.0, Universidad Francisco de Vitoria · June 2026
