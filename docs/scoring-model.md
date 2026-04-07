# Scoring Model

## Objective

Estimate how attractive a product is for a creator to promote in the current week, balancing momentum, creator fit, virality potential, saturation risk, and basic monetization upside.

## MVP scoring principle

The final score should be explainable, calibration-friendly, and partly deterministic. AI agents interpret complex patterns, but the final number is aggregated by deterministic logic.

## MVP runtime agents

- `Trend Agent`
- `Viral Potential Agent`
- `Creator Accessibility Agent`

## Deferred agents

- `Saturation Agent`
- `Commission/Revenue Agent`
- `Content Angle Agent`

## Deterministic MVP inputs

- normalized category and product metadata
- price band
- order and rating proxies when available
- repeat mentions across snapshots
- category momentum heuristics
- saturation proxy heuristic
- commission or revenue proxy heuristic

## Proposed MVP formula

```text
final_score =
  0.35 * trend_score +
  0.30 * viral_potential_score +
  0.25 * creator_accessibility_score +
  0.10 * monetization_score -
  saturation_penalty
```

Notes:

- `trend_score`, `viral_potential_score`, and `creator_accessibility_score` are normalized to `0-100`
- `monetization_score` starts as a deterministic heuristic in MVP
- `saturation_penalty` is a deterministic subtraction, initially in the `0-15` range
- weights should be stored in config and versioned per weekly run

## Signal dimensions

### Trend

- recent movement or mention frequency
- category momentum
- persistence across snapshots

### Viral potential

- visual demo potential
- hook strength
- novelty and shareability

### Creator accessibility

- difficulty for a smaller creator to sell
- need for authority, budget, or niche audience
- price/friction profile

### Monetization heuristic

- rough commission potential
- price-to-effort attractiveness

### Saturation heuristic

- evidence of overcrowding
- low differentiation signals
- too-common ad pattern indicators

## Classification bands

- `85-100`: Breakout candidate
- `70-84`: Strong weekly bet
- `55-69`: Test selectively
- `40-54`: Watchlist only
- `0-39`: Low priority

## Risk flags

- `high_saturation`
- `weak_evidence`
- `high_creator_barrier`
- `low_margin_proxy`
- `category_noise`

## JSON output contract

```json
{
  "product_id": "uuid",
  "week_start": "YYYY-MM-DD",
  "scores": {
    "trend": 0,
    "viral_potential": 0,
    "creator_accessibility": 0,
    "monetization": 0,
    "saturation_penalty": 0,
    "final": 0
  },
  "classification": "strong_weekly_bet",
  "risk_flags": ["high_saturation"],
  "explanation": {
    "summary": "short rationale",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "evidence": ["..."]
  }
}
```

## Explainability payload

Each final score should include:

- raw sub-scores
- applied weights
- applied penalty values
- top positive signals
- top negative signals
- risk flags
- human-readable summary

## Calibration strategy

1. Start with config-driven weights and stable heuristics.
2. Run weekly review on the top ranked products.
3. Compare ranked products with manual operator judgment.
4. Adjust weights only with a version bump and rationale.
5. Add dedicated agents only after deterministic gaps are clear.
