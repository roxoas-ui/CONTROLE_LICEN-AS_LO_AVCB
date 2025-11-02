# Guia de Deploy

Este documento lista os passos para preparar e publicar o projeto **Controle de Licencas Ambientais CRM** em producao.

## 1. Requisitos do servidor
- Python 3.11 ou 3.12 instalado.
- MySQL 8.x acessivel a partir do servidor de aplicacao.
- Conta ativa no SendGrid para envio de e-mails (opcional, mas recomendada).
- Acesso SSH para configurar variaveis de ambiente e servicos do sistema.

## 2. Configurar variaveis de ambiente
1. Copie `.env.example` para `.env`.
2. Substitua `SECRET_KEY`, credenciais do banco, `SENDGRID_API_KEY` e `FRONTEND_BASE_URL` pelos valores reais.
3. Exemplo PowerShell:
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```
4. Nunca versione o arquivo `.env` preenchido.

## 3. Instalar dependencias
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Migrar banco de dados
Enquanto as migracoes Alembic nao estiverem disponiveis, crie as tabelas manualmente com `app/database.py` ou scripts SQL fornecidos pelo time. Registre a pendencia para acompanhamento.

## 5. Testes
Execute os testes automatizados antes do deploy:
```bash
pytest
```

## 6. Executar aplicacao
### Opcao direta (uvicorn)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Para ambientes de homologacao com recarregamento restrito ao diretorio `app/`:
```bash
uvicorn app.main:app --reload --reload-dir app
```

### Opcao via systemd (Linux)
Crie `/etc/systemd/system/licencas.service`:
```ini
[Unit]
Description=Controle de Licencas FastAPI
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/licencas
EnvironmentFile=/opt/licencas/.env
ExecStart=/opt/licencas/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Depois execute:
```bash
sudo systemctl daemon-reload
sudo systemctl enable licencas
sudo systemctl start licencas
```

## 7. Proxy reverso (Nginx)
Encaminhe as requisicoes HTTPS para `127.0.0.1:8000`:
```nginx
server {
    listen 80;
    server_name licencas.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Configure SSL com Certbot ou ferramenta equivalente.

## 8. Checklist final
- [ ] `.env` preenchido e protegido.
- [ ] Conexao com banco validada (teste `SELECT 1`).
- [ ] `pytest` executado sem falhas.
- [ ] Servico uvicorn operacional e exposto via proxy.
- [ ] Logs monitorados (journalctl, servico de observabilidade ou similar).

## 9. Futuras melhorias
- Automatizar migracoes com Alembic.
- Criar pipeline CI/CD (GitHub Actions) para lint, testes e deploy.
- Empacotar imagem Docker para padronizar os builds.
