# Hospital Management System

Design-first project. The design lives in markdown under `docs/`:

- `docs/entities.md`: the 26 entities, key relationships and the happy-path ordering rules.
- `docs/entities/<entity>.md`: one doc per entity (purpose, decisions, columns, constraints, relationships).
- `docs/user_journey.md`: Peehu's stay from booking to payment; every entity is used at least once.
- `docs/personas/`: what each role needs and the gaps.
- `docs/brainstorming.md`: dropped or merged entities and open follow-ups.

There are no schema files, CSVs or code yet.

## Working agreement

- **Design first, implement only after confirmation.** Propose the design, wait for the user's explicit go-ahead, then build. Do not write application code, schemas, migrations or services until the user confirms the design.
- Keep the design basic and satisfactory: cover the core hospital workflows, avoid speculative extras.
- **Happy path only (for now).** Design and document the normal flow only. Do not design rejected claims or resubmissions, cancelled or no-show visits, emergency visits, refunds, or other exception flows until the user asks for them.
- Once a design is confirmed, implement only the confirmed scope; raise anything new as a design question first.
- There is no validator script. After a design change, keep the docs consistent by hand: update the entity doc, `docs/entities.md`, `docs/user_journey.md` (diagram, coverage table, notes) and any affected persona, and check that the entity count and the roles, statuses and `source_type` values match everywhere.
- This is for a college project.
