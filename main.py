from models import CAMPOS_ESTUDIANTE
from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    confirmar,
)
from views import (
    crear_estudiante,
    obtener_todos,
    obtener_por_id,
    buscar_estudiantes,
    actualizar_estudiante,
    eliminar_estudiante,
    agregar_nota,
    materias_ofertadas,
    estudiantes_en_comun,
)


def pausa():
    input("\nPresione Enter para continuar...")


def mostrar_estudiantes(estudiantes):
    print(
        f"{'ID':<5}{'NOMBRE':<25}{'EMAIL':<30}{'CARNET':<15}"
        f"{'PROMEDIO':<10}"
    )
    print("-" * 85)

    for estudiante in estudiantes:
        print(
            f"{estudiante.id:<5}"
            f"{estudiante.obtener_nombre_completo():<25}"
            f"{estudiante.email:<30}"
            f"{estudiante.carnet:<15}"
            f"{estudiante.obtener_promedio():<10}"
        )

    print("-" * 85)
    imprimir_info(f"Total: {len(estudiantes)} estudiante(s)")


# ---------- C · CREAR ----------

def opcion_crear():
    imprimir_titulo("CREAR NUEVO ESTUDIANTE")

    datos = {}

    for campo in CAMPOS_ESTUDIANTE:
        datos[campo] = input(f"{campo.capitalize()}: ")

    exito, mensaje = crear_estudiante(datos)

    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)

    pausa()


# ---------- R · LEER TODOS ----------

def opcion_ver_todos():
    imprimir_titulo("LISTA DE ESTUDIANTES")

    estudiantes = obtener_todos()

    if not estudiantes:
        imprimir_info(
            "Todavía no hay estudiantes. "
            "Use la opción 1 para crear el primero."
        )
    else:
        mostrar_estudiantes(estudiantes)

    pausa()


# ---------- S · BUSCAR ----------

def opcion_buscar():
    imprimir_titulo("BUSCAR ESTUDIANTE")

    termino = input("Nombre, apellido, email o carnet: ")
    encontrados = buscar_estudiantes(termino)

    if not encontrados:
        imprimir_info(
            f"Ningún estudiante coincide con '{termino}'."
        )
    else:
        mostrar_estudiantes(encontrados)

    pausa()


# ---------- R · LEER UNO ----------

def opcion_ver_por_id():
    imprimir_titulo("VER ESTUDIANTE POR ID")

    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        pausa()
        return

    estudiante = obtener_por_id(id_estudiante)

    if estudiante is None:
        imprimir_error(
            f"No existe un estudiante con id {id_estudiante}"
        )
    else:
        print(f"ID: {estudiante.id}")
        print(f"Nombre: {estudiante.obtener_nombre_completo()}")
        print(f"Email: {estudiante.email}")
        print(f"Carnet: {estudiante.carnet}")
        print(f"Materias: {', '.join(sorted(estudiante.materias)) or 'Ninguna'}")
        print(f"Promedio: {estudiante.obtener_promedio()}")

    pausa()


# ---------- U · ACTUALIZAR ----------

def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")

    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        pausa()
        return

    estudiante = obtener_por_id(id_estudiante)

    if estudiante is None:
        imprimir_error(
            f"No existe un estudiante con id {id_estudiante}"
        )
        pausa()
        return

    print("Deje vacío un campo si no desea modificarlo.\n")

    cambios = {}

    for campo in CAMPOS_ESTUDIANTE:
        valor = input(
            f"{campo.capitalize()} [{getattr(estudiante, campo)}]: "
        ).strip()

        if valor:
            cambios[campo] = valor

    exito, mensaje = actualizar_estudiante(id_estudiante, cambios)

    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)

    pausa()


# ---------- D · ELIMINAR ----------

