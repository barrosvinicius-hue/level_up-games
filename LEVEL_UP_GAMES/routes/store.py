from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import BancoDados
from models.entities import Cliente, Carrinho, ItemPedido, Pedido, Pagamento
from werkzeug.security import check_password_hash

store = Blueprint("store", __name__)
db = BancoDados()

@store.app_context_processor
def inject_globals():
    return {"cart_count": sum(session.get("carrinho", {}).values())}

@store.route("/")
def home():
    destaques = db.executar("SELECT * FROM produtos WHERE ativo=1 AND destaque=1 ORDER BY id DESC", retornar=True)
    recentes = db.executar("SELECT * FROM produtos WHERE ativo=1 ORDER BY id DESC LIMIT 6", retornar=True)
    categorias = db.executar("SELECT * FROM categorias ORDER BY nome", retornar=True)
    return render_template("home.html", destaques=destaques, recentes=recentes, categorias=categorias)

@store.route("/catalogo")
def catalogo():
    termo = request.args.get("q","").strip()
    categoria = request.args.get("categoria","")
    plataforma = request.args.get("plataforma","")
    sql = "SELECT p.*, c.nome AS categoria FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id WHERE p.ativo=1"
    params = []
    if termo:
        sql += " AND (p.nome LIKE ? OR p.descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        sql += " AND p.categoria_id=?"; params.append(categoria)
    if plataforma:
        sql += " AND p.plataforma=?"; params.append(plataforma)
    sql += " ORDER BY p.nome"
    produtos = db.executar(sql, params, True)
    categorias = db.executar("SELECT * FROM categorias ORDER BY nome", retornar=True)
    plataformas = db.executar("SELECT DISTINCT plataforma FROM produtos WHERE ativo=1 ORDER BY plataforma", retornar=True)
    return render_template("catalogo.html", produtos=produtos, categorias=categorias, plataformas=plataformas)

@store.route("/produto/<int:produto_id>")
def produto(produto_id):
    p = db.executar("SELECT p.*, c.nome AS categoria FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id WHERE p.id=? AND p.ativo=1",(produto_id,),True)
    if not p: flash("Produto não encontrado.","erro"); return redirect(url_for("store.catalogo"))
    return render_template("produto.html", produto=p[0])

@store.route("/carrinho")
def carrinho():
    carrinho = session.get("carrinho", {})
    itens=[]; total=0
    for pid, qtd in carrinho.items():
        rows=db.executar("SELECT * FROM produtos WHERE id=? AND ativo=1",(pid,),True)
        if rows:
            item=ItemPedido(rows[0],qtd); itens.append(item); total += item.subtotal
    return render_template("carrinho.html", itens=itens, total=total)

@store.post("/carrinho/adicionar/<int:produto_id>")
def adicionar_carrinho(produto_id):
    rows=db.executar("SELECT id,estoque FROM produtos WHERE id=? AND ativo=1",(produto_id,),True)
    if not rows: flash("Produto indisponível.","erro")
    else:
        cart=session.get("carrinho",{})
        cart[str(produto_id)] = min(cart.get(str(produto_id),0)+1, rows[0]["estoque"])
        session["carrinho"]=cart
        flash("Produto adicionado ao carrinho!","sucesso")
    return redirect(request.referrer or url_for("store.catalogo"))

@store.post("/carrinho/remover/<int:produto_id>")
def remover_carrinho(produto_id):
    cart=session.get("carrinho",{}); cart.pop(str(produto_id),None); session["carrinho"]=cart
    flash("Produto removido.","sucesso")
    return redirect(url_for("store.carrinho"))

@store.post("/carrinho/quantidade/<int:produto_id>")
def quantidade(produto_id):
    try: qtd=max(1,int(request.form.get("quantidade",1)))
    except ValueError: qtd=1
    rows=db.executar("SELECT estoque FROM produtos WHERE id=?",(produto_id,),True)
    if rows:
        cart=session.get("carrinho",{}); cart[str(produto_id)]=min(qtd,rows[0]["estoque"]); session["carrinho"]=cart
    return redirect(url_for("store.carrinho"))

