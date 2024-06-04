import sys
import threading
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import lightningchart as lc

window_width = 1600
window_height = 900


class App(QMainWindow):
    def __init__(self, url):
        super(App, self).__init__()
        self.setWindowTitle("Medical Dashboard")
        self.setGeometry(100, 100, window_width, window_height)

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.web_view.setUrl(QUrl(url))


with open("license_key.txt", "r") as file:  # License key is stored in 'license_key.txt'
    key = file.read()

lc.set_license(key)

dashboard_columns_amount = 1
dashboard_rows_amount = 2

if __name__ == "__main__":
    # Initialize dashboard
    dashboard = lc.Dashboard(columns=dashboard_columns_amount, rows=dashboard_rows_amount, theme=lc.Themes.Dark)
    nibp_file_path = 'data/nibp.csv'  # Put CSV data inside
    ecg_file_path = 'data/ecg.csv'  # 'data' folder
    df_nibp = pd.read_csv(nibp_file_path)  # Read CSV files  to DataFrames using pandas
    df_nibp = df_nibp[0:40000]  # Cut the record to 40 seconds
    df_ecg = pd.read_csv(ecg_file_path)
    df_ecg = df_ecg[0:40000]
    y_ecg = df_ecg['ECG']  # Extract Ys from DataFrame
    y_nibp = df_nibp['NIBP']
    x = df_ecg['time']  # Extract Xs from DataFrame

    # Create arrays from Xs and Ys
    xs = []
    ys_ecg = []
    ys_nibp = []
    for i in range(len(x)):
        xs.append(x[i])
        ys_ecg.append(y_ecg[i])
        ys_nibp.append(y_nibp[i])

    # Add ChartXY to dashboard
    chart_ecg = dashboard.ChartXY(column_index=0, row_index=0, title='Cardiogram')

    series_ecg = chart_ecg.add_line_series(
        data_pattern='ProgressiveX')  # This is needed for progressive adding of data, for the graph to be 'dynamic'
    series_ecg.set_line_color(lc.Color(255, 0, 0))  # Set the color for ECG (red)

    x_axis_ecg = chart_ecg.get_default_x_axis()  # Get the axes
    y_axis_ecg = chart_ecg.get_default_y_axis()  # of the chart
    x_axis_ecg.set_scroll_strategy(strategy='progressive')  # Set the x_axis_ecg to progressive scroll strategy
    x_axis_ecg.set_interval(start=-3, end=3, stop_axis_after=False)  # Set borders for the graph
    y_axis_ecg.set_default_interval(start=-1.6, end=1)
    y_axis_ecg.set_title('mV')  # Set titles for axes
    x_axis_ecg.set_title('ms')

    chart_nibp = dashboard.ChartXY(column_index=0, row_index=1, title='Blood Pressure')

    series_nibp = chart_nibp.add_line_series(data_pattern='ProgressiveX')
    series_nibp.set_line_color(lc.Color(0, 255, 0))

    x_axis_nibp = chart_nibp.get_default_x_axis()
    y_axis_nibp = chart_nibp.get_default_y_axis()
    x_axis_nibp.set_scroll_strategy(strategy='progressive')
    x_axis_nibp.set_interval(start=-3, end=3, stop_axis_after=False)
    y_axis_nibp.set_default_interval(start=70, end=130)
    y_axis_nibp.set_title('mmHg')
    x_axis_nibp.set_title('ms')

    # Set max sample count.
    # It is basically the amount of memory used by the chart before dropping older points
    series_ecg.set_max_sample_count(10000)
    series_nibp.set_max_sample_count(10000)


    # Function for gradually adding data
    def generate_data():
        for point in range(0, len(x), 10):
            series_ecg.add(xs[point:point + 10], ys_ecg[point:point + 10])
            series_nibp.add(xs[point:point + 10], ys_nibp[point:point + 10])


    # Initialize the real-time dashboard server and get the URL
    url = dashboard.open_live_server()
    # Create a thread which will generate and append data to the dashboard
    thread = threading.Thread(target=generate_data, args=()).start()

    # Create PyQt app
    app = QApplication(sys.argv)
    dashboard_app = App(url)
    dashboard_app.show()
    sys.exit(app.exec())
