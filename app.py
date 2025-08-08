import streamlit as st
from utils.conn_Gsheet import conexion_gsheet_produccion, abrir_hoja, cargar_datos
from utils.add_informacion import ingresar_gasto,eliminar_gasto,editar_gasto
from utils.func_dash import aplicar_filtros, mostrar_metricas_clave, graficar_distribucion_categoria, graficar_evolucion_temporal
from utils.func_dash import graficar_comparativa_persona, graficar_detalle_subcategoria, mostrar_tabla_detallada
from openai import OpenAI
from utils.func_openai import sugerir_categoria_ia,generar_resumen_ia

#--- INICIALIZAR CLIENTES ---
#Cliente de OpenAI
try:
    client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    # Si la clave no está, no rompemos la app, solo la funcionalidad de IA no estará disponible.
    client_openai = None

#--- CONEXIÓN A GOOGLE SHEETS ---
client = conexion_gsheet_produccion()  # Establece la conexión con Google Sheets
worksheet = abrir_hoja(client)  # Abre la hoja de cálculo específica

#--- INTERFAZ DE USUARIO DE STREAMLIT ---
st.set_page_config(page_title="Gestor de Finanzas", layout="wide")
st.title("Nuestro Gestor de Finanzas  Familiares 📊")
#--- Formulario para añadir gastos ---
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
#--- Lógica de envío actualizada ---
if submitted:
    # Llamamos a nuestra función actualizada, pasándole TODOS los datos del formulario
    exito, mensaje = ingresar_gasto(
    worksheet=worksheet,
    fecha=fecha_gasto,
    monto=monto_gasto,
    descripcion=descripcion_gasto,
    persona=persona_gasto,
    categoria=categoria_gasto,
    subcategoria=subcategoria_gasto,
    tipo_gasto=tipo_gasto_seleccionado,
    notas=notas_gasto
    )

# Mostramos el mensaje de éxito o error
if exito:
    st.success(mensaje)
else:
    st.error(mensaje)

#--- INICIO DEL DASHBOARD ---
st.header("Análisis y Visualización de Gastos 📈")
Cargar los datos una sola vez
df_original = cargar_datos(worksheet)
if df_original.empty:
    st.info("Aún no hay datos para mostrar. ¡Agrega tu primer gasto para comenzar!")
    st.stop()
#--- Configurar filtros en la barra lateral (esto no cambia) ---
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
#--- INICIO DEL NUEVO LAYOUT DEL DASHBOARD ---
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
        st.header("Gestionar Gastos Registrados")
        st.info("Aquí puedes editar o eliminar los gastos más recientes que coinciden con los filtros aplicados.")

        # ==========================================================
        # <<<<<<<  SOLUCIÓN: DEFINIR LOS DATOS AQUÍ  >>>>>>>
        # ==========================================================
        # 1. Definimos el DataFrame que usaremos para la gestión ANTES de cualquier lógica de UI.
        # Seleccionamos las columnas más importantes y los 20 gastos más recientes.
        gastos_a_gestionar = df_filtrado.sort_values(by="Fecha", ascending=False).head(20)
        # ==========================================================

        if gastos_a_gestionar.empty:
            st.info("No hay gastos para gestionar según los filtros actuales.")
        else:
            # 2. Iteramos sobre el DataFrame ya definido.
            for index, row in gastos_a_gestionar.iterrows():
                id_gasto = str(row['ID_Gasto'])
                
                # Creamos un expander para cada gasto. El título muestra info clave.
                with st.expander(f"📝 {row['Descripcion']} | 💵 ${row['Monto']:.2f} | 📅 {row['Fecha'].strftime('%d/%m/%Y')}"):
                    
                    # 3. Formulario de EDICIÓN dentro del expander
                    with st.form(key=f"edit_form_{id_gasto}"):
                        st.write(f"**Editando Gasto ID:** `{id_gasto}`")
                        
                        col_form1, col_form2 = st.columns(2)
                        
                        with col_form1:
                            nueva_fecha = st.date_input("Fecha", value=row['Fecha'].date(), key=f"date_{id_gasto}")
                            nuevo_monto = st.number_input("Monto", value=float(row['Monto']), format="%.2f", key=f"monto_{id_gasto}")
                            nueva_categoria = st.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(row['Categoria']) if row['Categoria'] in CATEGORIAS else 0, key=f"cat_{id_gasto}")
                        
                        with col_form2:
                            nueva_descripcion = st.text_input("Descripción", value=row['Descripcion'], key=f"desc_{id_gasto}")
                            nueva_subcategoria = st.text_input("Subcategoría", value=row['Subcategoria'], key=f"subcat_{id_gasto}")
                            nueva_persona = st.selectbox("Persona", PERSONAS, index=PERSONAS.index(row['Persona']) if row['Persona'] in PERSONAS else 0, key=f"pers_{id_gasto}")

                        # Botones de acción del formulario
                        col_btn1, col_btn2 = st.columns([1, 1])
                        
                        with col_btn1:
                            submitted_edit = st.form_submit_button("💾 Guardar Cambios")
                        
                        with col_btn2:
                            submitted_delete = st.form_submit_button("🗑️ Eliminar Gasto", help="¡Esta acción es permanente!")

                    # Lógica para cuando se presiona "Guardar Cambios"
                    if submitted_edit:
                        datos_actualizados = {
                            'Fecha': nueva_fecha.strftime('%Y-%m-%d'),
                            'Monto': nuevo_monto,
                            'Descripcion': nueva_descripcion,
                            'Categoria': nueva_categoria,
                            'Subcategoria': nueva_subcategoria,
                            'Persona': nueva_persona
                        }
                        exito, mensaje = editar_gasto(worksheet, id_gasto, datos_actualizados)
                        if exito:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)
                    
                    # Lógica para cuando se presiona "Eliminar Gasto"
                    if submitted_delete:
                        exito, mensaje = eliminar_gasto(worksheet, id_gasto)
                        if exito:
                            st.success(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)