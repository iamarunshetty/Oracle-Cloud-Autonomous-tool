"""
Segregation of Duties (SOD) conflict checker.

Rules are loaded from ``sod_rules.json`` in the project root.
Each rule declares two mutually exclusive roles; the check is bidirectional
and case-insensitive.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.utils.logger import get_logger

logger = get_logger("oracle_fusion_tool.services.sod")

_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_RULES_FILE = _ROOT / "sod_rules.json"


@dataclass
class SodConflict:
    """Represents a single SOD conflict detected during a role assignment check."""

    proposed_role: str
    conflicting_role: str
    description: str


class SodService:
    """
    Checks a proposed role assignment against a user's existing roles for SOD
    conflicts.

    Parameters
    ----------
    rules_file:
        Path to a JSON file containing SOD rules.  Defaults to
        ``sod_rules.json`` in the project root.  If the file is absent the
        service operates with an empty ruleset (no conflicts raised).
    """

    def __init__(self, rules_file: str | None = None) -> None:
        path = Path(rules_file) if rules_file else _DEFAULT_RULES_FILE
        self._rules: list[dict[str, str]] = self._load_rules(path)
        logger.debug("SodService loaded %d rule(s) from %s.", len(self._rules), path)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def check_conflicts(
        self, proposed_role: str, existing_roles: list[str]
    ) -> list[SodConflict]:
        """
        Return every SOD conflict between *proposed_role* and *existing_roles*.

        The check is:
        - **Bidirectional** – if rule says A ↔ B, then proposing B when A is
          held (or vice-versa) both trigger a conflict.
        - **Case-insensitive** – role names are compared upper-cased.
        """
        proposed_upper = proposed_role.upper()
        existing_upper = {r.upper() for r in existing_roles}

        conflicts: list[SodConflict] = []
        for rule in self._rules:
            a = rule.get("role_a", "").upper()
            b = rule.get("role_b", "").upper()
            if not a or not b:
                continue
            desc = rule.get("description", "")

            if proposed_upper == a and b in existing_upper:
                conflicts.append(SodConflict(proposed_role, rule["role_b"], desc))
            elif proposed_upper == b and a in existing_upper:
                conflicts.append(SodConflict(proposed_role, rule["role_a"], desc))

        return conflicts

    @property
    def rule_count(self) -> int:
        """Number of SOD rules currently loaded."""
        return len(self._rules)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_rules(path: Path) -> list[dict[str, str]]:
        if not path.exists():
            logger.warning("SOD rules file not found at %s – no rules loaded.", path)
            return []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data: dict[str, Any] = json.load(fh)
            rules = data.get("rules", [])
            if not isinstance(rules, list):
                logger.warning("Invalid SOD rules format in %s.", path)
                return []
            logger.info("Loaded %d SOD rule(s) from %s.", len(rules), path)
            return rules
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load SOD rules from %s: %s", path, exc)
            return []
