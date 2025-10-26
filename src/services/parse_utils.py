from datetime import timedelta
import re

def parse_time(time_str: str) -> timedelta:
    """Converte string de tempo para timedelta"""
    if time_str.isdigit():  # Se for apenas números, assume segundos
        return timedelta(seconds=int(time_str))

    pattern = r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    match = re.match(pattern, time_str.lower())

    if not match or not any(match.groups()):
        raise ValueError(
            "Formato de tempo inválido. Use: Xh, Ym, Zs ou combinações "
            "(ex: 1h30m, 45s, 2h15m30s)"
        )

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)