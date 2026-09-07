# AI Film Factory — Implementation Roadmap

## Chốt phạm vi

### Core: AI Film Factory
1. Project intake
2. Story generation
3. Screenplay generation
4. Scene breakdown
5. Shot planning
6. Character/location/prop bible
7. Production orchestration
8. AI generation adapters
9. Continuity state + QA
10. Automatic revision loop
11. Audio assembly
12. Video editing/rendering
13. Final master + publishing package

### Public website: minimal distribution platform
1. Home
2. Film catalog
3. Film detail/player
4. Search/filter
5. Categories
6. Admin-only publishing
7. Google advertising placements on suitable pages

### Explicitly out of scope for v1
- Public user accounts
- Creator channels
- User uploads
- Comments/social feed
- Likes/followers/subscriptions
- Creator revenue sharing
- Ads embedded in films

## Build order

### Phase 0 — Foundation
- Repository structure
- Architecture contracts
- Configuration and environment model
- Domain schemas
- Job/state model

### Phase 1 — Production brain
- FilmProject state machine
- Pipeline orchestrator
- Stage interface
- Retry/resume/idempotency
- Event/log model

### Phase 2 — Story to shot plan
- Creative brief
- Story planner
- Screenwriter
- Scene planner
- Shot planner
- Production bible
- Continuity ledger

### Phase 3 — Asset and generation layer
- Provider adapter interfaces
- Asset registry
- Prompt/input packages
- Generation jobs
- Artifact storage abstraction

### Phase 4 — QA and revision
- Script adherence checks
- Character/wardrobe continuity
- Location/prop continuity
- Visual quality checks
- Audio checks
- Automated repair decisions

### Phase 5 — Assembly
- Timeline model
- Dialogue/voice alignment
- Music/SFX tracks
- Subtitles
- Video rendering
- Final validation

### Phase 6 — Website
- Minimal public UI
- Film catalog/player
- Admin publishing
- SEO basics
- Ad placement abstraction

## Engineering principles

- Provider-agnostic: never hard-code the pipeline to one AI vendor.
- State-first: every production stage is observable and resumable.
- Asset identity matters: generated media must be traceable to the character/location/prop/version that produced it.
- Continuity is a first-class data model, not a prompt-only instruction.
- Fail gracefully: one failed shot must not destroy an entire film job.
- Keep the public website small and fast.
- Keep advertising separate from film media and the rendering pipeline.
- Build an MVP that can complete one short film end-to-end before adding scale features.
