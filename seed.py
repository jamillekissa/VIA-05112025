#!/usr/bin/env python3
# seed_random_times.py
import sqlite3
import bcrypt
from faker import Faker
import random
from datetime import datetime, timedelta
import argparse
import os

DB_PATH = "viaDB.db"
fake = Faker("pt_BR")

def get_conn():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Banco não encontrado: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def random_datetime_between(start_dt, end_dt):
    """Retorna uma datetime aleatória entre start_dt e end_dt."""
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    random_ts = random.randint(start_ts, end_ts)
    return datetime.fromtimestamp(random_ts)

def gerar_email_unico(base_nome, idx, domain, used):
    """Gera email tentando evitar duplicatas (aplica sufixo se necessário)."""
    slug = base_nome.lower().replace(" ", ".").replace("'", "")
    candidate = f"{slug}.{idx}@{domain}"
    if candidate in used:
        candidate = f"{slug}.{idx}.{random.randint(10,9999)}@{domain}"
    used.add(candidate)
    return candidate

def criar_usuario(conn, nome, email, senha, foto_url, curso, fatec, horas, disc_fac, disc_dif, ano_prova, data_cadastro):
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO usuarios
            (nome, email, senha_hash, foto_perfil_url, curso_desejado, fatec_escolhida, horas_estudo, disc_facilidade, disc_dificuldade, ano_prova, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, email, senha_hash, foto_url, curso, fatec, horas, disc_fac, disc_dif, ano_prova, data_cadastro))
        return True
    except sqlite3.IntegrityError:
        return False

def seed(n, domain, start_date, end_date, senha_padrao, criar_admin):
    conn = get_conn()
    cursos = ["Análise e Desenvolvimento de Sistemas", "Gestão Empresarial", "Logística", "Eventos", "Marketing"]
    fatecs = ["Fatec São Paulo", "Fatec Campinas", "Fatec Sorocaba", "Fatec Praia Grande", "Fatec Americana"]
    disciplinas = ["Matemática", "Português", "História", "Geografia", "Inglês", "Química", "Física", "Biologia"]

    used_emails = set()
    inserted = 0
    attempted = 0

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    # definir horário início às 00:00:00
    start_dt = start_dt.replace(hour=0, minute=0, second=0)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    # definir horário fim às 23:59:59
    end_dt = end_dt.replace(hour=23, minute=59, second=59)

    for i in range(n):
        attempted += 1
        nome = fake.name()
        email = gerar_email_unico(nome, i, domain, used_emails)
        senha = senha_padrao
        foto = "images/perfil-default.png"
        curso = random.choice(cursos)
        fatec = random.choice(fatecs)
        horas = f"{random.randint(1, 8)}h/dia"
        disc_fac = random.choice(disciplinas)
        disc_dif = random.choice([d for d in disciplinas if d != disc_fac])
        ano_prova = random.choice(["2023", "2024", "2025"])
        dt_rand = random_datetime_between(start_dt, end_dt).strftime("%Y-%m-%d %H:%M:%S")

        ok = criar_usuario(conn, nome, email, senha, foto, curso, fatec, horas, disc_fac, disc_dif, ano_prova, dt_rand)
        if ok:
            inserted += 1

    if criar_admin:
        admin_email = "admin@via.com"
        admin_senha = senha_padrao if senha_padrao else "Admin123!"
        # tenta inserir admin com data aleatória no fim do período (mais recente)
        admin_dt = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        criar_usuario(conn, "Administrador", admin_email, admin_senha, "images/perfil-default.png",
                      "Gestão de TI", "Fatec São Paulo", "N/A", "Admin", "Nenhuma", "2025", admin_dt)

    conn.commit()
    conn.close()
    print(f"✅ Tentados: {attempted} — Inseridos: {inserted} — Domain: {domain}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de usuários com timestamps aleatórios")
    parser.add_argument("-n", type=int, default=50, help="Número de usuários a criar")
    parser.add_argument("--domain", type=str, default="exemplo.com", help="Domínio para emails de teste")
    parser.add_argument("--start", type=str, default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                        help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%d"),
                        help="Data final (YYYY-MM-DD)")
    parser.add_argument("--senha", type=str, default="Test123!", help="Senha padrão para usuários de teste")
    parser.add_argument("--admin", action="store_true", help="Criar usuário admin admin@via.com")
    args = parser.parse_args()

    seed(args.n, args.domain, args.start, args.end, args.senha, args.admin)
