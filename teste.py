from routes.admin_routes import get_db_connection


conn = get_db_connection()
cursor = conn.cursor()
search = "%Armani%"
cursor.execute("""
    SELECT nome, email, curso_desejado
    FROM usuarios
    WHERE nome LIKE ? OR email LIKE ? OR curso_desejado LIKE ?
""", (search, search, search))
print(cursor.fetchall())