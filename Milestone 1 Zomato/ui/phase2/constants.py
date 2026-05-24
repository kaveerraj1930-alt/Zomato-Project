"""Shared UI constants."""

from models import BudgetBand

BUDGET_LABELS: dict[str, BudgetBand] = {
    "Low": BudgetBand.LOW,
    "Medium": BudgetBand.MEDIUM,
    "High": BudgetBand.HIGH,
}
