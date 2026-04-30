# cstati Event Analytics

Аналитический проект по исследованию портфеля мероприятий студенческой организации **cstati** на ФКН ВШЭ.

Проект рассматривает мероприятия не как отдельные события, а как **event-community product**: систему форматов, через которую организация привлекает новую аудиторию, удерживает участников и развивает комьюнити.

## Зачем этот проект

Цель проекта — построить продуктовую аналитику для event-комьюнити:

- понять, какие события работают на рост аудитории;
- какие события лучше удерживают участников;
- как участники переходят между мероприятиями;
- где есть проблемы качества данных;
- какие решения помогут cstati улучшить event portfolio.

Проект сделан в формате, близком к задачам продуктового аналитика: от data audit и identity resolution до метрик, интерпретации и actionable recommendations.

---

## Ключевые результаты

В анализе использовались данные по **18 мероприятиям** cstati.

В проекте построены два аналитических слоя:

| Layer | Rows | Unique participants | Events |
|---|---:|---:|---:|
| Full event-level layer | 5 257 | 3 636 | 18 |
| Clean identity layer | 2 933 | 2 527 | 16 |

Clean identity layer используется для чувствительных метрик: retention, repeat participation и event journeys.

### Основные выводы

1. **Массовые события работают как acquisition/reach engine.**  
   Крупнейшие события в clean layer: `Нейрорейв`, `Посвят'25`, `Посвят'23`.

2. **Community-heavy события лучше показывают repeat-сигнал.**  
   Самые сильные события по repeat-share: `Настолки'24`, `Антипосвят'25`, `Поход'25`.

3. **Портфель мероприятий работает как двухконтурная система.**  
   Одни события приводят новую аудиторию, другие возвращают участников и формируют ядро комьюнити.

4. **События нельзя сравнивать только по размеру аудитории.**  
   У разных форматов разные продуктовые роли: acquisition, activation, retention, community building.

5. **Качество регистрационных данных напрямую влияет на аналитику.**  
   Для части событий нужны special loaders или более стандартизированные формы регистрации.

---

## Продуктовая интерпретация

cstati event portfolio можно описать как систему из двух контуров.

### 1. Acquisition-контур

События, которые приводят большую новую аудиторию:

- `Нейрорейв`
- `Посвят`
- `CSFEST`

Их основная роль — расширять охват, приводить новых участников и знакомить их с организацией.

### 2. Retention/community-контур

События, которые лучше возвращают людей и усиливают ядро комьюнити:

- `Поход`
- `Антипосвят`
- `Настолки`
- часть событий формата `Экватор`

Их роль — создавать повторное участие, связи между участниками и устойчивое вовлечение.

---

## Ключевые метрики

В проекте рассчитываются:

- `clean_participants` — количество участников в clean identity layer;
- `new_participants` — участники, для которых событие стало первым в наблюдаемой истории;
- `repeat_participants` — участники, которые уже были на предыдущих событиях;
- `new_share` — доля новых участников;
- `repeat_share` — доля повторных участников;
- `clean_coverage_share` — доля участников, попавших в clean identity layer;
- `future_event_rate` — доля участников, у которых было следующее событие;
- `event transitions` — переходы участников между событиями;
- `portfolio_score` — composite score события по acquisition, retention и data quality.

---

## Пример продуктовых инсайтов

### Acquisition

`Нейрорейв` оказался крупнейшим событием в clean layer:

- 728 clean participants;
- `new_share = 1.000`.

Это делает его сильным reach/acquisition-событием, но также показывает необходимость post-event activation: после таких событий важно вести людей в следующие community-форматы.

### Retention

Самые сильные события по repeat-share:

| Event | Repeat share |
|---|---:|
| Настолки'24 | 0.511 |
| Антипосвят'25 | 0.416 |
| Поход'25 | 0.411 |

Это говорит о том, что более камерные и community-heavy форматы лучше работают на удержание.

### Event journeys

Самый сильный переход между событиями:

| From | To | Participants |
|---|---|---:|
| Поход'24 | Поход'25 | 50 |

Это хороший сигнал повторяемости формата и потенциальной лояльности аудитории.

---

## Рекомендации

### P1 — Post-event activation

После крупных acquisition-событий нужно запускать follow-up цепочку:

