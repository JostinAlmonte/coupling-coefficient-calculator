## Transformer Cantilever Model - Coupling Coefficient Calculator
# sec = Rx (receiver)
# pri = Tx (transmitter)
# units: nH

import numpy as np
import sympy as sp

# --- Input Measurements (nH) ---
Lopsec = 1181
Lscsec = 1176
Lscpri = 1255

Lmag = Lopsec
print(f"Lmag = {Lmag} nH")

# --- Solve for leakage inductance (Llk) and turns ratio (ne) ---
# Equations from cantilever model:
#   Lmag * Llk / (Lmag + Llk) = Lscsec
#   Llk * ne^2 = Lscpri

Llk, ne = sp.symbols("Llk ne")

eqns = [
    sp.Eq(Lmag * Llk / (Lmag + Llk), Lscsec),
    sp.Eq(Llk * ne**2, Lscpri),
]

solution = sp.solve(eqns, [Llk, ne])

print(f"\nAll solutions for (Llk, ne):")
for i, sol in enumerate(solution):
    print(f"  Solution {i+1}: Llk = {sp.N(sol[0], 6)}, ne = {sp.N(sol[1], 6)}")

# Use the positive real solution (matching MATLAB's ne(2))
Llk_val, ne_val = None, None
for sol in solution:
    llk_num = complex(sp.N(sol[0]))
    ne_num  = complex(sp.N(sol[1]))
    if llk_num.real > 0 and abs(llk_num.imag) < 1e-6 and ne_num.real > 0 and abs(ne_num.imag) < 1e-6:
        Llk_val = float(llk_num.real)
        ne_val  = float(ne_num.real)
        break

if Llk_val is None:
    raise ValueError("No positive real solution found. Check input measurements.")

print(f"\nSelected solution:")
print(f"  Llk = {Llk_val:.6f} nH")
print(f"  ne  = {ne_val:.6f}")

# --- Build Inductance Matrix ---
L11 = Lopsec
L12 = ne_val * Lmag
L21 = ne_val * Lmag
L22 = ne_val**2 * (Lmag + Llk_val)

X = np.array([[L11, L12],
              [L21, L22]])

print(f"\nInductance Matrix X (nH):")
print(X)

# --- Coupling Coefficient ---
coupling = L12 / np.sqrt(L11 * L22)

print(f"\nCoupling Coefficient k = {coupling:.6f}")
