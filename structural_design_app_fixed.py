
import streamlit as st
import math

st.set_page_config(layout="wide")
st.title("🧠 Structural Design Assistant – Beam, Column, Slab & Foundation")

tab1, tab2, tab3, tab4 = st.tabs(["🏗 Beam", "🏛 Column", "🧱 Slab", "🦶 Foundation"])

# Beam Design
with tab1:
    st.header("🏗 Beam Design")
    span = st.number_input("Beam Span (m)", value=4.0, key="beam_span")
    width = st.number_input("Beam Width (mm)", value=300, key="beam_width")
    depth = st.number_input("Beam Depth (mm)", value=500, key="beam_depth")
    cover = st.number_input("Clear Cover (mm)", value=25, key="beam_cover")
    fck = st.selectbox("Concrete Grade (fck)", [20, 25, 30], index=1, key="beam_fck")
    fy = st.selectbox("Steel Grade (fy)", [415, 500], index=1, key="beam_fy")
    support_type = st.selectbox("Support Type", ["Simply Supported", "Fixed"], key="beam_support")
    load_type = st.selectbox("Load Type", ["UDL (kN/m)", "Point Load at Midspan (kN)"], key="beam_load_type")

    if load_type == "UDL (kN/m)":
        w = st.number_input("Uniform Load w (kN/m)", value=20.0, key="beam_udl")
        factored_load = 1.5 * w
        Mu = (factored_load * span ** 2) / (8 if support_type == "Simply Supported" else 12)
        Vu = (factored_load * span) / 2
    else:
        P = st.number_input("Point Load P (kN)", value=40.0, key="beam_point")
        factored_P = 1.5 * P
        Mu = (factored_P * span) / 4
        Vu = factored_P / 2

    d = depth - cover
    Mu_Nmm = Mu * 1e6
    Ast = Mu_Nmm / (0.87 * fy * 0.9 * d)
    Ast = round(Ast, 2)
    bar_dia = 16
    bar_area = (math.pi / 4) * bar_dia**2
    num_bars = math.ceil(Ast / bar_area)
    Ast_provided = num_bars * bar_area
    tau_v = (Vu * 1e3) / (width * d)
    tau_c = 0.36 * math.sqrt(fck)
    span_mm = span * 1000
    span_d_ratio = span_mm / d
    limit = 20 if support_type == "Simply Supported" else 10

    st.subheader("📐 Beam Results")
    st.write(f"Mu = {Mu:.2f} kNm, Vu = {Vu:.2f} kN, d = {d} mm")
    st.write(f"Ast = {Ast} mm² → {num_bars} bars of {bar_dia} mm (Ast_prov = {Ast_provided:.2f})")
    st.write(f"τ_v = {tau_v:.2f} MPa vs τ_c = {tau_c:.2f} MPa")
    st.success("✅ Shear OK" if tau_v <= tau_c else "❌ Shear FAIL")
    st.write(f"Span/d = {span_d_ratio:.2f} (limit {limit})")
    st.success("✅ Deflection OK" if span_d_ratio <= limit else "❌ Deflection FAIL")
    if tau_v <= tau_c and span_d_ratio <= limit:
        st.success("✅ BEAM Design OK")

# Column Design
with tab2:
    st.header("🏛 Column Design")
    b = st.number_input("Column Width (mm)", value=300, key="col_width")
    D = st.number_input("Column Depth (mm)", value=400, key="col_depth")
    cover_col = st.number_input("Clear Cover (mm)", value=40, key="col_cover")
    Pu = st.number_input("Axial Load (kN)", value=1000.0, key="col_Pu")
    Mux = st.number_input("Moment about X-axis (kNm)", value=60.0, key="col_Mux")
    Muy = st.number_input("Moment about Y-axis (kNm)", value=40.0, key="col_Muy")
    fck_col = st.selectbox("Concrete Grade (fck)", [20, 25, 30], index=1, key="col_fck")
    fy_col = st.selectbox("Steel Grade (fy)", [415, 500], index=1, key="col_fy")
    Ac = b * D
    d_eff_x = D - cover_col
    d_eff_y = b - cover_col
    Mux1 = 0.138 * fck_col * b * (d_eff_x ** 2) / 1e6
    Muy1 = 0.138 * fck_col * D * (d_eff_y ** 2) / 1e6
    Ast_min = 0.008 * Ac
    Puz = 0.4 * fck_col * Ac + 0.67 * fy_col * Ast_min
    interaction = (Pu * 1e3 / Puz) + (Mux / Mux1) + (Muy / Muy1)
    interaction = round(interaction, 3)

    st.subheader("📐 Column Results")
    st.write(f"Min Ast = {Ast_min:.2f} mm²")
    st.write(f"Puz = {Puz:.2f} N, Interaction = {interaction:.3f}")
    st.success("✅ Column OK" if interaction <= 1.0 else "❌ Column FAIL")

# Foundation Design
with tab4:
    st.header("🦶 Foundation Design")
    Pu = st.number_input("Column Load (kN)", value=800.0, key="found_Pu")
    SBC = st.number_input("Soil Bearing Capacity (kN/m²)", value=200.0, key="found_SBC")
    fck = st.selectbox("Concrete Grade (fck)", [20, 25, 30], index=1, key="found_fck")
    fy = st.selectbox("Steel Grade (fy)", [415, 500], index=1, key="found_fy")
    col_b = st.number_input("Column Width (mm)", value=300, key="found_col_width")
    thickness = st.number_input("Footing Thickness (mm)", value=500, key="found_thick")
    cover = 50
    FS = 1.5
    A_req = Pu / (SBC / FS)
    B = round(math.sqrt(A_req), 2)
    d = thickness - cover
    q = Pu / (B ** 2)
    Mu = q * ((B - col_b / 1000) / 2) ** 2 / 2
    Ast = (Mu * 1e6) / (0.87 * fy * 0.9 * d)
    bar_dia = 16
    bar_area = (math.pi / 4) * bar_dia**2
    spacing = int((bar_area * 1000) / Ast)
    tau_v = (q * (B - (col_b / 1000 + d / 1000))) / d
    tau_c = 0.36 * math.sqrt(fck)

    st.subheader("📐 Foundation Results")
    st.write(f"Provide footing of {B:.2f} m × {B:.2f} m")
    st.write(f"Net Pressure = {q:.2f} kN/m²")
    st.write(f"Mu = {Mu:.2f} kNm → Ast = {Ast:.2f} mm²/m → 16 mm @ {spacing} mm")
    st.write(f"τ_v = {tau_v:.2f} MPa vs τ_c = {tau_c:.2f} MPa")
    if tau_v <= tau_c:
        st.success("✅ Foundation Design OK")
    else:
        st.error("❌ Shear Check Failed – Increase depth or area")
