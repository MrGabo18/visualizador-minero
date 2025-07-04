import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.title("Visualizador Minero 3D desde GitHub")

url_raw = "https://raw.githubusercontent.com/MrGabo18/visualizador-minero/main/Datos.xlsx"

try:
    df = pd.read_excel(url_raw)

    df["Cu"] = pd.to_numeric(df["Cu"], errors='coerce')
    df = df.dropna(subset=["Cu"])

    required_cols = ["X", "Y", "Z", "Cu"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"El archivo debe tener estas columnas: {required_cols}")
    else:
        cu_min, cu_max = df["Cu"].min(), df["Cu"].max()
        rango_cu = st.slider("Filtra por Ley de Cobre (Cu)", float(cu_min), float(cu_max), (float(cu_min), float(cu_max)))

        df_filtrado = df[(df["Cu"] >= rango_cu[0]) & (df["Cu"] <= rango_cu[1])]

        fig = go.Figure(data=[go.Scatter3d(
            x=df_filtrado["X"],
            y=df_filtrado["Y"],
            z=df_filtrado["Z"],
            mode='markers',
            marker=dict(
                size=5,
                color=df_filtrado["Cu"],
                colorscale='Plasma',
                colorbar=dict(title="Ley Cu"),
                opacity=0.8
            )
        )])

        fig.update_layout(
            scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
            margin=dict(l=0, r=0, b=0, t=40),
            height=700,
            title="Bloques Mineros coloreados por Ley de Cobre"
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar o procesar el archivo: {e}")
