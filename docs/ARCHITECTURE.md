# Architecture — AI Film Factory

## 1. High-level system

```text
User Idea
   ↓
Project Intake
   ↓
Story/Script Engine
   ↓
Scene & Shot Planner
   ↓
Production Orchestrator
   ├── Character / Location / Prop Assets
   ├── Image Generation
   ├── Video Generation
   ├── Voice / Dialogue
   ├── Music / SFX
   └── Continuity State
   ↓
QA / Continuity Evaluator
   ↓
Revision Loop ─────────┐
   │                    │
   └────────────────────┘
   ↓
Editor / Renderer
   ↓
Master Film
   ↓
Publishing
   ↓
Public Film Website
```

## 2. Production model

Every film is a resumable production job. The orchestrator stores explicit state for each stage and each scene/shot so failed or rejected work can be retried without rebuilding the entire film.

Core lifecycle:

`planned → running → evaluating → revising → approved → rendered → published`

## 3. Core domain objects

- `FilmProject`: project-level metadata, genre, language, target duration and creative brief.
- `Story`: logline, synopsis, structure and story constraints.
- `Scene`: screenplay scene with characters, location, time, actions and dialogue.
- `Shot`: atomic visual unit with camera, duration, composition, motion and continuity requirements.
- `Asset`: character, location, prop, wardrobe, reference image, voice or other production asset.
- `GenerationJob`: request to an external AI provider, status, inputs, outputs and retry history.
- `ContinuityState`: canonical state of characters, wardrobe, props, locations and timeline.
- `Evaluation`: automated QA result with issues, severity and suggested repair.
- `Render`: assembled video/audio outputs and technical metadata.

## 4. Provider abstraction

AI providers must be hidden behind adapters. The production engine should depend on capabilities, not vendor-specific APIs.

Examples of capabilities:

- `text.generate`
- `image.generate`
- `video.generate`
- `speech.generate`
- `music.generate`
- `sfx.generate`
- `vision.evaluate`

This allows providers to be replaced or combined without rewriting the orchestration layer.

## 5. Website scope (v1)

The public website is intentionally small:

- Home page
- Film catalog / discovery
- Film detail + player
- Search/filter
- Basic categories
- Admin-only publishing

No public creator channels, user uploads, social feed, comments, subscriptions or complex community features in v1.

Advertising is a website concern, not a film-rendering concern. The architecture must keep ad placements outside the video content so the viewing experience remains clean.
