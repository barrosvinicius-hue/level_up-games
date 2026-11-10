from flask import Flask, render_template
from config import Config
from models.database import BancoDados
from routes.store import store
from routes.admin import admin

def criar_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    BancoDados().inicializar()
    app.register_blueprint(store)
    app.register_blueprint(admin)

    @app.errorhandler(404)
    def pagina_nao_encontrada(_):
        return render_template("erro.html", codigo=404, mensagem="Página não encontrada."),404

    @app.errorhandler(500)
    def erro_servidor(_):
        return render_template("erro.html", codigo=500, mensagem="Ocorreu um erro interno."),500
    return app

app=criar_app()

if __name__=="__main__":
    app.run(debug=True)
