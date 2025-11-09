import flet as ft
import csv
from pathlib import Path
from datetime import datetime

def main(page: ft.Page):
    page.title = "Boleta de Calificaciones"
    page.bgcolor = ft.Colors.BLUE_100
    page.window_width = 1600
    page.window_height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- Snackbar para notificaciones ---
    snack_bar = ft.SnackBar(content=ft.Text(""), duration=3000)
    page.overlay.append(snack_bar)

    def mostrar_snackbar(texto: str, color=ft.Colors.GREEN):
        snack_bar.content = ft.Text(texto, color=ft.Colors.WHITE)
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()

    # --- Controles de entrada (Dropdowns) ---
    lista_alumnos = ft.Dropdown(
        width=300,
        label="Alumnos",
        options=[
            ft.dropdown.Option("Juan Manuel Martinez"),
            ft.dropdown.Option("Maria Fernanda Perez"),
            ft.dropdown.Option("Jose Luis González"),
            ft.dropdown.Option("Ana Maria Sanchez"),
            ft.dropdown.Option("Pedro Perez Perez"),
        ],
    )

    dropdowns_materias = {
        "Español": ft.Dropdown(width=200, label="Español", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Matemáticas": ft.Dropdown(width=200, label="Matemáticas", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Inglés": ft.Dropdown(width=200, label="Inglés", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Informática": ft.Dropdown(width=200, label="Informática", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Historia": ft.Dropdown(width=200, label="Historia", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Frameworks": ft.Dropdown(width=200, label="Frameworks de Desarrollo", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Metodologías Ágiles": ft.Dropdown(width=200, label="Metodologías Ágiles", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Humanidades": ft.Dropdown(width=200, label="Humanidades", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
        "Cultura Digital": ft.Dropdown(width=200, label="Cultura Digital", options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)]),
    }

    label_promedio = ft.Text(value="", size=20, width=100, color="White")

    # --- Tabla de Calificaciones ---
    tabla_calificaciones = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Alumno")),
            ft.DataColumn(label=ft.Text("Español")),
            ft.DataColumn(label=ft.Text("Matemáticas")),
            ft.DataColumn(label=ft.Text("Inglés")),
            ft.DataColumn(label=ft.Text("Informática")),
            ft.DataColumn(label=ft.Text("Historia")),
            ft.DataColumn(label=ft.Text("Frameworks")),
            ft.DataColumn(label=ft.Text("Metodologías Ágiles")),
            ft.DataColumn(label=ft.Text("Humanidades")),
            ft.DataColumn(label=ft.Text("Cultura Digital")),
            ft.DataColumn(label=ft.Text("Promedio")),
            ft.DataColumn(label=ft.Text("Acciones")), # Columna para el botón de eliminar
        ],
        rows=[]
    )

    # --- Funciones de los Botones ---

    def borrar_campos(e):
        lista_alumnos.value = None
        for dropdown in dropdowns_materias.values():
            dropdown.value = None
        label_promedio.value = ""
        mostrar_snackbar("Campos limpiados.", ft.Colors.BLUE_500)
        page.update()

    def eliminar_alumno(row_a_eliminar):
        tabla_calificaciones.rows.remove(row_a_eliminar)
        mostrar_snackbar("Alumno eliminado exitosamente.", ft.Colors.GREEN)
        page.update()

    def calcular_promedio(e):
        # Validaciones
        if not lista_alumnos.value:
            mostrar_snackbar("Por favor, selecciona un alumno.", ft.Colors.RED)
            return

        for materia, dropdown in dropdowns_materias.items():
            if not dropdown.value:
                mostrar_snackbar(f"Falta la calificación de {materia}.", ft.Colors.RED)
                return
        
        # Comprobar si el alumno ya existe en la tabla
        for row in tabla_calificaciones.rows:
            if row.cells[0].content.value == lista_alumnos.value:
                mostrar_snackbar("Este alumno ya tiene calificaciones registradas.", ft.Colors.ORANGE)
                return

        # Cálculo del promedio
        notas = [int(d.value) for d in dropdowns_materias.values()]
        promedio = sum(notas) / len(notas)
        label_promedio.value = f"{promedio:.2f}"

        # Botón para eliminar la fila específica
        boton_eliminar = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar Alumno"
        )

        # Crear la nueva fila
        nueva_fila = ft.DataRow(cells=[
            ft.DataCell(ft.Text(lista_alumnos.value)),
            *[ft.DataCell(ft.Text(d.value)) for d in dropdowns_materias.values()],
            ft.DataCell(ft.Text(f"{promedio:.2f}")),
            ft.DataCell(boton_eliminar),
        ])
        
        # Asignar la función de eliminar a este botón específico
        boton_eliminar.on_click = lambda _, fila=nueva_fila: eliminar_alumno(fila)
        
        tabla_calificaciones.rows.append(nueva_fila)
        mostrar_snackbar("Calificaciones agregadas correctamente.", ft.Colors.GREEN)
        borrar_campos(None) # Limpiar campos después de agregar
        page.update()

    def exportar_csv(e):
        if not tabla_calificaciones.rows:
            mostrar_snackbar("No hay datos para exportar.", ft.Colors.RED)
            return

        # Crear una ruta en la carpeta de descargas del usuario
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = Path.home() / "Downloads" / f"calificaciones_{timestamp}.csv"

        try:
            with open(ruta_archivo, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # Escribir encabezados (omitiendo la columna de "Acciones")
                headers = [col.label.value for col in tabla_calificaciones.columns[:-1]]
                writer.writerow(headers)

                # Escribir filas
                for row in tabla_calificaciones.rows:
                    # Extraer el valor de texto de cada celda (omitiendo la última)
                    fila_datos = [cell.content.value for cell in row.cells[:-1]]
                    writer.writerow(fila_datos)
            
            mostrar_snackbar(f"Datos exportados a {ruta_archivo}", ft.Colors.GREEN)
        except Exception as ex:
            mostrar_snackbar(f"Error al exportar: {ex}", ft.Colors.RED)
        
        page.update()

    # --- Botones de Acción ---
    boton_calcular = ft.ElevatedButton(text="Agregar y Calcular Promedio", on_click=calcular_promedio, icon=ft.Icons.ADD)
    boton_borrar_campos = ft.ElevatedButton(text="Limpiar Campos", on_click=borrar_campos, icon=ft.Icons.CLEAR_ALL)
    boton_exportar = ft.ElevatedButton(text="Exportar a CSV", on_click=exportar_csv, icon=ft.Icons.DOWNLOAD)

    # --- Diseño de la Interfaz ---
    fila_dropdowns = ft.Row(
        controls=[
            lista_alumnos,
            *dropdowns_materias.values(), # Desempaquetar los dropdowns de materias
            label_promedio
        ],
        wrap=True, # Permite que los elementos se ajusten a la siguiente línea si no hay espacio
        spacing=10,
        run_spacing=10,
    )

    fila_botones = ft.Row(
        [boton_calcular, boton_borrar_campos, boton_exportar],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    page.add(
        ft.Column(
            [
                ft.Text("Sistema de Registro de Calificaciones", size=32, weight=ft.FontWeight.BOLD),
                fila_dropdowns,
                ft.Divider(),
                fila_botones,
                ft.Divider(),
                ft.Row([tabla_calificaciones], scroll=ft.ScrollMode.ALWAYS) # Para hacer la tabla desplazable horizontalmente
            ],
            spacing=20
        )
    )

ft.app(target=main)