from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <h1>Simulador Cuántico (Demo Web)</h1>
    <p>¡Bienvenido! Esta es una versión web básica.<br>
    Puedes consultar el estado de la app o hacer pruebas de conexión a la base de datos.</p>
    <form method='post' action='/dbtest'>
        <button type='submit'>Probar conexión a PostgreSQL</button>
    </form>
    """)

@app.route('/dbtest', methods=['POST'])
def dbtest():
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL", "postgres://usuario:contraseña@host:puerto/dbname")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return f"<p>Conexión exitosa: {version}</p><a href='/'>Volver</a>"
    except Exception as e:
        return f"<p>Error de conexión: {e}</p><a href='/'>Volver</a>"

@app.route('/api/health')
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
