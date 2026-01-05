"""Object storage adapters for generated assets."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class ObjectStorage(ABC):
    @abstractmethod
    def put_object(self, key: str, data: bytes, content_type: str) -> str:
        """Persist an object and return its URI."""

    @abstractmethod
    def put_json(self, key: str, payload: dict) -> str:
        """Persist JSON payloads and return their URI."""

    @abstractmethod
    def get_local_path(self, uri: str) -> Optional[Path]:
        """Return a local filesystem path when available."""


class LocalStorage(ObjectStorage):
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def put_object(self, key: str, data: bytes, content_type: str) -> str:
        destination = self.base_path / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return destination.resolve().as_uri()

    def put_json(self, key: str, payload: dict) -> str:
        destination = self.base_path / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2))
        return destination.resolve().as_uri()

    def get_local_path(self, uri: str) -> Optional[Path]:
        path = Path(uri.replace("file://", ""))
        return path if path.exists() else None


class S3Storage(ObjectStorage):
    def __init__(self, bucket: str, client) -> None:
        self.bucket = bucket
        self.client = client

    def put_object(self, key: str, data: bytes, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self.bucket}/{key}"

    def put_json(self, key: str, payload: dict) -> str:
        return self.put_object(key, json.dumps(payload).encode("utf-8"), "application/json")

    def get_local_path(self, uri: str) -> Optional[Path]:
        return None


class GCSStorage(ObjectStorage):
    def __init__(self, bucket: str, client) -> None:
        self.bucket = bucket
        self.client = client

    def put_object(self, key: str, data: bytes, content_type: str) -> str:
        bucket = self.client.bucket(self.bucket)
        blob = bucket.blob(key)
        blob.upload_from_string(data, content_type=content_type)
        return f"gs://{self.bucket}/{key}"

    def put_json(self, key: str, payload: dict) -> str:
        return self.put_object(key, json.dumps(payload).encode("utf-8"), "application/json")

    def get_local_path(self, uri: str) -> Optional[Path]:
        return None
