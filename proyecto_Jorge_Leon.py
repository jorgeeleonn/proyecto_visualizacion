import streamlit as st
import pandas as pd
import calendar

#primero vamos a cargar los datos dados con lo estudiado en la asignatura Adquisición de Datos
st.set_page_config(layout="wide", page_title="Dashboard Ventas 2025") #ponemos la página a modo wide para mejor visualización 

df1 = pd.read_csv("parte_1.csv", parse_dates=["date"], low_memory=False)
df2 = pd.read_csv("parte_2.csv", parse_dates=["date"], low_memory=False)
df = pd.concat([df1, df2], ignore_index=True)

num_cols = ["sales","onpromotion","dcoilwtico","cluster","transactions","year","month","week","quarter"]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce") #pasamos los datos a numericos para que sea más cómodo

df = df.dropna(subset=["sales"])#quitamos los valores nulos

st.title("Dashboard Ventas 2025")

p1, p2, p3, p4 = st.tabs(["Situación de Ventas","Información por tienda","Información a nivel estado","Promociones"])#creamos las 4 prestañas

#pestaña1:
with p1:
    st.header("Situación global de las ventas")

    #apartado a)
    st.subheader("Conteo general")#sacamos los datos del dataframe directamente con pandas
    num_tiendas = df["store_nbr"].nunique()
    num_productos = df["family"].nunique()
    num_estados = df["state"].nunique()
    num_meses = df["month"].nunique()

    c1, c2, c3, c4 = st.columns(4) #los "introducimos" en nuestra página
    c1.metric("Nº total de tiendas", num_tiendas)
    c2.metric("Nº total de productos (familias)", num_productos)
    c3.metric("Nº de estados", num_estados)
    c4.metric("Nº de meses con datos", num_meses)


    #apartado b)
    st.subheader("Análisis en términos medios")
    #en este apartado sacamos los datos del dataframe de la misma manera y usamos bar_chart para crear un bar chart y que sea vea muy bien la diferencia de cada uno de los datos
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("**Top 10 productos más vendidos**")
        top_prod = df.groupby("family", as_index=False)["sales"].mean().sort_values("sales", ascending=False).head(10)
        st.bar_chart(top_prod.set_index("family")["sales"])

    with col_b2:
        st.markdown("**Distribución de ventas por tienda**")
        ventas_tienda = df.groupby("store_nbr", as_index=False)["sales"].mean().sort_values("sales", ascending=False)
        st.bar_chart(ventas_tienda.set_index("store_nbr")["sales"])

    st.markdown("---")
    st.markdown("**Top 10 tiendas por venta media en productos en promoción**")
    df_promo = df[df["onpromotion"] > 0]
    if not df_promo.empty:
        top_store_promo = df_promo.groupby("store_nbr", as_index=False)["sales"].mean().sort_values("sales", ascending=False).head(10)
        st.bar_chart(top_store_promo.set_index("store_nbr")["sales"])
    else:
        st.info("No hay registros con productos en promoción.")

    st.markdown("---")

    #apartado c)
    st.subheader("Análisis de la estacionalidad de las ventas")

    st.markdown("**Venta media por día de la semana**")
    ventas_dia = df.groupby("day_of_week", as_index=False)["sales"].mean().sort_values("sales", ascending=False)
    if not ventas_dia.empty:
        mejor_dia = ventas_dia.iloc[0]#como estan ordenados por el sort_values, es simplemente el primero de todos
        st.write(f"El día con mayor venta media es **{mejor_dia['day_of_week']}** con **{mejor_dia['sales']:.2f}** unidades.")
        st.bar_chart(ventas_dia.set_index("day_of_week")["sales"])
    else:
        st.info("No hay datos suficientes por día de la semana.")

    st.markdown("---")
    st.markdown("**Volumen de ventas medio por semana del año**")
    ventas_semana = df.dropna(subset=["week"]).groupby("week", as_index=False)["sales"].mean().sort_values("week")
    if not ventas_semana.empty:
        st.line_chart(ventas_semana.set_index("week")["sales"])#esta vez usamos line chart para poder ver el progreso mejor
    else:
        st.info("No hay datos suficientes.")

    st.markdown("**Volumen de ventas medio por mes**")
    ventas_mes = df.dropna(subset=["month"]).groupby("month", as_index=False)["sales"].mean().sort_values("month")
    if not ventas_mes.empty:
        meses_int = ventas_mes["month"].astype(int)
        nombres_mes_linea = [calendar.month_name[m] for m in meses_int]
        ventas_mes["month_name"] = nombres_mes_linea
        st.line_chart(ventas_mes.set_index("month_name")["sales"])
    else:
        st.info("No hay datos suficientes.")

