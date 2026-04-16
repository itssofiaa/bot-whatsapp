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


def cargar_datos():
    df = pd.read_csv("datos.csv", sep=None, engine="python", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df


def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/consultar", methods=["POST"])
def consultar():
    try:
        df = cargar_datos()

        cedula_input = request.form.get("cedula")
        cedula_limpia = limpiar_cedula(cedula_input)

        # usar la columna exacta del archivo
        df["Cedula"] = df["Cedula"].apply(limpiar_cedula)

        resultado = df[df["Cedula"] == cedula_limpia]

        if resultado.empty:
            return "❌ No se encontró la cédula"

        fila = resultado.iloc[0]

        return f"""
        <h2>Resultado</h2>
        <p><b>Nombre:</b> {fila['Nombre']}</p>
        <p><b>Vacante:</b> {fila['Vacante']}</p>
        <p><b>Fecha:</b> {fila['Fecha']}</p>
        <p><b>Hora:</b> {fila['Hora']}</p>
        <p><b>Descripción:</b> {fila['Descripcion']}</p>
        <p><b>Ubicación:</b> {fila['Ubicacion']}</p>

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
