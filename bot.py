from flask import Flask, request, render_template
import pandas as pd
import os
from supabase import create_client

app = Flask(__name__)

# 🔥 CONEXIÓN SUPABASE
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


# 🔹 Leer CSV (solo para consulta)
def cargar_datos():
    df = pd.read_csv("datos.csv", sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df


def obtener_columna_cedula(df):
    for col in df.columns:
        if "cedula" in col.lower():
            return col
    return None


def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


# 🔹 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 🔹 CONSULTAR
@app.route("/consultar", methods=["POST"])
def consultar():
    df = cargar_datos()
    col_cedula = obtener_columna_cedula(df)

    cedula_input = request.form.get("cedula")
    cedula_limpia = limpiar_cedula(cedula_input)

    df[col_cedula] = df[col_cedula].apply(limpiar_cedula)

    resultado = df[df[col_cedula] == cedula_limpia]

    if resultado.empty:
        return "❌ No se encontró la cédula"

    fila = resultado.iloc[0]

    return f"""
    <h2>Resultado</h2>
    <p>Nombre: {fila['Nombre']}</p>
    <p>Lugar: {fila['Lugar']}</p>
    <p>Hora: {fila['Hora']}</p>
    <p>Vacante: {fila['Vacante']}</p>

    <h3>¿Confirmas tu asistencia?</h3>
    <form action="/confirmar" method="POST">
        <input type="hidden" name="cedula" value="{cedula_limpia}">
        <button name="respuesta" value="SI">Sí asistiré</button>
        <button name="respuesta" value="NO">No asistiré</button>
    </form>
    """


# 🔥 GUARDAR EN SUPABASE
@app.route("/confirmar", methods=["POST"])
def confirmar():
    cedula = limpiar_cedula(request.form.get("cedula"))
    respuesta = request.form.get("respuesta")

    supabase.table("respuestas").insert({
        "cedula": cedula,
        "respuesta": respuesta
    }).execute()

    return """
    <h2>✅ Respuesta guardada</h2>
    <p>Gracias por confirmar tu asistencia</p>
    """


if __name__ == "__main__":
    app.run()