@store.route("/cadastro", methods=["GET","POST"])
def cadastro():
    if request.method=="POST":
        nome=request.form.get("nome","").strip(); email=request.form.get("email","").strip().lower()
        senha=request.form.get("senha","")
        if not nome or not email or len(senha)<6:
            flash("Preencha todos os campos. A senha deve ter pelo menos 6 caracteres.","erro")
        else:
            try:
                usuario=Cliente(nome,email,senha)
                db.executar("INSERT INTO usuarios(nome,email,senha_hash,tipo) VALUES (?,?,?,'cliente')",(usuario.nome,usuario.email,usuario.senha_hash))
                flash("Cadastro realizado! Faça seu login.","sucesso"); return redirect(url_for("store.login"))
            except Exception:
                flash("Este e-mail já está cadastrado ou os dados são inválidos.","erro")
    return render_template("auth.html", modo="cadastro")

@store.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower(); senha=request.form.get("senha","")
        rows=db.executar("SELECT * FROM usuarios WHERE email=?",(email,),True)
        if rows and check_password_hash(rows[0]["senha_hash"],senha):
            u=rows[0]; session["usuario"]={"id":u["id"],"nome":u["nome"],"email":u["email"],"tipo":u["tipo"]}
            flash("Login realizado com sucesso!","sucesso")
            return redirect(url_for("admin.dashboard") if u["tipo"]=="admin" else url_for("store.home"))
        flash("E-mail ou senha incorretos.","erro")
    return render_template("auth.html", modo="login")

@store.route("/sair")
def sair():
    session.pop("usuario",None); flash("Você saiu da sua conta.","sucesso"); return redirect(url_for("store.home"))

@store.route("/checkout", methods=["GET","POST"])
def checkout():
    if not session.get("usuario"): flash("Entre na sua conta para finalizar a compra.","erro"); return redirect(url_for("store.login"))
    cart=session.get("carrinho",{}); itens=[]; total=0
    for pid,qtd in cart.items():
        rows=db.executar("SELECT * FROM produtos WHERE id=? AND ativo=1",(pid,),True)
        if rows:
            item=ItemPedido(rows[0],qtd); itens.append(item); total+=item.subtotal
    if not itens: flash("Seu carrinho está vazio.","erro"); return redirect(url_for("store.catalogo"))
    if request.method=="POST":
        metodo=request.form.get("metodo","")
        if metodo not in ("Pix (simulado)","Cartão (simulado)","Boleto (simulado)"):
            flash("Selecione uma forma de pagamento.","erro")
        else:
            try:
                pedido=Pedido(session["usuario"]["id"],itens)
                with db.conectar() as con:
                    for item in itens:
                        atual=con.execute("SELECT estoque FROM produtos WHERE id=?",(item.produto["id"],)).fetchone()
                        if not atual or atual["estoque"] < item.quantidade: raise ValueError("Estoque insuficiente para um dos produtos.")
                    cur=con.execute("INSERT INTO pedidos(usuario_id,total,status) VALUES (?,?,?)",(pedido.usuario_id,pedido.total,"Pagamento simulado"))
                    pedido_id=cur.lastrowid
                    for item in itens:
                        con.execute("INSERT INTO itens_pedido(pedido_id,produto_id,nome_produto,quantidade,preco_unitario) VALUES (?,?,?,?,?)",
                            (pedido_id,item.produto["id"],item.produto["nome"],item.quantidade,item.produto["preco"]))
                        con.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?",(item.quantidade,item.produto["id"]))
                    pagamento=Pagamento(metodo)
                    con.execute("INSERT INTO pagamentos(pedido_id,metodo,status) VALUES (?,?,?)",(pedido_id,pagamento.metodo,pagamento.status))
                session["carrinho"]={}
                return render_template("confirmacao.html", pedido_id=pedido_id, total=total, metodo=metodo)
            except ValueError as e: flash(str(e),"erro")
    return render_template("checkout.html",itens=itens,total=total)

@store.route("/meus-pedidos")
def meus_pedidos():
    if not session.get("usuario"): return redirect(url_for("store.login"))
    pedidos=db.executar("SELECT * FROM pedidos WHERE usuario_id=? ORDER BY id DESC",(session["usuario"]["id"],),True)
    return render_template("meus_pedidos.html",pedidos=pedidos)
