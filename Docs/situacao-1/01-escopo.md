# 01 – Escopo do Projeto (revisado) – Bonsai Store

**Disciplina:** Projeto Integrador Transdisciplinar em Engenharia de Software II
**Situação-Problema 1:** Revisão, Planejamento e Modelagem (Kaizen)
**Versão:** 2 (substitui a versão do PI I, mantida em `Docs/01 – Escopo_do_Projeto.md.txt` para histórico)

## 1. Objetivo do sistema

A Bonsai Store é uma aplicação web para a venda de bonsais. Ela permite que o lojista cadastre produtos (com foto e estoque) e clientes, e que um comprador monte um carrinho e finalize pedidos, com baixa automática do estoque e acompanhamento do status de cada pedido.

## 2. Ponto de partida (PI I) e problemas identificados

No Projeto Integrador I o escopo era um MVP mínimo: página inicial, lista **estática** de bonsais e uma simulação de carrinho. Na revisão desta etapa foram identificados os seguintes problemas:

1. Os dados do catálogo não eram persistidos: o banco tinha uma única tabela (`produtos`) e a lista era estática.
2. Não havia como registrar um pedido, então o "carrinho" era só uma ideia e o sistema não cumpria o objetivo de vender.
3. O código ficava separado por área (Backend, Database, Frontend) e não seguia o padrão MVC exigido.
4. Não havia validação de dados nem tratamento de erros: dados inválidos podiam ser gravados.
5. Não havia testes automatizados.
6. Os arquivos do back-end estavam salvos como `.py.txt`, portanto não executavam.

## 3. Escopo revisado (versão atual)

### 3.1 Requisitos funcionais

| Código | Requisito |
|---|---|
| RF01 | Exibir a vitrine de bonsais com foto, espécie, descrição, preço e disponibilidade |
| RF02 | Adicionar um produto ao carrinho, respeitando o estoque disponível |
| RF03 | Remover um item do carrinho |
| RF04 | Finalizar o pedido para um cliente, gravando o pedido e seus itens e baixando o estoque |
| RF05 | Cadastrar, listar, editar e excluir produtos, com envio de foto |
| RF06 | Cadastrar, listar, editar e excluir clientes |
| RF07 | Listar os pedidos e consultar o detalhe de cada um |
| RF08 | Alterar o status do pedido (Pendente, Pago, Enviado, Entregue) |
| RF09 | Validar os formulários e exibir mensagens de erro claras |

### 3.2 Requisitos não funcionais

| Código | Requisito |
|---|---|
| RNF01 | **Arquitetura:** back-end em Python (Flask) seguindo o padrão MVC |
| RNF02 | **Persistência:** banco de dados relacional SQLite, com chaves estrangeiras e restrições de integridade |
| RNF03 | **Usabilidade:** interface simples, consistente e com retorno imediato ao usuário (faixas de sucesso e de erro) |
| RNF04 | **Qualidade:** testes automatizados com pytest (34 testes) |
| RNF05 | **Segurança básica:** exclusões feitas somente por requisição POST com confirmação; uploads limitados a PNG, JPG, GIF e WEBP de até 3 MB |
| RNF06 | **Manutenibilidade:** código separado em models, controllers e templates, versionado no GitHub |

### 3.3 Regras de negócio

- O preço de um produto deve ser maior que zero e o estoque não pode ser negativo.
- O e-mail do cliente deve ser válido e único.
- Um produto sem estoque aparece como "Esgotado" e não pode ser adicionado ao carrinho.
- O pedido guarda o preço do produto no momento da compra (`preco_unitario`), de modo que mudanças posteriores de preço não alteram pedidos antigos.
- Se o estoque acabar entre a escolha e a finalização, o pedido é desfeito por completo (transação com *rollback*).
- Um produto que já participou de um pedido não pode ser excluído; o mesmo vale para clientes com pedidos.

### 3.4 Fora do escopo (limitações assumidas)

- Não há login nem controle de acesso: as telas de gerenciamento (produtos, clientes e pedidos) ficam abertas.
- Não há integração com meios de pagamento nem cálculo de frete.
- O carrinho é guardado na sessão do navegador e não persiste entre dispositivos.

## 4. Melhorias Kaizen aplicadas

| # | Antes (PI I) | Depois (PI II) | Motivo |
|---|---|---|---|
| 1 | Lista de produtos estática | Catálogo vindo do banco, com CRUD completo e fotos | Dados reais e gerenciáveis |
| 2 | Carrinho apenas simulado | Carrinho funcional e pedidos gravados com baixa de estoque | Cumprir o objetivo de vender |
| 3 | Uma tabela (`produtos`) | Quatro tabelas relacionadas (produto, cliente, pedido, item_pedido) | Representar clientes e pedidos sem redundância |
| 4 | Pastas por área (Backend, Database, Frontend) | Estrutura MVC (`models`, `controllers`, `templates`) | Exigência da disciplina e melhor manutenção |
| 5 | Sem validação de dados | Validação no Model e mensagens claras na tela | Evitar dados inválidos e orientar o usuário |
| 6 | Sem testes | 34 testes automatizados (unitários e de integração) | Garantir que as funções principais não quebrem |
| 7 | Arquivos `.py.txt` | Arquivos `.py` executáveis | Corrigir um erro que impedia a execução |
| 8 | Telas sem imagens | Fotos nos produtos e vitrine em cartões | Melhor experiência do usuário |

## 5. Feedback inicial dos colegas sobre o planejamento

A Situação 1 pede a opinião de colegas sobre o planejamento antes da codificação. Registrar abaixo os comentários recebidos e o que foi ajustado.

| Colega | Data | Comentário sobre o planejamento | Ajuste feito |
|---|---|---|---|
| *(preencher)* | | | |
| *(preencher)* | | | |

## 6. Estrutura do repositório

```
bonsai-store/
├── app/
│   ├── models/        (regras de negócio, validações e acesso ao banco)
│   ├── controllers/   (rotas de cada área)
│   ├── templates/     (views em HTML)
│   ├── static/        (CSS e fotos enviadas)
│   └── database.py    (criação das tabelas e conexão)
├── tests/             (testes automatizados com pytest)
├── docs/              (documentação das situações 1, 2 e 3)
├── run.py
└── requirements.txt
```
