import os
import sys
import cv2
import time
import math
import threading
import numpy as np
from os import path
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from scipy.stats import norm
from PyQt5.uic import loadUiType
# from PyQt5 import QtWidgets
# from PyQt5.QtCore import QTimer
# from PyQt5.QtGui import QPixmap
# from PyQt5 import QtCore, QtGui, QtWidgets



FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__), "gui.ui"))
class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self , parent=None):
        pg.setConfigOption('background', (25,25,35))
        
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.gravity = 9.8 
        self.dotted_pen = pg.mkPen(color=(31, 204, 54), width=3, style=Qt.DashLine)
        self.yellow_pen = pg.mkPen(color=(227, 224, 32), width=1)
        # self.graphicsView.setBackgroundBrush(QBrush(QImage("images/yard1.jpg")))
        
        self.title = "Sports Simulation"
        self.setWindowTitle(self.title)
        # self.setWindowIcon(QIcon("images/icons/wizard.png"))
        
        
        self.doubleSpinBox_theta.valueChanged.connect(self.ball_elevations)
        self.doubleSpinBox_v.valueChanged.connect(self.ball_elevations)
        self.doubleSpinBox_s.valueChanged.connect(self.ball_elevations)
        
        self.doubleSpinBox_mu.valueChanged.connect(self.score_probability)
        self.doubleSpinBox_std.valueChanged.connect(self.score_probability)
        self.doubleSpinBox_spd.valueChanged.connect(self.score_probability)
        
        
    def ball_elevations(self):
    
        """" 
        velocity_x = v0 * math.cos(theta)
        velocity_y = v0 * math.sin(theta) - self.gravity * elapsed_t 
        
        theta: the kick angle
        v0: The initial velocity
        distance_s: distance from start to goal plane 
        elapsed_t1: The horizontal distance between the kicking point and the goal plane
        elapsed_t2: The horizontal distance between the goal plane and the maximum elevation point
        t: range of total time (0 : total time) with a step of 0.01
        """
        
        #####################################################
        #                   Control Knobs                   #
        #####################################################
        
        theta = self.doubleSpinBox_theta.value()
        theta = math.radians(theta)
        v0 = self.doubleSpinBox_v.value()
        distanc_s = self.doubleSpinBox_s.value()
        
        #####################################################
        #                 Height Calculation                #
        #####################################################
       
        elapsed_t1 = (v0 * math.sin(theta))/self.gravity  
        print("T", elapsed_t1)

        self.max_height = (v0 * elapsed_t1 * math.sin(theta)) - (0.5 * self.gravity * (elapsed_t1**2))
        
        distance_maxh = v0 * elapsed_t1 * math.cos(theta)
        print("S", distance_maxh)
        
        elapsed_t2 = (distanc_s - distance_maxh) / (v0 * math.cos(theta))
        print("Tao", elapsed_t2,'\n')
        
        self.goal_height = self.max_height - (0.5 * self.gravity * (elapsed_t2**2))
        
        if self.goal_height < 0: self.goal_height = 0
        
        self.labelMaxHeight.setText(str(round(self.max_height,2))+" m")   # height units
        self.labelGoalHeight.setText(str(round(self.goal_height,2))+" m")      
        
        t =  np.arange(0,(elapsed_t1+elapsed_t2),0.01)        
        x = v0 * t * np.cos(theta)
        y = v0 * t * np.sin(theta) - (0.5 * self.gravity * t**2)

        for index, value in enumerate(y):
            if value < 0:
                y[index] = 0
        
        """ testing (don't bother)"""
        # self.image = cv2.imread("images/grass.jpg")
        # self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        # img = pg.ImageItem( image=self.image )
        # plott = pg.PlotItem.addItem.plot(x, y, pen= self.dotted_pen)
        
        self.graphicsView.clear()
        # self.graphicsView.setBackgroundBrush(QBrush(QImage("images/grass.jpg")))
        # self.graphicsView.setCacheMode(QGraphicsView.CacheBackground)
        self.graphicsView.plot(x, y, pen= self.dotted_pen)
        
        """" At maximum height, velocity_y = 0
            line 76: We get time1 at that point from velocity_y equation @line 53 """
        
        """ line 79: Get max height by integrating velocity_y @line 53 """
        
        """ line 81: Get distance from start point to max height point by integrating velocity_x @line 52 """
        
        """ The horizontal distance between the goal plane and the maximum height point 
            equals the integration of velocity_x along that duration 
            line 84: v0 * t2 *cos(theta) = S - """
        
        """ During the falling phase the ball dynamics is described by velocity_y = -gt
            by integrating that we acquire the effect of gravity in the - y direction
            line 87: height at goal plane = maximum height - effect of gravity """
        
        """ line 89: if height at goal plane is negative, replace it with a zero """
        
        """ line 94: x & y axes, velocity equations integrated to get distance equations 
            (mainly for the graphical curve)"""
        
        """ line 98: for every negative height value, replace it with a zero """
        
        
    def score_probability(self):
        
        mu = self.doubleSpinBox_mu.value()     # mean
        std = self.doubleSpinBox_std.value()   # standard deviation
        speed = self.doubleSpinBox_spd.value() # hit speed 
        
        x = np.linspace(mu - 3*std, mu + 3*std, int(6*std)) 
        sub = speed - (mu-(3*std)) # the start of the curve on the x axis
        if sub<0: sub = 0
        self.graphicsView_normal.clear()
        self.graphicsView_normal.plot(x, norm.pdf(x, mu, std), pen=self.yellow_pen, brush=(50,50,200,60))
        self.graphicsView_normal.plot(x[:int(sub)], norm.pdf(x, mu, std)[:int(sub)], pen=self.yellow_pen, fillLevel=0.0, brush=(50,200,100,100))
        cdf = norm.cdf(speed, loc=mu, scale=std)
        
        self.labelProbability.setText(str(int(round(cdf,2)*100))+" %")
        
        """ 
            x axis: mean in the middle with 3*std on both sides
            
            In the empirical sciences, the so-called three-sigma rule of thumb 
            (or 3σ rule) expresses a conventional heuristic that nearly all values 
            are taken to lie within three standard deviations of the mean, and thus 
            it is empirically useful to treat 99.7% probability as near certainty.
        """
        
        
        
             
