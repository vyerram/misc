# JSON Schema Governance Framework

---

## Abstract

This document defines a comprehensive governance framework for managing JSON Schema and OpenAPI specifications in enterprise repositories. Schemas are essential assets that act as contracts for interoperability between systems. To ensure trust and maintainability, schemas must follow standard conventions, lifecycle governance, versioning rules, and validation practices.

The framework presented here establishes:

- Repository structure standards
- Schema authoring conventions
- Metadata governance
- Versioning and lifecycle policies
- Automation and validation practices
- Best practices for reuse and maintainability

Appendices include complete example schemas for `modelMetadata`, `census`, and `censusMember`, serving as templates for domain-specific extensions.

---

## 1. Introduction

Modern systems rely on data exchange through APIs, files, and event streams. JSON has emerged as the de facto format, with JSON Schema providing a validation layer that guarantees data quality.

Without governance, schemas risk becoming fragmented, duplicated, and misaligned, leading to integration failures and wasted development cycles. This framework ensures that schemas are:

- **Authoritative** → A single source of truth exists.
- **Reusable** → Shared definitions reduce redundancy.
- **Evolvable** → Semantic versioning controls change.
- **Governed** → Metadata tracks lifecycle and accountability.
- **Validated** → Automation enforces compliance.

This guide is intended for solution architects, developers, and governance leads responsible for designing and maintaining schemas.

---

## 2. Guiding Principles

Schemas must align with the following principles:

### 2.1 Single Source of Truth

All schemas are managed in a central repository. No copies or divergent definitions are allowed in downstream services. This ensures that the repository is the authoritative registry.

### 2.2 Semantic Versioning

Schemas follow MAJOR.MINOR.PATCH:

- MAJOR → breaking changes (e.g., remove a field).
- MINOR → backward-compatible additions (e.g., new optional field).
- PATCH → corrections or clarifications.

Every new version is placed in its own folder (never overwrite).

### 2.3 Backward Compatibility

Schemas must not break consumers unexpectedly. Changes are additive whenever possible, and deprecated fields remain documented.

### 2.4 Reuse Over Redefinition

Common objects like `modelMetadata`, `address`, and `contact` are stored in common/ schemas and referenced with `$ref`. This avoids duplication.

### 2.5 Automation First

Validation runs automatically in:

- Developer IDE (VS Code tasks).
- Git pre-push hooks.
- GitHub Actions CI/CD pipelines.

### 2.6 Transparency

Every schema must carry metadata that shows its lifecycle state and version. This avoids ambiguity about which schemas are draft, production-ready, or deprecated.

### 2.7 Non-Destructive Change

Schemas evolve through deprecation and retirement, never deletion. History is preserved for audits and backward compatibility.

---

## 3. Repository & Folder Structure

```
<repo-root>/
 ├─ schemas/
 │   ├─ json/
 │   │   ├─ census/
 │   │   │   └─ v1.0.0/census.schema.json
 │   │   ├─ censusMember/
 │   │   │   └─ v1.0.0/censusMember.schema.json
 │   │   └─ common/
 │   │       ├─ modelMetadata/v1.0.0/modelMetadata.schema.json
 │   │       ├─ address/v1.0.0/address.schema.json
 │   │       └─ contact/v1.0.0/contact.schema.json
 │   └─ openapi/
 │       ├─ v1.0.0/openapi.yaml
 │       └─ v1.1.0/openapi.yaml
 ├─ scripts/
 │   └─ prepush.py
 ├─ .github/workflows/
 │   └─ validate.yml
 ├─ requirements.txt
 └─ README.md
```

**Standards:**

- `camelCase` → properties
- `kebab-case` → filenames
- `vMAJOR.MINOR.PATCH` → version folders
- `$id` URIs mirror folder paths

---

## 4. Schema Conventions

### 4.1 Naming Standards

- Use **camelCase** for property names (`firstName`, `effectiveDate`).
- Use **kebab-case** for schema file names (`census-member.schema.json`).

### 4.2 Required Schema Keywords

All schemas must contain:

- `$schema`, `$id`, `title`, `type`, `properties`, `required`, `additionalProperties`.

### 4.3 Constraints & Validation

- `enum` → for restricted values.
- `pattern` → for regex (SSN, phone).
- `format` → for ISO dates, emails.
- `maxLength`, `minItems` → enforce boundaries.

### 4.4 Documentation

