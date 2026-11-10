import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash
from config import Config

class BancoDados:
    """Gerencia a conexão e a inicialização do banco SQLite."""
    def conectar(self):
        conexao = sqlite3.connect(Config.DATABASE)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    def inicializar(self):
        Path(Config.DATABASE).parent.mkdir(parents=True, exist_ok=True)
        with self.conectar() as con:
            schema = (Path(__file__).resolve().parent.parent / "database" / "schema.sql").read_text(encoding="utf-8")
            con.executescript(schema)
            if con.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
                con.executemany("INSERT INTO categorias(nome) VALUES (?)", [
                    ("Ação",), ("Aventura",), ("Esportes",), ("RPG",), ("Acessórios",)
                ])
            if con.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'").fetchone()[0] == 0:
                admin_email = os.environ.get("ADMIN_EMAIL", "admin@levelup.local")
                admin_password = os.environ.get("ADMIN_PASSWORD", "LevelUp@2026")
                con.execute("INSERT INTO usuarios(nome,email,senha_hash,tipo) VALUES (?,?,?,'admin')",
                    ("Administrador", admin_email, generate_password_hash(admin_password)))
            if con.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
                exemplos = [
                    (1,"Cyber Quest","Uma aventura futurista em uma metrópole cheia de desafios.","PC",149.90,15,"https://images.unsplash.com/photo-1542751371-adc38448a05e?w=900",1),
                    (2,"The Last Realm","Explore um mundo misterioso e descubra seus segredos.","PlayStation",199.90,10,"https://images.unsplash.com/photo-1511512578047-dfb367046420?w=900",1),
                    (3,"Futebol Pro 26","Monte seu time e dispute partidas emocionantes.","Multi-plataforma",249.90,20,"https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=900",1),
                    (4,"Legends of Eldoria","RPG de fantasia com missões e personagens marcantes.","PC",179.90,8,"https://images.unsplash.com/photo-1493711662062-fa541dadf2b0?w=900",0),
                    (5,"Headset Gamer X","Headset com microfone para suas partidas.","Acessórios",229.90,12,"https://images.unsplash.com/photo-1599669454699-248893623440?w=900",0),
                    (1,"Neon Racers","Corridas em pistas iluminadas por neon.","Xbox",119.90,7,"https://images.unsplash.com/photo-1511882150382-421056c89033?w=900",0)
                ]
                con.executemany("""INSERT INTO produtos(categoria_id,nome,descricao,plataforma,preco,estoque,imagem,destaque)
                    VALUES (?,?,?,?,?,?,?,?)""", exemplos)

    def executar(self, sql, parametros=(), retornar=False):
        with self.conectar() as con:
            cur = con.execute(sql, parametros)
            if retornar:
                return cur.fetchall()
            return cur.lastrowid
