# core/utils.py
from io import BytesIO
import matplotlib.pyplot as plt

def generate_table_image(df, title=None):
    from io import BytesIO
    import matplotlib.pyplot as plt

    fig_height = len(df) * 0.43 + 0.6  # even tighter vertical space
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.axis('off')

    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.93)  # title closer to table

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

    plt.subplots_adjust(top=1, bottom=0.01)  # tighter layout

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300, pad_inches=0.01)  # minimal padding
    buf.seek(0)
    return buf
