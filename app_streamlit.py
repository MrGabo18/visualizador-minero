import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="Visualizador Minero 3D", layout="wide")
st.title("🔍 Visualizador 3D desde Google Sheets (CSV)")

# URL pública fija del Google Sheets exportado a CSV
url_csv = "https://docs.google.com/spreadsheets/d/1CeNxt3T8Y0ktm8PrvfnbCtAkR1H2LCY4/export?format=csv"

try:
    df = pd.read_csv(url_csv)
    columnas = ["X", "Y", "Z", "Cu", "Clasificación"]
    if not all(col in df.columns for col in columnas):
        st.error(f"❌ El archivo debe contener las columnas: {columnas}")
        st.stop()
    df = df[columnas].dropna()
    df["Clasificación"] = df["Clasificación"].astype(str)
    st.success("✅ Archivo cargado con éxito.")
except Exception as e:
    st.error(f"❌ Error al cargar CSV: {e}")
    st.stop()

cu_min, cu_max = df["Cu"].min(), df["Cu"].max()
categorias = df["Clasificación"].str.lower().unique()
categorias_default = [c for c in categorias if c != "esteril"]

st.sidebar.header("🎛️ Controles")
categorias_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Clasificación:",
    options=[c.capitalize() for c in categorias],
    default=[c.capitalize() for c in categorias_default]
)
categorias_seleccionadas = [c.lower() for c in categorias_seleccionadas]

ley_corte = st.sidebar.slider(
    "Ley de corte mínima (% Cu):",
    min_value=float(cu_min),
    max_value=float(cu_max),
    value=float(cu_min),
    step=0.01
)

df_filtrado = df[
    (df["Clasificación"].str.lower().isin(categorias_seleccionadas)) &
    (df["Cu"] >= ley_corte)
]

def crear_trace(sub_df, nombre):
    texto = [
        f"X: {x}, Y: {y}, Z: {z}, %Cu: {cu:.2f}"
        for x, y, z, cu in zip(sub_df["X"], sub_df["Y"], sub_df["Z"], sub_df["Cu"])
    ]
    return go.Scatter3d(
        x=sub_df["X"], y=sub_df["Y"], z=sub_df["Z"],
        mode="markers",
        text=texto,
        hoverinfo="text",
        marker=dict(
            size=5,
            color=sub_df["Cu"],
            colorscale="plasma",
            cmin=cu_min,
            cmax=cu_max,
            opacity=0.8,
            showscale=True,
            colorbar=dict(title="% Cu")
        ),
        name=nombre
    )

data = []
for cat in categorias_seleccionadas:
    sub_df = df_filtrado[df_filtrado["Clasificación"].str.lower() == cat]
    if not sub_df.empty:
        data.append(crear_trace(sub_df, cat.capitalize()))

layout = go.Layout(
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Z",
        aspectmode="data"
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    height=700
)
fig = go.Figure(data=data, layout=layout)
st.plotly_chart(fig, use_container_width=True)
