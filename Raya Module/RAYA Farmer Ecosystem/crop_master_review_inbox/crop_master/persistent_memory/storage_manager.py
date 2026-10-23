"""
RAYA Phase 4A
Persistent Farmer Intelligence Layer

Generic JSON Storage Manager.

This module is the persistence foundation for Phase 4.
Business modules should use this layer instead of directly
reading or writing JSON files.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIRECTORY = PROJECT_ROOT / "data" / "persistent_memory"

FARMERS_FILE = DATA_DIRECTORY / "farmers.json"
FARMS_FILE = DATA_DIRECTORY / "farms.json"
FIELDS_FILE = DATA_DIRECTORY / "fields.json"
SOIL_PROFILES_FILE = DATA_DIRECTORY / "soil_profiles.json"
SEASONS_FILE = DATA_DIRECTORY / "seasons.json"
ADVISORY_HISTORY_FILE = DATA_DIRECTORY / "advisory_history.json"
FIELD_ACTIVITY_FILE = DATA_DIRECTORY / "field_activity.json"


# ============================================================
# STORAGE MANAGER
# ============================================================

class StorageManager:
    """
    Thread-safe JSON persistence layer.

    Phase 4A entities:
        - farmers
        - farms
        - fields

    This class intentionally contains no agricultural
    business logic.
    """

    _lock = RLock()

    def __init__(self, data_directory: Optional[Path] = None):
        self.data_directory = (
            Path(data_directory)
            if data_directory is not None
            else DATA_DIRECTORY
        )

        self.data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._entity_files = {
            "farmers": self.data_directory / "farmers.json",
            "farms": self.data_directory / "farms.json",
            "fields": self.data_directory / "fields.json",
            "soil_profiles": self.data_directory / "soil_profiles.json",
            "seasons": self.data_directory / "seasons.json",
            "advisory_history": self.data_directory / "advisory_history.json",
            "field_activity": self.data_directory / "field_activity.json",
        }

        self.initialize_storage()

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def initialize_storage(self) -> None:
        """
        Ensure all Phase 4A storage files exist.
        """

        for file_path in self._entity_files.values():

            if not file_path.exists():
                self._atomic_write(
                    file_path,
                    [],
                )

    # ========================================================
    # FILE ACCESS
    # ========================================================

    def _get_file_path(
        self,
        entity_type: str,
    ) -> Path:
        """
        Return the storage file for an entity type.
        """

        if entity_type not in self._entity_files:
            raise ValueError(
                f"Unsupported entity type: {entity_type}. "
                f"Supported: {list(self._entity_files.keys())}"
            )

        return self._entity_files[entity_type]

    # ========================================================
    # JSON READ
    # ========================================================

    def read_all(
        self,
        entity_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Read all records for an entity type.

        Returns:
            List of dictionaries.
        """

        file_path = self._get_file_path(
            entity_type,
        )

        with self._lock:

            try:

                with file_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:

                    data = json.load(file)

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    f"Storage corruption detected in "
                    f"{file_path.name}: {exc}"
                ) from exc

            if not isinstance(data, list):

                raise RuntimeError(
                    f"Invalid storage format in "
                    f"{file_path.name}. "
                    f"Expected a JSON list."
                )

            return data

    # ========================================================
    # JSON WRITE
    # ========================================================

    def write_all(
        self,
        entity_type: str,
        records: List[Dict[str, Any]],
    ) -> None:
        """
        Persist all records for an entity type.
        """

        if not isinstance(records, list):

            raise TypeError(
                "records must be a list"
            )

        file_path = self._get_file_path(
            entity_type,
        )

        with self._lock:

            self._atomic_write(
                file_path,
                records,
            )

    def _atomic_write(
        self,
        file_path: Path,
        data: Any,
    ) -> None:
        """
        Safely write JSON using temporary-file replacement.

        This reduces the risk of partially written JSON files
        if the application stops during a write operation.
        """

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_file = None

        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=file_path.parent,
                delete=False,
                suffix=".tmp",
            ) as temp:

                json.dump(
                    data,
                    temp,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

                temp.flush()

                os.fsync(
                    temp.fileno()
                )

                temporary_file = Path(
                    temp.name
                )

            os.replace(
                temporary_file,
                file_path,
            )

        finally:

            if (
                temporary_file
                and temporary_file.exists()
            ):
                temporary_file.unlink(
                    missing_ok=True
                )

    # ========================================================
    # RECORD LOOKUP
    # ========================================================

    def get_by_id(
        self,
        entity_type: str,
        record_id: str,
        id_field: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve one record by its ID.
        """

        records = self.read_all(
            entity_type,
        )

        for record in records:

            if record.get(id_field) == record_id:

                return record

        return None

    def find(
        self,
        entity_type: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Find records matching all supplied filters.
        """

        records = self.read_all(
            entity_type,
        )

        matches = []

        for record in records:

            is_match = all(
                record.get(key) == value
                for key, value
                in filters.items()
            )

            if is_match:

                matches.append(
                    record
                )

        return matches

    # ========================================================
    # RECORD OPERATIONS
    # ========================================================

    def insert(
        self,
        entity_type: str,
        record: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Insert a record.

        Duplicate validation belongs to the registry layer.
        """

        records = self.read_all(
            entity_type,
        )

        records.append(
            record
        )

        self.write_all(
            entity_type,
            records,
        )

        return record

    def insert_if_unique(
        self,
        entity_type: str,
        record: Dict[str, Any],
        unique_field: str,
    ) -> tuple[Dict[str, Any], bool]:
        """Insert a record once per entity and unique-field value."""

        unique_value = record.get(unique_field)
        if not unique_value:
            raise ValueError(
                f"Record must provide a value for {unique_field}."
            )

        with self._lock:
            records = self.read_all(entity_type)

            for existing in records:
                if existing.get(unique_field) == unique_value:
                    return existing, False

            records.append(record)
            self.write_all(entity_type, records)

        return record, True

    def update_by_id(
        self,
        entity_type: str,
        record_id: str,
        id_field: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Update a record by ID.
        """

        records = self.read_all(
            entity_type,
        )

        updated_record = None

        for index, record in enumerate(records):

            if record.get(id_field) == record_id:

                records[index] = {
                    **record,
                    **updates,
                }

                updated_record = (
                    records[index]
                )

                break

        if updated_record is not None:

            self.write_all(
                entity_type,
                records,
            )

        return updated_record

    def delete_by_id(
        self,
        entity_type: str,
        record_id: str,
        id_field: str,
    ) -> bool:
        """
        Delete a record by ID.

        Higher-level relationship validation belongs
        to the registry layer.
        """

        records = self.read_all(
            entity_type,
        )

        filtered_records = [

            record
            for record in records
            if record.get(id_field) != record_id

        ]

        if len(filtered_records) == len(records):

            return False

        self.write_all(
            entity_type,
            filtered_records,
        )

        return True

    # ========================================================
    # METADATA HELPERS
    # ========================================================

    @staticmethod
    def utc_timestamp() -> str:
        """
        Return an ISO-8601 UTC timestamp.
        """

        return (
            datetime.now(
                timezone.utc
            )
            .replace(
                microsecond=0
            )
            .isoformat()
        )

    @staticmethod
    def generate_id(
        prefix: str,
    ) -> str:
        """
        Generate a unique entity ID.

        Example:
            FARMER_A1B2C3D4
        """

        import uuid

        token = (
            uuid.uuid4()
            .hex
            .upper()[:12]
        )

        return f"{prefix}_{token}"


# ============================================================
# SINGLETON ACCESSOR
# ============================================================

_default_storage_manager: Optional[
    StorageManager
] = None


def get_storage_manager() -> StorageManager:
    """
    Return the default application storage manager.
    """

    global _default_storage_manager

    if _default_storage_manager is None:

        _default_storage_manager = (
            StorageManager()
        )

    return _default_storage_manager


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    storage = get_storage_manager()

    print("=" * 60)
    print("RAYA PHASE 4A — STORAGE MANAGER TEST")
    print("=" * 60)

    print(
        "Data directory:",
        storage.data_directory,
    )

    for entity in [
        "farmers",
        "farms",
        "fields",
    ]:

        records = storage.read_all(
            entity
        )

        print(
            f"{entity}: "
            f"{len(records)} records"
        )

    print("\nStorage initialization: PASS")