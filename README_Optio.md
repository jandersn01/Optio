# 🚀 Optio

## 📌 Descrição

O **Optio** é uma aplicação web desenvolvida para centralizar e facilitar a busca por cursos de pós-graduação gratuitos no Brasil.

A proposta do sistema é permitir que usuários informem critérios de busca — como palavras-chave, área de conhecimento, modalidade e estado — e recebam posteriormente os resultados processados de forma assíncrona.

O projeto utiliza uma arquitetura baseada em **Django**, **PostgreSQL**, **RabbitMQ** e um **worker separado** para processamento em segundo plano.

---

## 💡 Problema que resolve

Atualmente, encontrar cursos gratuitos de pós-graduação pode ser um processo demorado e desorganizado, pois as informações estão espalhadas em diferentes sites, instituições e plataformas.

O Optio busca resolver esse problema ao:

- Centralizar solicitações de busca em uma aplicação web;
- Permitir filtros estruturados por área, modalidade e estado;
- Processar buscas de forma assíncrona;
- Preparar o sistema para envio posterior de resultados por e-mail;
- Organizar as solicitações em banco de dados para rastreabilidade.

---

## 🛠️ Tecnologias utilizadas

O projeto utiliza as seguintes tecnologias:

- **Python** — linguagem principal do projeto;
- **Django** — framework web utilizado para backend, views, forms, models e admin;
- **PostgreSQL** — banco de dados relacional utilizado pela aplicação;
- **RabbitMQ** — broker de mensagens utilizado para processamento assíncrono;
- **Pika** — biblioteca Python usada para comunicação com o RabbitMQ;
- **Docker** — utilizado para padronizar o ambiente de desenvolvimento;
- **Docker Compose** — utilizado para orquestrar os serviços da aplicação;
- **HTML/Templates Django** — utilizado para renderização inicial das páginas.

> Não é necessário instalar PostgreSQL ou RabbitMQ diretamente na máquina. Esses serviços rodam via Docker.

---

## 🏗️ Arquitetura do Projeto

A arquitetura atual é composta por quatro serviços principais:

```text
[ Usuário ]
    ↓
[ Django Web ]
    ↓
[ PostgreSQL ]

[ Django Web ]
    ↓ publica mensagem
[ RabbitMQ ]
    ↓ entrega mensagem
[ Worker ]
```

### 🔹 Web / Django

O serviço `web` executa a aplicação Django.

Ele é responsável por:

- Renderizar o formulário de busca;
- Validar os dados enviados pelo usuário;
- Salvar a solicitação no PostgreSQL;
- Publicar uma mensagem no RabbitMQ;
- Disponibilizar o Django Admin.

### 🔹 PostgreSQL

O serviço `db` executa o banco de dados PostgreSQL.

Ele armazena os dados persistentes da aplicação, incluindo:

- Usuários do Django;
- Migrations;
- Solicitações de busca (`SearchRequest`);
- Demais tabelas futuras do sistema.

Os dados são persistidos em um volume Docker chamado `postgres_data`.

### 🔹 RabbitMQ

O serviço `rabbitmq` funciona como broker de mensagens.

Ele recebe mensagens publicadas pelo Django e as disponibiliza para o worker consumir.

No fluxo atual:

1. Django publica uma `SearchRequest`;
2. RabbitMQ coloca a mensagem na fila;
3. Worker consome a mensagem.

A interface web do RabbitMQ fica disponível em:

```text
http://localhost:15672
```

Credenciais padrão:

```text
Usuário: guest
Senha: guest
```

### 🔹 Worker

O serviço `worker` é um processo Python separado da aplicação web.

Ele é responsável por:

- Conectar ao RabbitMQ;
- Escutar a fila de solicitações de busca;
- Consumir mensagens do tipo `search_requested`;
- Registrar no log os dados recebidos.

No futuro, esse worker será responsável por:

- Buscar dados em fontes externas;
- Integrar com ferramentas de scraping;
- Processar dados com LLM;
- Salvar resultados;
- Disparar notificações/e-mails.

---

## 📦 Estrutura do Projeto

Estrutura geral esperada:

