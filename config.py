import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'data.db')
DIST_DIR = os.path.join(BASE_DIR, 'dist')

# Pre-defined color palette for auto-assigning line colors
COLOR_PALETTE = [
    '#5470C6', '#91CC75', '#FAC858', '#EE6666',
    '#73C0DE', '#3BA272', '#FC8452', '#9A60B4',
    '#EA7CCC', '#48C9B0', '#F5A623', '#D0021B',
]
