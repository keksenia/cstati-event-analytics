 SQL Layer

Эта папка содержит reference SQL для аналитического слоя проекта.

Основная обработка в проекте выполнена в Python-ноутбуках, но SQL-файлы показывают, как те же сущности и метрики могут быть реализованы в production-like аналитическом хранилище.

## Структура

- `staging/` — базовые очищенные представления над исходными таблицами;
- `marts/` — продуктовые витрины: event metrics, retention, transitions, scorecard;
- `checks/` — data quality checks.

## Основные сущности

- `stg_events` — справочник событий;
- `stg_identity_records` — строки участников после identity resolution;
- `stg_event_participations` — deduplicated event × participant layer;
- `mart_event_metrics` — event-level продуктовые метрики;
- `mart_family_metrics` — метрики по семействам событий;
- `mart_retention` — repeat participation и retention proxy;
- `mart_event_transitions` — переходы между событиями;
- `mart_event_scorecard` — итоговая оценка событий.

## Privacy

SQL не содержит персональных данных.  
Raw identifiers, такие как ФИО, Telegram, телефон и email, не должны попадать в публичные таблицы.
