import psycopg2
from flask import Flask, jsonify

def creat_app():
    conn = psycopg2.connect(
        user='postgres',
        password='root',
        host='127.0.0.1',
        dbname='test')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_things (
            x INTEGER,
            y VARCHAR(255),
            z FLOAT
        )
        """)

    cursor.execute("DELETE from test_things")
    row = 1
    cursor.execute(
        "INSERT INTO test_things (x, y, z) "
        "VALUES (%(x)s, %(y)s, %(z)s)",
        {"x": row, "y": "row number %d" % row,
         "z": row * 4.57292, }
    )
    cursor.close()
    conn.commit()

    app = Flask(__name__)

    @app.route('/db')
    def test_db():
        cursor = conn.cursor()
        cursor.execute(
            "select * from test_things")
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    return app
app = creat_app()
if __name__ == '__main__':
    app.run(port=8080, debug=False)