import streamlit as st
import pandas as pd
import os
import re

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Autopartes Ramos",
    layout="wide"
)

# ---------------- ESTILOS ----------------
st.markdown("""
<style>
body {
    background-color: #f5f5f5;
}

input {
    background-color: #ffffff !important;
    color: #000000 !important;
}

input::placeholder {
    color: #777777 !important;
}

h1, h2, h3 {
    color: #b30000;
}

.precio-venta {
    font-size: 22px;
    font-weight: bold;
    color: #b30000;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=130)

with col2:
    st.markdown("## 🔧 Buscador y comparador de proveedores")

st.divider()

# ---------------- FUNCION NORMALIZAR ----------------
def normalizar(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

# ---------------- CARGA DE PROVEEDORES ----------------
carpeta = "proveedores"
dataframes = []

for archivo in os.listdir(carpeta):
    if archivo.endswith(".xlsx") and not archivo.startswith("~$"):
        ruta = os.path.join(carpeta, archivo)
        df = pd.read_excel(ruta)
        df.columns = df.columns.str.lower()
        df["proveedor"] = archivo.replace(".xlsx", "")

        # columnas normalizadas
        df["desc_norm"] = df["descripcion"].apply(normalizar)
        df["cod_norm"] = df["codigo"].apply(normalizar)

        dataframes.append(df)

catalogo = pd.concat(dataframes, ignore_index=True)

# ---------------- BUSCADOR ----------------
busqueda = st.text_input(
    "🔍 Buscar por descripción o código",
    placeholder="Ej: DUNA | B.F.DC | 51443 | BOMBA FRENO"
)

# ---------------- RESULTADOS ----------------
if busqueda:
    q = normalizar(busqueda)

    resultado = catalogo[
        catalogo["desc_norm"].str.contains(q, na=False) |
        catalogo["cod_norm"].str.contains(q, na=False)
    ]

    if resultado.empty:
        st.warning("No se encontraron resultados")
    else:
        resultado = resultado.sort_values(by="venta")

        mostrar = resultado[[
            "proveedor",
            "codigo",
            "descripcion",
            "costo",
            "venta"
        ]]

        st.dataframe(mostrar, use_container_width=True, hide_index=True)

        mejor = mostrar.iloc[0]

        st.markdown(
            f"""
            ### 💰 Mejor opción
            **Proveedor:** {mejor['proveedor']}  
            **Descripción:** {mejor['descripcion']}  
            **Código:** {mejor['codigo']}  
            **Precio venta:** <span class="precio-venta">${mejor['venta']:,.0f}</span>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("👆 Escribí parte del código o descripción")
