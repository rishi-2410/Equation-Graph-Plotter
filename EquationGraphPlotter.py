import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QGraphicsItem, QScrollArea, QHBoxLayout,
    QMenuBar, QMenu, QAction,QCheckBox
)
import sympy as sp
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.colors import to_hex
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QProxyStyle

class MovableGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super(MovableGraphicsView, self).__init__(scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setInteractive(True)
        self.prev_pos = None
        self.setStyleSheet("""
            border: none;
            background:#F0F0F0;
        """)

    def wheelEvent(self, event):
        factor = 1.2  # Zoom factor

        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(factor, factor)
        else:
            # Zoom out
            self.scale(1.0 / factor, 1.0 / factor)

    def mouseMoveEvent(self, event):
        if self.prev_pos:
            delta = event.pos() - self.prev_pos
            self.translate(delta.x(), delta.y())
        self.prev_pos = event.pos()
        super(MovableGraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.prev_pos = None
        super(MovableGraphicsView, self).mouseReleaseEvent(event)

class GraphPlotterApp(QMainWindow):
    def __init__(self):
        super(GraphPlotterApp, self).__init__()

        self.setWindowTitle("Graph Plotter")
        self.setGeometry(100, 100, 1200, 600)

        self.setStyleSheet("""




            """)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Overall layout is now a QHBoxLayout
        self.layout = QHBoxLayout(self.central_widget)

        # Left side: Graph view
        self.scene = QGraphicsScene(self)
        self.graphics_view = MovableGraphicsView(self.scene)
        self.layout.addWidget(self.graphics_view, 2)  # Set stretch factor for enlargement

        # Right side: Line edits and buttons
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop)  # Align to the top

        # Add labels and line edits for x and y axis limits
        limit_layout = QHBoxLayout()

        x_label = QLabel("x:")
        x_label.setStyleSheet("""

color:black;
font-size:17px;

            """)
        self.x_limit_entry = QLineEdit()
        self.x_limit_entry.setPlaceholderText("Enter x-axis limit")
        self.x_limit_entry.setStyleSheet("""

padding:5px;
border-radius:4px;
color:black;
font-size:13px;
border-bottom:1px solid blue;

            """)

        y_label = QLabel("y:")
        y_label.setStyleSheet("""

color:black;
font-size:17px;

            """)
        self.y_limit_entry = QLineEdit()
        self.y_limit_entry.setPlaceholderText("Enter y-axis limit")
        self.y_limit_entry.setStyleSheet("""

padding:5px;
border-radius:4px;
color:black;
font-size:13px;
border-bottom:1px solid blue;

            """)

        limit_layout.addWidget(x_label)
        limit_layout.addWidget(self.x_limit_entry)
        limit_layout.addWidget(y_label)
        limit_layout.addWidget(self.y_limit_entry)

        self.right_layout.addLayout(limit_layout)  # Add the QHBoxLayout to the main layout

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""


border-radius:3px;

            """)
        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_content)

        self.line_number = 1  # Initialize line number
        self.equation_entries = []  # List to store equation entries
        self.equation_labels = []  # List to store equation labels
        self.delete_buttons = []  # List to store delete buttons
        self.line_colors = []  # List to store line colors

        # Add the first QLineEdit
        self.add_equation()

        # Set the layout of the scroll area content
        self.scroll_area_content.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_content)
        self.right_layout.addWidget(self.scroll_area)  # Add scroll area to the right layout

        # Add "Add Equation" button and "Delete All" button side by side
        buttons_layout = QHBoxLayout()

        self.add_equation_button = QPushButton("")
        self.add_equation_button.clicked.connect(self.add_equation)
        buttons_layout.addWidget(self.add_equation_button)
        add_equation_button_font = QFont()
        add_equation_button_font.setPointSize(10)
        add_equation_button_font.setFamily("Arial Rounded MT")
        self.add_equation_button.setFont(add_equation_button_font)
        self.add_equation_button.setStyleSheet("""

padding:3px;
border-radius:8px;
border:2px solid lightgrey;

            """)
        add_equation_icon = QIcon("C:\\Users\\rishi\\OneDrive\\Desktop\\Graph\\Icons_for_plotgraph\\add.png")  # Replace with the actual path to your icon file
        self.add_equation_button.setIcon(add_equation_icon)
        self.add_equation_button.setIconSize(QSize(32,32))

        # Add "Plot Graph" button
        self.plot_button = QPushButton("")
        self.plot_button.clicked.connect(self.plot_graph)
        buttons_layout.addWidget(self.plot_button)  # Align to the top
        plot_button_font = QFont()
        plot_button_font.setPointSize(10)
        plot_button_font.setFamily("Arial Rounded MT")
        self.plot_button.setFont(plot_button_font)
        self.plot_button.setStyleSheet("""

padding:3px;
border-radius:8px;
border:2px solid lightgrey;

            """)
        plot_icon = QIcon("C:\\Users\\rishi\\OneDrive\\Desktop\\Graph\\Icons_for_plotgraph\\plotgraph.png")  # Replace with the actual path to your icon file
        self.plot_button.setIcon(plot_icon)
        self.plot_button.setIconSize(QSize(32,32))

        self.delete_all_button = QPushButton("")#Delete all button
        self.delete_all_button.clicked.connect(self.delete_all_equations)
        buttons_layout.addWidget(self.delete_all_button)
        delete_all_button_font = QFont()
        delete_all_button_font.setPointSize(10)
        delete_all_button_font.setFamily("Arial Rounded MT")
        self.delete_all_button.setFont(delete_all_button_font)
        self.delete_all_button.setStyleSheet("""

padding:3px;
border-radius:8px;
border:2px solid lightgrey;

            """)
        delete_all_icon = QIcon("C:\\Users\\rishi\\OneDrive\\Desktop\\Graph\\Icons_for_plotgraph\\deleteall.png")  # Replace with the actual path to your icon file
        self.delete_all_button.setIcon(delete_all_icon)
        self.delete_all_button.setIconSize(QSize(32,32))

        self.right_layout.addLayout(buttons_layout)

        self.layout.addLayout(self.right_layout, 1)  # Set stretch factor for enlargement

        self.equations = []

        # Add menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

    #     menu_bar.setStyleSheet("""
    #     background-color: #353535;
    #     padding: 4px;
    #     color: white;
    #     font-size:15px;
    #     border-radius:5px;
    #     margin:3px;
    # """)

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.delete_all_equations_for_new)

        open_action = QAction("Open", self)

        save_action = QAction("Save", self)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Edit")

        # Line Type submenu
        line_type_submenu = QMenu("Line Type", self)

        solid_line_action = QAction("Solid Line", self)
        solid_line_action.triggered.connect(lambda: self.set_line_type('solid'))
        line_type_submenu.addAction(solid_line_action)

        dashed_line_action = QAction("Dash Dot Line", self)
        dashed_line_action.triggered.connect(lambda: self.set_line_type('dashed'))
        line_type_submenu.addAction(dashed_line_action)

        dotted_line_action = QAction("Dashed Line", self)
        dotted_line_action.triggered.connect(lambda: self.set_line_type('dotted'))
        line_type_submenu.addAction(dotted_line_action)

        # Add Line Type submenu to Edit menu
        edit_menu.addMenu(line_type_submenu)

    def set_line_type(self, line_type):
        try:
            self.scene.clear()
            x = np.linspace(-10, 10, 400)

            self.equations = [entry.text().strip() for entry in self.equation_entries if entry.text().strip()]

            # Get the size of the graphics view
            view_size = self.graphics_view.size()

            fig, ax = plt.subplots(figsize=(view_size.width() / 80, view_size.height() / 80))  # Adjust the scaling factor as needed

            for equation_str, line_color in zip(self.equations, self.line_colors):
                try:
                    # Parse the equation using sympy
                    equation = sp.parse_expr(equation_str)
                    # Convert the equation to a function
                    y_func = sp.lambdify('x', equation, 'numpy')
                    # Evaluate the function
                    y = y_func(x)

                    # Set line style based on the chosen line type
                    linestyle = '-' if line_type == 'solid' else '--' if line_type == 'dotted' else '-.'
                    ax.plot(x, y, label=equation_str, color=line_color, linestyle=linestyle)
                except Exception as e:
                    # Handle equation parsing or evaluation errors
                    print(f"Error processing equation '{equation_str}': {str(e)}")

            ax.set_title("Graph of Equations")
            ax.grid(True)
            ax.legend()

            # Set limits for x and y axes based on user input
            x_limit = float(self.x_limit_entry.text()) if self.x_limit_entry.text() else 10.0
            y_limit = float(self.y_limit_entry.text()) if self.y_limit_entry.text() else 10.0

            ax.set_xlim(-x_limit, x_limit)
            ax.set_ylim(-y_limit, y_limit)

            # Set the aspect ratio to 'auto'
            ax.set_aspect('auto')
            # Set the origin of the graph at the center
            ax.spines['left'].set_position('center')
            ax.spines['bottom'].set_position('center')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')

            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
            canvas.updateGeometry()
            canvas.setStyleSheet("""

background-color:#0b0b0b;
border-radius:5px;
border:0px;

""")

            proxy = QGraphicsProxyWidget()
            proxy.setWidget(canvas)
            proxy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
            proxy.setFlag(QGraphicsItem.ItemIsMovable)
            self.scene.addItem(proxy)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.show_error_dialog(error_message)

    def add_equation(self):
        equation_entry = QLineEdit()

        # Set font for the QLineEdit
        font = QFont()
        font.setPointSize(12)  # Set the desired font size
        font.setFamily("Cosmic Sans")
        equation_entry.setFont(font)

        # Set alignment to the top
        equation_entry.setAlignment(Qt.AlignTop)

        # Generate a random color for the border
        line_color = self.generate_random_color()

        # Apply style sheet with line color for padding and rounded borders
        equation_entry.setStyleSheet(f"QLineEdit {{ padding: 5px; border: 3px solid {line_color}; border-radius: 8px; background:white; font-size:18px; color:black; }}")
        

        delete_button = QPushButton("")
        delete_button.clicked.connect(lambda _, entry=equation_entry, button=delete_button: self.remove_equation(entry, button))
        button_font = QFont()
        button_font.setPointSize(10)
        button_font.setFamily("Arial Rounded MT")
        delete_button.setFont(button_font)
        delete_button.setStyleSheet("""

padding:0px;
border-radius:8px;

            """)
        delete_icon = QIcon("C:\\Users\\rishi\\OneDrive\\Desktop\\Graph\\Icons_for_plotgraph\\delete.png")  # Replace with the actual path to your icon file
        delete_button.setIcon(delete_icon)
        delete_button.setIconSize(QSize(20,20))

        label = QLabel(f"{self.line_number}.")  # Create label with line number
        label.setAlignment(Qt.AlignTop)
        label_font = QFont()
        label_font.setPointSize(10)
        label_font.setFamily("Arial Rounded MT")
        label.setFont(label_font)
        label.setStyleSheet("""

color:black;

            """)

        # Set alignment of the layout to the top
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(label)
        layout.addWidget(equation_entry)
        layout.addWidget(delete_button)

        self.scroll_area_layout.addLayout(layout)  # Add line edit, label, and delete button to the layout

        # Add the equation entry, label, delete button, and line color to their respective lists
        self.equation_entries.append(equation_entry)
        self.equation_labels.append(label)
        self.delete_buttons.append(delete_button)
        self.line_colors.append(line_color)

        # Increment line number for the next equation
        self.line_number += 1

    def generate_random_color(self):
        # Generate a random RGB color
        rgb_color = [random.random() for _ in range(3)]
        # Convert to hex format for styling
        hex_color = to_hex(rgb_color)
        return hex_color

    def remove_equation(self, entry, button):
        # Find the index of the entry in the list
        index = self.equation_entries.index(entry)

        # Remove the corresponding line edit, label, delete button, and line color
        entry.deleteLater()
        self.equation_labels[index].deleteLater()
        button.deleteLater()
        del self.equation_entries[index]
        del self.equation_labels[index]
        del self.delete_buttons[index]
        del self.line_colors[index]

        # Update the line numbers for the remaining entries
        for i, label in enumerate(self.equation_labels):
            label.setText(f"{i + 1}.")

        # Replot the graph without the deleted equation
        self.plot_graph()

    def delete_all_equations_for_new(self):

        # Delete all line edits, labels, delete buttons, and clear the lists
        for entry, label, button in zip(self.equation_entries, self.equation_labels, self.delete_buttons):
            entry.deleteLater()
            label.deleteLater()
            button.deleteLater()

        self.equation_entries.clear()
        self.equation_labels.clear()
        self.delete_buttons.clear()
        self.line_colors.clear()

        # Reset line number to 1
        self.line_number = 1

        # Clear the scroll area layout
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Replot the graph (this will result in an empty graph)
        self.plot_graph()

        # Clear the graph from the scene
        self.scene.clear()

    def delete_all_equations(self):
        # Delete all line edits, labels, delete buttons, and clear the lists
        for entry, label, button in zip(self.equation_entries, self.equation_labels, self.delete_buttons):
            entry.deleteLater()
            label.deleteLater()
            button.deleteLater()

        self.equation_entries.clear()
        self.equation_labels.clear()
        self.delete_buttons.clear()
        self.line_colors.clear()

        # Reset line number to 1
        self.line_number = 1

        # Clear the scroll area layout
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Replot the graph
        self.plot_graph()

    def plot_graph(self):
        try:
            plt.style.use('default')  # Set normal theme for Matplotlib
            self.scene.clear()
            x = np.linspace(-10, 10, 400)

            self.equations = [entry.text().strip() for entry in self.equation_entries if entry.text().strip()]

            # Get the size of the graphics view
            view_size = self.graphics_view.size()

            fig, ax = plt.subplots(figsize=(view_size.width() / 80, view_size.height() / 80))  # Adjust the scaling factor as needed

            for equation_str, line_color in zip(self.equations, self.line_colors):
                try:
                    # Parse the equation using sympy
                    equation = sp.parse_expr(equation_str)
                    # Convert the equation to a function
                    y_func = sp.lambdify('x', equation, 'numpy')
                    # Evaluate the function
                    y = y_func(x)
                    ax.plot(x, y, label=equation_str, color=line_color)
                except Exception as e:
                    # Handle equation parsing or evaluation errors
                    print(f"Error processing equation '{equation_str}': {str(e)}")

            ax.set_title("Graph of Equations")
            ax.grid(True)
            ax.legend()

            # Set limits for x and y axes based on user input
            x_limit = float(self.x_limit_entry.text()) if self.x_limit_entry.text() else 10.0
            y_limit = float(self.y_limit_entry.text()) if self.y_limit_entry.text() else 10.0

            ax.set_xlim(-x_limit, x_limit)
            ax.set_ylim(-y_limit, y_limit)

            # Set the aspect ratio to 'auto'
            ax.set_aspect('auto')
            # Set the origin of the graph at the center
            ax.spines['left'].set_position('center')
            ax.spines['bottom'].set_position('center')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')

            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
            canvas.updateGeometry()

            proxy = QGraphicsProxyWidget()
            proxy.setWidget(canvas)
            proxy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy
            proxy.setFlag(QGraphicsItem.ItemIsMovable)
            self.scene.addItem(proxy)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.show_error_dialog(error_message)

    def show_error_dialog(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

def main():
    app = QApplication(sys.argv)
    window = GraphPlotterApp()
    window.showMaximized()  # Set the main window to be maximized
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
