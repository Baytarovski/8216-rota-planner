# core/utils.py
from io import BytesIO
import matplotlib.pyplot as plt

def generate_table_image(df, title=None):

    fig_height = len(df) * 0.6 + 1.0  # increase visual height for table
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.axis('off')

    if title:
        fig.text(0.5, 0.985, title, fontsize=14, fontweight='bold', ha='center', va='bottom')  # place title very close

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

    plt.subplots_adjust(top=1.0, bottom=0.02)  # almost no space above/below

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300, pad_inches=0)
    buf.seek(0)
    return buf


