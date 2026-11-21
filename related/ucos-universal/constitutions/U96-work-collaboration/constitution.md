# U96 — Work & Collaboration Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U96-collaboration` |
| Layer | L5 Business Capability |
| Domain | 03 Business |
| Steward | `ucos:org:productivity` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 (projects, tasks, comments, mentions, team spaces), P6 (docs/wiki, chat, meetings integration) |
| Depends on | U11 Party, U10 Org (teams/org units), U13 Temporal (due dates, sprints, calendars), U40 Communication, U43 Asset, U42 Document, U60 Workflow (tasks from processes), U44 Search, U95 Software Delivery (issue↔commit links) |
| Depended on by | ERP/projects packs, PSA (professional services: timesheets → billing), internal ops portals, ITSM, U82 Field Service (internal tasks), human-AI collaboration (agents as team members) |
| Master references | Master "Collaboration, Projects, Tasks, Human-AI Collaboration" (A-37) |

> Collaboration owns **how people and agents organise and do knowledge work together**: workspaces/spaces, projects, tasks/issues (with boards, lists, timelines), comments & mentions on any object (a universal comment thread capability), timesheets/effort, documents/wiki pages, and integrations with chat/meeting tools. Process-driven human tasks remain U60; Collaboration provides free-form and project-based work.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| COL-L1 | Comments/mentions attach to any canonical object through one universal thread model (no per-universe comment tables). | Extension point `collab.thread` for all views. |
| COL-L2 | Access to threads/tasks inherits the subject object's policies plus explicit sharing. | PDP composition. |
| COL-L3 | Agents can be assignees only with delegated authority; their actions are labelled. | Identity kind=agent + UI label. |

## 2. Objects
`Space { org/team, members, visibility }` · `Project { space, goals, timeline (TimeRange), status, methodology: kanban|scrum|waterfall }` · `Task { project?, title, description, assignees (persons/agents), status (configurable workflow), priority, due (TemporalRef), estimate, dependencies, links (any object) }` · `Sprint/Milestone` · `Thread { subject: ObjectRef, comments: [{author, body (rich text), mentions, attachments, reactions, at: TimePoint}] }` · `Timesheet { person, entries: [{task/project, range: TimeRange, billable, rate?}] }` · `Page { space, content (blocks), versions }`.

## 3. Commands, Queries, Events, APIs
Commands: `CreateProject/Task`, `Assign`, `Transition`, `Comment`, `Mention`, `LogTime`, `SubmitTimesheet`, `ApproveTimesheet`, `CreatePage`.
Events: `collab.task.created|assigned|completed`, `collab.comment.added`, `collab.mention.created`, `collab.timesheet.approved`.
```text
POST /v1/collab/tasks   POST /v1/collab/threads/{subject}/comments   POST /v1/collab/timesheets
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(object_view_without_thread, V) :- view(V), kind(V, detail), collaboration_enabled(V), not thread_widget(V).
```
AI: task breakdown, summaries of threads, agent teammates executing tasks (bounded), timesheet suggestions from activity. Views: board/list/timeline/calendar (U13), task detail, universal comment drawer (W-anywhere), timesheet grid, wiki. T2.

## Appendix
- **C.** 0.1.0.
