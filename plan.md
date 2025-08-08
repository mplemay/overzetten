# Testing Plan: SQLAlchemy to Pydantic DTO Library

This document outlines a comprehensive testing plan for the `overzetten` library, which converts SQLAlchemy models to Pydantic DTOs.

## 1. Core Functionality Tests (Enhanced)

### Basic DTO Creation
**Test Suite:** `test_basic_dto_creation.py`
- ~Test creating a basic DTO with no configuration (`DTOConfig()`).~
- ~Test that all SQLAlchemy fields are properly converted with correct Python types.~
- ~Test that the generated Pydantic model has correct field names matching SQLAlchemy columns.~
- ~Test that the returned class is actually a Pydantic model (instance of `BaseModel`).~
- ~**New:** Test that `__name__` and `__qualname__` are set correctly on generated models.~
- ~**New:** Test that generated models have proper `__module__` attribution.~
- ~**New:** Test creating multiple DTOs from the same SQLAlchemy model with different configs.~

### Type Conversion Tests
**Test Suite:** `test_type_conversion.py`
- ~Test conversion of all basic SQLAlchemy types:~
  - ~`String` → `str`~
  - ~`Integer` → `int`~
  - ~`Boolean` → `bool`~
  - ~`DateTime` → `datetime`~
  - ~`Date` → `date`~
  - ~`Time` → `time`~
  - ~`Text` → `str`~
  - ~`Float` → `float`~
  - ~`Numeric`/`DECIMAL` → `Decimal`~
  - ~`LargeBinary` → `bytes`~
- ~**New:** Test PostgreSQL-specific types (`UUID`, `JSONB`, `ARRAY`, `ENUM`).~
- ~**New:** Test MySQL-specific types (`YEAR`, `SET`, `ENUM` variations).~
- ~**New:** Test SQLite type handling and limitations.~
- ~**New:** Test custom SQLAlchemy types with `python_type` property.~
- ~Test handling of `Mapped[T]` annotations vs raw column types.~
- ~**New:** Test type conversion with generic types (`Mapped[List[str]]`, `Mapped[Dict[str, int]]`).~
- ~**New:** Test handling of types that don't have direct Python equivalents.~

### Nullable Field Handling (Enhanced)
- ~Test that nullable fields become `Optional[T]` correctly.~
- ~Test that non-nullable fields remain required (no `Optional` wrapper).~
- ~Test mixed nullable and non-nullable fields in same model.~
- ~**New:** Test that `Optional[T]` fields aren't double-wrapped as `Optional[Optional[T]]`.~
- ~**New:** Test nullable fields with custom type mappings (nullable + `EmailStr` → `Optional[EmailStr]`).~
- ~**New:** Test server-side nullable vs Python-side nullable handling.~

## 2. Configuration Tests (Significantly Enhanced)

### Field Mapping (`mapped` parameter)
**Test Suite:** `test_field_mapping.py`
- ~Comprehensive Pydantic Type Testing:~
  - ~`EmailStr`, `HttpUrl`~
  - ~`UUID4`, `Json`, `SecretStr`~
  - ~Custom Pydantic validators and constraints~
  - ~`Field()` with validation, description, examples~
  - ~Annotated types with metadata~
- ~Test mapping to complex types:~
  - ~`List[CustomType]`, `Dict[str, CustomType]`~
  - ~`Union` types, `Literal` types~
  - ~Custom Pydantic models as field types~
- ~Test mapping relationships to other DTO types.~
- ~Test circular mapping references.~
- ~**New:** Test mapping same field to different types in different DTOs.~
- ~**New:** Test mapping fields that don't exist in SQLAlchemy model (should error).~
- ~Test mapping with inheritance (parent class mappings).~

### Field Exclusion (`exclude` parameter) (Enhanced)
- ~Test excluding various field types (columns, relationships, hybrids).~
- ~Test excluding inherited fields from parent models.~
- ~Test excluding fields with foreign key constraints.~
- ~**New:** Test excluding fields that are referenced in `mapped` (should take precedence).~
- ~**New:** Test excluding all fields except one (edge case).~
- ~**New:** Test excluding computed/hybrid properties.~

### Field Inclusion (`include` parameter) (New Section)
**Test Suite:** `test_field_inclusion.py`
- ~Test including only specific subset of fields.~
- ~Test that `exclude` takes precedence over `include`.~
- ~Test including relationships vs columns.~
- ~Test including inherited fields selectively.~
- ~Test empty `include` set behavior.~
- ~Test `include` with `mapped` combinations.~