```text
Optio/
│
├── app/
│   ├── manage.py
│   ├── optio/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   └── search/
│       ├── choices.py
│       ├── forms.py
│       ├── models.py
│       ├── publishers.py
│       ├── urls.py
│       ├── views.py
│       ├── admin.py
│       ├── templates/
│       │   └── search/
│       │       └── search_request_form.html
│       └── migrations/
│
├── worker/
│   └── worker.py
│
├── docker/
│   ├── web/
│   │   └── Dockerfile
│   └── worker/
│       └── Dockerfile
│
├── specs/
│   └── requirements/
│       └── proposta_de_projeto.md
│
├── docker-compose.yml
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 📁 Explicação das principais pastas e arquivos

### `app/`

Contém o projeto Django.

É dentro dessa pasta que ficam:

- `manage.py`;
- Configurações do projeto;
- Apps Django;
- Templates;
- Models;
- Forms;
- Views.

### `app/optio/`

Contém as configurações principais do projeto Django.

Arquivos importantes:

- `settings.py` — configurações do Django, banco de dados, apps instalados etc.;
- `urls.py` — rotas principais do projeto;
- `wsgi.py` e `asgi.py` — arquivos usados para execução da aplicação.

### `app/search/`

App Django responsável pelo fluxo de solicitação de busca.

Arquivos principais:

- `models.py` — define o model `SearchRequest`;
- `choices.py` — centraliza choices de área, modalidade, estado e status;
- `forms.py` — define o formulário de solicitação de busca;
- `views.py` — recebe `GET`/`POST` do formulário;
- `publishers.py` — encapsula a publicação de mensagens no RabbitMQ;
- `urls.py` — define a rota `/busca/`;
- `admin.py` — registra o model no Django Admin;
- `templates/search/` — contém o template HTML do formulário.

### `worker/`

Contém o código do worker assíncrono.

Atualmente, o `worker.py`:

- Conecta ao RabbitMQ;
- Aguarda mensagens;
- Consome mensagens da fila configurada;
- Imprime no log os dados da solicitação de busca.

### `docker/`

Contém os Dockerfiles da aplicação.

#### `docker/web/Dockerfile`

Define a imagem do serviço Django.

#### `docker/worker/Dockerfile`

Define a imagem do worker.

### `docker-compose.yml`

Arquivo responsável por subir todos os serviços do ambiente:

- `web`;
- `worker`;
- `db`;
- `rabbitmq`.

### `requirements.txt`

Lista as dependências Python utilizadas pelo projeto.

Exemplos:

- Django;
- psycopg2-binary;
- pika;
- python-dotenv;
- requests;
- selenium.

### `.env`

Arquivo de variáveis de ambiente.

Ele contém configurações locais como:

- Nome do banco;
- Usuário do banco;
- Senha do banco;
- Host do PostgreSQL;
- Host do RabbitMQ;
- Nome da fila.

Esse arquivo é necessário para rodar o projeto localmente.

---

## ⚙️ Configuração do ambiente

### Pré-requisitos

Para rodar o projeto, você precisa ter instalado:

- Docker;
- Docker Compose;
- Git.

Você não precisa instalar Python, PostgreSQL ou RabbitMQ diretamente na sua máquina, pois tudo roda em containers.

---

## 🔐 Arquivo `.env`

Antes de subir o projeto, crie um arquivo `.env` na raiz do projeto.

Exemplo:

```env
DEBUG=1
SECRET_KEY=dev-secret-key

POSTGRES_DB=optio
POSTGRES_USER=optio_user
POSTGRES_PASSWORD=optio_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

RABBITMQ_HOST=rabbitmq
RABBITMQ_QUEUE=search_requests
```

> Em ambiente real, nunca utilize senhas simples ou `SECRET_KEY` de desenvolvimento.

---

## 🚀 Como rodar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/optio.git
```

Entre na pasta do projeto:

```bash
cd Optio
```

### 2. Criar o arquivo `.env`

Crie o arquivo `.env` na raiz do projeto usando o exemplo acima.

### 3. Subir os containers

```bash
docker compose up --build
```

Esse comando irá subir os serviços:

- Django;
- PostgreSQL;
- RabbitMQ;
- Worker.

A aplicação Django ficará disponível em:

```text
http://localhost:8000
```

A interface do RabbitMQ ficará disponível em:

```text
http://localhost:15672
```

### 4. Rodar as migrations

Em outro terminal, com os containers rodando, execute:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Isso cria as tabelas no PostgreSQL.

### 5. Criar um superusuário

Para acessar o Django Admin:

```bash
docker compose exec web python manage.py createsuperuser
```

