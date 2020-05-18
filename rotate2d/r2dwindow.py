import errno
import json

import zarr
import matplotlib
import matplotlib.axes
import numpy as np
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from scipy.ndimage import map_coordinates


class R2DWindow(QtWidgets.QMainWindow):

    XY_VIEW = "X/Y"
    THREE_PANEL_VIEW = "Three panel"

    def __init__(self):
        super(R2DWindow, self).__init__()
        self.fixed_img = None
        self.moving_img = None

        self.setGeometry(0, 0, 1024, 768)
        #
        # Menus
        #
        self.file_menu = QtWidgets.QMenu("&File", self)
        self.file_menu.addAction("Open Fixed", self.open_fixed)
        self.file_menu.addAction("Open Moving", self.open_moving)
        self.file_menu.addAction("Save", self.save)
        self.menuBar().addMenu(self.file_menu)
        #
        # Splitter
        #
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        top_layout = QtWidgets.QVBoxLayout()
        main_widget.setLayout(top_layout)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        top_layout.addWidget(splitter)
        #
        # Controls
        #
        left_widget = QtWidgets.QWidget()
        splitter.addWidget(left_widget)
        left_layout = QtWidgets.QVBoxLayout()
        left_widget.setLayout(left_layout)
        # offset
        group = QtWidgets.QGroupBox("Offset")
        left_layout.addWidget(group)
        group_layout = QtWidgets.QVBoxLayout()
        group.setLayout(group_layout)

        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("X:"))
        self.w_off_x = QtWidgets.QSpinBox()
        hlayout.addWidget(self.w_off_x)

        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("Y:"))
        self.w_off_y = QtWidgets.QSpinBox()
        hlayout.addWidget(self.w_off_y)
        # center
        group = QtWidgets.QGroupBox("Center")
        left_layout.addWidget(group)
        group_layout = QtWidgets.QVBoxLayout()
        group.setLayout(group_layout)

        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("X:"))
        self.w_center_x = QtWidgets.QSpinBox()
        hlayout.addWidget(self.w_center_x)

        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("Y:"))
        self.w_center_y = QtWidgets.QSpinBox()
        hlayout.addWidget(self.w_center_y)

        self.w_center_button = QtWidgets.QPushButton("Center")
        group_layout.addWidget(self.w_center_button)
        self.w_center_button.clicked.connect(self.on_center)
        # angle
        group = QtWidgets.QGroupBox("Rotation")
        left_layout.addWidget(group)
        group_layout = QtWidgets.QVBoxLayout()
        group.setLayout(group_layout)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("Angle in degrees:"))
        self.w_angle = QtWidgets.QDoubleSpinBox()
        hlayout.addWidget(self.w_angle)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        self.w_flip_lr = QtWidgets.QCheckBox("Flip left/right")
        hlayout.addWidget(self.w_flip_lr)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        self.w_flip_ud = QtWidgets.QCheckBox("Flip up/down")
        hlayout.addWidget(self.w_flip_ud)
        # z heights
        group = QtWidgets.QGroupBox("Z height and downsample")
        left_layout.addWidget(group)
        group_layout = QtWidgets.QVBoxLayout()
        group.setLayout(group_layout)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("Fixed:"))
        self.fixed_img_z = QtWidgets.QSpinBox()
        hlayout.addWidget(self.fixed_img_z)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("Moving:"))
        self.moving_img_z = QtWidgets.QSpinBox()
        hlayout.addWidget(self.moving_img_z)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("Downsample: "))
        self.w_downsample = QtWidgets.QSpinBox()
        hlayout.addWidget(self.w_downsample)
        self.w_downsample.setMinimum(1)
        self.w_downsample.setMaximum(32)
        self.w_downsample.setValue(1)
        hlayout = QtWidgets.QHBoxLayout()
        group_layout.addLayout(hlayout)
        hlayout.addWidget(QtWidgets.QLabel("View"))
        self.w_view_choice = QtWidgets.QComboBox()
        self.w_view_choice.addItems([self.XY_VIEW, self.THREE_PANEL_VIEW])
        self.w_view_choice.setCurrentIndex(1)
        self.w_view_choice.setEditable(False)
        hlayout.addWidget(self.w_view_choice)

        self.show_button = QtWidgets.QPushButton("Show")
        left_layout.addWidget(self.show_button)
        self.show_button.setDisabled(True)
        self.show_button.clicked.connect(self.on_show)

        left_layout.addStretch(1)
        #
        # Matplotlib canvas
        #
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        splitter.addWidget(self.canvas)
        self.addToolBar(NavigationToolbar(self.canvas, self))
        self.figure.add_subplot(1, 1, 1)
        self.canvas.draw()

    def open_fixed(self):
        try:
            self.fixed_img = self.open_any("Fixed")
        except UserWarning:
            return
        except FileNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "File not found", e.strerror)
            return
        self.fixed_img_z.setMinimum(0)
        self.fixed_img_z.setMaximum(self.fixed_img.shape[2])
        self.w_center_x.setMaximum(self.fixed_img.shape[0])
        self.w_center_y.setMaximum(self.fixed_img.shape[1])
        self.update_ui()

    def open_any(self, name):
        # Grrr... native directory dialogs are BROKEN in Gnome, it seems.
        # So use the generic built-in
        #
        filename = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "%s ZARR file name" % name,
            ".",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontUseNativeDialog
        )
        if len(filename) == 0:
            raise UserWarning("No filename entered")
        try:
            return zarr.open(filename, mode="r")
        except:
            raise FileNotFoundError(errno.ENOENT,
                                    "Unable to open %s as ZARR file" % filename,
                                    filename)

    def open_moving(self):
        try:
            self.moving_img = self.open_any("Moving")
        except UserWarning:
            return
        except FileNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "File not found", e.strerror())
            return
        self.w_off_x.setMinimum(-self.moving_img.shape[0])
        self.w_off_x.setMaximum(self.moving_img.shape[0])
        self.w_off_y.setMinimum(-self.moving_img.shape[1])
        self.w_off_y.setMaximum(self.moving_img.shape[1])
        self.moving_img_z.setMinimum(0)
        self.moving_img_z.setMaximum(self.moving_img.shape[2])
        self.update_ui()

    def save(self):
        filename, filter_type = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save parameters",
            filter="JSON file (*.json)",
            options=QtWidgets.QFileDialog.DontUseNativeDialogs
        )
        d = dict(
            x_offset=self.w_off_x.value(),
            y_offset=self.w_off_y.value(),
            x_center=self.w_center_x.value(),
            y_center=self.w_center_y.value(),
            angle=self.w_angle.value(),
            flip_lr=self.w_flip_lr.isChecked(),
            flip_ud=self.w_flip_ud.isChecked()
        )
        with open(filename, "w") as fd:
            json.dump(d, fd, indent=2)

    def update_ui(self):
        if self.fixed_img is not None and self.moving_img is not None:
            self.show_button.setEnabled(True)
        else:
            self.show_button.setDisabled(True)

    def on_center(self, *args):
        if self.fixed_img is not None:
            center_x = self.fixed_img.shape[0] // 2
            center_y = self.fixed_img.shape[1] // 2
            self.w_center_x.setValue(center_x)
            self.w_center_y.setValue(center_y)

    def on_show(self, *args):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.figure.clf()
        if self.w_view_choice.currentText() == self.XY_VIEW:
            self.show_xy(self.figure.add_subplot(1, 1, 1))
        else:
            ax_xy = self.figure.add_subplot(2, 2, 1)
            ax_xz = self.figure.add_subplot(2, 2, 2)
            ax_yz = self.figure.add_subplot(2, 2, 4)
            self.show_xy(ax_xy)
            self.show_xz(ax_xz)
            self.show_yz(ax_yz)
        self.canvas.draw()
        QtWidgets.QApplication.restoreOverrideCursor()

    def show_xy(self, axes):
        downsample = self.w_downsample.value()
        fixed_slice = self.fixed_img[::downsample, ::downsample,
                                     self.fixed_img_z.value()].transpose()
        moving_slice = self.moving_img[::downsample, ::downsample,
                                       self.moving_img_z.value()].transpose()
        if self.w_flip_lr.isChecked():
            moving_slice = np.fliplr(moving_slice)
        if self.w_flip_ud.isChecked():
            moving_slice = np.flipud(moving_slice)
        angle = self.w_angle.value() * np.pi / 180
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)],
                               [np.sin(angle), np.cos(angle)]])
        y, x = np.mgrid[0:fixed_slice.shape[0], 0:fixed_slice.shape[1]]
        center = np.array([self.w_center_y.value(),
                           self.w_center_x.value()]).reshape(1, 2) // downsample
        offset = np.array([self.w_off_y.value(),
                           self.w_off_x.value()]).reshape(1, 2) // downsample
        yx = np.column_stack([y.flatten(), x.flatten()])
        yxt = ((yx - center - offset) @ rot_matrix) + center
        yt, xt = yxt.transpose()
        yt, xt = [_.reshape(fixed_slice.shape) for _ in (yt, xt)]
        cimg = np.zeros((fixed_slice.shape[0], fixed_slice.shape[1], 3), np.float32)
        cimg[:, : , 0] = fixed_slice
        map_coordinates(moving_slice, [yt, xt], cimg[:, :, 1])
        axes.cla()
        clip = np.quantile(cimg.flatten(), .90)
        axes.imshow(np.clip(cimg, 0, clip) / clip)
        self.redo_axes_ticks(axes, self.fixed_img.shape[0], self.fixed_img.shape[1])

    def redo_axes_ticks(self, axes:matplotlib.axes.Axes, x_len:int, y_len:int):
        downsample = self.w_downsample.value()
        x_stops = np.linspace(0, x_len, 6)
        x_stops_downsampled = x_stops / downsample
        axes.set_xticks(x_stops_downsampled)
        axes.set_xticklabels(["%d" % x for x in x_stops])
        y_stops = np.linspace(0, y_len, 6)[::-1]
        y_stops_downsampled = y_stops / downsample
        axes.set_yticks(y_stops_downsampled)
        axes.set_yticklabels(["%d" % y for y in y_stops])

    def show_xz(self, axes):
        downsample = self.w_downsample.value()
        y = self.fixed_img.shape[1] // 2
        min_x = min(self.fixed_img.shape[0], self.moving_img.shape[0])
        min_z = min(self.fixed_img.shape[2], self.moving_img.shape[2])
        fixed_slice = self.fixed_img[:min_x:downsample, y,
                                     :min_z:downsample].transpose()
        moving_slice = self.moving_img[:min_x:downsample, y,
                                       :min_z:downsample].transpose()
        combined = np.stack([fixed_slice, moving_slice, np.zeros_like(fixed_slice)], 2).astype(np.float32)
        clip = np.quantile(combined.flatten(), .90)
        combined = np.clip(combined, 0, clip)
        axes.imshow(combined)
        z_fixed = self.fixed_img_z.value() // downsample
        z_moving = self.moving_img_z.value() // downsample
        axes.plot([0, min_x // downsample], [z_fixed, z_fixed])
        axes.plot([0, min_x // downsample], [z_moving, z_moving])
        self.redo_axes_ticks(axes, min_x, min_z)

    def show_yz(self, axes):
        downsample = self.w_downsample.value()
        x = self.fixed_img.shape[0] // 2
        min_y = min(self.fixed_img.shape[1], self.moving_img.shape[1])
        min_z = min(self.fixed_img.shape[2], self.moving_img.shape[2])
        fixed_slice = self.fixed_img[x,
                                     :min_y:downsample,
                                     :min_z:downsample]
        moving_slice = self.moving_img[x,
                                       :min_y:downsample,
                                       :min_z:downsample]
        combined = np.stack([fixed_slice, moving_slice, np.zeros_like(fixed_slice)], 2).astype(np.float32)
        clip = np.quantile(combined.flatten(), .90)
        combined = np.clip(combined, 0, clip)
        axes.imshow(combined)
        z_fixed = self.fixed_img_z.value() // downsample
        z_moving = self.moving_img_z.value() // downsample
        axes.plot([z_fixed, z_fixed], [0, min_y // downsample])
        axes.plot([z_moving, z_moving], [0, min_y // downsample])
        self.redo_axes_ticks(axes, min_z, min_y)