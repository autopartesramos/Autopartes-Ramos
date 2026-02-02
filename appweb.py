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

.card {
    background-color: #ffffff;
    padding: 12px;
    border-radius: 10px;
    box-shadow: 0 0 6px rgba(0,0,0,0.1);
    margin-bottom: 15px;
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

        if "descripcion" not in df.columns:
            df["descripcion"] = ""
        if "codigo" not in df.columns:
            df["codigo"] = ""
        if "costo" not in df.columns:
            df["costo"] = 0
        if "venta" not in df.columns:
            df["venta"] = 0

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
        ]].copy()

        mostrar["costo"] = mostrar["costo"].fillna(0).astype(int)
        mostrar["venta"] = mostrar["venta"].fillna(0).astype(int)

        st.dataframe(mostrar, use_container_width=True, hide_index=True)

        st.subheader("📦 Resultados con imagen")

        carpeta_img = "imagenes"

        for _, fila in mostrar.iterrows():
            ruta_img = None
            if os.path.exists(carpeta_img):
                for ext in ["jpg", "png", "jpeg", "webp"]:
                    posible = os.path.join(carpeta_img, f"{fila['codigo']}.{ext}")
                    if os.path.exists(posible):
                        ruta_img = posible
                        break

            col_img, col_txt = st.columns([1, 3])

            with col_img:
                if ruta_img:
                    st.image(ruta_img, use_container_width=True)
                else:
                    st.caption("Sin imagen")

            with col_txt:
                st.markdown(
                    f"""
                    <div class="card">
                    <b>Proveedor:</b> {fila['proveedor']}<br>
                    <b>Código:</b> {fila['codigo']}<br>
                    <b>Descripción:</b> {fila['descripcion']}<br>
                    <b>Venta:</b> <span class="precio-venta">${fila['venta']:,}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # ---------------- MEJOR OPCION ----------------
        mejor = mostrar.iloc[0]

        ruta_img = None
        if os.path.exists(carpeta_img):
            for ext in ["jpg", "png", "jpeg", "webp"]:
                posible = os.path.join(carpeta_img, f"{mejor['codigo']}.{ext}")
                if os.path.exists(posible):
                    ruta_img = posible
                    break

        st.divider()
        st.subheader("🏆 Mejor opción")

        col_img, col_info = st.columns([1, 2])

        with col_img:
            if ruta_img:
                st.image(ruta_img, use_container_width=True)
            else:
                st.caption("Sin imagen disponible")

        with col_info:
            st.markdown(
                f"""
                **Proveedor:** {mejor['proveedor']}  
                **Descripción:** {mejor['descripcion']}  
                **Código:** {mejor['codigo']}  
                **Precio venta:** <span class="precio-venta">${mejor['venta']:,}</span>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("👆 Escribí parte del código o descripción")
