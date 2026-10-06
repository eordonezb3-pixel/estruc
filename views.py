from models import Estudiante, CAMPOS_ESTUDIANTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


gestor = GestorJSON("data/estudiantes.json")

# TUPLAS de configuración: son campos fijos del sistema.
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")


# ===================== AYUDAS INTERNAS =====================

def carnets_registrados(excepto_id=None):
    """CONJUNTO con los carnets ya usados."""
    return {
        registro["carnet"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def siguiente_id():
    # LISTA: contiene los registros cargados desde JSON.
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


# ===================== C · CREATE =====================

def crear_estudiante(datos):
    """Crea un estudiante. Devuelve (exito, mensaje)."""
    try:
        # DICCIONARIO: normalizamos los datos recibidos.
        valores = {
            campo: str(datos.get(campo, "")).strip()
            for campo in CAMPOS_ESTUDIANTE
        }

        faltantes = [
            campo for campo in CAMPOS_OBLIGATORIOS
            if not valores[campo]
        ]

        if faltantes:
            return False, (
                f"Faltan campos obligatorios: {', '.join(faltantes)}"
            )

        if not es_email_valido(valores["email"]):
            return False, "El email no tiene un formato válido"

        if valores["carnet"].lower() in carnets_registrados():
            return False, "Ese carnet ya está registrado"

        estudiante = Estudiante(siguiente_id(), **valores)

        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())

        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return (
            True,
            f"Estudiante {estudiante.obtener_nombre_completo()} "
            f"creado con id {estudiante.id}",
        )

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== R · READ =====================

def obtener_todos():
    """Devuelve una LISTA de objetos Estudiante."""
    return [
        Estudiante.desde_diccionario(registro)
        for registro in gestor.leer()
    ]


def obtener_por_id(id_estudiante):
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante

    return None


# ===================== S · SEARCH =====================

def buscar_estudiantes(termino):
    """Búsqueda lineal por nombre, apellido, email o carnet."""
    termino = str(termino).strip().lower()

    if not termino:
        return []

    encontrados = []

    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(
                    Estudiante.desde_diccionario(registro)
                )
                break

    return encontrados


# ===================== U · UPDATE =====================

def actualizar_estudiante(id_estudiante, cambios):
    """Actualiza únicamente los campos recibidos en cambios."""
    try:
        desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)

        if desconocidos:
            return False, (
                f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            )

        if not cambios:
            return False, "No se indicó ningún cambio"

        valores = {
            campo: str(valor).strip()
            for campo, valor in cambios.items()
        }

        for campo in CAMPOS_OBLIGATORIOS:
            if campo in valores and not valores[campo]:
                return False, f"El campo {campo} no puede estar vacío"

        if "email" in valores:
            if not es_email_valido(valores["email"]):
                return False, "El email no tiene un formato válido"

        if "carnet" in valores:
            if valores["carnet"].lower() in carnets_registrados(
                excepto_id=id_estudiante
            ):
                return False, "Ese carnet ya lo usa otro estudiante"

        registros = gestor.leer()
        posicion = None

        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                posicion = indice
                break

        if posicion is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        registros[posicion].update(valores)

        if not gestor.guardar(registros):
            return False, "No se pudo guardar la actualización"

        return (
            True,
            f"Estudiante {id_estudiante} actualizado "
            f"({len(cambios)} campo/s)",
        )

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== D · DELETE =====================

def eliminar_estudiante(id_estudiante):
    registros = gestor.leer()

    # LISTA nueva sin el registro eliminado.
    quedan = [
        registro
        for registro in registros
        if registro["id"] != id_estudiante
    ]

    if len(quedan) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"

    if not gestor.guardar(quedan):
        return False, "No se pudo guardar el archivo"

    return True, f"Estudiante {id_estudiante} eliminado"


# ===================== EXTRA · NOTAS =====================

def agregar_nota(id_estudiante, materia, nota):
    """Agrega una nota válida entre 0 y 20."""
    try:
        estudiante = obtener_por_id(id_estudiante)

        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        materia = str(materia).strip()

        if not materia:
            return False, "La materia no puede estar vacía"

        try:
            nota = float(nota)
        except (TypeError, ValueError):
            return False, "La nota debe ser un número entre 0 y 20"

        if nota < 0 or nota > 20:
            return False, "La nota debe estar entre 0 y 20"

        if nota.is_integer():
            nota = int(nota)

        estudiante.agregar_nota(materia, nota)

        registros = gestor.leer()

        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                registros[indice] = estudiante.a_diccionario()
                break

        if not gestor.guardar(registros):
            return False, "No se pudo guardar la nota"

        return (
            True,
            f"Nota {nota} agregada en {materia} "
            f"al estudiante {estudiante.obtener_nombre_completo()}",
        )

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== EXTRA · MATERIAS =====================

def materias_ofertadas():
    """CONJUNTO con todas las materias, sin duplicados."""
    materias = set()

    for estudiante in obtener_todos():
        materias.update(estudiante.materias)

    return materias


def estudiantes_en_comun(id_a, id_b):
    """Devuelve el CONJUNTO de materias compartidas por dos estudiantes."""
    estudiante_a = obtener_por_id(id_a)
    estudiante_b = obtener_por_id(id_b)

    if estudiante_a is None or estudiante_b is None:
        return None

    return estudiante_a.materias_en_comun(estudiante_b)
