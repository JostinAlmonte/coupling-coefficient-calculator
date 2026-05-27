import streamlit as st
import numpy as np
import sympy as sp
import cmath

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
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-left: 5px solid #4f8ef7;
    border-radius: 10px;
    padding: 16px 24px;
    margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.result-label {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 4px;
}
.result-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
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

    # --- Solution picking (3-tier priority) ---
    # Tier 1: positive real solution
    # Tier 2: any real solution (negative values — still usable, show warning)
    # Tier 3: complex/imaginary solution — show flagged result
    Llk_val, ne_val = None, None
    result_type = "normal"  # "normal" | "negative" | "imaginary"

    for sol in solution:
        llk_num = complex(sp.N(sol[0]))
        ne_num  = complex(sp.N(sol[1]))
        if (llk_num.real > 0 and abs(llk_num.imag) < 1e-6
                and ne_num.real > 0 and abs(ne_num.imag) < 1e-6):
            Llk_val = llk_num
            ne_val  = ne_num
            result_type = "normal"
            break

    if Llk_val is None:
        for sol in solution:
            llk_num = complex(sp.N(sol[0]))
            ne_num  = complex(sp.N(sol[1]))
            if abs(llk_num.imag) < 1e-6 and abs(ne_num.imag) < 1e-6:
                Llk_val = llk_num
                ne_val  = ne_num
                result_type = "negative"
                break

    if Llk_val is None and solution:
        llk_num = complex(sp.N(solution[0][0]))
        ne_num  = complex(sp.N(solution[0][1]))
        Llk_val = llk_num
        ne_val  = ne_num
        result_type = "imaginary"

    if Llk_val is None:
        st.error("❌ No solution found. Please check your input values.")
        st.stop()

    # Helper: format a complex number for display
    def fmt_val(val, decimals=2):
        if abs(val.imag) > 1e-6:
            sign = "+" if val.imag >= 0 else "−"
            return f"{val.real:.{decimals}f} {sign} {abs(val.imag):.{decimals}f}j"
        return f"{val.real:.{decimals}f}"

    # Build inductance matrix (using complex arithmetic throughout)
    L11 = complex(Lopsec)
    L12 = ne_val * Lmag
    L21 = ne_val * Lmag
    L22 = ne_val**2 * (Lmag + Llk_val)
    denom = cmath.sqrt(L11 * L22)
    coupling = L12 / denom if abs(denom) > 1e-12 else complex(0)

    # --- Results ---
    st.subheader("📤 Results")

    # Banner for non-normal results
    if result_type == "negative":
        st.warning("⚠️ No positive solution found — negative values returned. Results may not be physically meaningful.")
    elif result_type == "imaginary":
        st.warning("⚠️ Solution contains imaginary components. Results are shown with complex notation.")

    # Imaginary tag for labels
    imag_tag = ' &nbsp;<span style="font-size:11px;background:#fef3c7;color:#92400e;border-radius:4px;padding:2px 6px;font-weight:700;">IMAGINARY</span>' if result_type == "imaginary" else ""

    st.markdown(f"""
    <div class="result-card">
        <div class="result-label">Lmag (nH)</div>
        <div class="result-value">{Lmag:.2f} nH</div>
    </div>
    <div class="result-card">
        <div class="result-label">Llk — Leakage Inductance (nH){imag_tag}</div>
        <div class="result-value">{fmt_val(Llk_val, 2)} nH</div>
    </div>
    <div class="result-card">
        <div class="result-label">ne — Turns Ratio{imag_tag}</div>
        <div class="result-value">{fmt_val(ne_val, 6)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Coupling coefficient with color indicator
    st.subheader("🔗 Coupling Coefficient  k")

    k_is_imaginary = abs(coupling.imag) > 1e-6
    k_display      = fmt_val(coupling, 6)
    k_real         = coupling.real
    k_pct          = abs(coupling) * 100  # use magnitude for progress bar

    if k_is_imaginary:
        k_color  = "#7c3aed"
        k_status = "Imaginary Result 🔮"
        bar_pct  = min(k_pct, 100)
    elif k_real >= 0.9:
        k_color  = "#4caf50"
        k_status = "Tight Coupling ✅"
        bar_pct  = k_real * 100
    elif k_real >= 0.5:
        k_color  = "#f0a500"
        k_status = "Moderate Coupling ⚠️"
        bar_pct  = k_real * 100
    else:
        k_color  = "#e05c5c"
        k_status = "Loose Coupling ❌"
        bar_pct  = max(k_real * 100, 0)

    k_pct_label = f"{coupling.real * 100:.2f}%" if not k_is_imaginary else f"|k| = {abs(coupling):.4f}"

    st.markdown(f"""
    <div class="result-card" style="border-left-color: {k_color};">
        <div class="result-label">Coupling Coefficient k</div>
        <div class="result-value" style="color: {k_color};">{k_display}</div>
        <div style="margin-top: 6px; font-size: 13px; color: {k_color}; font-weight: 600;">
            {k_pct_label} &nbsp;—&nbsp; {k_status}
        </div>
        <div style="margin-top: 12px; background: #e5e7eb; border-radius: 6px; height: 8px;">
            <div style="width: {min(bar_pct, 100):.2f}%; background: {k_color};
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
        "Col 1": [fmt_val(L11, 4), fmt_val(L21, 4)],
        "Col 2": [fmt_val(L12, 4), fmt_val(L22, 4)],
    })

    st.divider()

    # All solutions
    with st.expander("🔍 All Symbolic Solutions"):
        for i, sol in enumerate(solution):
            st.write(f"**Solution {i+1}:** Llk = `{sp.N(sol[0], 6)}`,  ne = `{sp.N(sol[1], 6)}`")
