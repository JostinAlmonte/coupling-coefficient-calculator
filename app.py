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

# --- Global Styles ---
st.markdown("""
<style>
.result-card {
    background-color: #1e1e2e;
    border: 1px solid #3a3a5c;
    border-left: 5px solid #4f8ef7;
    border-radius: 10px;
    padding: 16px 24px;
    margin-bottom: 14px;
}
.result-label {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9a9abf;
    margin-bottom: 4px;
}
.result-value {
    font-size: 28px;
    font-weight: 700;
    color: #e8e8f0;
    letter-spacing: 0.02em;
}
</style>
""", unsafe_allow_html=True)

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

    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">Lmag (nH)</div>
        <div class="result-value">{Lmag:.2f} nH</div>
    </div>
    <div class="result-card">
        <div class="result-label">Llk — Leakage Inductance (nH)</div>
        <div class="result-value">{Llk_val:.2f} nH</div>
    </div>
    <div class="result-card">
        <div class="result-label">ne — Turns Ratio</div>
        <div class="result-value">{ne_val:.6f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Coupling coefficient with color indicator
    st.subheader("🔗 Coupling Coefficient  k")
    k_pct = coupling * 100

    if coupling >= 0.9:
        k_color  = "#4caf50"
        k_status = "Tight Coupling ✅"
    elif coupling >= 0.5:
        k_color  = "#f0a500"
        k_status = "Moderate Coupling ⚠️"
    else:
        k_color  = "#e05c5c"
        k_status = "Loose Coupling ❌"

    st.markdown(f"""
    <div class="result-card" style="border-left-color: {k_color};">
        <div class="result-label">Coupling Coefficient k</div>
        <div class="result-value" style="color: {k_color};">{coupling:.6f}</div>
        <div style="margin-top: 6px; font-size: 13px; color: {k_color}; font-weight: 600;">
            {k_pct:.2f}% &nbsp;—&nbsp; {k_status}
        </div>
        <div style="margin-top: 12px; background: #3a3a5c; border-radius: 6px; height: 8px;">
            <div style="width: {k_pct:.2f}%; background: {k_color};
                        height: 8px; border-radius: 6px; transition: width 0.4s ease;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
