import io
from matplotlib.backends.backend_agg import FigureCanvasAgg

def figure_to_bytes(figure):
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(figure)
    canvas.print_png(buf)
    return buf.getvalue()
