import sys
from PyQt4 import QtCore, QtGui

COLOR_LIST = ['red','blue','green', 'black', 'cyan', 'magenta']
ANIMATION_SPEED = 500


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
        self.resize(QtCore.QSize(500, 200))

        # widgets
        self.mainwidget = AnimatedTabWidget()
        self.setCentralWidget(self.mainwidget)


class AnimatedTabWidget(QtGui.QWidget):
    def __init__(self, parent=None, tabs=COLOR_LIST):

        QtGui.QWidget.__init__(self, parent)

        self.animating = False
        self.stack_animation = None

        self.btnframe = QtGui.QFrame(self)
        self.stackedwidget = QtGui.QStackedWidget(self)

        self.line = QtGui.QFrame(self.btnframe)
        self.line.setFixedHeight(3)
        self.line.setStyleSheet('QFrame{'
                                '  background-color:#1974f4'
                                '}')

        # layouts
        self.vlayout = QtGui.QVBoxLayout(self)
        self.setLayout(self.vlayout)

        self.vlayout.addWidget(self.btnframe)
        self.vlayout.addWidget(self.stackedwidget)

        self.hlayout = QtGui.QGridLayout(self.btnframe)
        self.btnframe.setLayout(self.hlayout)
        self.hlayout.addWidget(self.line, 1, 0)

        # build frames
        for i, tab in enumerate(tabs):
            widget = QtGui.QWidget()
            widget.setStyleSheet('QWidget{'
                                 '  background-color: '+tab+';'
                                 '}')
            widget.setObjectName(tab)
            self.stackedwidget.addWidget(widget)

            btn = QtGui.QPushButton(tab, self.btnframe)
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.pressed.connect(make_callback(self.change_color, tab))
            btn.setStyleSheet('QPushButton:hover {'
                              '  color:#1974f4;'
                              '  font: 75 10pt "MS Shell Dlg 2";'
                              '  background-color: transparent;'
                              '}'
                              'QPushButton:pressed {'
                              '  color: #1974f4;'
                              '  background-color: transparent;'
                              '  font: 75 10pt "MS Shell Dlg 2";'
                              '}'
                              'QPushButton:checked {'
                              '  color:#1974f4;'
                              '  font: 75 10pt "MS Shell Dlg 2";'
                              '  background-color: transparent;'
                              '}')
            self.hlayout.addWidget(btn, 0, i)




    def change_color(self, new_color):

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

    def animate(self, from_, to, direction='horizontal'):
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
        from_widget.show()
        from_widget.setHidden(False)
#        to_widget.lower()
#        to_widget.raise_()

        print(self.stackedwidget.currentIndex())

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