def opcion_eliminar():
    imprimir_titulo("ELIMINAR ESTUDIANTE")

    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        pausa()
        return

    estudiante = obtener_por_id(id_estudiante)

    if estudiante is None:
        imprimir_error(
            f"No existe un estudiante con id {id_estudiante}"
        )
        pausa()
        return

    pregunta = (
        f"¿Eliminar a {estudiante.obtener_nombre_completo()}?"
    )

    if confirmar(pregunta):
        exito, mensaje = eliminar_estudiante(id_estudiante)

        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)
    else:
        imprimir_info("Operación cancelada")

    pausa()


# ---------- EXTRA · AGREGAR NOTA ----------

def opcion_agregar_nota():
    imprimir_titulo("AGREGAR NOTA")

    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        pausa()
        return

    materia = input("Materia: ")

    try:
        nota = float(input("Nota (0-20): "))
    except ValueError:
        imprimir_error("La nota debe ser un número entre 0 y 20")
        pausa()
        return

    exito, mensaje = agregar_nota(
        id_estudiante,
        materia,
        nota,
    )

    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)

    pausa()


# ---------- EXTRA · PROMEDIO ----------

def opcion_ver_promedio():
    imprimir_titulo("VER PROMEDIO")

    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        pausa()
        return

    estudiante = obtener_por_id(id_estudiante)

    if estudiante is None:
        imprimir_error(
            f"No existe un estudiante con id {id_estudiante}"
        )
    else:
        print(
            f"Estudiante: {estudiante.obtener_nombre_completo()}"
        )
        print(f"Promedio: {estudiante.obtener_promedio()}")

        if estudiante.notas:
            print("\nNotas por materia:")

            for materia, notas in estudiante.notas.items():
                print(f"- {materia}: {notas}")

    pausa()


# ---------- EXTRA · MATERIAS EN COMÚN ----------

def opcion_materias_en_comun():
    imprimir_titulo("MATERIAS EN COMÚN")

    try:
        id_a = int(input("Id del primer estudiante: "))
        id_b = int(input("Id del segundo estudiante: "))
    except ValueError:
        imprimir_error("Los id deben ser números enteros")
        pausa()
        return

    materias = estudiantes_en_comun(id_a, id_b)

    if materias is None:
        imprimir_error("Uno o ambos estudiantes no existen")
    elif not materias:
        imprimir_info("No tienen materias en común")
    else:
        imprimir_info("Materias en común:")
        for materia in sorted(materias):
            print(f"- {materia}")

    pausa()


# ---------- EXTRA · MATERIAS OFERTADAS ----------

def opcion_materias_ofertadas():
    imprimir_titulo("MATERIAS OFERTADAS")

    materias = materias_ofertadas()

    if not materias:
        imprimir_info("Todavía no hay materias registradas.")
    else:
        for materia in sorted(materias):
            print(f"- {materia}")

    pausa()


OPCIONES = {
    "1": opcion_crear,
    "2": opcion_ver_todos,
    "3": opcion_buscar,
    "4": opcion_ver_por_id,
    "5": opcion_actualizar,
    "6": opcion_eliminar,
    "7": opcion_agregar_nota,
    "8": opcion_ver_promedio,
    "9": opcion_materias_en_comun,
    "10": opcion_materias_ofertadas,
}


def mostrar_menu():
    print("1. Crear estudiante")
    print("2. Ver todos los estudiantes")
    print("3. Buscar estudiante")
    print("4. Ver estudiante por ID")
    print("5. Actualizar estudiante")
    print("6. Eliminar estudiante")
    print("7. Agregar nota")
    print("8. Ver promedio")
    print("9. Materias en común")
    print("10. Ver materias ofertadas")
    print("0. Salir")


def main():
    while True:
        imprimir_titulo("SISTEMA DE ESTUDIANTES")
        mostrar_menu()

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "0":
            imprimir_info("Programa finalizado.")
            break

        funcion = OPCIONES.get(opcion)

        if funcion:
            funcion()
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    main()