#pestaña2:
with p2:
    st.header("Información por tienda")

    tiendas = sorted(df["store_nbr"].unique())
    tienda_sel = st.selectbox("Selecciona la tienda", tiendas)#usamos el selectbox para poder elegir que tienda queremos analizar
    df_tienda = df[df["store_nbr"] == tienda_sel]

    st.subheader("Número total de ventas por año")
    ventas_anio_tienda = df_tienda.groupby("year", as_index=False)["sales"].sum().sort_values("year")
    if not ventas_anio_tienda.empty:
        st.bar_chart(ventas_anio_tienda.set_index("year")["sales"])
    else:
        st.info("No hay datos de ventas para esta tienda.")

    st.markdown("---")
    st.subheader("Productos vendidos")
    total_ventas = df_tienda["sales"].sum()
    total_ventas_promo = df_tienda[df_tienda["onpromotion"] > 0]["sales"].sum()
    c1, c2 = st.columns(2)
    c1.metric("Total productos vendidos", f"{total_ventas:,.0f}")
    c2.metric("Productos vendidos en promoción", f"{total_ventas_promo:,.0f}")

#pestaña3:
with p3:
    st.header("Información a nivel estado")

    estados = sorted(df["state"].dropna().unique())
    estado_sel = st.selectbox("Selecciona el estado", estados)#con esto hacemos que podamos elegir el estado que queremos analizar
    df_estado = df[df["state"] == estado_sel]

    st.subheader("Número total de transacciones por año")
    if "transactions" in df_estado.columns:
        trans_anio = df_estado.dropna(subset=["transactions"]).groupby("year", as_index=False)["transactions"].sum().sort_values("year")
        if not trans_anio.empty:
            st.bar_chart(trans_anio.set_index("year")["transactions"])
        else:
            st.info("No hay datos de transacciones para este estado.")
    else:
        st.info("La columna 'transactions' no está en el dataset.")

    st.markdown("---")
    st.subheader(f"Ranking de tiendas con más ventas en {estado_sel}")
    ranking_tiendas_estado = df_estado.groupby("store_nbr", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
    if not ranking_tiendas_estado.empty:
        st.bar_chart(ranking_tiendas_estado.set_index("store_nbr")["sales"])
    else:
        st.info("No hay ventas disponibles para este estado.")

    st.markdown("---")
    st.subheader(f"Producto más vendido en {estado_sel}")
    prod_estado = df_estado.groupby("family", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
    if not prod_estado.empty:
        top_prod_estado = prod_estado.iloc[0]#cogemos el primero porque con el sort_values es el más vendido
        st.write(f"En **{estado_sel}**, el producto (familia) más vendido es **{top_prod_estado['family']}** con **{top_prod_estado['sales']:.0f}** unidades.")
        st.bar_chart(prod_estado.set_index("family")["sales"])
    else:
        st.info("No hay datos de productos para este estado.")

#pestaña4:
with p4:
    st.header("Peso de las promociones por año")

    st.markdown(
        """
        Análisis del **peso de las promociones en las ventas por año**.
        Analizaremos qué parte del negocio depende de las promociones.
        """
    )

    df["es_promo"] = df["onpromotion"] > 0
    resumen_promo = df.groupby(["year","es_promo"], as_index=False)["sales"].sum()
    tabla_promo = resumen_promo.pivot_table(index="year", columns="es_promo", values="sales", fill_value=0)
    tabla_promo.columns = ["No promoción","Promoción"]
    tabla_promo["Total"] = tabla_promo["No promoción"] + tabla_promo["Promoción"]
    tabla_promo["% Promoción"] = 100 * tabla_promo["Promoción"] / tabla_promo["Total"]

    años_disponibles = list(tabla_promo.index)
    año_sel = st.selectbox("Selecciona un año para el detalle", años_disponibles)#damos opción de elegir cualquier año 

    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas totales", f"{tabla_promo.loc[año_sel,'Total']:,.0f}")
    col2.metric("Ventas en promoción", f"{tabla_promo.loc[año_sel,'Promoción']:,.0f}")
    col3.metric("% de ventas en promoción", f"{tabla_promo.loc[año_sel,'% Promoción']:.1f}%")

    st.markdown("---")
    st.subheader("Evolución del % de ventas en promoción")
    st.line_chart(tabla_promo["% Promoción"])

    st.markdown(
        """
        • Un % muy alto puede indicar que se depende demasiado en los descuentos.  
        • Un % muy bajo puede significar que no se aprovechan bien esas promociones.  
        """
    )
