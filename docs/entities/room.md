# room

**Context:** org (hospital structure and staff)

## Purpose

A room inside a ward (e.g. Room 3 in General Ward A). Beds sit inside rooms, so the room is what says which beds share a space. It completes the location chain: ward -> room -> bed. A room is private or shared and carries a daily rate, which is where bed charges get their price.

## Decisions

- **Kept as an entity.** Reason: it says which beds share a space (e.g. a 4-bed room) and completes the ward -> room -> bed chain.
- **Room type (private or shared) and daily rate live on `room`, at the user's request (2026-10-19).** Reason: bed charges need a price source, and the room is the level where private and shared differ.
- **`daily_rate` is the charge per patient per day** (per bed stay), whether the room is private or shared. Reason: keeps billing one rule: days stayed x the rate of the room the bed is in. A private room is simply priced higher.
- **The rate is copied onto the invoice line when the invoice is made** (see `invoice_line`). Reason: a later rate change must not alter an old bill.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `ward_id` | INT | FK -> ward, NOT NULL |  |
| `room_number` | VARCHAR(20) | NOT NULL | Name or number within the ward |
| `room_type` | VARCHAR(20) | NOT NULL | private or shared |
| `daily_rate` | DECIMAL(10,2) | NOT NULL | Charge per patient per day |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

`(ward_id, room_number)` is unique.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_room_number_not_blank`: `TRIM(room_number) <> ''`
- `ck_room_type`: `room_type IN ('private', 'shared')`
- `ck_room_daily_rate`: `daily_rate >= 0`

## Relationships

- ward 1 -> 0..n room
- room 1 -> 0..n bed
