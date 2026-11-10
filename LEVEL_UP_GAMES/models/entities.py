from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    def __init__(self, nome, email, senha, tipo="cliente", id=None):
        self.id, self.nome, self.email, self.tipo = id, nome, email, tipo
        self.senha_hash = generate_password_hash(senha) if senha else None

    def conferir_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Cliente(Usuario):
    def __init__(self, nome, email, senha, id=None):
        super().__init__(nome, email, senha, "cliente", id)

class Administrador(Usuario):
    def __init__(self, nome, email, senha, id=None):
        super().__init__(nome, email, senha, "admin", id)

class Produto:
    def __init__(self, nome, descricao, plataforma, preco, estoque, categoria_id=None, imagem="", destaque=0, id=None):
        self.id, self.nome, self.descricao = id, nome, descricao
        self.plataforma, self.preco, self.estoque = plataforma, float(preco), int(estoque)
        self.categoria_id, self.imagem, self.destaque = categoria_id, imagem, int(destaque)

class ItemPedido:
    def __init__(self, produto, quantidade):
        self.produto, self.quantidade = produto, int(quantidade)
        self.subtotal = float(produto["preco"]) * self.quantidade

class Carrinho:
    def __init__(self, itens=None):
        self.itens = itens or {}

    def adicionar(self, produto_id, quantidade=1):
        chave = str(produto_id)
        self.itens[chave] = self.itens.get(chave, 0) + int(quantidade)

    def remover(self, produto_id):
        self.itens.pop(str(produto_id), None)

class Pedido:
    def __init__(self, usuario_id, itens):
        self.usuario_id, self.itens = usuario_id, itens
        self.total = sum(item.subtotal for item in itens)

class Pagamento:
    def __init__(self, metodo):
        self.metodo, self.status = metodo, "Simulado"
