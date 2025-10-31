# Arquitetura proposta - Novo Controle de Licenças

Visão geral
- Backend: Laravel 10 (MVC + Services + Repositories)
- Banco: PostgreSQL 14+
- Filas: Redis + Laravel Queues
- Storage: local para desenvolvimento / S3 para produção
- Autenticação: Laravel Breeze ou Sanctum + 2FA (Google Authenticator)
- ACL: spatie/laravel-permission
- Frontend: Blade + Bootstrap 5 (ou Inertia + Vue/React)
- Realtime: Laravel Echo + Pusher/Redis para notificações in-app

Camadas
- Controllers: validação e resposta HTTP
- Services: regras de negócio e orquestração
- Repositories: acesso ao banco, queries complexas
- Jobs: tarefas assíncronas (envio de e-mails, geração de relatórios, OCR)
- Events/Listeners: audit logs e notificações

Contrato mínimo (exemplo)
- Inputs: JSON via API ou formulário web
- Outputs: JSON padronizado (data, meta, errors)
- Erros: 4xx para cliente, 5xx para erro servidor

Modelos principais e relações (resumido)
- Client 1:N Project
- Project 1:N License
- License 1:N Conditional
- License 1:N Attachment
- License 1:N Process
- License 1:N Avcb
- Avcb 1:N Attachment
- Conditional 1:N ConditionalExecution (historical)
- User N:M Project (permissions scoped)

Observações operacionais
- Indexar colunas de pesquisa (full-text) para título, número, descrição
- Usar JSONB para campos dinâmicos/personalizáveis
- Audits: tabela separada com who/what/when/context
- Backups e retention para storage de documentos

Segurança
- Validar uploads (mime, tamanho, antivirus se possível)
- ACL granular por projeto
- 2FA para perfis de maior privilégio
- TLS/HTTPS obrigatório em produção
