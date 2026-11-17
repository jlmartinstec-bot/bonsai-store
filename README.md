# Bonsai Store

Loja virtual de bonsais (Projeto Integrador Transdisciplinar - Engenharia de Software II).

## Funcionalidades

- Vitrine de bonsais com foto, preço e botão de carrinho
- Cadastro de produtos (listar, cadastrar, editar, excluir, enviar foto)
- Cadastro de clientes
- Carrinho de compras e finalização de pedidos (com baixa automática de estoque)
- Acompanhamento de pedidos e alteração de status
- Validação de formulários e tratamento de erros com mensagens claras

## Como rodar

```
python -m pip install -r requirements.txt
python run.py
```

Depois abra http://127.0.0.1:5000 no navegador.

## Como rodar os testes

```
python -m pytest
```

## Estrutura (padrão MVC)

- `app/models`: regras de negócio, validações e acesso ao banco (produto, cliente, carrinho, pedido)
- `app/controllers`: controladores (rotas) de cada área
- `app/templates`: views (HTML)
- `app/static`: CSS e fotos enviadas (`uploads`)
- `app/database.py`: criação das tabelas e conexão com o SQLite
- `tests`: testes automatizados (pytest)
- `docs`: documentação de cada situação-problema

## Banco de dados

SQLite, com 4 tabelas: `produto`, `cliente`, `pedido` e `item_pedido`.
O arquivo `bonsai.db` é criado automaticamente na primeira execução.
