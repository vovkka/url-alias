# URL Alias Service

Сервис преобразования длинных URL в короткие уникальные URL с возможностью управления ссылками и сбора статистики переходов.

## Технологии

- **Python 3.12**
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy + AsyncPG** - ORM и драйвер БД
- **Alembic** - миграции БД
- **Docker & Docker Compose** - контейнеризация
- **uv** - управление зависимостями

## Требования

- Python 3.12+
- Docker и Docker Compose
- uv (для локальной разработки)

## Быстрый старт с Docker

### 1. Клонирование и настройка

```bash
git clone https://github.com/vovkka/url-alias.git
cd url-alias
```

### 2. Настройка переменных окружения

Скопируйте файл окружения и заполните его:

```bash
cp .env.example .env
```

### 3. Запуск сервиса

```bash
# Собрать образы, применить миграции и запустить сервисы
make start-dev
```

Сервис будет доступен по адресу: http://localhost:8000

API документация: http://localhost:8000/docs

### 4. Остановка сервиса

```bash
make down
```

## Управление базой данных

### Миграции

```bash
# Создание новой миграции
make migrate-generate message="Описание изменений"

# Применение миграций
make migrate-up
```

### Pre-commit хуки

Проект использует pre-commit хуки для автоматической проверки кода:

```bash
# Установка pre-commit хуков
make install-pre-commit

# Запуск проверок вручную на всех файлах
make run-pre-commit
```

Pre-commit автоматически проверяет:
- **black** - форматирование кода 
- **isort** - сортировка импортов
- **flake8** - линтинг кода

После установки хуки будут запускаться автоматически при каждом commit.
