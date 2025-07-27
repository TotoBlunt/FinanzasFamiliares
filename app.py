import streamlit as st
from utils.conn_Gsheet import conexion_gsheet_produccion, abrir_hoja, cargar_datos
from utils.add_informacion import ingresar_gasto,eliminar_gasto
from utils.func_dash import aplicar_filtros, mostrar_metricas_clave, graficar_distribucion_categoria, graficar_evolucion_temporal
from utils.func_dash import graficar_comparativa_persona, graficar_detalle_subcategoria, mostrar_tabla_detallada

# --- CONEXIÓN A GOOGLE SHEETS ---
client = conexion_gsheet_produccion()  # Establece la conexión con Google Sheets
worksheet = abrir_hoja(client)  # Abre la hoja de cálculo específica
# --- INTERFAZ DE USUARIO DE STREAMLIT ---
st.set_page_config(page_title="Gestor de Finanzas", layout="wide")
st.title("Nuestro Gestor de Finanzas  Familiares 📊")

# --- Formulario para añadir gastos ---
with st.form("entry_form_1", clear_on_submit=True):
    st.header("Añadir un nuevo gasto")

    # Definir categorías y personas
    CATEGORIAS = ["Comida", "Hogar", "Transporte", "Ocio", "Salud", "Ropa y Calzado", "Tecnología", "Otro"] 
    PERSONAS = ["Milagros Valladolid", "Jose Longa"] # Lista de personas que pueden registrar gastos
    TIPOS_GASTO = ["Fijo Mensual", "Variable Diario", "Ocasional", "Ahorro/Inversión", "Deuda"]
    
    # Usaremos columnas para organizar mejor el formulario
    col1, col2 = st.columns(2)

    with col1:
        fecha_gasto = st.date_input("Fecha")
        descripcion_gasto = st.text_input("Descripción (Obligatorio)", placeholder="En que gastaste el dinero?")
        categoria_gasto = st.selectbox("Categoría", CATEGORIAS)
        # NUEVO CAMPO: Subcategoría
        subcategoria_gasto = st.text_input("Subcategoría (Opcional)", placeholder="Ej: Supermercado, Gasolina, Netflix")

    with col2:
        monto_gasto = st.number_input("Monto (Obligatorio)", min_value=0.01, format="%.2f", placeholder="")
        persona_gasto = st.radio("Pagado por", PERSONAS)
        # NUEVO CAMPO: Tipo de Gasto
        tipo_gasto_seleccionado = st.selectbox("Tipo de Gasto", TIPOS_GASTO)
    
    # NUEVO CAMPO: Notas (debajo de las columnas para que ocupe todo el ancho)
    notas_gasto = st.text_area("Notas (Opcional)", placeholder="Añade cualquier detalle extra aquí")
    
    submitted = st.form_submit_button("✅ Agregar Gasto")


# --- Lógica de envío actualizada ---
if submitted:
    # Llamamos a nuestra función actualizada, pasándole TODOS los datos del formulario
    exito, mensaje = ingresar_gasto(
        worksheet=worksheet,
        fecha=fecha_gasto,
        monto=monto_gasto,
        descripcion=descripcion_gasto,
        persona=persona_gasto,
        categoria=categoria_gasto,
        subcategoria=subcategoria_gasto,      # <-- NUEVO
        tipo_gasto=tipo_gasto_seleccionado,  # <-- NUEVO
        notas=notas_gasto                    # <-- NUEVO
    )
    
    # Mostramos el mensaje de éxito o error
    if exito:
        st.success(mensaje)
    else:
        st.error(mensaje)

# --- INICIO DEL DASHBOARD ---
st.header("Análisis y Visualización de Gastos 📈")

# Cargar los datos una sola vez
df_original = cargar_datos(worksheet)

if df_original.empty:
    st.info("Aún no hay datos para mostrar. ¡Agrega tu primer gasto para comenzar!")
    st.stop()

