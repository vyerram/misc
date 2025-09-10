#!/usr/bin/env python3
"""
Universal validator for JSON Schema, JSON instances, and OpenAPI specs.

Supports:
- Manual validation with --schema / --instance flags
- Auto-discovery for Git pre-push hooks
- GitHub Actions workflow validation

Rules:
1. *.schema.json → validate against Draft 2020-12 metaschema
2. *.schema.yaml / *.schema.yml → validate as OpenAPI schema
3. *.json (instances):
     - If $schema present → validate against referenced schema
     - Else fallback to schemas/... path convention
4. *.yaml / *.yml (instances) → validate as OpenAPI spec
"""

import argparse
import json
import pathlib
import sys
import urllib.request
import yaml
from jsonschema import Draft202012Validator, RefResolver, validate, ValidationError, SchemaError
from openapi_spec_validator import validate_spec


# -------------------------------
# Utility functions
# -------------------------------

def load_json(path: pathlib.Path):
    with open(path, "r") as f:
        return json.load(f)

def load_yaml(path: pathlib.Path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_draft202012_metaschema():
    url = "https://json-schema.org/draft/2020-12/schema"
    with urllib.request.urlopen(url) as response:
        return json.load(response)


# -------------------------------
# Validators
# -------------------------------

def validate_json_schema(schema_path: pathlib.Path):
    """Validate JSON schema against Draft 2020-12 metaschema."""
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    metaschema = load_draft202012_metaschema()
    validate(instance=schema, schema=metaschema)
    print(f"✅ {schema_path} is a valid Draft 2020-12 JSON Schema")

def validate_openapi_spec(path: pathlib.Path):
    """Validate OpenAPI schema or instance."""
    spec = load_yaml(path)
    validate_spec(spec)
    print(f"✅ {path} is a valid OpenAPI specification")

def validate_instance_against_schema(instance_path: pathlib.Path, schema_path: pathlib.Path):
    """Validate JSON instance against schema with $ref resolution."""
    schema = load_json(schema_path)
    instance = load_json(instance_path)

    base_uri = schema_path.resolve().as_uri()
    resolver = RefResolver(base_uri=base_uri, referrer=schema)

    Draft202012Validator(schema, resolver=resolver).validate(instance)
    print(f"✅ {instance_path} is valid against {schema_path} (with $ref support)")

def validate_json_instance(instance_path: pathlib.Path):
    """Validate a JSON instance, resolving schema via $schema or fallback path."""
    instance = load_json(instance_path)

    # Case A: instance explicitly declares $schema
    if "$schema" in instance:
        schema_uri = instance["$schema"]
        schema_path = pathlib.Path(schema_uri)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema path in $schema not found: {schema_path}")
        validate_instance_against_schema(instance_path, schema_path)
        return

    # Case B: fallback convention: instances/json/... -> schemas/json/... and .json -> .schema.json
    schema_path = (
        pathlib.Path(str(instance_path).replace("instances/json", "schemas/json"))
        .with_suffix(".schema.json")
    )
    if not schema_path.exists():
        raise FileNotFoundError(
            f"No $schema property in {instance_path}, and fallback schema not found (expected {schema_path})"
        )
    validate_instance_against_schema(instance_path, schema_path)


# -------------------------------
# Auto-discovery driver
# -------------------------------

def discover_and_validate(root: pathlib.Path):
    """Walk through repo and validate everything."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.name.endswith(".schema.json"):
                validate_json_schema(path)
            elif path.suffix in [".yaml", ".yml"] and ".schema." in path.name:
                validate_openapi_spec(path)
            elif path.suffix == ".json" and not path.name.endswith(".schema.json"):
                validate_json_instance(path)
            elif path.suffix in [".yaml", ".yml"]:
                validate_openapi_spec(path)
        except Exception as e:
            print(f"❌ Validation failed for {path}: {e}")
            sys.exit(1)


# -------------------------------
# Main CLI
# -------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate JSON Schema, JSON instances, and OpenAPI specs")
    parser.add_argument("--schema", type=str, help="Path to schema file (.schema.json/.schema.yaml)")
    parser.add_argument("--instance", type=str, help="Path to instance file (.json/.yaml)")
    args = parser.parse_args()

    try:
        if args.schema and not args.instance:
            schema_path = pathlib.Path(args.schema)
            if schema_path.suffix == ".json":
                validate_json_schema(schema_path)
            elif schema_path.suffix in [".yaml", ".yml"]:
                validate_openapi_spec(schema_path)

        elif args.schema and args.instance:
            instance_path = pathlib.Path(args.instance)
            schema_path = pathlib.Path(args.schema)
            if instance_path.suffix == ".json" and schema_path.suffix == ".json":
                validate_instance_against_schema(instance_path, schema_path)
            elif instance_path.suffix in [".yaml", ".yml"]:
                validate_openapi_spec(instance_path)

        elif args.instance and not args.schema:
            instance_path = pathlib.Path(args.instance)
            if instance_path.suffix == ".json":
                validate_json_instance(instance_path)
            elif instance_path.suffix in [".yaml", ".yml"]:
                validate_openapi_spec(instance_path)

        else:
            # no args: run discovery across repo (git hook / CI mode)
            repo_root = pathlib.Path(__file__).resolve().parents[1]  # go up from scripts/
            print(f"🔍 Auto-discovering validations under {repo_root}")
            discover_and_validate(repo_root)
            print("🎉 All validations passed!")

    except (ValidationError, SchemaError) as e:
        print(f"❌ Validation failed: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
