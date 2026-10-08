# Приложение учёта спортсменов (Django)

Учебное Django-приложение с двумя источниками данных:
файлы (JSON/XML) и база данных SQLite.

## Возможности

- Добавление спортсмена с выбором места хранения: SQLite / JSON-файл / XML-файл
- Валидация формы (ФИО, вид спорта, страна — минимум 2 символа; возраст 10–100)
- Загрузка файлов `.json` / `.xml` с проверкой расширения, кодировки UTF-8 и структуры
- Имя файла на сервере генерируется через `uuid4` (имя пользователя не используется)
- Просмотр данных с переключателем источника: файлы / база данных
- Проверка дубликатов записей в БД по (name, sport, age, country)
- AJAX-поиск по БД (name, sport, country, achievements) без перезагрузки страницы
- Редактирование и удаление записей (удаление — через AJAX с CSRF)
- Bootstrap 5 через CDN

## Запуск

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Приложение будет доступно на http://127.0.0.1:8000/

## Пример JSON

```json
[
  {
    "name": "Иванов Иван",
    "sport": "Плавание",
    "age": 25,
    "country": "Россия",
    "achievements": "Чемпион Европы 2023"
  }
]
```

## Пример XML

```xml
<?xml version='1.0' encoding='utf-8'?>
<athletes>
  <athlete>
    <name>Иванов Иван</name>
    <sport>Плавание</sport>
    <age>25</age>
    <country>Россия</country>
    <achievements>Чемпион Европы 2023</achievements>
  </athlete>
</athletes>
```
