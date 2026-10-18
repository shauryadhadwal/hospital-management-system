# insurance_policy

**Context:** patient

## Purpose

A patient's policy with an insurer. Records the policy number and the date range it is valid for, and links the patient to an `insurance_provider`. `insurance_claim` refers to it.

## Decisions

- **Kept as an entity.** Reason: a patient can hold several policies over time and a policy has a validity period, so billing needs to know which policy was active when care was given. It is the link between patient, insurer and claim.
- **One policy row belongs to one patient.** A policy shared by several people (e.g. a family floater) is not supported: `(provider_id, policy_number)` is unique, so it can only be recorded for one of them. Accepted to keep the design basic.
- **Claims need a matching policy.** The application checks that a claim's policy belongs to the visit's patient and was valid on the visit date (see `insurance_claim`).
- **Date of birth is an estimate.** `patient.date_of_birth` is derived from an age, so it may not match the insurer's records when a claim is checked.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `patient_id` | INT | FK -> patient, NOT NULL |  |
| `provider_id` | INT | FK -> insurance_provider, NOT NULL |  |
| `policy_number` | VARCHAR(50) | NOT NULL |  |
| `valid_from` | DATE | NOT NULL |  |
| `valid_to` | DATE | NOT NULL |  |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

`(provider_id, policy_number)` is unique.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_policy_validity`: `valid_to >= valid_from`
- `ck_policy_number_not_blank`: `TRIM(policy_number) <> ''`

## Relationships

- patient 1 -> 0..n insurance_policy
- insurance_provider 1 -> 0..n insurance_policy
- insurance_policy 1 -> 0..n insurance_claim
