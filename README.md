Large Group Schemas - Repository Guide

# Large Group Schemas
    This repository contains canonical **JSON Schema** and **OpenAPI** specifications for Large Group models. It provides a standardized, versioned, and validated source of truth for schema definitions that can be used across services##  Purpose
        - Define **data models** using JSON Schema Draft 2020-12
        - Define **API specifications** using OpenAPI 3.0+
        - Ensure consistency across teams and services
        - Automate **validation locally (VS Code)** and **remotely (GitHub Actions CI)**


##  Repository Structure
    largegroup-schemas/
        schemas/
            json/
                census
                    /v1.0.0
                        /census.schema.json
                census-member/
                    v1.0.0/
                        census-member.schema.json
        instances/
            json/
                account
                    /v1.0.0
                        /census.json
                census-member/
                    v1.0.0/
                        census-member.json

        scripts/
            prepush.py
        .github/workflows/validate.yml
        requirements.txt
        README.md


##  Conventions
    - **File naming** → lowercase, kebab-case, semantic versioning
    - **Versioning** → semantic versioning (MAJOR.MINOR.PATCH)
    - **Suffix** → .schema.json for JSON Schema, .yaml for OpenAPI

##  Local Validation (VS Code)
    ### Install dependencies
        pip install -r requirements.txt

    ### Run validators manually
        python scripts/validate_json.py
        python scripts/validate_openapi.py

### Run all validations
    python scripts/prepush.py
    ##  Git Pre-Push Hook (Optional)
        cat << 'EOF' > .git/hooks/pre-push
        #!/bin/bash
        python scripts/prepush.py
        EOF
        chmod +x .git/hooks/pre-push


##  GitHub Actions CI
    All schemas and specs are automatically validated in CI/CD.
        - Runs on every push and pull request to main or develop.
        - Uses Python 3.11 with jsonschema and openapi-spec-validator.
        - Fails the pipeline if any schema or OpenAPI spec is invalid.
##  Example Outputs
    JSON Schema valid: schemas/json/account/v1.0.0/account.schema.json
    OpenAPI spec valid: schemas/openapi/v1.0.0/openapi.yaml
    Schema error in schemas/json/account/v1.0.0/account.schema.json: 'properties' must be an object

##  Tech Stack
    - JSON Schema Draft 2020-12
    - OpenAPI 3.0+
    - Python jsonschema
    - OpenAPI Spec Validator
    - GitHub Actions

##  Roadmap
- Add auto-release tagging for versioned schemas
