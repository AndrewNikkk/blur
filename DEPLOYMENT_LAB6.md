# Лабораторная работа №6: Контейнеризация и автоматизация развертывания

## 1. Архитектура контейнеризации

### Сервисы
- `reverse-proxy` (Nginx) — единая точка входа на `http://localhost`.
- `frontend` (Nginx + build React) — отдает статические файлы SPA.
- `backend` (FastAPI + Uvicorn) — API и бизнес-логика.
- `db` (PostgreSQL) — основная БД приложения.
- `minio` (S3-compatible) — объектное хранилище для файлов.

### Сетевая схема
- Все контейнеры работают в bridge-сети `app_net`.
- Внешний трафик идет в `reverse-proxy:80`.
- Проксирование:
  - `/` -> `frontend:80`
  - `/api/*` -> `backend:8000` (с переписыванием префикса `/api`).
- `backend` подключается к:
  - `db:5432`
  - `minio:9000`

## 2. Контейнеризация компонентов

- `Dockerfile.backend` — сборка backend-образа FastAPI.
- `frontend/Dockerfile.frontend` — multi-stage сборка React + отдача через Nginx.
- `infra/nginx/nginx.conf` — reverse proxy правила.
- `.dockerignore` — исключает тяжелые/секретные/временные файлы.

## 3. Оркестрация через Docker Compose

Файл: `docker-compose.yml`

Реализовано:
- единый запуск всех сервисов;
- порты/сети/тома/переменные окружения;
- `healthcheck` для `db`, `minio`, `backend`, `frontend`, `reverse-proxy`;
- `depends_on` с условием `service_healthy`.

Запуск:

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

Остановка:

```bash
docker compose down
```

Полная очистка:

```bash
docker compose down -v
```

## 4. Безопасная и управляемая конфигурация

- Все параметры вынесены в `.env`.
- Пример конфигурации: `.env.example`.
- Секреты не должны коммититься:
  - не хранить реальные `SECRET_KEY`, `REFRESH_SECRET_KEY`, API-ключи в репозитории;
  - использовать secrets в CI/CD и на хосте.

## 5. CI/CD

Workflow: `.github/workflows/ci-cd.yml`

### CI
- backend tests + coverage;
- frontend lint + tests;
- сборка Docker-образов backend/frontend;
- валидация `docker compose config`.

### CD
- для ветки `main` есть job `deploy`;
- деплой выполняется при наличии секретов:
  - `DEPLOY_HOST`
  - `DEPLOY_USER`
  - `DEPLOY_SSH_KEY`
- сценарий: `git pull` + `docker compose up -d --build`.

## 6. Проверка итоговой конфигурации

### 6.1 Воспроизводимость
- `cp .env.example .env`
- `docker compose up -d --build`

### 6.2 Корректность сервисов
- `docker compose ps`
- `docker compose logs backend --tail=100`
- `curl http://localhost/api/`

### 6.3 Сохранение функциональности MVP
- Проверить авторизацию, загрузку/обработку файла, просмотр/скачивание, профиль.
- Запустить тесты:
  - `python -m pytest tests/backend --cov=app --cov-report=term-missing`
  - `cd frontend && npm run test`

### 6.4 Устойчивость к типовым сбоям

1) Падение backend:
```bash
docker compose stop backend
docker compose ps
docker compose start backend
```

2) Недоступность MinIO:
```bash
docker compose stop minio
docker compose logs backend --tail=50
docker compose start minio
```

3) Ошибка внешнего API:
- отключить интернет/подменить `EXTERNAL_TIP_API_KEY`;
- убедиться, что backend возвращает fallback-совет.

4) Неуспешная миграция/инициализация БД:
- временно указать неверный `POSTGRES_PASSWORD` в `.env`;
- проверить, что backend не перейдет в healthy;
- вернуть корректные параметры и перезапустить:
```bash
docker compose up -d --build
```
