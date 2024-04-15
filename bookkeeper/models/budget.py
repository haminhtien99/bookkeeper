"""
Модель Бюджет
"""
from dataclasses import dataclass


@dataclass
class Budget:
    """
    Бюджет
    pk- id в базе данных
    day - бюджет на день
    week - бюджет на неделю
    month - бюджет на месяц
    """
    day: float = 0.
    week: float = 0.
    month: float = 0.
    pk: int = 0
