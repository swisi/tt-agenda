"""
Konfigurierbare Farben für Aktivitätstypen
Separate Farben für Light- und Dark-Mode
"""

# Farbkonfiguration für Light-Mode (Pastellfarben)
LIGHT_MODE_COLORS = {
    'team': '#C4B5FD',         # Club Purple (soft)
    'prepractice': '#E5E7EB',  # Silver
    'individual': '#DDD6FE',   # Light Purple
    'group': '#CBD5E1'         # Cool Silver
}

# Farbkonfiguration für Dark-Mode (dunklere, aber immer noch erkennbare Farben)
DARK_MODE_COLORS = {
    'team': '#6D28D9',         # Club Purple
    'prepractice': '#64748B',  # Silver Slate
    'individual': '#7C3AED',   # Vivid Purple
    'group': '#334155'         # Near-Black
}

def get_activity_color(activity_type, theme='light'):
    """
    Gibt die Farbe für einen Aktivitätstyp zurück.
    
    Args:
        activity_type: Der Typ der Aktivität ('team', 'prepractice', 'individual', 'group')
        theme: 'light' oder 'dark'
    
    Returns:
        Hex-Farbcode als String
    """
    color_map = DARK_MODE_COLORS if theme == 'dark' else LIGHT_MODE_COLORS
    return color_map.get(activity_type, '#E8E8E8' if theme == 'light' else '#4A4A4A')

def get_all_colors(theme='light'):
    """
    Gibt alle Farben für ein Theme zurück.
    
    Args:
        theme: 'light' oder 'dark'
    
    Returns:
        Dictionary mit allen Aktivitätsfarben
    """
    return DARK_MODE_COLORS.copy() if theme == 'dark' else LIGHT_MODE_COLORS.copy()
