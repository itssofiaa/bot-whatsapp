from flask import Flask, request, render_template
import pandas as pd
import sqlite3

app = Flask(__name__)

# 🔥 BASE DE DATOS
def guardar_respuesta(cedula, respuesta):
    conn = sqlite3.connect("respuestas.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            cedula TEXT,
            respuesta TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO respuestas (cedula, respuesta)
        VALUES (?, ?)
    """, (cedula, respuesta))

    conn.commit()
    conn.close()


# 🔥 Leer CSV
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


# 🔥 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 🔥 CONSULTAR
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


# 🔥 CONFIRMAR (GUARDA EN DB)
@app.route("/confirmar", methods=["POST"])
def confirmar():
    cedula = limpiar_cedula(request.form.get("cedula"))
    respuesta = request.form.get("respuesta")

    guardar_respuesta(cedula, respuesta)

    return """
    <h2>✅ Respuesta guardada</h2>
    <p>Gracias por confirmar</p>
    """


# 🔒 OPCIONAL: VER RESPUESTAS (PROTEGER)
@app.route("/admin")
def admin():
    clave = request.args.get("clave")

    if clave != "1234":  # 🔥 cámbiala
        return "⛔ Acceso denegado"

    conn = sqlite3.connect("respuestas.db")
    df = pd.read_sql_query("SELECT * FROM respuestas", conn)
    conn.close()

    return df.to_html()


if __name__ == "__main__":
    app.run()