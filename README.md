# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

команда запуска сервиса uvicorn recommendations_service:app

Логика работы:
1. Получает оффлайн-рекомендации из suggestion_system
2. Получает онлайн-рекомендации на основе последних действий пользователя
3. Объединяет их, чередуя онлайн и оффлайн рекомендации
4. Удаляет дубликаты, сохраняя порядок

сервис будет достпен по порту 8000, в случае, если он не занят.
Эндпоинты:
POST /suggestions - получение комбинированных рекомендаций для пользователя
POST /realtime_suggestions - получение рекомендаций в реальном ыремени на основе последних деействий
POST /lpg_action - логирование действий пользователя
GET /user_actions - получение истории действий пользователя
GET /refresh_suggestions - принудительное обновление рекомендаций
GET /system_metrics - получение метрик использования системы

# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`. Вывод сохраняется в файле.