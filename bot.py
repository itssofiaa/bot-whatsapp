from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# 🔥 ACTIVAR DEBUG (CLAVE)
app.config["DEBUG"] = True


# 🔥 Función para leer datos
def cargar_datos():
    df = pd.read_csv("datos.csv", sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df


# 🔥 Detectar columna de cédula
def obtener_columna_cedula(df):
    for col in df.columns:
        if "cedula" in col.lower():
            return col
    return None


# 🔥 Limpiar cédula
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
    <p>✅ Nombre: {fila['Nombre']}</p>
    <p>📍 Lugar: {fila['Lugar']}</p>
    <p>🕒 Hora: {fila['Hora']}</p>
    <p>💼 Vacante: {fila['Vacante']}</p>

    <form action="/confirmar" method="POST">
        <input type="hidden" name="cedula" value="{cedula_limpia}">
        <button name="respuesta" value="SI">Sí asistiré</button>
        <button name="respuesta" value="NO">No asistiré</button>
    </form>
    """


# 🔥 CONFIRMAR (SIN RIESGO)
@app.route("/confirmar", methods=["POST"])
def confirmar():
    df = cargar_datos()
    col_cedula = obtener_columna_cedula(df)

    cedula = limpiar_cedula(request.form.get("cedula"))
    respuesta = request.form.get("respuesta")

    df[col_cedula] = df[col_cedula].apply(limpiar_cedula)

    if "Asistencia" not in df.columns:
        df["Asistencia"] = ""

    df.loc[df[col_cedula] == cedula, "Asistencia"] = respuesta

    # 🔥 GUARDAR SIN FALLAR
    df.to_csv("/tmp/datos_actualizados.csv", index=False)

    return f"""
    <h2>✅ Guardado</h2>
    <p>{respuesta}</p>
    <a href="/ver">Ver datos</a>
    """


# 🔥 VER
@app.route("/ver")
def ver():
    df = cargar_datos()
    return df.to_html()


# 🔥 ERROR HANDLER GLOBAL
@app.errorhandler(Exception)
def handle_error(e):
    return f"❌ ERROR REAL:<br><br>{str(e)}", 500


if __name__ == "__main__":
    app.run()