### Model Naming (Enhanced)
**Test Suite:** `test_model_naming.py`
- ~Test all naming configuration combinations:~
  - ~`model_name` override~
  - ~`model_name_prefix` + `model_name_suffix`~
  - ~Default naming patterns~
- ~**New:** Test name conflicts and resolution.~
- ~**New:** Test very long names (edge case).~
- ~**New:** Test names with special characters.~
- ~**New:** Test that naming doesn't affect functionality.~

## 3. Default Values and Required Fields (Enhanced)

### SQLAlchemy Defaults (More Comprehensive)
**Test Suite:** `test_defaults_and_required.py`
- ~Test scalar defaults (`default=True`, `default='value'`).~
- ~Test callable defaults (`default=datetime.now`).~
- ~Test server defaults (`server_default=func.now()`).~
- ~Test `insert_default` vs `default` vs `server_default` handling.~
- ~Test defaults with custom type mappings.~
- ~Test `init=False` fields (should not appear in DTO constructor).~
- ~Test autoincrement fields.~
- ~Test sequence defaults.~

### Custom Defaults (`field_defaults`) (New Focus)
- ~Test overriding SQLAlchemy defaults.~
- ~Test setting defaults for required fields.~
- ~Test defaults for excluded fields (should be ignored).~
- ~Test callable vs static defaults.~
- ~Test defaults that don't match field types (should validate).~

### Required Field Logic (New Section)
- ~Test logic: not nullable and no default = required.~
- ~Test logic: nullable and no default = `Optional` with `None` default.~
- ~Test logic: not nullable but has default = `T` with default.~
- ~Test interaction with custom `field_defaults`.~

## 4. Inheritance and Relationships (Major Enhancement)

### SQLAlchemy Model Inheritance (More Detailed)
**Test Suite:** `test_inheritance.py`
- ~Single Table Inheritance:~
  - ~Test parent and child DTOs.~
  - ~Test discriminator column handling.~
  - ~Test inherited field exclusion/mapping.~
- ~Joined Table Inheritance:~
  - ~Test field distribution across tables.~
  - ~Test foreign key relationships between parent/child.~
- ~Concrete Table Inheritance:~
  - ~Test independent table DTOs.~
- ~Mixin Classes:~
  - ~Test DTOs from models with mixins.~
  - ~Test mixin field inheritance.~
- ~Abstract Base Classes:~
  - ~Test that abstract models can't create DTOs directly.~

### Relationships (Comprehensive New Section)
**Test Suite:** `test_relationships.py`
- ~One-to-Many:~
  - ~Test parent DTO including children collection.~
  - ~Test child DTO excluding parent reference.~
  - Test lazy loading behavior preservation.
- ~Many-to-One:~
  - ~Test foreign key field handling.~
  - ~Test relationship object inclusion.~
- ~Many-to-Many:~
  - ~Test association table handling.~
  - ~Test through-model relationships.~
- ~Self-Referential:~
  - ~Test tree structures, hierarchical data.~
- ~Advanced Relationship Options:~
  - ~`back_populates`, `backref` handling.~
  - `cascade` option preservation.
  - `secondary` table relationships.
- ~Relationship Mapping:~
  - ~Test mapping relationships to other DTO types.~
  - ~Test circular DTO references.~
  - ~Test relationship validation.~

## 5. Advanced Features (Enhanced)

### Caching (More Thorough)
**Test Suite:** `test_caching.py`
- ~Test cache key generation uniqueness.~
- ~Test that functionally identical configs share cache.~
- ~Test cache invalidation scenarios.~
- ~**New:** Test cache size limits and LRU behavior.~
- ~**New:** Test thread safety of cache.~
- ~**New:** Test cache memory leaks with many models.~
- ~**New:** Test cache behavior with dynamic imports.~

### Pydantic Configuration (Comprehensive)
**Test Suite:** `test_pydantic_config.py`
- ~Test all `ConfigDict` options:~
  - ~`validate_assignment`, `use_enum_values`, `populate_by_name`~
  - ~`str_strip_whitespace`, `json_schema_extra`~
  - ~`frozen`, `extra='forbid'/'allow'/'ignore'`~
- ~Test custom serialization (`model_serializer`).~
- ~Test custom validation (`field_validator`, `model_validator`).~
- ~**New:** Test JSON schema generation options.~
- ~**New:** Test performance settings (`validate_default`).~

## 6. Edge Cases and Error Handling (Major Enhancement)

### Invalid Configurations (Comprehensive)
**Test Suite:** `test_error_handling.py`
- ~SQLAlchemy Model Issues:~
  - ~Non-`MappedAsDataclass` models (should error clearly).~
  - ~Models without `__tablename__`.~
  - ~Models with `__abstract__ = True`.~
