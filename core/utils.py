# core/utils.py
from io import BytesIO
import matplotlib.pyplot as plt

def generate_table_image(df, title=None):

    fig_height = len(df) * 0.6 + 1.0  # adjust height for better fit
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.axis('off')

    if title:
        # Add title with minimal spacing
        fig.text(0.5, 1.01, title, fontsize=14, fontweight='bold', ha='center', va='bottom')

    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        rowLabels=df.index,
        loc='center',
        cellLoc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.2)

    fig.subplots_adjust(top=0.95, bottom=0.05)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300, pad_inches=0)
    buf.seek(0)
    return buf





