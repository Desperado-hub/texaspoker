"""Storage and caching scaffolding aligned with the README description."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CacheLayer:
    sessions: Dict[str, str] = field(default_factory=dict)
    table_snapshots: Dict[str, dict] = field(default_factory=dict)
    timers: Dict[str, float] = field(default_factory=dict)

    def set_session(self, token: str, player_id: str) -> None:
        self.sessions[token] = player_id

    def cache_table(self, table_id: str, snapshot: dict) -> None:
        self.table_snapshots[table_id] = snapshot

    def get_table(self, table_id: str) -> Optional[dict]:
        return self.table_snapshots.get(table_id)


@dataclass
class RelationalDatabase:
    players: Dict[str, dict] = field(default_factory=dict)
    events: Dict[str, list] = field(default_factory=dict)
    economy_logs: Dict[str, list] = field(default_factory=dict)

    def save_player(self, player_id: str, profile: dict) -> None:
        self.players[player_id] = profile

    def append_event(self, table_id: str, event: dict) -> None:
        self.events.setdefault(table_id, []).append(event)

    def log_economy(self, player_id: str, record: dict) -> None:
        self.economy_logs.setdefault(player_id, []).append(record)


@dataclass
class ObjectStorage:
    replays: Dict[str, bytes] = field(default_factory=dict)
    reports: Dict[str, bytes] = field(default_factory=dict)

    def upload_replay(self, key: str, data: bytes) -> None:
        self.replays[key] = data

    def upload_report(self, key: str, data: bytes) -> None:
        self.reports[key] = data


class StorageFacade:
    """Facade to coordinate cache, database, and object storage."""

    def __init__(self) -> None:
        self.cache = CacheLayer()
        self.db = RelationalDatabase()
        self.obj = ObjectStorage()

    def archive_hand(self, table_id: str, replay_bytes: bytes) -> None:
        self.obj.upload_replay(f"{table_id}.replay", replay_bytes)
        self.cache.cache_table(table_id, {})

    def save_snapshot_and_event(self, table_id: str, snapshot: dict, event: dict) -> None:
        self.cache.cache_table(table_id, snapshot)
        self.db.append_event(table_id, event)

    def backup_player_profile(self, player_id: str, profile: dict, report: Optional[bytes] = None) -> None:
        self.db.save_player(player_id, profile)
        if report is not None:
            self.obj.upload_report(f"{player_id}.report", report)
