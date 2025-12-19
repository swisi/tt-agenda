"""
Konfigurierbare Farben für Aktivitätstypen
Separate Farben für Light- und Dark-Mode
"""

# Farbkonfiguration für Light-Mode (Pastellfarben)
LIGHT_MODE_COLORS = {
    'team': '#A8D5E2',      # Pastell-Blau
    'prepractice': '#FFD6CC',  # Pastell-Rosa
    'individual': '#D4E4C5',   # Pastell-Grün
    'group': '#FFE5B4'        # Pastell-Gelb
}

# Farbkonfiguration für Dark-Mode (dunklere, aber immer noch erkennbare Farben)
DARK_MODE_COLORS = {
    'team': '#4A90A4',      # Dunkleres Blau
    'prepractice': '#C97A6B',  # Dunkleres Rosa
    'individual': '#7A9B6B',   # Dunkleres Grün
    'group': '#C9A86B'        # Dunkleres Gelb
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

