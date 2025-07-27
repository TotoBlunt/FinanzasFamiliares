from datetime import datetime

def ingresar_gasto(worksheet, fecha, monto, descripcion, persona, categoria, subcategoria, tipo_gasto, notas):
    """
    Ingresa una nueva fila de gasto en la hoja de cálculo especificada.

    Args:
        worksheet (gspread.Worksheet): El objeto de la hoja de cálculo donde se insertarán los datos.
        fecha (datetime.date): La fecha del gasto.
        monto (float): El valor monetario del gasto.
        descripcion (str): Una descripción del gasto.
        persona (str): Quién realizó el gasto.
        categoria (str): La categoría del gasto.

    Returns:
        tuple: Una tupla (bool, str) indicando el éxito (True/False) y un mensaje.
    """
    try:
        # 1. Validar los datos de entrada
        if not descripcion or monto <= 0:
            return (False, "La descripción no puede estar vacía y el monto debe ser positivo.")

        # 2. Preparar la fila para ser insertada
        id_gasto = datetime.now().strftime("%Y%m%d%H%M%S")
        fecha_str = fecha.strftime("%Y-%m-%d")
        
        # El orden DEBE coincidir con las columnas de tu Google Sheet
        nueva_fila = [
            id_gasto, 
            fecha_str, 
            monto, 
            descripcion, 
            persona, 
            categoria, 
            subcategoria,  # Subcategoría (vacío por ahora)
            tipo_gasto, # Tipo de Gasto (vacío por ahora)
            notas # Notas (vacío por ahora)
        ]

        # 3. Insertar la fila en la hoja de cálculo
        worksheet.append_row(nueva_fila)
        
        # 4. Devolver un resultado exitoso
        return (True, "¡Gasto agregado exitosamente!")

    except Exception as e:
        # Manejo de cualquier error que pueda ocurrir durante la comunicación con la API
        error_message = f"Ocurrió un error al guardar el dato: {e}"
        print(error_message) # Imprime el error en la consola del servidor para depuración
        return (False, "No se pudo guardar el gasto. Revisa la conexión o los permisos.")

def eliminar_gasto(worksheet, id_gasto):
    """
    Encuentra una fila por su ID_Gasto y la elimina de la hoja de cálculo.

    Args:
        worksheet (gspread.Worksheet): El objeto de la hoja de cálculo.
        id_gasto (str): El ID único del gasto que se desea eliminar.

    Returns:
        tuple: Una tupla (bool, str) indicando el éxito (True/False) y un mensaje.
    """
    try:
        # 1. Encontrar la celda que contiene el ID del gasto.
        # find() busca el valor y devuelve un objeto Cell si lo encuentra.
        # Le decimos que busque en la primera columna (col=1)
        cell = worksheet.find(id_gasto, in_column=1)
        
        if cell is None:
            # Si no se encuentra la celda, el gasto no existe.
            return (False, f"Error: No se encontró el gasto con ID {id_gasto}.")

        # 2. Si se encuentra, obtenemos el número de la fila.
        row_to_delete = cell.row
        
        # 3. Eliminar la fila completa usando su número.
        worksheet.delete_rows(row_to_delete)
        
        return (True, f"¡Gasto con ID {id_gasto} eliminado exitosamente!")

    except gspread.exceptions.APIError as e:
        error_message = f"Error de API al intentar eliminar: {e}"
        print(error_message)
        return (False, "Error de comunicación con Google Sheets. Inténtalo de nuevo.")
    except Exception as e:
        error_message = f"Ocurrió un error inesperado al eliminar: {e}"
        print(error_message)
        return (False, "Ocurrió un error inesperado.")