- ~Configuration Conflicts:~
  - ~Mapping non-existent fields.~
  - ~Excluding and including same field.~
  - ~Invalid type mappings (non-type objects).~
- ~Type System Issues:~
  - ~Mapping to incompatible types.~
  - ~Generic type edge cases.~

### Complex SQLAlchemy Features (New Section)
**Test Suite:** `test_complex_sqlalchemy.py`
- ~Hybrid Properties: Test inclusion/exclusion, type detection.~
- ~Association Objects: Test many-to-many through objects.~
- Synonyms: Test field aliasing.
- Column Properties: Test computed columns, SQL expressions.
- ~Custom Types: Test user-defined column types.~
- Multiple Schemas: Test cross-schema relationships.
- ~Polymorphic Models: Test `polymorphic_on`, `with_polymorphic`.~

### Memory and Performance (Enhanced)
**Test Suite:** `test_performance.py`
- Load Testing: Generate 1000s of DTOs rapidly.
- Memory Profiling: Track memory usage patterns.
- Concurrent Access: Test thread safety.
- Large Model Testing: Models with 100+ fields.
- Deep Inheritance: 10+ levels of model inheritance.
- Benchmark Comparisons: vs manual Pydantic models, vs dataclasses.

## 7. Integration Tests (Significantly Enhanced)

### FastAPI Integration (Comprehensive)
**Test Suite:** `test_fastapi_integration.py`
- Request/Response Models:
    - DTOs as request bodies with validation.
    - DTOs as response models with serialization.
    - DTOs in path parameters, query parameters.
- OpenAPI Generation:
    - Schema generation correctness.
    - Documentation strings, examples.
    - Type hints in generated schemas.
- Validation Behavior:
    - Request validation errors.
    - Response serialization errors.
    - Custom validator interaction.
- Advanced FastAPI Features:
    - Dependency injection with DTOs.
    - Background tasks with DTOs.
    - File uploads combined with DTOs.
    - WebSocket message DTOs.

### SQLAlchemy Integration (Enhanced)
**Test Suite:** `test_sqlalchemy_integration.py`
- Different SQLAlchemy Versions: 2.0+, test version compatibility.
- Database Engines: PostgreSQL, MySQL, SQLite specific behaviors.
- Session Integration:
    - `model_validate()` with session-loaded objects.
    - Lazy loading interaction.
    - Session expiry handling.
- Query Integration:
    - DTOs from query results.
    - Bulk operations with DTOs.
- Transaction Integration:
    - DTO validation in transactions.
    - Rollback behavior.

### Pydantic Integration (New Comprehensive Section)
**Test Suite:** `test_pydantic_integration.py`
- Version Compatibility: Test with Pydantic v1 vs v2.
- Serialization Formats:
    - JSON serialization/deserialization.
    - Dictionary conversion.
    - Custom serializers.
- Validation Integration:
    - Field validators with SQLAlchemy data.
    - Root validators.
    - Custom error handling.
- Schema Generation:
    - JSON Schema output.
    - OpenAPI schema compatibility.
    - Custom schema modifications.

## 8. Metaclass and Generic Behavior (Enhanced)

### Generic Type Resolution (More Thorough)
**Test Suite:** `test_generics_and_metaclass.py`
- Test `DTO[Model]` syntax variations.
- Test multiple type parameters (future expansion).
- Test nested generic scenarios.
- **New:** Test generic type resolution with inheritance.
- **New:** Test type variable constraints.
- **New:** Test runtime type inspection (`get_args`, `get_origin`).

### Metaclass Edge Cases (Comprehensive)
**Test Suite:** `test_generics_and_metaclass.py`
- Test multiple DTO inheritance scenarios.
- Test metaclass interaction with decorators.
- Test dynamic class creation scenarios.
- **New:** Test metaclass behavior with `__slots__`.
- **New:** Test metaclass + dataclass + Pydantic interaction.
- **New:** Test pickle/unpickle of generated DTOs.

## 9. Real-World Scenarios (Major Enhancement)

### Common CRUD Patterns (Comprehensive)
**Test Suite:** `test_real_world_crud.py`
- User Management System:
    - `UserCreateDTO` (no ID, timestamps)
    - `UserUpdateDTO` (optional fields, no ID)
    - `UserResponseDTO` (no password, all fields)
    - `UserListDTO` (minimal fields for lists)
- Blog System:
    - Post/Comment/Author DTOs with relationships.
    - Nested DTO serialization.
    - Permission-based field inclusion.
