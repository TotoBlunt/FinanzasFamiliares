# Importaciones existentes
import streamlit as st
from utils.conn_Gsheet import conexion_gsheet_produccion, abrir_hoja, cargar_datos
from utils.add_informacion import ingresar_gasto, eliminar_gasto, editar_gasto
from utils.func_dash import aplicar_filtros, mostrar_metricas_clave, graficar_distribucion_categoria, graficar_evolucion_temporal
from utils.func_dash import graficar_comparativa_persona, graficar_detalle_subcategoria, mostrar_tabla_detallada

# Importaciones nuevas para IA
from openai import OpenAI
from utils.func_openai import sugerir_categoria_ia, generar_resumen_ia

# --- INICIALIZAR CLIENTES ---
# Cliente de OpenAI
try:
    client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    # Si la clave no está, no rompemos la app, solo la funcionalidad de IA no estará disponible.
    client_openai = None

# --- CONEXIÓN A GOOGLE SHEETS ---
client_gsheet = conexion_gsheet_produccion()
worksheet = abrir_hoja(client_gsheet)

# --- CONFIGURACIÓN DE LA PÁGINA Y CONSTANTES ---
st.set_page_config(page_title="Gestor de Finanzas", layout="wide")
st.title("Nuestro Gestor de Finanzas Familiares 📊")

# Definir constantes en un solo lugar
CATEGORIAS = ["Comida", "Hogar", "Transporte", "Ocio", "Salud", "Ropa y Calzado", "Tecnología", "Regalos", "Educación", "Otro"]
PERSONAS = ["Milagros Valladolid", "Jose Longa"]
TIPOS_GASTO = ["Fijo Mensual", "Variable Diario", "Ocasional", "Ahorro/Inversión", "Deuda"]

# --- FORMULARIO PARA AÑADIR GASTOS (CON IA) ---
# Usamos clear_on_submit=False para que la sugerencia de IA no se borre al hacer clic
with st.form("entry_form_1", clear_on_submit=False):
    st.header("Añadir un nuevo gasto")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_gasto = st.date_input("Fecha")
        descripcion_gasto = st.text_input("Descripción (Obligatorio)", placeholder="Ej: Compra semanal en el supermercado")
    
    with col2:
        monto_gasto = st.number_input("Monto (Obligatorio)", min_value=0.01, format="%.2f")
        persona_gasto = st.radio("Pagado por", PERSONAS)

    # --- NUEVO: Botón de sugerencia de IA ---
    if st.form_submit_button("🤖 Sugerir Categoría con IA", use_container_width=True):
        if descripcion_gasto and client_openai:
            with st.spinner("Pensando... 🤔"):
                sugerencia = sugerir_categoria_ia(descripcion_gasto, CATEGORIAS, client_openai)
                if sugerencia:
                    # Guardamos la sugerencia en el estado de la sesión para que persista
                    st.session_state.sugerencia_categoria = sugerencia
                else:
                    st.warning("No se pudo obtener una sugerencia.")
        elif not client_openai:
            st.warning("La funcionalidad de IA no está disponible. ¿Configuraste la API Key de OpenAI?")
        else:
            st.warning("Por favor, escribe una descripción primero.")
    
    # --- Widget de Categoría Modificado para usar la sugerencia ---
    sugerencia_guardada = st.session_state.get('sugerencia_categoria', None)
    indice_sugerido = 0
    if sugerencia_guardada and sugerencia_guardada in CATEGORIAS:
        indice_sugerido = CATEGORIAS.index(sugerencia_guardada)

    categoria_gasto = st.selectbox("Categoría", CATEGORIAS, index=indice_sugerido)
    subcategoria_gasto = st.text_input("Subcategoría (Opcional)", placeholder="Ej: Supermercado, Gasolina, Netflix")
    tipo_gasto_seleccionado = st.selectbox("Tipo de Gasto", TIPOS_GASTO)
    notas_gasto = st.text_area("Notas (Opcional)", placeholder="Añade cualquier detalle extra aquí")
    
    # Botón de envío principal
    submitted_add = st.form_submit_button("✅ Agregar Gasto", use_container_width=True, type="primary")

