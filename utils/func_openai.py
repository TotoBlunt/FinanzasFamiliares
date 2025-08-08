
def sugerir_categoria_ia(descripcion, categorias_posibles, cliente_openai):
    """
    Usa la IA para sugerir una categoría basada en la descripción de un gasto.
    """
    if not cliente_openai:
        return None # Si el cliente no se inicializó, no hacemos nada.

    # Prompt claro y directo para la IA
    prompt = f"""
    Dada la siguiente descripción de un gasto: "{descripcion}"

    ¿Cuál de las siguientes categorías es la más apropiada?
    Categorías disponibles: {', '.join(categorias_posibles)}

    Responde únicamente con el nombre exacto de la categoría de la lista. No añadas explicaciones ni texto adicional.
    Si ninguna categoría parece apropiada, responde con "Otro".
    """
    try:
        response = cliente_openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, # Queremos la respuesta más predecible
            max_tokens=15 
        )
        sugerencia = response.choices[0].message.content.strip()
        
        # Verificamos que la sugerencia esté en nuestra lista de categorías
        if sugerencia in categorias_posibles:
            return sugerencia
        else:
            return "Otro" # Si la IA devuelve algo inesperado, asignamos "Otro"
            
    except Exception as e:
        print(f"Error al llamar a la API de OpenAI para sugerir categoría: {e}")
        return None

def generar_resumen_ia(df_filtrado, cliente_openai):
    """
    Analiza un DataFrame de gastos y genera un resumen y consejos con IA.
    """
    if not cliente_openai:
        return "La funcionalidad de IA no está disponible. Revisa la configuración de la API Key."
        
    if df_filtrado.empty:
        return "No hay datos suficientes en el período seleccionado para generar un resumen."

    # 1. Calcular métricas clave con Pandas
    gasto_total = df_filtrado['Monto'].sum()
    gastos_por_categoria = df_filtrado.groupby('Categoria')['Monto'].sum().sort_values(ascending=False)
    categoria_mayor_gasto = gastos_por_categoria.index[0]
    monto_mayor_gasto = gastos_por_categoria.iloc[0]

    # 2. Construir el prompt para la IA
    prompt = f"""
    Actúa como un asesor financiero personal amigable y constructivo para una pareja. Analiza los siguientes datos de gastos del período seleccionado:

    - Gasto Total: ${gasto_total:,.2f}
    - La categoría con el mayor gasto fue '{categoria_mayor_gasto}' con un total de ${monto_mayor_gasto:,.2f}.
    - Desglose de gastos por categoría:
    {gastos_por_categoria.to_string()}

    Basado en esta información, escribe un breve resumen financiero (máximo 3 párrafos). Tu resumen debe incluir:
    1. Un punto positivo o un logro evidente en sus finanzas.
    2. Un área principal donde podrían enfocarse para mejorar o reducir gastos.
    3. Un consejo práctico y accionable para el próximo período.

    Usa un tono positivo, motivador y evita el lenguaje técnico. Dirígete a ellos como "ustedes".
    """

    try:
        response = cliente_openai.chat.completions.create(
            model="gpt-4o-mini", # Mejor para análisis y redacción
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, # Permite un poco de creatividad en la redacción
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al llamar a la API de OpenAI para generar resumen: {e}")
        return "Ocurrió un error al intentar generar el resumen. Por favor, inténtalo de nuevo más tarde."