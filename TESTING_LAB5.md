# Лабораторная работа №5: Комплексное тестирование

## 1. Тестовая модель приложения

### 1.1 Критические пользовательские сценарии
- Регистрация, вход, обновление токена, выход.
- Загрузка файла (авторизованный и анонимный пользователь).
- Обработка файла, скачивание pre-signed URL, удаление.
- Фильтрация, сортировка, пагинация списка файлов.
- Получение совета из внешнего API и fallback при отказе.

### 1.2 Ключевые бизнес-правила и ограничения
- Доступ к файлам только владельцу (`user_id`) или владельцу сессии (`session_id`).
- Сохранение файла возможно только в статусе `processed`/`saved`.
- Проверка ограничений upload по MIME и размеру.
- Обязательная авторизация для приватных endpoint'ов.
- Внешний API не должен ломать сценарий при отказах.

### 1.3 Области повышенного риска
- JWT/refresh-flow и истечение сессии.
- Проверка прав доступа (401/403).
- Интеграция с S3/MinIO.
- Интеграция со сторонним API с retry/cache/fallback.

## 2. Реализованные тесты backend

- `tests/backend/unit/test_external_tip_service.py`
  - fallback без API-ключа;
  - кеширование ответа;
  - fallback при сетевой ошибке.
- `tests/backend/integration/test_auth_endpoints.py`
  - register/login/me;
  - refresh-flow;
  - валидация входных данных (422).
- `tests/backend/integration/test_files_endpoints.py`
  - anonymous upload + list;
  - 401 без `X-Session-ID`;
  - 403 при доступе другого пользователя;
  - 400 при попытке process non-image.

## 3. Реализованные тесты frontend

- `frontend/src/services/auth.test.ts`
  - сохранение токенов;
  - очистка токенов при logout;
  - проверка `isAuthenticated`.
- `frontend/src/services/files.test.ts`
  - ошибки при download/view без токена и `session_id`.
- `frontend/src/components/Login.test.tsx`
  - валидация пустых полей;
  - успешный переход после входа.
- `frontend/src/components/PrivacyTipCard.test.tsx`
  - успешная загрузка внешнего совета;
  - отображение ошибки.

## 4. Сквозные (E2E) проверки

- `frontend/e2e/smoke.spec.ts`
  - вход на главную и переход на страницу логина;
  - переход на несуществующий маршрут и проверка 404.

## 5. Тестовая инфраструктура

- Backend:
  - `pytest.ini` с маркерами `unit/integration/e2e`;
  - изолированная SQLite БД в фикстурах (`tests/backend/conftest.py`);
  - подмена зависимостей FastAPI (`get_db`);
  - моки внешних зависимостей.
- Frontend:
  - `vitest.config.ts` + `src/test/setup.ts`;
  - `playwright.config.ts` для E2E.

## 6. Метрики и правила

- Минимальные целевые покрытия:
  - backend: 70%;
  - frontend: 60%.
- Разделение запусков:
  - быстрые unit;
  - integration;
  - e2e.
- Именование:
  - `test_<module>_<behavior>_<expected>`.

## 7. Команды запуска

- Backend:
  - `python -m pytest -m "unit or integration" --cov=app --cov-report=term-missing`
- Frontend:
  - `npm run test`
  - `npm run test:coverage`
- E2E:
  - `npm run e2e`
