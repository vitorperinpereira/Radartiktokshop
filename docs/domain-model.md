# Domain Model

## Domain intent

The system tracks product opportunities over time. It must preserve raw evidence, normalize product identity, store extracted signals, and publish weekly ranked outputs.

## Core entities

### `products`

Canonical product identity.

- `id`
- `canonical_key`
- `title`
- `brand`
- `category`
- `subcategory`
- `image_url`
- `status`
- `created_at`
- `updated_at`

### `product_aliases`

Alternative titles, seller names, or upstream identifiers mapped to the canonical product.

- `id`
- `product_id`
- `alias_type`
- `alias_value`
- `source_name`
- `created_at`

### `product_snapshots`

Raw or lightly normalized observations captured from adapters for a product at a point in time.

- `id`
- `product_id`
- `source_name`
- `source_record_id`
- `captured_at`
- `price`
- `orders_estimate`
- `rating`
- `commission_rate`
- `raw_payload`
- `created_at`

### `creators`

Optional creator profile used for future personalization or comparison.

- `id`
- `handle`
- `tier`
- `primary_niche`
- `region`
- `created_at`

### `product_signals`

Derived deterministic or agent-generated signals.

- `id`
- `product_id`
- `signal_name`
- `signal_value`
- `signal_type`
- `observed_at`
- `evidence`
- `source_kind`
- `created_at`

### `product_scores`

Weekly score output for each product.

- `id`
- `product_id`
- `week_start`
- `run_id`
- `trend_score`
- `viral_potential_score`
- `creator_accessibility_score`
- `saturation_penalty`
- `revenue_estimate`
- `final_score`
- `classification`
- `explainability_payload`
- `created_at`

### `content_angles`

Suggested hooks or content directions associated with a ranked product.

- `id`
- `product_id`
- `week_start`
- `run_id`
- `angle_type`
- `hook_text`
- `supporting_rationale`
- `created_at`

### `reports`

Published or draft weekly report artifacts.

- `id`
- `week_start`
- `run_id`
- `status`
- `report_payload`
- `published_at`
- `created_at`

### `ingestion_jobs`

Tracks import attempts and lineage.

- `id`
- `source_name`
- `input_type`
- `status`
- `records_received`
- `records_written`
- `started_at`
- `finished_at`
- `metadata`

### `pipeline_runs`

Tracks a weekly scoring execution.

- `id`
- `week_start`
- `status`
- `started_at`
- `finished_at`
- `input_job_ids`
- `config_version`
- `error_summary`

## Relationship summary

- one `product` has many `product_aliases`
- one `product` has many `product_snapshots`
- one `product` has many `product_signals`
- one `product` has many `product_scores`
- one `product` has many `content_angles`
- one `pipeline_run` produces many `product_scores`
- one `pipeline_run` can produce one or more `reports`
- one `ingestion_job` can feed one or more `pipeline_runs`

## Lifecycle

```text
raw import
  -> ingestion_jobs
  -> product_snapshots
  -> normalization and alias mapping
  -> canonical products
  -> deterministic feature extraction
  -> product_signals
  -> runtime agents
  -> scored outputs
  -> content angles
  -> reports
```

## Normalization rules

1. Normalize titles by trimming noise, standardizing casing, and removing seller-specific clutter.
2. Use a canonical key built from normalized title, brand, category, and stable identifiers when present.
3. Preserve upstream identifiers as aliases instead of overwriting canonical identity.
4. Treat package-size or flavor differences as variants only when the analysis requires separate commercial behavior.
5. Keep raw payloads untouched for audit and debugging.

## Deduplication policy

1. Prefer exact match on stable source identifiers when available.
2. Fall back to canonical key matching.
3. Use alias history to prevent repeated split identities.
4. Flag ambiguous merges for manual review instead of forcing aggressive collapse.

## Indexing guidance

- unique index on `products(canonical_key)`
- index on `product_snapshots(product_id, captured_at desc)`
- index on `product_signals(product_id, signal_name, observed_at desc)`
- index on `product_scores(week_start, final_score desc)`
- index on `reports(week_start)`

## Data boundaries

- Raw adapter payload stays in `product_snapshots.raw_payload`
- Normalized product identity stays in `products` and `product_aliases`
- Derived signals stay in `product_signals`
- Decision outputs stay in `product_scores`, `content_angles`, and `reports`
