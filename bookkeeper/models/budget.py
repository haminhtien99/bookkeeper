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
    pk:int = 0
    day:float
    week:float
    month:float
