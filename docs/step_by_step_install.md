Guia passo-a-passo (Windows PowerShell) — criar backend Laravel e integrar scaffold

1) Verifique requisitos
- PHP 8.1+
- Git
- Node.js 18+
- Chocolatey (opcional) para instalar ferramentas

2) Instalar Composer (se necessário)
Baixe e execute: https://getcomposer.org/Composer-Setup.exe
Verifique:
```powershell
composer --version
```

3) Rodar o script de bootstrap (recomendado)
Abra PowerShell como usuário (ou administrador se necessário):
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
cd "C:\Users\roxoa\OneDrive\PROGRAMADOR JUNIOR\NOVO CONTROLE DE LICENCAS\laravel-scaffold\scripts"
.\bootstrap.ps1 -RunNow
```
O script criará o diretório `backend/`, criará o projeto Laravel 10, copiará os arquivos do scaffold, instalará dependências e rodará as migrations e seeds.

4) Passos manuais (alternativa ao bootstrap)
```powershell
cd "C:\Users\roxoa\OneDrive\PROGRAMADOR JUNIOR\NOVO CONTROLE DE LICENCAS"
composer create-project laravel/laravel backend "10.*"
cd backend
# Copiar arquivos do scaffold (exemplo)
Copy-Item -Path "..\laravel-scaffold\database\migrations\*" -Destination ".\database\migrations\" -Recurse
Copy-Item -Path "..\laravel-scaffold\app\*" -Destination ".\app\" -Recurse
Copy-Item -Path "..\laravel-scaffold\routes\*" -Destination ".\routes\" -Recurse
Copy-Item -Path "..\laravel-scaffold\resources\*" -Destination ".\resources\" -Recurse

composer require spatie/laravel-permission barryvdh/laravel-dompdf phpoffice/phpspreadsheet pragmarx/google2fa-laravel
npm install
npm run build
php artisan key:generate
php artisan migrate
php artisan db:seed
php artisan storage:link
php artisan serve
```

5) Pós-instalação
- Configure `.env` com DB, AWS, MAIL and QUEUE settings
- Registrar `RepositoryServiceProvider` em `config/app.php`
- Publicar configs do spatie: `php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"`
- Testar rotas: `http://localhost:8000/licenses`

6) Executar agendador no Windows
- Configurar Task Scheduler para executar `php artisan schedule:run` a cada minuto.

Se quiser, eu posso executar o script de bootstrap aqui (posso rodá-lo no terminal) — diga se autoriza e eu executo (depois confirmo resultados).