# DESIGN-BY-SECURITY

## Security Architecture & Engineering Operating System

This repository implements the architecture described by the Design-by-Security presentation as an executable, testable security engineering operating model.

It combines two complementary planes:

- **Design-by-Security** — architecture-first security design, threat modeling, requirements, controls, validation and security gates.
- **Security Copilot v4** — operational SOC, IR, DFIR, hunting, detection and security-engineering analysis.

The planes are intentionally separated and connected by explicit adapters.

### Master operating model

```text
BUSINESS → SECURITY GOALS → ASSETS → DATA FLOWS → TRUST BOUNDARIES
→ ATTACK SURFACE → THREAT MODEL → ATTACK PATHS → REQUIREMENTS
→ CONTROLS → ARCHITECTURE → BUILD → VALIDATE → DEPLOY → DETECT
→ RESPOND → RECOVER → LEARN → REDESIGN
```

### Repository structure

```text
.
├── .github/workflows/security-design-integration.yml
├── design-by-security/
├── skills/security-copilot/
├── tests/security-design-pipeline/
├── schemas/security-design.schema.json
├── examples/web-api/security-design.yaml
├── gost-compliance/
├── docs/
├── DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md
├── AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md
├── SECURITY-METRICS.md
├── DEPENDENCIES.md
├── REPOSITORY-MAP.md
├── build-security-copilot.sh
├── LICENSE
└── SECURITY.md
```

Use `REPOSITORY-MAP.md` as the canonical navigation map. `SECURITY-METRICS.md` defines the 12-axis measurement model and repository KPIs. `DEPENDENCIES.md` defines the runtime and CI dependency contract.

## Design principles

Security is a design property, not a post-production patch.

The architecture process starts with business context and evidence, not technology selection. Critical attack paths must have prevention, detection, response and recovery coverage or an explicit detection gap. Unknowns are preserved as unknowns and never silently promoted to evidence.

Controls are assessed as:

`EXISTS → CONFIGURED → EFFECTIVE → TESTED`

Compliance mapping is not treated as proof of actual security.

## Feedback loop

Operational findings return to architecture through:

`OBSERVATION → FINDING → ROOT CAUSE → SECURITY DEBT / DESIGN FLAW → REQUIREMENT OR CONTROL CHANGE → VALIDATION → REDESIGN`

Destructive response actions require human authorization.

## Machine-readable contract

The canonical required artifact set is defined by `tests/security-design-pipeline/pipeline-manifest.yml`; a human-readable explanation is in `docs/SECURITY-DESIGN-CONTRACT.md`; the machine-readable artifact shape is in `schemas/security-design.schema.json`.

A reference web API artifact is available under `examples/web-api/`.

## Integration validation