Depois acesse:

```text
http://localhost:8000/admin/
```

### 6. Acessar o formulário de busca

A rota atual do formulário é:

```text
http://localhost:8000/busca/
```

Ao enviar o formulário:

1. O Django valida os dados;
2. Salva uma `SearchRequest` no PostgreSQL;
3. Publica uma mensagem no RabbitMQ;
4. O worker consome essa mensagem;
5. O usuário recebe uma mensagem de confirmação.

---

## 🧪 Como verificar se está funcionando

### Ver logs do worker

```bash
docker compose logs -f worker
```

Ao enviar uma busca pelo formulário, o worker deve exibir informações como:

```text
Nova solicitação de busca recebida
ID da busca: 1
E-mail de notificação: usuario@email.com
Palavras-chave: engenharia de software
Área: engenharias
Modalidade: ead
Estado: PB
```

### Verificar filas no RabbitMQ

```bash
docker compose exec rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged consumers
```

Resultado esperado:

```text
name              messages_ready    messages_unacknowledged    consumers
search_requests   0                 0                          1
```

O valor `consumers = 1` indica que o worker está conectado à fila.

### Acessar o shell do banco pelo Django

```bash
docker compose exec web python manage.py dbshell
```

Dentro do shell do PostgreSQL, você pode listar as tabelas:

```sql
\dt
```

Para sair:

```sql
\q
```

---

## 🗄️ Banco de dados

O projeto utiliza PostgreSQL rodando em container.

O serviço do banco é definido no `docker-compose.yml` como:

```text
db
```

Por isso, no Django, o host do banco deve ser:

```text
db
```

e não:

```text
localhost
```

O `localhost` dentro do container `web` apontaria para o próprio container `web`, não para o PostgreSQL.

---

## ⚠️ Resetando o banco local

Caso as credenciais do PostgreSQL tenham sido alteradas depois que o volume já foi criado, pode ocorrer erro de autenticação.

Nesse caso, em ambiente de desenvolvimento, é possível resetar o banco com:

```bash
docker compose down -v
```

Depois suba novamente:

```bash
docker compose up --build
```

E rode as migrations:

```bash
docker compose exec web python manage.py migrate
```

> Atenção: o comando abaixo apaga os dados locais do banco:
>
> ```bash
> docker compose down -v
> ```
>
> Use apenas em ambiente de desenvolvimento.

---

## 🧭 Fluxo atual da aplicação

Fluxo implementado até o momento:

```text
Usuário acessa /busca/
        ↓
Preenche o formulário
        ↓
Django valida os dados
        ↓
SearchRequest é salva no PostgreSQL
        ↓
Django publica mensagem JSON no RabbitMQ
        ↓
Worker consome a mensagem
        ↓
Worker registra os dados no log
```

---

## 🎯 Funcionalidades atuais

- Formulário de solicitação de busca;
- Validação de entrada com Django Forms;
- Choices para área, modalidade, estado e status;
- Persistência de solicitações no PostgreSQL;
- Publicação de mensagem no RabbitMQ;
- Worker assíncrono consumindo mensagens;
- Django Admin para gerenciamento dos registros;
- Ambiente local totalmente conteinerizado com Docker.

---

## 🚧 Próximas etapas

Funcionalidades ainda previstas:

- Autenticação e cadastro de usuários;
- Processamento real da busca;
- Integração com fontes externas;
- Integração com scraping/Firecrawl;
- Integração com LLM;
- Armazenamento dos resultados;
- Envio de resultados por e-mail;
- Painel de histórico de buscas;
- Favoritos;
- Alertas salvos;
- Testes automatizados;
- Melhorias visuais no frontend.

---

## 👩‍💻 Equipe de Desenvolvimento

- Felipe de Brito;
- Janderson Lima;
- Joana Elise;
- Maria Eduarda Vitorino.

---

## ✅ Objetivo do Projeto

Este projeto tem como objetivo desenvolver uma aplicação web capaz de facilitar a busca por cursos de pós-graduação gratuitos, utilizando uma arquitetura simples, reprodutível e preparada para processamento assíncrono.

A base atual prioriza:

- Clareza arquitetural;
- Ambiente padronizado com Docker;
- Persistência com PostgreSQL;
- Processamento assíncrono com RabbitMQ;
- Separação de responsabilidades entre web e worker;
- Evolução incremental do sistema.
