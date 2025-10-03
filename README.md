# Documentação do Projeto
## 📋 Índice

    Frontend

    Backend

    Docker Compose

    Testes Unitários

    Rotas Principais

## 🎨 Frontend
### Descrição

Aplicação web desenvolvida em Next.js com TypeScript para gerenciamento de usuários e clientes.
Tecnologias

    Next.js 14 - Framework React

    TypeScript - Tipagem estática

    Tailwind CSS - Estilização

    React Hook Form - Gerenciamento de formulários

    Zod - Validação de schemas

    TanStack Query - Gerenciamento de estado do servidor

    Lucide React - Ícones

## Estrutura do Projeto

```
frontend/
├── app/                    # App Router do Next.js
│   ├── login/             # Página de login
│   ├── register/          # Página de registro
│   ├── dashboard/         # Dashboard principal
│   ├── clients/           # Gerenciamento de clientes
│   └── layout.tsx         # Layout principal
├── components/            # Componentes reutilizáveis
│   ├── ui/               # Componentes de UI
│   ├── button.tsx        # Componente de botão
│   └── protected-route.tsx # Rota protegida
├── hooks/                 # Custom hooks
│   └── use-auth.ts       # Hook de autenticação
├── lib/                   # Utilitários e configurações
│   ├── validation.ts     # Schemas de validação Zod
│   └── api.ts            # Cliente HTTP
└── types/                 # Definições de tipos TypeScript
```
## Como Executar

```
docker compose up
```
Acesse o frontend em: http://localhost:3000/login

## 🚀 Backend
### Descrição

API REST desenvolvida em Python com FastAPI para autenticação e gerenciamento de usuários e clientes.
Tecnologias

    FastAPI - Framework web moderno

    Python 3.11+ - Linguagem de programação

    SQLAlchemy - ORM database

    PostgreSQL - Banco de dados

    JWT - Autenticação

    Pydantic - Validação de dados

    Alembic - Migrations de banco

    Pytest - Testes unitários

## Estrutura do Projeto

```
backend/
├── app/
│   ├── main.py           # Aplicação FastAPI principal
│   ├── models/           # Modelos de banco de dados
│   │   └── user.py       # Modelo de usuário
│   ├── schemas/          # Schemas Pydantic
│   │   ├── user.py       # Schema de usuário
│   │   └── client.py     # Schema de cliente
│   ├── api/              # Rotas da API
│   │   ├── endpoints/
│   │   │   ├── auth.py   # Rotas de autenticação
│   │   │   └── clients.py # Rotas de clientes
│   │   └── dependencies.py # Dependências FastAPI
│   ├── core/             # Configurações centrais
│   │   ├── config.py     # Configurações da aplicação
│   │   └── security.py   # Utilidades de segurança
│   └── database.py       # Configuração do banco
├── tests/                # Testes unitários
│   ├── test_auth.py      # Testes de autenticação
│   └── test_clients.py   # Testes de clientes
├── requirements.txt      # Dependências Python
└── Dockerfile           # Configuração do Docker
```

Acesse o backend em: http://localhost:8000/docs

## 🐳 Docker Compose
### Executar Aplicação Completa

```
# Clone o repositório
git clone <repository-url>

# Execute com Docker Compose
docker-compose up -d

# Ou para desenvolvimento com rebuild
docker-compose up -d --build
```

## Comandos Úteis

```
# Ver logs dos serviços
docker-compose logs -f

# Parar serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Executar comandos em um serviço específico
docker-compose exec backend python -m pytest
```

## 📊 Status de Implementação
## ⚠️ Limitações Atuais

Devido a restrições de tempo, não foi possível implementar todas as telas do frontend correspondentes aos endpoints disponíveis no backend. Abaixo está o status atual da implementação:
✅ Funcionalidades Implementadas

## Backend (Completo)

    ✅ Autenticação JWT (login/registro)

    ✅ CRUD completo de usuários

    ✅ CRUD completo de clientes

    ✅ Documentação automática (Swagger/OpenAPI)

    ✅ Validações com Pydantic

    ✅ Testes unitários

## Frontend (Parcial)

    ✅ Sistema de autenticação

    ✅ Página de login

    ✅ Página de registro de usuários

    ✅ Página de registro de clientes

    ✅ Listagem básica de clientes

    ✅ Proteção de rotas

    ✅ Integração com API

❌ Funcionalidades Pendentes no Frontend

Gestão de Clientes

    ❌ Edição de clientes existentes

    ❌ Exclusão de clientes

    ❌ Visualização detalhada de cliente

    ❌ Paginação na listagem

    ❌ Filtros e busca

Gestão de Usuários

    ❌ Perfil do usuário logado

    ❌ Edição de perfil

    ❌ Alteração de senha

    ❌ Listagem de usuários (admin)

Features Avançadas

    ❌ Dashboard com métricas

    ❌ Upload de arquivos

    ❌ Notificações

    ❌ Relatórios

    ❌ Exportação de dados

## 🎯 Próximos Passos Recomendados

Para completar a aplicação, seriam necessárias as seguintes implementações:

    Páginas de CRUD completo para clientes

        Tela de edição (/clients/[id]/edit)

        Tela de detalhes (/clients/[id])

        Modal de confirmação para exclusão

    Melhorias na UX/UI

        Loading states em todas as ações

        Confirmações para ações destrutivas

        Mensagens de sucesso/erro melhoradas

        Design responsivo refinado

    Features adicionais

        Paginação na listagem de clientes

        Sistema de busca e filtros

        Dashboard com gráficos e métricas

        Sistema de permissões de usuário

## 🔧 Trabalho Futuro

O backend está 100% funcional e pronto para ser consumido. O frontend possui uma base sólida com:

    Arquitetura bem estruturada

    Sistema de autenticação funcionando

    Integração com API

    Componentes reutilizáveis

    Adicionar cache no backend(Redis)

As funcionalidades pendentes podem ser implementadas incrementalmente seguindo os mesmos padrões já estabelecidos no código.