Run locally with:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
```

For the process/evidence overlay:

```bash
bash gost-compliance/pipeline/gost-validate.sh
bash gost-compliance/pipeline/evidence-package.sh ./evidence-output/package
```

The same gates run in GitHub Actions for `main`, integration, hardening and audit branches and for pull requests targeting `main`.

## Presentation alignment

`docs/ARCHITECTURE.md`, `docs/ENGINE-CATALOG.md`, `docs/PRESENTATION-MAP.md` and `REPOSITORY-MAP.md` translate the presentation into repository-level implementation responsibilities. The presentation's architecture is therefore represented by executable contracts, reference artifacts, adapters, measurements and CI gates rather than by documentation alone.

# DESIGN-BY-SECURITY

## Архитектура безопасности и проектирование операционных систем

Этот репозиторий реализует архитектуру, описанную в презентации **Design-by-Security**, в виде исполняемой и тестируемой операционной модели инженерии безопасности.

Он объединяет два взаимодополняющих плана:

- **Design-by-Security** — проектирование безопасности «сверху вниз**: threat modeling, требования, контроли, валидация и security gates.
- **Security Copilot v4** — операционный уровень SOC: IR, DFIR, hunting, detection и инженерный анализ безопасности.

Эти планы намеренно разделены и связаны явными адаптерами.

---

## Мастер-модель процесса

```text
БИЗНЕС → ЦЕЛИ БЕЗОПАСНОСТИ → АКТИВЫ → ПОТОКИ ДАННЫХ → ГРАНИЦЫ ДОВЕРИЯ
→ ПОВЕРХНОСТЬ АТАКИ → МОДЕЛЬ УГРОЗ → ПУТИ АТАК → ТРЕБОВАНИЯ
→ КОНТРОЛИ → АРХИТЕКТУРА → СБОРКА → ВАЛИДАЦИЯ → РАЗВЁРТЫВАНИЕ → ДЕТЕКТИРОВАНИЕ
→ РЕАГИРОВАНИЕ → ВОССТАНОВЛЕНИЕ → ИЗВЛЕЧЕНИЕ УРОКОВ → ПЕРЕПРОЕКТИРОВАНИЕ
```

Это сквозной цикл: безопасность начинается с бизнес-целей и замыкается через операционные находки обратно в архитектуру.

---

## Структура репозитория

```text
.
├── .github/workflows/security-design-integration.yml
├── design-by-security/
├── skills/security-copilot/
├── tests/security-design-pipeline/
├── schemas/security-design.schema.json
├── examples/web-api/security-design.yaml
├── gost-compliance/
├── docs/
├── DESIGN-BY-SECURITY-COPILOT-2.0-MASTER-PROMPT.md
├── AI_SECURITY_COPILOT_2_1-1ppdkbstc7no5rj61t8dbufn3e.md
├── SECURITY-METRICS.md
├── DEPENDENCIES.md
├── REPOSITORY-MAP.md
├── build-security-copilot.sh
├── LICENSE
└── SECURITY.md
```

- `REPOSITORY-MAP.md` — каноническая навигационная карта репозитория.
- `SECURITY-METRICS.md` — 12-осевая модель измерений и KPI репозитория.
- `DEPENDENCIES.md` — контракт зависимостей (runtime + CI).

---

## Принципы проектирования

- **Безопасность — свойство дизайна, а не пост-релизный патч.**
- Процесс начинается с **бизнес-контекста и доказательств**, а не с выбора технологий.
- Критические пути атаки должны иметь покрытие **предотвращение + детектирование + реагирование + восстановление** либо явный зазор детектирования.
- Неизвестное сохраняется как **unknown** и никогда молчаливо не превращается в «доказанное**.

Контроли оцениваются по цепочке:

```text
EXISTS → CONFIGURED → EFFECTIVE → TESTED
```

Соответствие стандартам (compliance) не считается доказательством реальной безопасности.

---

## Обратная связь (feedback loop)

Операционные находки возвращаются в архитектуру через:

```text
НАБЛЮДЕНИЕ → НАХОДКА → ПРИЧИНА → ДОЛГ ПО БЕЗОПАСНОСТИ / ПРОЕКТНЫЙ ДЕФЕКТ
→ ИЗМЕНЕНИЕ ТРЕБОВАНИЙ ИЛИ КОНТРОЛЕЙ → ВАЛИДАЦИЯ → ПЕРЕПРОЕКТИРОВАНИЕ
```

Деструктивные действия реагирования требуют **ручного подтверждения**.

---

## Машиночитаемый контракт

- Набор обязательных артефактов определён в `tests/security-design-pipeline/pipeline-manifest.yml`.
- Человекочитаемое пояснение — в `docs/SECURITY-DESIGN-CONTRACT.md`.
- Форма машиночитаемого артефакта — в `schemas/security-design.schema.json`.
- Референсный артефакт для веб-API — в `examples/web-api/`.

---

## Валидация интеграции

Локальный запуск:

```bash
bash tests/security-design-pipeline/run-pipeline.sh
```

Для наложения процесса/доказательств:

```bash
bash gost-compliance/pipeline/gost-validate.sh
bash gost-compliance/pipeline/evidence-package.sh ./evidence-output/package
```

Те же гейты выполняются в GitHub Actions для веток `main`, интеграционных/харденинг/аудит и для pull request в `main`.

---

## Соответствие презентации

Файлы `docs/ARCHITECTURE.md`, `docs/ENGINE-CATALOG.md`, `docs/PRESENTATION-MAP.md` и `REPOSITORY-MAP.md` транслируют презентацию в ответственность на уровне репозитория. Таким образом, архитектура презентации представлена **исполняемыми контрактами, референсными артефактами, адаптерами, измерениями и CI-гейтами**, а не только документацией.
