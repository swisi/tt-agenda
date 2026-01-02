"""
Konfigurierbare Farben für Aktivitätstypen
Separate Farben für Light- und Dark-Mode
"""

# Farbkonfiguration für Light-Mode (klar, aber nicht zu dominant)
LIGHT_MODE_COLORS = {
    'team': '#C6B8FF',         # Soft Indigo
    'prepractice': '#FFE0B3',  # Soft Amber
    'individual': '#BFE9D3',   # Soft Mint
    'group': '#B7D4FF'         # Soft Blue
}

# Farbkonfiguration für Dark-Mode (kräftiger, gut unterscheidbar)
DARK_MODE_COLORS = {
    'team': '#8B7BFF',         # Bright Indigo
    'prepractice': '#FB923C',  # Warm Amber
    'individual': '#34D399',   # Emerald
    'group': '#60A5FA'         # Bright Blue
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
