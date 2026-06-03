"""Validazione del dataset di CampusCare AI.

Il modulo controlla che il dataset generato sia coerente con il dominio
definito in domain.py.

Questa validazione è utile per verificare che i dati usati dal modello ML
non contengano valori fuori vocabolario o incoerenze rispetto alla knowledge base.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .domain import (
    DEVICES,
    PRIORITIES,
    ROOM_COORDINATES,
    ROOM_TYPE_BY_NAME,
    ROOM_TYPES,
    SYMPTOMS,
)
from .generate_dataset import DATASET_PATH, generate_dataset


@dataclass(frozen=True)
class ValidationReport:
    """Risultato della validazione del dataset."""

    path: Path
    rows: int
    columns: int
    errors: list[str]
    warnings: list[str]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


EXPECTED_COLUMNS = [
    "report_id",
    "room_name",
    "room_type",
    "device",
    "symptom",
    "event_in_minutes",
    "users_involved",
    "exam_or_lecture",
    "temperature",
    "network_load",
    "priority",
]


def load_or_generate_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    """Carica il dataset oppure lo genera se non esiste."""

    if not path.exists():
        return generate_dataset(output_path=path)

    return pd.read_csv(path)


def validate_columns(dataset: pd.DataFrame) -> list[str]:
    """Controlla che le colonne attese siano presenti."""

    errors = []

    missing_columns = set(EXPECTED_COLUMNS) - set(dataset.columns)
    extra_columns = set(dataset.columns) - set(EXPECTED_COLUMNS)

    if missing_columns:
        errors.append(f"Missing columns: {sorted(missing_columns)}")

    if extra_columns:
        errors.append(f"Unexpected columns: {sorted(extra_columns)}")

    return errors


def validate_categorical_values(dataset: pd.DataFrame) -> list[str]:
    """Controlla i valori categorici rispetto al dominio."""

    errors = []

    valid_room_names = set(ROOM_COORDINATES.keys())
    valid_room_types = set(ROOM_TYPES)
    valid_devices = set(DEVICES)
    valid_symptoms = set(SYMPTOMS)
    valid_priorities = set(PRIORITIES)

    invalid_room_names = set(dataset["room_name"]) - valid_room_names
    invalid_room_types = set(dataset["room_type"]) - valid_room_types
    invalid_devices = set(dataset["device"]) - valid_devices
    invalid_symptoms = set(dataset["symptom"]) - valid_symptoms
    invalid_priorities = set(dataset["priority"]) - valid_priorities

    if invalid_room_names:
        errors.append(f"Invalid room names: {sorted(invalid_room_names)}")

    if invalid_room_types:
        errors.append(f"Invalid room types: {sorted(invalid_room_types)}")

    if invalid_devices:
        errors.append(f"Invalid devices: {sorted(invalid_devices)}")

    if invalid_symptoms:
        errors.append(f"Invalid symptoms: {sorted(invalid_symptoms)}")

    if invalid_priorities:
        errors.append(f"Invalid priorities: {sorted(invalid_priorities)}")

    return errors


def validate_room_type_consistency(dataset: pd.DataFrame) -> list[str]:
    """Controlla che room_name e room_type siano coerenti."""

    errors = []

    for index, row in dataset.iterrows():
        room_name = row["room_name"]
        room_type = row["room_type"]

        expected_room_type = ROOM_TYPE_BY_NAME.get(room_name)

        if expected_room_type is None:
            continue

        if room_type != expected_room_type:
            errors.append(
                f"Row {index}: room '{room_name}' has type '{room_type}', "
                f"expected '{expected_room_type}'"
            )

    return errors


def validate_numeric_ranges(dataset: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Controlla intervalli numerici ragionevoli."""

    errors = []
    warnings = []

    if (dataset["event_in_minutes"] < 0).any():
        errors.append("event_in_minutes contains negative values")

    if (dataset["users_involved"] < 0).any():
        errors.append("users_involved contains negative values")

    if not dataset["exam_or_lecture"].isin([0, 1]).all():
        errors.append("exam_or_lecture must contain only 0 or 1")

    if not dataset["network_load"].between(0.0, 1.0).all():
        errors.append("network_load must be between 0 and 1")

    if not dataset["temperature"].between(0.0, 50.0).all():
        warnings.append("temperature contains values outside the expected 0-50 range")

    return errors, warnings


def validate_class_distribution(dataset: pd.DataFrame) -> list[str]:
    """Segnala classi troppo rare."""

    warnings = []

    counts = dataset["priority"].value_counts()
    total = len(dataset)

    for priority, count in counts.items():
        ratio = count / total

        if ratio < 0.05:
            warnings.append(
                f"Priority class '{priority}' is rare: {count} examples "
                f"({ratio:.2%})"
            )

    return warnings


def validate_dataset(path: Path = DATASET_PATH) -> ValidationReport:
    """Esegue la validazione completa."""

    dataset = load_or_generate_dataset(path)

    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(validate_columns(dataset))
    errors.extend(validate_categorical_values(dataset))
    errors.extend(validate_room_type_consistency(dataset))

    numeric_errors, numeric_warnings = validate_numeric_ranges(dataset)
    errors.extend(numeric_errors)
    warnings.extend(numeric_warnings)

    warnings.extend(validate_class_distribution(dataset))

    return ValidationReport(
        path=path,
        rows=len(dataset),
        columns=len(dataset.columns),
        errors=errors,
        warnings=warnings,
    )


def main() -> None:
    """Esegue la validazione e stampa un report."""

    report = validate_dataset()

    print("Dataset validation report")
    print("-------------------------")
    print(f"Path: {report.path}")
    print(f"Rows: {report.rows}")
    print(f"Columns: {report.columns}")
    print(f"Valid: {report.is_valid}")
    print()

    if report.errors:
        print("Errors:")
        for error in report.errors:
            print(f"- {error}")
    else:
        print("Errors: none")

    print()

    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")
    else:
        print("Warnings: none")


if __name__ == "__main__":
    main()