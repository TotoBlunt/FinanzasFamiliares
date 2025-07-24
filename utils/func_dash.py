import pandas as pd
import streamlit as st
import plotly.express as px

def aplicar_filtros(df, persona, fechas, categorias):
    """Filtra el DataFrame según las selecciones del usuario."""
    df_filtrado = df.copy()
    
    # Filtro de fecha
    if len(fechas) == 2:
        fecha_inicio, fecha_fin = pd.to_datetime(fechas[0]), pd.to_datetime(fechas[1])
        df_filtrado = df_filtrado[(df_filtrado['Fecha'] >= fecha_inicio) & (df_filtrado['Fecha'] <= fecha_fin)]

    # Filtro de persona
    if persona != "Ambos":
        df_filtrado = df_filtrado[df_filtrado['Persona'] == persona]

    # Filtro de categoría
    if "Todas" not in categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]
        
    return df_filtrado

def mostrar_metricas_clave(df):
    """Muestra las métricas principales (KPIs) del DataFrame filtrado."""
    st.subheader("Resumen del Período Seleccionado")
    total_gastado = df['Monto'].sum()
    num_transacciones = len(df)
    gasto_promedio = df['Monto'].mean() if num_transacciones > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total", f"S/{total_gastado:,.2f}")
    col2.metric("Nº de Transacciones", f"{num_transacciones}")
    col3.metric("Gasto Promedio", f"S/{gasto_promedio:,.2f}")
    st.markdown("---")
    
def graficar_distribucion_categoria(df):
    """Muestra un gráfico de torta con la distribución de gastos por categoría."""
    st.write("#### ¿En qué estamos gastando más?")
    gastos_por_categoria = df.groupby('Categoria')['Monto'].sum().sort_values(ascending=False)
    
    if not gastos_por_categoria.empty:
        fig = px.pie(
            gastos_por_categoria, 
            values=gastos_por_categoria.values, 
            names=gastos_por_categoria.index, 
            title="Proporción de Gasto por Categoría"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar en este gráfico.")
        
def graficar_evolucion_temporal(df):
    """Muestra un gráfico de líneas con la evolución de los gastos en el tiempo."""
    st.write("#### ¿Cómo han variado nuestros gastos día a día?")
    gastos_diarios = df.groupby(df['Fecha'].dt.date)['Monto'].sum()
    
    if not gastos_diarios.empty:
        fig = px.line(
            gastos_diarios, 
            x=gastos_diarios.index, 
            y=gastos_diarios.values, 
            title="Evolución de Gastos Diarios",
            labels={'x': 'Fecha', 'y': 'Monto Gastado'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar en este gráfico.")
        
def graficar_comparativa_persona(df):
    """Muestra un gráfico de barras comparando los gastos por persona."""
    st.write("#### ¿Quién ha gastado más en este período?")
    gastos_por_persona = df.groupby('Persona')['Monto'].sum().sort_values(ascending=False)
    
    if not gastos_por_persona.empty:
        fig = px.bar(
            gastos_por_persona, 
            x=gastos_por_persona.index, 
            y=gastos_por_persona.values, 
            title="Gasto Total por Persona",
            labels={'x': 'Persona', 'y': 'Monto Total Gastado'},
            text=gastos_por_persona.values,
            color=gastos_por_persona.index
        )
        fig.update_traces(texttemplate='S/%{text:.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar en este gráfico.")
        
def graficar_detalle_subcategoria(df):
    """Muestra un treemap con el desglose de gastos por categoría y subcategoría."""
    st.write("#### Desglose por Subcategoría")
    df_subcat = df[df['Subcategoria'].notna() & (df['Subcategoria'] != '')].copy()

    if not df_subcat.empty:
        gastos_por_subcat = df_subcat.groupby(['Categoria', 'Subcategoria'])['Monto'].sum().reset_index()
        fig = px.treemap(
            gastos_por_subcat,
            path=[px.Constant("Todos los Gastos"), 'Categoria', 'Subcategoria'],
            values='Monto',
            title='Gastos por Categoría y Subcategoría'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos con subcategorías para los filtros seleccionados.")

def mostrar_tabla_detallada(df):
    """Muestra una tabla con todos los gastos del período seleccionado."""
    st.write("#### Todos los gastos del período seleccionado")
    df_display = df[['Fecha', 'Descripcion', 'Categoria', 'Subcategoria', 'Monto', 'Persona']].copy()
    df_display['Monto'] = df_display['Monto'].map('${:,.2f}'.format)
    df_display['Fecha'] = df_display['Fecha'].dt.strftime('%Y-%m-%d')
    st.dataframe(df_display.sort_values(by="Fecha", ascending=False), use_container_width=True)