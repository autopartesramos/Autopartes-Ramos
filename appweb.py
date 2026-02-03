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
    if archivo.endswith((".xlsx", ".xls")) and not archivo.startswith("~$"):
        ruta = os.path.join(carpeta, archivo)

        df = pd.read_excel(ruta)
        df.columns = df.columns.str.lower()
        df["proveedor"] = archivo.rsplit(".", 1)[0]

        df["descripcion"] = df.get("descripcion", "")
        df["codigo"] = df.get("codigo", "")
        df["costo"] = df.get("costo", 0)
        df["venta"] = df.get("venta", 0)

        df["desc_norm"] = df["descripcion"].apply(normalizar)
        df["cod_norm"] = df["codigo"].apply(normalizar)

        dataframes.append(df)

catalogo = pd.concat(dataframes, ignore_index=True)

# ---------------- BUSCADOR ----------------
busqueda = st.text_input(
    "🔍 Buscar por descripción o código",
    placeholder="Ej: b.f. sandero | freno logan | 51443"
)

# ---------------- RESULTADOS ----------------
if busqueda:
    # 🔹 separar palabras ANTES de normalizar
    palabras = re.split(r'\s+', busqueda.lower())

    palabras_norm = [normalizar(p) for p in palabras if p.strip()]

    mask = pd.Series(True, index=catalogo.index)

    for p in palabras_norm:
        mask = mask & (
            catalogo["desc_norm"].str.contains(p, na=False) |
            catalogo["cod_norm"].str.contains(p, na=False)
        )

    resultado = catalogo[mask]

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
        ]].copy()

        mostrar["costo"] = mostrar["costo"].fillna(0).astype(int)
        mostrar["venta"] = mostrar["venta"].fillna(0).astype(int)

        st.dataframe(mostrar, use_container_width=True, hide_index=True)

        mejor = mostrar.iloc[0]

        # ---------------- IMAGEN ----------------
        ruta_img = None
        carpeta_img = "imagenes"

        if os.path.exists(carpeta_img):
            for ext in ["jpg", "png", "jpeg", "webp"]:
                posible = os.path.join(carpeta_img, f"{mejor['codigo']}.{ext}")
                if os.path.exists(posible):
                    ruta_img = posible
                    break

        col_img, col_info = st.columns([1, 2])

        with col_img:
            if ruta_img:
                st.image(ruta_img, use_container_width=True)
            else:
                st.caption("Sin imagen disponible")

        with col_info:
            st.markdown(
                f"""
                ### 💰 Mejor opción
                **Proveedor:** {mejor['proveedor']}  
                **Descripción:** {mejor['descripcion']}  
                **Código:** {mejor['codigo']}  
                **Precio venta:** <span class="precio-venta">${mejor['venta']:,}</span>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("👆 Escribí parte del código o descripción")
