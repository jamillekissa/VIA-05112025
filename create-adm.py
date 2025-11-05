import sqlite3
import bcrypt

ADMIN_EMAIL = "admin@via.com"
ADMIN_PASS = "adm123"   # altere para a senha que você quiser (melhor: escolha uma forte)

senha_hash = bcrypt.hashpw(ADMIN_PASS.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = sqlite3.connect("viaDB.db")
cursor = conn.cursor()

# Tenta inserir; se já existir, atualiza a senha
try:
    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha_hash, foto_perfil_url, data_cadastro)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, ("Administrador", ADMIN_EMAIL, senha_hash, "images/perfil-default.png"))
    conn.commit()
    print("Admin criado com sucesso.")
except sqlite3.IntegrityError:
    cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (senha_hash, ADMIN_EMAIL))
    conn.commit()
    print("Admin já existia. Senha atualizada.")

cursor.close()
conn.close()


#////////////////////////////////////////////////////////////////////////////////////////

