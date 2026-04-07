# Epic: Video Ranking Dashboard

This epic covers the delivery of the complete Video Ranking Dashboard, which consumes the cached TikTok top-selling videos and presents an interactive UI.

## Story 1: Backend API Router

**As a** consumer  
**I want** to fetch ranking entries via API  
**So that** I can build the dashboard

- Create `ranking_api/service.py` to load from cache
- Create `ranking_api/router.py` with endpoints `/latest`, `/latest/entries`, `/meta`
- Support pagination, sorting, and filtering in `/latest/entries`
- Register router in `main.py`

## Story 2: Base UI and API Hooks

**As a** developer  
**I want** hooks and utils for the dashboard  
**So that** I can decouple data fetching from presentation

- Create formatters and color utilities
- Create `useRanking` and `useFilters` hooks
- API client wrapper using `fetch`

## Story 3: Ranking Dashboard Presentation

**As a** user  
**I want** to see the top selling products visually  
**So that** I can evaluate trends and scores

- Implement `RankingDashboard` and `FilterBar`
- Implement `ProductRow` with `ScoreBreakdown`
- Ensure dark mode constraints and badges styling (no Tailwind)
- Skeleton loaders during data fetch

## Story 4: Video Drawer Integration

**As a** user  
**I want** to click and expand videos directly from the ranking  
**So that** I can analyze content immediately

- Adapt the existing `VideoFeed` inside `<VideoDrawer />`
- Smooth height transitions and exclusive toggle (only one expanded at a time)
