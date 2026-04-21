# 🚀 Optio

## 📌 Descrição

O **Optio** é uma aplicação web desenvolvida para facilitar a busca, organização e visualização de cursos de forma prática e eficiente.

A proposta do sistema é centralizar informações relevantes sobre cursos e permitir que usuários encontrem rapidamente opções que atendam às suas necessidades.

### 💡 Problema que resolve

Atualmente, encontrar cursos relevantes pode ser um processo desorganizado, com informações espalhadas em diferentes plataformas.

O Optio resolve isso ao:
- Centralizar dados em um único sistema
- Permitir busca e filtragem eficiente
- Exibir informações claras e organizadas

---

## 🛠️ Tecnologias

O projeto foi desenvolvido com uma stack moderna e simples, focada em produtividade e deploy rápido:

- **Django** → Framework principal (monólito)
- **PostgreSQL** → Banco de dados relacional
- **Docker** → Padronização de ambiente
- **GitHub Actions** → CI/CD automatizado
- **Render** → Deploy gratuito na nuvem

---

## 🏗️ Arquitetura

A arquitetura do sistema foi pensada para ser simples, funcional e escalável:

### 🔹 Monólito (Django)
- Backend e lógica central no Django
- Responsável por API, regras de negócio e renderização

### 🔹 Worker separado
- Processo independente para tarefas assíncronas (ex: processamento de dados)
- Pode ser executado como um serviço separado no Render

### 🔹 Banco de dados compartilhado
- PostgreSQL centralizado
- Utilizado tanto pelo monólito quanto pelo worker

### 📌 Resumo da arquitetura:

[ Cliente ]
     ↓
[ Django (Monólito) ] ←→ [ PostgreSQL ]
           ↓
     [ Worker ]

---

## 🚀 Como rodar localmente

### Pré-requisitos:
- Docker
- Docker Compose

### Passos:

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/optio.git

# Acesse a pasta do projeto
cd optio

# Suba os containers
docker-compose up --build
```

A aplicação estará disponível em:
http://localhost:8000

---

## 🌐 Deploy

O sistema está hospedado no Render (plano gratuito).

🔗 **Acesse aqui:**  
https://seu-app.onrender.com

---

## 🎯 Funcionalidades (MVP)

- 📚 Listagem de cursos
- 🔎 Busca e filtro de cursos
- 📄 Exibição de detalhes de cada curso
- 💾 Persistência de dados no banco PostgreSQL

---

## 📦 Estrutura do Projeto (sugestão)

optio/
│
├── app/                
├── worker/             
├── docker/             
├── .github/workflows/  
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

---

## 👩‍💻 Equipe de Desenvolvimento

- Felipe de Brito  
- Janderson Lima
- Joana Elise    
- Maria Eduarda Vitorino  

---

## ✅ Objetivo do Projeto

Este projeto foi desenvolvido com foco em:

- Simplicidade de arquitetura
- Facilidade de deploy
- Boas práticas de desenvolvimento
- Estrutura profissional para portfólio
