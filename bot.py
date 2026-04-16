from flask import Flask, request, render_template
import pandas as pd
import os
from supabase import create_client

app = Flask(__name__)

# CONEXIÓN SUPABASE
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY")

supabase = create_client(url, key)


# Leer CSV de forma robusta
def cargar_datos():
    df = pd.read_csv("datos.csv", sep=None, engine="python", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df


# Buscar columna ignorando mayúsculas y acentos exactos del archivo
def obtener_columna(df, nombre_buscado):
    for col in df.columns:
        if col.strip().lower() == nombre_buscado.strip().lower():
            return col
    return None


# Limpiar cédula
def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/consultar", methods=["POST"])
def consultar():
    try:
        df = cargar_datos()

        col_cedula = obtener_columna(df, "Cédula")
        col_nombre = obtener_columna(df, "Nombre")
        col_vacante = obtener_columna(df, "Vacante")
        col_fecha = obtener_columna(df, "Fecha")
        col_hora = obtener_columna(df, "Hora")
        col_descripcion = obtener_columna(df, "Descripción")
        col_direccion = obtener_columna(df, "Dirección")
        col_link = obtener_columna(df, "Link")

        if not col_cedula:
            return f"❌ Error en consulta: no se encontró la columna Cédula. Columnas detectadas: {list(df.columns)}"

        cedula_input = request.form.get("cedula")
        cedula_limpia = limpiar_cedula(cedula_input)

        df[col_cedula] = df[col_cedula].apply(limpiar_cedula)

        resultado = df[df[col_cedula] == cedula_limpia]

        if resultado.empty:
            return "❌ No se encontró la cédula"

        fila = resultado.iloc[0]

        link_html = ""
        if col_link and pd.notna(fila[col_link]) and str(fila[col_link]).strip():
            link_html = f'<p><b>Link:</b> <a href="{fila[col_link]}" target="_blank">Abrir enlace</a></p>'

        return f"""
        <h2>Resultado</h2>
        <p><b>Nombre:</b> {fila[col_nombre] if col_nombre else ''}</p>
        <p><b>Vacante:</b> {fila[col_vacante] if col_vacante else ''}</p>
        <p><b>Fecha:</b> {fila[col_fecha] if col_fecha else ''}</p>
        <p><b>Hora:</b> {fila[col_hora] if col_hora else ''}</p>
        <p><b>Descripción:</b> {fila[col_descripcion] if col_descripcion else ''}</p>
        <p><b>Ubicación:</b> {fila[col_direccion] if col_direccion else ''}</p>
        {link_html}

        <h3>¿Confirmas tu asistencia?</h3>
        <form action="/confirmar" method="POST">
            <input type="hidden" name="cedula" value="{cedula_limpia}">
            <button name="respuesta" value="SI">Sí asistiré</button>
            <button name="respuesta" value="NO">No asistiré</button>
        </form>
        """

    except Exception as e:
        return f"❌ Error en consulta: {str(e)}"


@app.route("/confirmar", methods=["POST"])
def confirmar():
    try:
        cedula = limpiar_cedula(request.form.get("cedula"))
        respuesta = request.form.get("respuesta")

        existente = supabase.table("respuestas").select("*").eq("cedula", cedula).execute()

        if existente.data:
            supabase.table("respuestas").update({
                "respuesta": respuesta
            }).eq("cedula", cedula).execute()

            return """
            <h2>✅ Respuesta actualizada</h2>
            <p>Tu respuesta fue modificada correctamente.</p>
            """
        else:
            supabase.table("respuestas").insert({
                "cedula": cedula,
                "respuesta": respuesta
            }).execute()

            return """
            <h2>✅ Respuesta guardada</h2>
            <p>Gracias por confirmar tu asistencia.</p>
            """

    except Exception as e:
        return f"❌ Error real: {str(e)}"


if __name__ == "__main__":
    app.run()