- приглашение на ближайшее community-событие;
- подборка следующих мероприятий;
- вступление в Telegram-канал или чат;
- персонализированное сообщение для новых участников.

**Метрики для отслеживания:** `future_event_rate`, `repeat_share`, доля участников с 2+ событиями.

### P1 — Retention mechanics

Использовать `Поход`, `Антипосвят` и `Настолки` как retention/community-ядро портфеля.

**Метрики для отслеживания:** `repeat_share`, `returned_later`, `event_depth`.

### P1 — Registration data quality

Стандартизировать регистрационные формы:

- обязательный Telegram или email;
- единый формат ФИО;
- единые поля курса, программы и статуса участника;
- одинаковые названия колонок между событиями.

**Метрики для отслеживания:** `clean_coverage_share`, `strong_identifier_share`, `identity_conflict_rate`.

### P2 — Event journey design

Проектировать события как цепочки, а не как независимые мероприятия.

Пример:

```text
onboarding event → community event → seasonal event
Метрики для отслеживания: event_transition_rate, family_transition_rate.
P2 — Special loaders
Сделать отдельную обработку для событий со сложной структурой данных, например:
Коллаб'24;
Бал ФКН'24.
Это позволит честнее учитывать их в clean metrics.

Методология
Проект состоит из пяти аналитических этапов:
Notebook
Purpose
01_data_audit.ipynb
Первичный аудит файлов, колонок, пропусков, дублей и manual-справочников
02_identity_resolution.ipynb
Связывание участников между событиями и построение clean identity layer
03_portfolio_overview.ipynb
Event-level, family-level, repeat и transition metrics
04_deep_dive_events.ipynb
Глубокий разбор ключевых событий
05_recommendations.ipynb
Финальные выводы, рекомендации и README-ready summary


Identity resolution
Для анализа повторного участия нужно связать участников между событиями.
Использовались нормализованные идентификаторы:
Telegram;
телефон;
email;
ФИО + группа / программа / курс.
Для каждой строки строится participant_key_internal, а затем приватный hash.
Confidence levels
Level
Logic
high
Telegram, телефон или email
medium
ФИО + группа / программа / курс
low
только ФИО
missing
нет пригодного идентификатора

Для retention и journeys используется строгий clean layer:
clean_identity_df = identity_records_df[
    (identity_records_df["is_auxiliary_source"] == False)
    & (identity_records_df["identity_conflict_flag"] == False)
    & (identity_records_df["identity_confidence"].isin(["high", "medium"]))
].copy()

Такой подход снижает риск false-positive stitching.

Privacy
Raw-данные с персональными данными не публикуются.
В публичный репозиторий не попадают:
ФИО участников;
Telegram;
телефоны;
email;
raw CSV-файлы;
private identity layer;
intermediate private tables.
В репозитории могут публиковаться только:
код;
методология;
агрегированные метрики;
обезличенные outputs;
графики;
synthetic/sample data.
Подробнее: docs/privacy.md
Структура репозитория
cstati-event-analytics/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── manual/
│   ├── event_metadata.csv
│   ├── event_aliases.csv
│   └── attendance_corrections.csv
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_identity_resolution.ipynb
│   ├── 03_portfolio_overview.ipynb
│   ├── 04_deep_dive_events.ipynb
│   └── 05_recommendations.ipynb
│
├── src/
│   ├── loaders.py
│   ├── normalizers.py
│   ├── identity_resolution.py
│   ├── metrics.py
│   ├── plots.py
│   └── pipeline.py
│
├── sql/
│   ├── staging/
│   ├── marts/
│   └── checks/
│
├── data/
│   ├── processed_public/
│   └── samples_public/
│
├── docs/
│   ├── methodology.md
│   ├── privacy.md
│   └── figures/
│
└── dashboards/


Кодовая структура
Reusable logic вынесена в src/:
loaders.py — загрузка raw/manual/processed таблиц;
normalizers.py — нормализация ФИО, Telegram, телефона, email и названий событий;
identity_resolution.py — participant stitching и identity conflict checks;
metrics.py — event-level, family-level, retention и transition metrics;
plots.py — функции визуализации;
pipeline.py — skeleton будущего production pipeline.
