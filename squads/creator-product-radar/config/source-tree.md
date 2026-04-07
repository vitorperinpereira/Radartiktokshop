# Source Tree - Creator Product Radar

## Squad Package

```text
squads/creator-product-radar/
|-- squad.yaml
|-- README.md
|-- config/
|-- agents/
|-- tasks/
|-- workflows/
|-- checklists/
|-- templates/
`-- data/
```

## Target Product Repository Shape

```text
apps/
|-- api/
`-- dashboard/
services/
|-- agents/
|-- workers/
|-- scoring/
|-- reporting/
`-- ingestion/
infra/
|-- docker/
`-- migrations/
docs/
|-- architecture.md
|-- prd.md
|-- domain-model.md
|-- scoring-model.md
|-- agents.md
|-- setup.md
`-- roadmap.md
tests/
|-- unit/
|-- integration/
`-- smoke/
scripts/
|-- seed/
`-- ops/
```

## Ownership Mapping

- `agents/` in this squad defines domain specialists, not runtime application agents.
- `tasks/` captures domain design and governance actions before or alongside implementation.
- `workflows/` orchestrates how core AIOX and squad specialists collaborate.
- `checklists/` protects creator fairness, source compliance, and report usefulness.
- `templates/` provides repeatable output structure for recurring reporting artifacts.
