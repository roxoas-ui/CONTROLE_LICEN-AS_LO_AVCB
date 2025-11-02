# Controle de Licenças Ambientais CRM

Sistema CRM para gestão de licenças ambientais, condicionantes, resíduos e AVCB com backend em FastAPI, banco MySQL remoto e frontend básico com Tailwind CSS via CDN.

## Tecnologias principais

- Python 3.11+
- FastAPI
- SQLAlchemy + MySQL Connector
- Tailwind CSS (CDN)
- SendGrid (notificações)
- FPDF2 (relatórios PDF)

## Pré-requisitos

1. Python 3.11 ou 3.12 instalado (SQLAlchemy ainda não suporta Python 3.14).
2. Ambiente virtual configurado (recomendado).
3. Acesso ao banco de dados MySQL informado pelo cliente.
4. Chave de API do SendGrid (opcional para desenvolvimento, obrigatório para envio real de e-mails).

## Configuração do ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edite .env com as credenciais reais e chaves necessárias
```

## Execução da aplicação

```powershell
uvicorn app.main:app --reload
```

A API ficará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

## Estrutura principal

- `app/main.py`: inicialização FastAPI e roteadores.
- `app/api/`: endpoints REST (auth, usuários, licenças, resíduos, AVCB, relatórios, dashboard).
- `app/models/`: modelos SQLAlchemy.
- `app/schemas/`: modelos Pydantic para requisições/respostas.
- `app/crud/`: operações CRUD.
- `app/services/`: serviços auxiliares (e-mail, relatórios).
- `app/utils/file_storage.py`: utilitário para upload de PDFs.
- `uploads/`: diretório padrão para armazenamento de documentos.

## Testes

```powershell
pytest
```

## Próximos passos sugeridos

- Implementar autenticação JWT no frontend e consumo das rotas.
- Integrar schedulers (cron) para enviar notificações automáticas.
- Criar migrações usando Alembic.
- Criar interface frontend completa ou painel administrativo.
