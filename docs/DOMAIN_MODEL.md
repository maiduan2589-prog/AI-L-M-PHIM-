# Domain Model v1

## FilmProject

```text
id
name
creative_brief
language
genre
target_duration
status
created_at
updated_at
```

## Story

```text
project_id
logline
premise
synopsis
structure
themes
constraints
version
```

## Scene

```text
project_id
scene_number
slugline
location_id
time_of_day
characters[]
actions[]
dialogue[]
continuity_in[]
continuity_out[]
version
```

## Shot

```text
scene_id
shot_number
duration
visual_prompt
camera
composition
movement
lighting
characters[]
location_id
props[]
required_assets[]
status
version
```

## Asset

```text
id
type
name
canonical_description
reference_artifacts[]
metadata
version
status
```

Asset types initially include: `character`, `location`, `prop`, `wardrobe`, `voice`, `music`, `sfx`, `image`, `video`.

## GenerationJob

```text
id
project_id
stage
provider
capability
input_refs[]
output_refs[]
status
attempt
error
created_at
completed_at
```

## ContinuityState

```text
project_id
scene_id
character_states{}
wardrobe_states{}
prop_states{}
location_state{}
timeline_state{}
```

## Evaluation

```text
id
project_id
scene_id
shot_id
checks[]
score
severity
issues[]
repair_plan
status
```

## Render

```text
id
project_id
version
timeline_ref
video_artifact
subtitle_artifact
audio_artifact
status
technical_validation
```

## Design rule

The domain model deliberately separates **creative intent**, **production state**, **generated artifacts**, and **evaluation results**. This makes the pipeline replaceable, auditable, resumable, and suitable for autonomous revision.
