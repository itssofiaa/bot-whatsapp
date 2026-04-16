from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# 🔥 Leer archivo detectando separador automáticamente
data = pd.read_csv("datos.csv", sep=None, engine="python")

# 🔥 Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DETECTADAS:")
print(data.columns)

print("PRIMERAS FILAS:")
print(data.head())

# 🔥 Detectar columna de cédula automáticamente
col_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        col_cedula = col
        break

print("COLUMNA DE CÉDULA USADA:", col_cedula)


# 🔥 Función para limpiar cédulas (solo números)
def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


# 🔥 Ruta principal
@app.route("/")
def home():
    return render_template("index.html")


# 🔥 Ruta para consultar
@app.route("/consultar", methods=["POST"])
def consultar():
    cedula_input = request.form.get("cedula")

    if not col_cedula:
        return "❌ Error: no se encontró la columna de cédula"

    # 🔥 limpiar entrada usuario
    cedula_limpia = limpiar_cedula(cedula_input)

    print("CÉDULA INGRESADA:", cedula_input)
    print("CÉDULA LIMPIA:", cedula_limpia)

    # 🔥 limpiar columna completa
    data[col_cedula] = data[col_cedula].apply(limpiar_cedula)

    print("CÉDULAS EN DATA:")
    print(data[col_cedula].head(10))

    # 🔥 buscar
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
    """


# 🔥 Ejecutar app
if __name__ == "__main__":
    app.run()