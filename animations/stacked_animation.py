import sys
from PyQt4 import QtCore, QtGui

COLOR_LIST = ['red', 'blue', 'green', 'black', 'cyan', 'magenta']
ANIMATION_SPEED = 400


def make_callback(func, *param):
    '''
    Helper function to make sure lambda functions are cached and not lost.
    '''
    return lambda: func(*param)


class App(QtGui.QMainWindow):

    def __init__(self, app, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        # reference to qapp instance
        self.app = app

        self.animating = False
        self.stack_animation = None

        self.resize(QtCore.QSize(500, 200))

        # widgets
        self.mainwidget = QtGui.QWidget()
        self.setCentralWidget(self.mainwidget)

        self.listwidget = QtGui.QListWidget()
        self.listwidget.addItems(COLOR_LIST)
        self.listwidget.itemSelectionChanged.connect(self.change_color)

        self.stackedwidget = QtGui.QStackedWidget()

        for color in COLOR_LIST:
            widget = QtGui.QWidget()
            widget.setStyleSheet('QWidget{'
                                 '  background-color: '+color+';'
                                 '}')
            widget.setObjectName(color)
            self.stackedwidget.addWidget(widget)

        # layouts
        self.hlayout = QtGui.QHBoxLayout(self.mainwidget)
        self.mainwidget.setLayout(self.hlayout)

        self.hlayout.addWidget(self.listwidget)
        self.hlayout.addWidget(self.stackedwidget)

    def change_color(self):

        new_color = str(self.listwidget.currentItem().text())
        old_color = str(self.stackedwidget.currentWidget().objectName())

        old_index = self.stackedwidget.currentIndex()
        new_index = 0
        for i in range(self.stackedwidget.count()):
                widget = self.stackedwidget.widget(i)
                if new_color == str(widget.objectName()):
                    new_index = i
                    break

        print('Changing from:', old_color, old_index,
              'To:', new_color, new_index)

        self.animate(old_index, new_index)

    def animate(self, from_, to, direction='vertical'):
        """ animate changing of qstackedwidget """

        # check to see if already animating
        if self.animating and self.stack_animation is not None:
            self.stack_animation.stop()

        from_widget = self.stackedwidget.widget(from_)
        to_widget = self.stackedwidget.widget(to)

        # get from geometry
        width = from_widget.frameGeometry().width()
        height = from_widget.frameGeometry().height()

        # offset
        # bottom to top
        if direction == 'vertical' and from_ < to:
            offsetx = 0
            offsety = height
        # top to bottom
        elif direction == 'vertical' and from_ > to:
            offsetx = 0
            offsety = -height
        elif direction == 'horizontal' and from_ < to:
            offsetx = width
            offsety = 0
        elif direction == 'horizontal' and from_ > to:
            offsetx = -width
            offsety = 0
        else:
            return

        # move to widget and show
        # set the geometry of the next widget
        to_widget.setGeometry(0 + offsetx, 0 + offsety, width, height)
        to_widget.show()

        # animate
        # from widget
        animnow = QtCore.QPropertyAnimation(from_widget, "pos")
        animnow.setDuration(ANIMATION_SPEED)
        animnow.setEasingCurve(QtCore.QEasingCurve.InOutQuint)
        animnow.setStartValue(
            QtCore.QPoint(0,
                          0))
        animnow.setEndValue(
            QtCore.QPoint(0 - offsetx,
                          0 - offsety))

        # to widget
        animnext = QtCore.QPropertyAnimation(to_widget, "pos")
        animnext.setDuration(ANIMATION_SPEED)
        animnext.setEasingCurve(QtCore.QEasingCurve.InOutQuint)
        animnext.setStartValue(
            QtCore.QPoint(0 + offsetx,
                          0 + offsety))
        animnext.setEndValue(
            QtCore.QPoint(0,
                          0))

        # animation group
        self.stack_animation = QtCore.QParallelAnimationGroup()
        self.stack_animation.addAnimation(animnow)
        self.stack_animation.addAnimation(animnext)
        self.stack_animation.finished.connect(
            make_callback(self.animate_stacked_widget_finished,
                          from_, to)
            )
        self.stack_animation.stateChanged.connect(
            make_callback(self.animate_stacked_widget_finished,
                          from_, to)
            )

        self.animating = True
        self.stack_animation.start()

    def animate_stacked_widget_finished(self, from_, to):
        """ cleanup after animation """
        if self.stack_animation.state() == QtCore.QAbstractAnimation.Stopped:
            self.stackedwidget.setCurrentIndex(to)
            from_widget = self.stackedwidget.widget(from_)
            from_widget.hide()
            from_widget.move(0, 0)
            self.animating = False

    def animate_state_changed(self, from_, to):
        """ check to see if the animation has been stopped """

        self.animate_stacked_widget_finished(from_, to)


if __name__ == '__main__':
    qapp = QtGui.QApplication(sys.argv)

    app = App(qapp)
    app.show()
    qapp.exec_()
    qapp.deleteLater()
    sys.exit()
