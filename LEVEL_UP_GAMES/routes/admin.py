from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models.database import BancoDados
from models.entities import Produto

admin = Blueprint("admin", __name__, url_prefix="/admin")
db=BancoDados()

def somente_admin(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        usuario=session.get("usuario")
        if not usuario or usuario.get("tipo")!="admin":
            flash("Acesso restrito ao administrador.","erro")
            return redirect(url_for("store.login"))
        return fn(*args,**kwargs)
    return wrapper

@admin.route("/")
@somente_admin
def dashboard():
    produtos=db.executar("SELECT COUNT(*) FROM produtos WHERE ativo=1",retornar=True)[0][0]
    clientes=db.executar("SELECT COUNT(*) FROM usuarios WHERE tipo='cliente'",retornar=True)[0][0]
    pedidos=db.executar("SELECT COUNT(*) FROM pedidos",retornar=True)[0][0]
    lista=db.executar("SELECT p.*,c.nome AS categoria FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id ORDER BY p.id DESC",retornar=True)
    categorias=db.executar("SELECT * FROM categorias ORDER BY nome",retornar=True)
    return render_template("admin.html", produtos=produtos, clientes=clientes, pedidos=pedidos, lista=lista, categorias=categorias)

@admin.route("/produto/salvar",methods=["POST"])
@somente_admin
def salvar_produto():
    try:
        pid=request.form.get("id")
        p=Produto(request.form["nome"].strip(),request.form["descricao"].strip(),request.form["plataforma"].strip(),
            request.form["preco"],request.form["estoque"],request.form.get("categoria_id") or None,
            request.form.get("imagem","").strip(),1 if request.form.get("destaque") else 0)
        if not p.nome or p.preco<0 or p.estoque<0: raise ValueError()
        if pid:
            db.executar("""UPDATE produtos SET categoria_id=?,nome=?,descricao=?,plataforma=?,preco=?,estoque=?,imagem=?,destaque=? WHERE id=?""",
                (p.categoria_id,p.nome,p.descricao,p.plataforma,p.preco,p.estoque,p.imagem,p.destaque,pid))
            flash("Produto atualizado.","sucesso")
        else:
            db.executar("""INSERT INTO produtos(categoria_id,nome,descricao,plataforma,preco,estoque,imagem,destaque) VALUES (?,?,?,?,?,?,?,?)""",
                (p.categoria_id,p.nome,p.descricao,p.plataforma,p.preco,p.estoque,p.imagem,p.destaque))
            flash("Produto cadastrado.","sucesso")
    except Exception: flash("Não foi possível salvar. Confira os campos.","erro")
    return redirect(url_for("admin.dashboard"))

@admin.post("/produto/excluir/<int:pid>")
@somente_admin
def excluir_produto(pid):
    db.executar("UPDATE produtos SET ativo=0 WHERE id=?",(pid,))
    flash("Produto removido do catálogo.","sucesso")
    return redirect(url_for("admin.dashboard"))

@admin.route("/pedidos")
@somente_admin
def pedidos():
    lista=db.executar("""SELECT p.*,u.nome AS cliente,u.email,pg.metodo FROM pedidos p
        JOIN usuarios u ON u.id=p.usuario_id LEFT JOIN pagamentos pg ON pg.pedido_id=p.id ORDER BY p.id DESC""",retornar=True)
    return render_template("admin_pedidos.html",pedidos=lista)

@admin.route("/clientes")
@somente_admin
def clientes():
    lista=db.executar("SELECT id,nome,email,criado_em FROM usuarios WHERE tipo='cliente' ORDER BY id DESC",retornar=True)
    return render_template("admin_clientes.html",clientes=lista)
