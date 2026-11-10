# LEVEL UP GAMES

Loja virtual acadêmica desenvolvida com Flask, Python orientado a objetos, SQLite, HTML, CSS e JavaScript.

## Requisitos
- Python 3.10 ou superior
- Navegador atualizado
- Internet para carregar as fontes e imagens externas (opcional)

## Como executar no Windows
1. Extraia o ZIP.
2. Abra a pasta `LEVEL_UP_GAMES` no VS Code.
3. Abra o terminal nessa pasta.
4. (Opcional, recomendado) Crie ambiente virtual:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
5. Instale as dependências:
   ```powershell
   py -m pip install -r requirements.txt
   ```
6. Execute:
   ```powershell
   py app.py
   ```
7. Acesse `http://127.0.0.1:5000`.

O banco `database/levelup.db` e os produtos de demonstração são criados automaticamente na primeira execução.

## Acesso administrativo inicial
- E-mail: `admin@levelup.local`
- Senha: `LevelUp@2026`

**Importante:** altere essa senha antes de qualquer uso fora do ambiente local. O usuário administrador é criado automaticamente pelo sistema na primeira execução.

## Funcionalidades
- Catálogo com pesquisa e filtros
- Detalhe do produto
- Cadastro e login com hash de senha
- Carrinho persistente na sessão
- Checkout acadêmico com pagamento simulado
- Registro de pedidos, itens e pagamentos no banco
- Área administrativa para cadastrar, editar e desativar produtos
- Consulta de clientes e pedidos

## Banco de dados
O projeto usa SQLite para facilitar a execução local sem configurar um servidor separado. O modelo é relacional e o esquema SQL está em `database/schema.sql`. Para reiniciar os dados, pare o servidor e exclua `database/levelup.db`; o banco será recriado na próxima execução.

## Observações para apresentação
- O pagamento é apenas uma simulação; não existe cobrança real.
- As imagens de demonstração são carregadas de URLs externas.
- A loja inicia com produtos de exemplo para permitir testar a interface. Eles podem ser editados ou removidos no painel administrativo.
- O projeto demonstra DWS (HTML/CSS/JS), POO (classes Python) e BD (SQLite, tabelas, chaves e relacionamentos).