Every property must include a **description** in plain business language. Descriptions can be multi-line using `\n`.

### 4.5 Vendor Extensions

- `xPrimaryKey` → marks primary identifiers.
- `xUnique` → declares uniqueness in arrays.
- `xStatus` → highlights lifecycle state.

---

## 5. Metadata & Lifecycle

### 5.1 Metadata Model

The `modelMetadata` schema defines governance metadata:

- `canonical`
- `version` (regex enforced)
- `metaVersion`
- `status` (draft, active, deprecated, retired)
- `createdDate`, `lastModifiedDate`, `lastReviewedDate`

### 5.2 Lifecycle Workflow

1. **Draft** → under development
2. **Active** → approved and stable
3. **Deprecated** → retained but replaced
4. **Retired** → archived, not deleted

---

## 6. Drafts & Placeholders

Placeholder schemas may exist (e.g., `address`). They must:

- Carry `status: draft`.
- Allow `additionalProperties: true`.
- Be finalized in future versions.

---

## 7. Primary Keys & Uniqueness

- Unique IDs must be marked with `xPrimaryKey: true`.
- Arrays requiring unique elements must declare `xUnique: "field"`.
- Enforcement occurs via CI/CD validators.

---

## 8. Validation & Automation

- Local validation → Python scripts (`prepush.py`).
- Git hooks → block invalid pushes.
- GitHub Actions → validate only changed schemas.

---

## 9. Best Practices

- Always increment version → never overwrite.
- Preserve history → deprecate, don’t delete.
- Factor shared objects into common/.
- Document every property.
- Provide example instances.
- Use CI/CD enforcement.

---

## Appendix A – modelMetadata.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.example.com/json/common/modelMetadata/v1.0.0/modelMetadata.schema.json",
  "$anchor": "modelMetadata",
  "title": "Model Metadata",
  "type": "object",
  "additionalProperties": false,

  "properties": {
    "canonical": {
      "type": "string",
      "description": "Canonical base URL for this schema family"
    },
    "version": {
      "type": "string",
      "description": "Semantic version of this schema (MAJOR.MINOR.PATCH)",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
      "examples": ["1.0.0"]
    },
    "metaVersion": {
      "type": "integer",
      "description": "Internal metadata version (bumped when metadata changes)"
    },
    "status": {
      "type": "string",
      "enum": ["draft", "active", "deprecated"],
      "description": "Lifecycle status of this schema"
    },
    "createdDate": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp when this schema document was first created"
    },
    "lastModifiedDate": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp when this schema document was last updated"
    },
    "lastReviewedDate": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp when this schema document was last reviewed for accuracy"
    }
  },

  "required": ["canonical", "version", "metaVersion", "status", "createdDate"]
}

```

---

## Appendix B – census.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://test.com/json/census/v1.0.0/census.schema.json",
  "$anchor": "census",
  "title": "Census",
  "type": "object",
  "additionalProperties": false,

  "model": {
    "$ref":"https://capbluecross.com/schemas/json/common/modelmetadata/v1.0.0/modelMetadata.schema.json",
    "default": {
      "canonical": "https://capbluecross.com/json/census",
      "version": "1.0.0",
      "metaVersion": 1,
      "status": "draft"
    }
  },

  "required": ["censusName", "status", "members"],

  "properties": {
    "censusName": {
      "type": "string",
      "maxLength": 80,
      "description": "Census Name"
    },
    "account": {
      "type": "string",
      "description": "Group Name"
    },
    "effectiveDate": {
      "type": "string",
      "format": "date",
      "description": "Census Effective Date"
    },
    "producerRelationship": {
      "type": "string",
      "description": "ID to the Agency with visibility to the Census and Quote"
    },
    "standardAgency": {
      "type": "string",
      "description": "Agency Name with visibility to the Census and Quote"
    },
    "status": {
      "type": "string",
      "description": "Census Status",
      "xSfRequired": true
    },
    "segments": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Available Segments (multi-select)"
    },
    "preferredAgency": {
      "type": "string",
      "description": "Preferred Agency Name with visibility to the Census and Quote"
    },
    "annualAttestation": {
      "type": "string",
      "description": "Id for the Attestation"
    },
    "size": {
      "type": "string",
      "description": "Agency size"
    },
    "totalEligible": {
      "type": "number",
      "description": "Total Eligible Health Plan people count"
    },
    "validWaivers": {
      "type": "number",
      "description": "Count of waivers"
    },
    "waiversNoOther": {
      "type": "number",
      "description": "Count of waivers with no other insurance"
    },
    "totalSubscribers": {
      "type": "number",
      "description": "Total subscribers"
    },
    "totalSpouseEe": {
      "type": "number",
      "description": "Total Employee plus spouse"
    },
    "totalMembers": {
      "type": "number",
      "description": "Total members"
    },
    "retireesEnrolled": {
      "type": "number",
      "description": "Total retirees"
    },
    "authorizations": {
      "type": "number",
      "description": "Total authorizations"
    },
    "compliance": {
      "type": "boolean",
      "description": "Compliance flag"
    },
    "coveredEligible": {
      "type": "number",
      "description": "Covered eligible (formula)"
    },
    "totalGroupParticipationPct": {
      "type": "number",
      "description": "Percentage of Total Group Participation"
    },
    "retireeEnrollmentPct": {
      "type": "number",
      "description": "Percentage of Retiree Enrollment"
    },
    "percentageAuthorization": {
      "type": "number",
      "description": "Percentage of Authorizations / Total Enrolled"
    },

    "members": {
      "type": "array",
      "description": "Census Member Object (1..n)",
      "minItems": 1,
      "items": {
        "$ref": "https://capbluecross.com/json/censusMember/v1.0.0/censusMember.schema.json"
      }
    }
  }
}

```