# --- Lógica de envío del formulario ---
if submitted_add:
    exito, mensaje = ingresar_gasto(
        worksheet=worksheet, fecha=fecha_gasto, monto=monto_gasto, descripcion=descripcion_gasto,
        persona=persona_gasto, categoria=categoria_gasto, subcategoria=subcategoria_gasto,
        tipo_gasto=tipo_gasto_seleccionado, notas=notas_gasto
    )
    
    if exito:
        st.success(mensaje)
        # Limpiamos la sugerencia después de usarla para que no afecte al siguiente gasto
        if 'sugerencia_categoria' in st.session_state:
            del st.session_state.sugerencia_categoria
        st.rerun() # Refrescamos para mostrar el formulario limpio
    else:
        st.error(mensaje)

# --- INICIO DEL DASHBOARD ---
st.markdown("---")
st.header("Análisis y Visualización de Gastos 📈")

df_original = cargar_datos(worksheet)
if df_original.empty:
    st.info("Aún no hay datos para mostrar. ¡Agrega tu primer gasto para comenzar!")
    st.stop()

# --- Filtros en la barra lateral ---
st.sidebar.header("Filtros del Dashboard")
persona_sel = st.sidebar.selectbox("Filtrar por Persona:", ["Ambos"] + list(df_original['Persona'].unique()))
fecha_sel = st.sidebar.date_input("Filtrar por Rango de Fechas:",
    value=(df_original['Fecha'].min().date(), df_original['Fecha'].max().date()),
    min_value=df_original['Fecha'].min().date(), max_value=df_original['Fecha'].max().date())
# Corregido: 'Categoría' en lugar de 'Categoria' si ese es el nombre de la columna
categoria_sel = st.sidebar.multiselect("Filtrar por Categoría:",
    options=["Todas"] + list(df_original['Categoria'].unique()), default="Todas")

df_filtrado = aplicar_filtros(df_original, persona_sel, fecha_sel, categoria_sel)

# --- Layout del Dashboard ---
if df_filtrado.empty:
    st.warning("No se encontraron datos para los filtros seleccionados.")
else:
    mostrar_metricas_clave(df_filtrado)
    
    st.subheader("Visión General de Gastos")
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        graficar_distribucion_categoria(df_filtrado)
    with col_dash2:
        graficar_evolucion_temporal(df_filtrado)

    st.markdown("---")
    st.subheader("Análisis Detallado y Gestión")
    
    # --- NUEVO: Añadimos la pestaña de IA ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Comparativa", 
        "🌳 Subcategorías", 
        "📄 Tabla de Datos",
        "⚙️ Gestionar Gastos",
        "🧠 Resumen con IA"
    ])

    with tab1:
        graficar_comparativa_persona(df_filtrado)
    with tab2:
        graficar_detalle_subcategoria(df_filtrado)
    with tab3:
        mostrar_tabla_detallada(df_filtrado)
    with tab4:
        st.header("Gestionar Gastos Registrados")
        gastos_a_gestionar = df_filtrado.sort_values(by="Fecha", ascending=False).head(20)
        if gastos_a_gestionar.empty:
            st.info("No hay gastos para gestionar.")
        else:
            for index, row in gastos_a_gestionar.iterrows():
                id_gasto = str(row['ID_Gasto'])
                with st.expander(f"📝 {row['Descripcion']} | 💵 ${row['Monto']:.2f} | 📅 {row['Fecha'].strftime('%d/%m/%Y')}"):
                    with st.form(key=f"edit_form_{id_gasto}"):
                        st.write(f"**Editando Gasto ID:** `{id_gasto}`")
                        # ... (código del formulario de edición que ya tienes) ...
                        # ...
                        submitted_edit = st.form_submit_button("💾 Guardar Cambios")
                        submitted_delete = st.form_submit_button("🗑️ Eliminar Gasto")
                    
                    if submitted_edit:
                        # ... (lógica de edición) ...
                        st.rerun()
                    if submitted_delete:
                        # ... (lógica de eliminación) ...
                        st.rerun()

    # --- NUEVO: Lógica para la pestaña de IA ---
    with tab5:
        st.header("Asistente Financiero con IA")
        st.info("Obtén un análisis y consejos personalizados sobre tus gastos para el período de tiempo seleccionado en los filtros.")
        
        if not client_openai:
            st.warning("La funcionalidad de IA no está disponible. Revisa tu API Key de OpenAI en los secretos.")
        else:
            if st.button("💡 Generar Resumen y Consejos", use_container_width=True, type="primary"):
                with st.spinner("Analizando tus finanzas y preparando tus consejos... ⏳"):
                    resumen = generar_resumen_ia(df_filtrado, client_openai)
                    st.markdown("---")
                    st.subheader("Aquí está tu análisis:")
                    with st.container(border=True):
                        st.markdown(resumen)