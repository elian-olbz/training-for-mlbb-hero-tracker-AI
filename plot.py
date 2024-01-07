import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import pandas as pd
from PIL import Image

# Load your custom data
data_url = "loc.csv"
custom_data = pd.read_csv(data_url)

# Extract unique frames and classes
frames = custom_data['Frame'].unique()[::15]
classes = custom_data['Class'].unique()

# Make figure
fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}

# Add the background image to the layout
fig_dict["layout"]["images"] = [dict(
    source=Image.open("map.png"),
    x=0,
    y=0,
    xref="paper",
    yref="paper",
    xanchor="left",
    yanchor="bottom",
    sizex=1,
    sizey=1,
    sizing= "stretch",
    opacity=1,
    layer="below"
)]


# Fill in most of the layout
fig_dict["layout"]["xaxis"] = {"range": [0, 720], "title": "X", "showgrid": False}
fig_dict["layout"]["yaxis"] = {"range": [0, 720], "title": "Y", "showgrid": False}
fig_dict["layout"]["hovermode"] = "closest"
fig_dict["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 500, "redraw": True},
                                "fromcurrent": True, "transition": {"duration": 300,
                                                                    "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }
]

sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "Frame:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 300, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": []
}

# Make data
for class_name in classes:
    data_by_class = custom_data[custom_data["Class"] == class_name]
    data_dict = {
        "x": [],
        "y": [],
        "mode": "markers",
        "text": [],
        "marker": {"size": 10},
        "name": class_name
    }
    fig_dict["data"].append(data_dict)

# Make frames
for frame in frames:
    frame_data = custom_data[custom_data["Frame"] == frame]
    frame_dict = {"data": [], "name": str(frame)}
    for class_name in classes:
        data_by_class = frame_data[frame_data["Class"] == class_name]
        data_dict = {
            "x": data_by_class["X"],
            "y": data_by_class["Y"],
            "mode": "markers",
            "text": data_by_class["Class"],
            "marker": {"size": 40, 
                       "line": {"width": 3, "color":'rgba(255, 255, 255, 0.75)'}},
            "name": class_name
        }
        frame_dict["data"].append(data_dict)
    
    fig_dict["frames"].append(frame_dict)
    slider_step = {"args": [
        [frame],
        {"frame": {"duration": 300, "redraw": True},
         "mode": "immediate",
         "transition": {"duration": 300}}
    ],
        "label": str(frame),
        "method": "animate"}
    sliders_dict["steps"].append(slider_step)

fig_dict["layout"]["sliders"] = [sliders_dict]

fig = go.Figure(fig_dict)
#pio.write_image(fig, 'map.png')

# Create the Plotly HTML representation
plotly_html = fig.to_html()


# PyQt application
class PlotlyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotly Visualization in PyQt")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.webview = QWebEngineView()
        self.webview.setHtml(plotly_html)
        layout.addWidget(self.webview)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

# Create a PyQt application instance
app = QApplication(sys.argv)
window = PlotlyApp()
window.show()

# Run the event loop
sys.exit(app.exec())
