# Testing

## Quick Start

```bash
make test          # run all tests
make test-cov      # run tests with coverage report
make lint          # lint tools/ and config/
make check         # lint + test combined
```

Or directly via pytest:

```bash
pytest tests/ -v --tb=short
pytest tests/test_skills.py -v          # single file
pytest tests/ -k "rpz"                  # filter by name
```

## Coverage

```bash
make test-cov
# or
pytest --cov=tools --cov=config tests/ --cov-report=term-missing
```

Coverage is configured in `pyproject.toml` under `[tool.coverage.*]`.

## Test Structure

| File | Covers |
|------|--------|
| `test_skills.py` | Skill structure, references, triggers, API checks (24 tests) |
| `test_fmea_standards.py` | S/O/D scales, safety overrides from `config/fmea_standards.py` |
| `test_rpz_calculator.py` | RPZ calculation and classification logic |
| `test_load_plant_data.py` | Loading and validating `anlagendaten.json` |
| `test_validate_anlagendaten.py` | Schema validation for plant data |
| `test_validate_completeness_enhanced.py` | Enhanced completeness checks |
| `test_validate_completeness_direct.py` | Direct completeness validation |
| `test_schema_validation.py` | JSON schema validation |
| `test_workflow_state.py` | Workflow state management |
| `test_storage.py` | Storage layer tests |
| `test_structure_analysis.py` | Structure analysis tool |
| `test_calibration.py` | Calibration logic |
| `test_quality_report.py` | Quality report generation |
| `test_export.py` | Export functionality |
| `test_report_generator.py` | Report generation |
| `test_full_pipeline.py` | End-to-end pipeline |
| `eval_goldstandard.py` | Goldstandard eval (formal, completeness, plausibility, comparison) |
| `eval_fmea_rpz.py` | RPZ evaluation checks |

## Adding New Tests

1. Create `tests/test_<feature>.py`
2. Use standard pytest conventions (`test_` prefix for functions/classes)
3. Import shared helpers from `tests/helpers.py`
4. Run `make test` to verify
