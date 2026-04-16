from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# 🔥 Leer archivo detectando separador automáticamente
data = pd.read_csv("datos.csv", sep=None, engine="python")

# 🔥 Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DETECTADAS:")
print(data.columns)

# 🔥 Detectar columna de cédula
col_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        col_cedula = col
        break

print("COLUMNA DE CÉDULA USADA:", col_cedula)


# 🔥 Función para limpiar cédula
def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


# 🔥 Ruta principal
@app.route("/")
def home():
    return render_template("index.html")


# 🔥 Consultar cédula
@app.route("/consultar", methods=["POST"])
def consultar():
    cedula_input = request.form.get("cedula")

    if not col_cedula:
        return "❌ Error: no se encontró la columna de cédula"

    cedula_limpia = limpiar_cedula(cedula_input)

    # limpiar columna
    data[col_cedula] = data[col_cedula].apply(limpiar_cedula)

    resultado = data[data[col_cedula] == cedula_limpia]

    if resultado.empty:
        return "❌ No se encontró la cédula"

    fila = resultado.iloc[0]

    return f"""
    <h2>Resultado</h2>
    <p>✅ Nombre: {fila['Nombre']}</p>
    <p>📍 Lugar: {fila['Lugar']}</p>
    <p>🕒 Hora: {fila['Hora']}</p>
    <p>💼 Vacante: {fila['Vacante']}</p>

    <h3>¿Confirmas tu asistencia?</h3>
    <form action="/confirmar" method="POST">
        <input type="hidden" name="cedula" value="{cedula_limpia}">
        <button name="respuesta" value="SI">✅ Sí asistiré</button>
        <button name="respuesta" value="NO">❌ No asistiré</button>
    </form>
    """


# 🔥 Confirmar asistencia
@app.route("/confirmar", methods=["POST"])
def confirmar():
    global data

    cedula = request.form.get("cedula")
    respuesta = request.form.get("respuesta")

    cedula = limpiar_cedula(cedula)

    # limpiar columna
    data[col_cedula] = data[col_cedula].apply(limpiar_cedula)

    # 🔥 crear columna si no existe
    if "Asistencia" not in data.columns:
        data["Asistencia"] = ""

    # 🔥 actualizar asistencia
    data.loc[data[col_cedula] == cedula, "Asistencia"] = respuesta

    # 🔥 guardar en archivo NUEVO (evita error en Render)
    data.to_csv("datos_actualizados.csv", index=False)

    return f"""
    <h2>✅ Respuesta guardada</h2>
    <p>Tu respuesta fue: <b>{respuesta}</b></p>
    <br>
    <a href="/ver">🔎 Ver todas las respuestas</a>
    """


# 🔥 Ver todos los datos
@app.route("/ver")
def ver():
    return data.to_html()


# 🔥 Ejecutar app
if __name__ == "__main__":
    app.run()