def main():
    app = QApplication(sys.argv)
    style = """
        
        QMainWindow{
             background-image : url(images/grass.jpg);
             
             background-image: rgba(255,255,255,0.5);
             border : 1px solid white;
            }
        QWidget{
            color: White;
            font-weight: bold;
            font-size: 12px;
            }
        QLabel{
            color: #53ed5d;
			font-size: 15px;
            }
        QSplitter::handle {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
            stop:0 rgba(255, 255, 255, 0), 
            stop:0.407273 rgba(200, 200, 200, 255), 
            stop:0.4825 rgba(101, 104, 113, 235), 
            stop:0.6 rgba(255, 255, 255, 0));
        
             }
        /* QSplitter::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: 2px;
            margin-bottom: 2px;
            border-radius: 4px;
            } */
        QDoubleSpinBox{
            border: 1px solid #000;
            border-radius: 4px;
            padding: 2px;
            color: #17273b;
           }
        QGraphicsView{
            /* background-image : url(images/grass.jpg);
            background-image: rgba(255,255,255,0.5); */
            
            border: 1px solid #fff;
            border-radius: 4px;
            padding: 2px;
            color: #fff;
            }
        QGraphicsView::menu{
            color: black;
            }
        QPushButton{
            color: white;
            background: #1C658C;
            border: 1px #DADADA solid;
            padding: 4px 10px;
            border-radius:  2px;
            font-weight: bold;
            font-size: 12px;
            outline: none;
            }
        QPushButton:hover{
            border: 1px #C6C6C6 solid;
            background: #0892D0;
            }
        QPushButton:!enabled{
            border: 1px #C6C6C6 solid;
            background: #88a8b9;
            }
        QTabWidget::pane {
            color: white;
            background: #04070f;
            border: 2px solid #DADADA;
            padding: 2px 2px;
            border-radius: 4px;
            
            }

        QTabBar::tab {
            background: red;
            background: #262D37; 
            border: 1px solid lightgray; 
            border-radius: 4px;
            padding: 5px;
            min-width: 200px;
            font-size: 15px;
            } 
        QTabBar::tab:selected { 
            background: #4d5b70; 
            margin-bottom: -1px; 
            }
        QGroupBox{
            border: 1px solid #fff;
            padding: 4px 10px;
            border-radius:  4px;
            }
        QMenuBar{
            /* background: #262D37; */
            }
        QMenuBar{
            /* border: 1px solid #fff;
            padding: 4px 10px;
            */
            border-radius: 4px;
            }
        QMenuBar::item::selected{
            background: #4b596b;
            color: #fff;
            }
        QMenu::item{
            /* background: #3b444f;
            border: 1px #C6C6C6 solid;
            border-radius: 4px; */
            }
        QMenu::item::selected
            {
            background: #4b596b;
            color: #fff;
            }
    """
    app.setStyleSheet(style)
    window = MainApp()
    window.show()
    app.exec_()
if __name__ == '__main__':
    main()