# --- Configurar filtros en la barra lateral (esto no cambia) ---
st.sidebar.header("Filtros del Dashboard")
persona_sel = st.sidebar.selectbox("Filtrar por Persona:", ["Ambos"] + list(df_original['Persona'].unique()))
fecha_sel = st.sidebar.date_input(
    "Filtrar por Rango de Fechas:",
    value=(df_original['Fecha'].min().date(), df_original['Fecha'].max().date()),
    min_value=df_original['Fecha'].min().date(),
    max_value=df_original['Fecha'].max().date()
)
categoria_sel = st.sidebar.multiselect(
    "Filtrar por Categoría:",
    options=["Todas"] + list(df_original['Categoria'].unique()),
    default="Todas"
)

# Aplicar los filtros
df_filtrado = aplicar_filtros(df_original, persona_sel, fecha_sel, categoria_sel)

# --- INICIO DEL NUEVO LAYOUT DEL DASHBOARD ---
if df_filtrado.empty:
    st.warning("No se encontraron datos para los filtros seleccionados.")
else:
    # --- SECCIÓN 1: RESUMEN GENERAL (KPIs) ---
    mostrar_metricas_clave(df_filtrado)

    # --- SECCIÓN 2: VISUALIZACIONES CLAVE (LADO A LADO) ---
    st.subheader("Visión General de Gastos")
    col1, col2 = st.columns(2)

    # --- SECCIÓN 3: ANÁLISIS DETALLADO (EN PESTAÑAS) ---
    st.subheader("Análisis y Gestión")
    
    with col1:
        # Llamamos a la función del gráfico de torta
        graficar_distribucion_categoria(df_filtrado)
    
    with col2:
        # Llamamos a la función del gráfico de líneas
        graficar_evolucion_temporal(df_filtrado)

    st.markdown("---") # Separador visual

    # --- SECCIÓN 3: ANÁLISIS DETALLADO (EN PESTAÑAS) ---
    st.subheader("Análisis Detallado")
    
    tab1, tab2, tab3, tab4= st.tabs([
        "👥 Comparativa por Persona", 
        "🌳 Detalle por Subcategoría", 
        "📄 Tabla de Datos",
         "⚙️ Gestionar Gastos"
    ])

    with tab1:
        # Llamamos a la función del gráfico de barras por persona
        graficar_comparativa_persona(df_filtrado)

    with tab2:
        # Llamamos a la función del treemap de subcategorías
        graficar_detalle_subcategoria(df_filtrado)

    with tab3:
        # Llamamos a la función que muestra la tabla de datos
        mostrar_tabla_detallada(df_filtrado)

    with tab4: # <-- LÓGICA DE LA NUEVA PESTAÑA
        st.write("#### Eliminar un gasto registrado")
        st.warning("⚠️ ¡Atención! La eliminación de un gasto es permanente.", icon="🔥")

        # Mostramos los 15 gastos más recientes del DataFrame filtrado
        gastos_recientes = df_filtrado.sort_values(by="Fecha", ascending=False).head(15)
        
        if gastos_recientes.empty:
            st.info("No hay gastos para mostrar según los filtros actuales.")
        else:
            for index, row in gastos_recientes.iterrows():
                # Creamos un contenedor para cada gasto para una mejor organización visual
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1.5])
                    
                    with col1:
                        st.text(f"📝 {row['Descripcion']}")
                        st.caption(f"📅 {row['Fecha'].strftime('%d/%m/%Y')} | 👤 {row['Persona']}")
                    
                    with col2:
                        st.text(f"💵 ${row['Monto']:.2f}")
                        st.caption(f"🔖 {row['Categoria']}")
                    
                    with col3:
                        # Usamos un expander como paso de confirmación
                        with st.expander("Eliminar"):
                            # El botón de confirmación necesita una clave única
                            if st.button("🚨 Confirmar Eliminación", key=f"del_{row['ID_Gasto']}"):
                                exito, mensaje = eliminar_gasto(worksheet, row['ID_Gasto'])
                                
                                if exito:
                                    st.success(mensaje)
                                    # Forzamos un re-run de la app para que la lista se actualice
                                    st.experimental_rerun()
                                else:
                                    st.error(mensaje)
                    st.markdown("---")