- E-commerce System:
    - Product/Order/Customer DTOs.
    - Complex relationships and calculations.
    - Money/currency handling.

### API Versioning (New Section)
**Test Suite:** `test_api_versioning.py`
- Test multiple DTO versions for same model.
- Test backward compatibility.
- Test field deprecation strategies.
- Test migration between DTO versions.

### Performance Optimization (New Section)
**Test Suite:** `test_optimization_patterns.py`
- Test lazy loading with DTOs.
- Test partial field loading.
- Test DTO caching strategies.
- Test bulk serialization patterns.

### Security Patterns (New Section)
**Test Suite:** `test_security_patterns.py`
- Test sensitive field exclusion (passwords, tokens).
- Test role-based DTO generation.
- Test data sanitization in DTOs.
- Test audit logging with DTOs.

## 10. Documentation and Examples (Enhanced)

### Code Examples Validation (Automated)
**Test Suite:** `test_documentation.py`
- Automated testing of all README examples.
- Docstring example validation (doctest).
- Tutorial code verification.
- **New:** Test examples with different Python versions.
- **New:** Test examples with various dependency combinations.

### Type Hints and IDE Support (New Section)
**Test Suite:** `test_type_support.py`
- Test mypy static analysis passes.
- Test PyRight/Pylance compatibility.
- Test IDE autocompletion scenarios.
- Test type hint accuracy in generated models.

## 11. Migration and Compatibility (New Major Section)

### SQLAlchemy Migrations (New)
**Test Suite:** `test_migrations.py`
- Test DTO behavior when models change.
- Test Alembic migration compatibility.
- Test graceful handling of missing fields.
- Test field type changes.

### Dependency Version Matrix (New)
**Test Suite:** `test_compatibility_matrix.py`
- Test with different SQLAlchemy versions (2.0.0+).
- Test with different Pydantic versions (2.0+).
- Test with different Python versions (3.9+).
- Test with different FastAPI versions.

## 12. Specialized Testing Tools (New Section)

### Property-Based Testing (New)
**Test Suite:** `test_property_based.py`
- Use Hypothesis to generate:
    - Random SQLAlchemy models.
    - Random DTO configurations.
    - Random data for validation.
- Test invariants hold across all generated cases.

### Mutation Testing (New)
- Use tools like `mutmut` to test test quality.
- Ensure tests catch regressions.
- Verify error handling paths are tested.

### Performance Benchmarking (New)
**Test Suite:** `test_benchmarks.py`
- Benchmark DTO creation time.
- Benchmark serialization performance.
- Compare with manual Pydantic models.
- Track performance regressions.

## Enhanced Test Implementation Strategy

### Test Organization
```
tests/
├── unit/                           # Fast, isolated tests
│   ├── core/
│   │   ├── test_basic_dto_creation.py
│   │   ├── test_type_conversion.py
│   │   └── test_field_handling.py
│   ├── config/
│   │   ├── test_field_mapping.py
│   │   ├── test_field_exclusion.py
│   │   ├── test_field_inclusion.py
│   │   ├── test_model_naming.py
│   │   └── test_defaults_and_required.py
│   ├── advanced/
│   │   ├── test_caching.py
│   │   ├── test_pydantic_config.py
│   │   ├── test_inheritance.py
│   │   └── test_relationships.py
│   └── edge_cases/
│       ├── test_error_handling.py
│       ├── test_complex_sqlalchemy.py
│   └── test_generics_and_metaclass.py
├── integration/                    # Cross-component tests
│   ├── test_fastapi_integration.py
│   ├── test_sqlalchemy_integration.py
│   ├── test_pydantic_integration.py
│   └── test_real_world_crud.py
├── performance/                    # Performance and load tests
│   ├── test_benchmarks.py
│   ├── test_memory_usage.py
│   └── test_optimization_patterns.py
├── compatibility/                  # Version and platform tests
│   ├── test_compatibility_matrix.py
│   ├── test_migrations.py
│   └── test_api_versioning.py
├── security/                      # Security-focused tests
│   ├── test_security_patterns.py
│   └── test_data_sanitization.py
├── fixtures/                      # Shared test data
│   ├── sqlalchemy_models.py      # Comprehensive model definitions
│   ├── sample_data.py            # Test data generators
│   └── dto_configs.py            # Reusable DTO configurations
├── utils/                         # Test utilities
│   ├── assertions.py             # Custom assertions
│   ├── factories.py              # Data factories
│   └── profiling.py              # Performance measurement
└── conftest.py                    # Global pytest configuration
```