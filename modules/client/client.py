"""Client-side scaffolding inspired by the module README.

The code models a basic client that can:
- Fetch lobby and account data via HTTP calls.
- Maintain a realtime channel for table interactions.
- Handle reconnect by requesting a snapshot then applying pending deltas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

Action = Literal["fold", "call", "raise", "all_in"]


@dataclass
class TableSnapshot:
    table_id: str
    seats: int
    chips: Dict[str, int]
    community_cards: List[str] = field(default_factory=list)
    pot: int = 0


@dataclass
class DeltaEvent:
    kind: str
    payload: Dict[str, object]


class ClientApp:
    """Small in-memory model of the responsibilities listed in the README."""

    def __init__(self) -> None:
        self.snapshot: Optional[TableSnapshot] = None
        self.pending_events: List[DeltaEvent] = []
        self.realtime_connected = False

    def fetch_basic_data(self, account_id: str) -> Dict[str, object]:
        """Simulate HTTP retrieval of account and lobby data."""
        return {
            "account_id": account_id,
            "balance": 10_000,
            "lobbies": [
                {"name": "6-max", "min_buy_in": 50, "big_blind": 2},
                {"name": "9-max", "min_buy_in": 100, "big_blind": 5},
            ],
        }

    def connect_realtime(self) -> None:
        """Establish the realtime channel (WebSocket/RTC)."""
        self.realtime_connected = True

    def send_action(self, action: Action, amount: int | None = None) -> DeltaEvent:
        """Send a player action over the realtime link."""
        if not self.realtime_connected:
            raise RuntimeError("Realtime channel not connected")
        payload: Dict[str, object] = {"action": action}
        if action in {"raise", "all_in"}:
            payload["amount"] = amount or 0
        event = DeltaEvent(kind="player_action", payload=payload)
        self.pending_events.append(event)
        return event

    def receive_table_delta(self, event: DeltaEvent) -> None:
        """Consume server-pushed table delta and apply to snapshot."""
        if self.snapshot is None:
            # store until snapshot is available
            self.pending_events.append(event)
            return
        if event.kind == "chips_update" and self.snapshot:
            for player, change in event.payload.get("deltas", {}).items():
                self.snapshot.chips[player] = self.snapshot.chips.get(player, 0) + int(change)
        elif event.kind == "community_card" and self.snapshot:
            card = event.payload.get("card")
            if isinstance(card, str):
                self.snapshot.community_cards.append(card)

    def reconnect_and_resync(self, snapshot: TableSnapshot) -> None:
        """Handle reconnect: set snapshot then replay cached deltas."""
        self.snapshot = snapshot
        cached = list(self.pending_events)
        self.pending_events.clear()
        for event in cached:
            self.receive_table_delta(event)