---

## Appendix C – censusMember.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.example.com/json/censusMember/v1.0.0/censusMember.schema.json",
  "$anchor": "censusMember",
  "title": "Census Member",
  "type": "object",
  "additionalProperties": false,

  "properties": {
    "model": {
      "$ref": "https://schemas.example.com/json/common/modelMetadata/v1.0.0/modelMetadata.schema.json",
      "default": {
        "canonical": "https://schemas.example.com/json/censusMember",
        "version": "1.0.0",
        "metaVersion": 1,
        "status": "draft",
        "createdDate": "2025-09-09T00:00:00Z"
      }
    },

    "memberId": {
      "type": "string",
      "description": "Unique identifier for the member"
    },
    "firstName": {
      "type": "string",
      "maxLength": 50,
      "description": "Member's first name"
    },
    "lastName": {
      "type": "string",
      "maxLength": 50,
      "description": "Member's last name"
    },
    "dob": {
      "type": "string",
      "format": "date",
      "description": "Date of birth (YYYY-MM-DD)"
    },
    "gender": {
      "type": "string",
      "enum": ["male", "female", "other", "unknown"],
      "description": "Gender of the member"
    },
    "relationship": {
      "type": "string",
      "enum": ["employee", "spouse", "child", "other"],
      "description": "Relationship of member to subscriber"
    },
    "ssn": {
      "type": "string",
      "pattern": "^[0-9]{9}$",
      "description": "Social Security Number (9 digits)"
    },
    "address": {
      "$ref": "https://schemas.example.com/json/common/address/v1.0.0/address.schema.json",
      "description": "Member's residential address"
    },
    "phoneNumber": {
      "type": "string",
      "pattern": "^[0-9]{10}$",
      "description": "Member's phone number (10 digits)"
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "Member's email address"
    },
    "employmentStatus": {
      "type": "string",
      "enum": ["active", "terminated", "retired", "leave"],
      "description": "Employment status of the member"
    },
    "coverageStartDate": {
      "type": "string",
      "format": "date",
      "description": "Coverage start date"
    },
    "coverageEndDate": {
      "type": "string",
      "format": "date",
      "description": "Coverage end date (if applicable)"
    }
  },

  "required": ["model", "memberId", "firstName", "lastName", "dob", "relationship"]
}

```

---

## Glossary

- **JSON Schema**: Validation vocabulary for JSON.
- **OpenAPI**: REST API specification.
- **\$ref**: Schema reference.
- **Semantic Versioning**: `MAJOR.MINOR.PATCH`.
- **Placeholder Schema**: Temporary draft schema.

---

## References

- JSON Schema Official Spec: [https://json-schema.org/](https://json-schema.org/)
- Semantic Versioning: [https://semver.org/](https://semver.org/)
- OpenAPI Specification: [https://swagger.io/specification/](https://swagger.io/specification/)
- RFC 3339 Date-Time Format: [https://www.rfc-editor.org/rfc/rfc3339](https://www.rfc-editor.org/rfc/rfc3339)

