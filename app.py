import streamlit as st
import numpy as np
import sympy as sp

# --- Page Config ---
st.set_page_config(
    page_title="Coupling Coefficient Calculator",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Transformer Coupling Coefficient Calculator")
st.caption("Cantilever (T-circuit) Model  |  sec = Rx  |  pri = Tx")
st.divider()

# --- Input Section ---
st.subheader("📥 Input Measurements (nH)")

col1, col2, col3 = st.columns(3)
with col1:
    Lopsec = st.number_input("Lopsec", min_value=0.0, value=1181.0, step=1.0,
                              help="Open-circuit secondary inductance (nH)")
with col2:
    Lscsec = st.number_input("Lscsec", min_value=0.0, value=1176.0, step=1.0,
                              help="Short-circuit secondary inductance (nH)")
with col3:
    Lscpri = st.number_input("Lscpri", min_value=0.0, value=1255.0, step=1.0,
                              help="Short-circuit primary inductance (nH)")

st.divider()

# --- Calculate Button ---
if st.button("🔢 Calculate", use_container_width=True, type="primary"):

    Lmag = Lopsec

    # Validate inputs
    if Lscsec >= Lopsec:
        st.error("❌ Lscsec must be less than Lopsec for a valid solution.")
        st.stop()

    # Solve symbolically
    Llk_sym, ne_sym = sp.symbols("Llk ne")
    eqns = [
        sp.Eq(Lmag * Llk_sym / (Lmag + Llk_sym), Lscsec),
        sp.Eq(Llk_sym * ne_sym**2, Lscpri),
    ]
    solution = sp.solve(eqns, [Llk_sym, ne_sym])

    # Pick positive real solution
    Llk_val, ne_val = None, None
    for sol in solution:
        llk_num = complex(sp.N(sol[0]))
        ne_num  = complex(sp.N(sol[1]))
        if (llk_num.real > 0 and abs(llk_num.imag) < 1e-6
                and ne_num.real > 0 and abs(ne_num.imag) < 1e-6):
            Llk_val = float(llk_num.real)
            ne_val  = float(ne_num.real)
            break

    if Llk_val is None:
        st.error("❌ No positive real solution found. Please check your input values.")
        st.stop()

    # Build inductance matrix
    L11 = Lopsec
    L12 = ne_val * Lmag
    L21 = ne_val * Lmag
    L22 = ne_val**2 * (Lmag + Llk_val)
    coupling = L12 / np.sqrt(L11 * L22)

    # --- Results ---
    st.subheader("📤 Results")

    r1, r2, r3 = st.columns(3)
    r1.metric("Lmag", f"{Lmag:.2f} nH")
    r2.metric("Llk (Leakage) (nH)", f"{Llk_val:.4f} nH")
    r3.metric("ne (Turns Ratio)", f"{ne_val:.6f}")

    st.divider()

    # Coupling coefficient with color indicator
    st.subheader("🔗 Coupling Coefficient  k")
    k_pct = coupling * 100

    if coupling >= 0.9:
        st.success(f"**k = {coupling:.6f}** ({k_pct:.2f}%)  — Tight coupling ✅")
    elif coupling >= 0.5:
        st.warning(f"**k = {coupling:.6f}** ({k_pct:.2f}%)  — Moderate coupling ⚠️")
    else:
        st.error(f"**k = {coupling:.6f}** ({k_pct:.2f}%)  — Loose coupling ❌")

    st.progress(float(np.clip(coupling, 0, 1)))

    st.divider()

    # Inductance matrix
    st.subheader("🧮 Inductance Matrix (nH)")
    st.table({
        "": ["L11 (sec self)", "L21 (mutual)"],
        "Col 1": [f"{L11:.4f}", f"{L21:.4f}"],
        "Col 2": [f"{L12:.4f}", f"{L22:.4f}"],
    })

    st.divider()

    # All solutions
    with st.expander("🔍 All Symbolic Solutions"):
        for i, sol in enumerate(solution):
            st.write(f"**Solution {i+1}:** Llk = `{sp.N(sol[0], 6)}`,  ne = `{sp.N(sol[1], 6)}`")
