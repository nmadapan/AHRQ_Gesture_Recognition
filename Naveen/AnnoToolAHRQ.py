# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 05:26:05 2019

@author: user
"""

# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Feb 15 2019)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import cv2
import numpy as np
import time
import vlc
import ctypes
from pydub import AudioSegment

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrameAHRQ ( wx.Frame ):

	def __init__( self, parent ):
        
		self.ImWidth = VideoDisplaySize[0] 
		self.ImHeight = VideoDisplaySize[1] 
		self.wildcard='Video Files(*.avi)|*.avi|All Files(*.*)|*.*' 
		self.AnnotationList = []
		self.video_path = ''
		self.write_path = ''
		self.ts = []
		self.tsg = []
		self.gest = []
		self.yon = []
		self.cont = -1 
		self.index = 0
		self.tbg = 0
		self.speed = 1.5
		self.speed_change = 0.666666667
        
		wx.Frame.__init__ ( self, parent, id = 1, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1448,665 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Video File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		bSizer2.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_textCtrl1, 7, wx.ALL, 5 )

		self.m_button2 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_button2, 1, wx.ALL, 5 )


		bSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )

		self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1.Add( self.m_bitmap1, 1, wx.ALL|wx.FIXED_MINSIZE, 5 )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.m_slider1 = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizer3.Add( self.m_slider1, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_toggleBtn1 = wx.ToggleButton( self, wx.ID_ANY, u"Pause", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_toggleBtn1.SetValue( True )
		bSizer3.Add( self.m_toggleBtn1, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_button4 = wx.Button( self, wx.ID_ANY, u"Previous Gesture", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button4, 1, wx.ALL, 5 )

		self.m_button5 = wx.Button( self, wx.ID_ANY, u"Next Gesture", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5.Add( self.m_button5, 1, wx.ALL, 5 )


		bSizer4.Add( bSizer5, 1, wx.EXPAND, 5 )

		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

		m_radioBox1Choices = [ u"Yes", u"No" ]
		self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, u"Focus Shift", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 2, wx.RA_SPECIFY_COLS )
		self.m_radioBox1.SetSelection( 0 )
		bSizer7.Add( self.m_radioBox1, 1, wx.ALL, 5 )

		self.m_button6 = wx.Button( self, wx.ID_ANY, u"Write", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.m_button6, 2, wx.ALL, 5 )

		self.m_button7 = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.m_button7, 2, wx.ALL, 5 )


		bSizer4.Add( bSizer7, 1, wx.EXPAND, 5 )


		bSizer3.Add( bSizer4, 1, wx.EXPAND, 5 )


		bSizer1.Add( bSizer3, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_timer1 = wx.Timer()
		self.m_timer1.SetOwner( self, wx.ID_ANY )

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_button2.Bind( wx.EVT_BUTTON, self.Load )
		self.m_slider1.Bind( wx.EVT_SCROLL, self.Scroll )
		self.m_toggleBtn1.Bind( wx.EVT_TOGGLEBUTTON, self.Pause )
		self.m_button4.Bind( wx.EVT_BUTTON, self.Previous )
		self.m_button5.Bind( wx.EVT_BUTTON, self.Next )
		self.m_button6.Bind( wx.EVT_BUTTON, self.Write )
		self.m_button7.Bind( wx.EVT_BUTTON, self.Save )
		self.Bind( wx.EVT_TIMER, self.OnTime, id=wx.ID_ANY )
        
        #Set Flags
        
		self.PAUSE_FLAG = False
		self.PROCESSING_FLAG = False
		self.TEXT_FLAG = False
        

	def __del__( self ):
		self.m_timer1.Stop()
		pass


	# Virtual event handlers, overide them in your derived class
	def Load( self, event ):
		dlg = wx.FileDialog(self, message='Open Video File',
                            defaultDir='',
                            defaultFile='',
                            wildcard=self.wildcard,
                            style=wx.FD_OPEN)
        
		if dlg.ShowModal() == wx.ID_OK:  #Do something
            
		    self.AnnotationList = []
		    self.video_path = dlg.GetPath()
		    print(self.video_path)
		    dlg.Destroy()
		    fpath = self.video_path.split('.')
		    self.write_path = fpath[0][:-4] + 'annoted.txt'
		    print(self.write_path)
            
		    # read timestamps for screen video
		    self.ts_path = fpath[0][:-4] + 'screents30.txt' #if the file is named as xxx_depthts or rgbts
		    print(self.ts_path)
		    f = open(self.ts_path, 'r+')
		    for line in f.readlines():
		        self.ts.append(float(line))
		    f.close()
            
            #Modify audio file
		    self.audio_rpath = fpath[0][:-4] + 'screen.mp3'
		    self.audio = AudioSegment.from_mp3(self.audio_rpath)
		    self.slow_audio = self.Speed_Change(self.audio, self.speed_change)
		    self.audio_wpath = fpath[0][:-4] + 'slow.mp3'
		    self.slow_audio.export(self.audio_wpath, format = "mp3")
		    self.sound = vlc.MediaPlayer(self.audio_wpath)
                
		    self.PROCESSING_FLAG = True
		    self.videoCapture = cv2.VideoCapture(self.video_path)
		    if(self.videoCapture == None):
		        wx.SafeShowMessage('start', 'Open Failed')
		        return
		    self.TotalFrame = self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
		    self.fps = self.videoCapture.get(cv2.CAP_PROP_FPS)
		    self.FrameTime = (1000 / self.fps)  #In miliseconds
		    self.TotalTime = self.TotalFrame*self.FrameTime
		    self.m_slider1.SetMax(int(self.TotalFrame))
		    self.m_textCtrl1.SetValue('Video Loaded : ' + self.video_path)
            
            # Read timestamps for gestures
		    self.ts_gest = fpath[0][:-4] + 'kthreelog.txt' #file time stamps gestures
		    g = open(self.ts_gest, 'r+')
		    for line in g.readlines():
		        self.tsg.append(float(line.split(',')[0]))
		        self.gest.append(line.split(',')[19])
		        self.yon.append(line.split(',')[18])
		    g.close()
            
            #Start timer and audio
		    self.m_timer1.Start(1000/self.fps)
		    self.sound.play()
            
		event.Skip()

	def Scroll( self, event ):
		if self.PROCESSING_FLAG:
		    self.Frame = self.m_slider1.GetValue()
		    self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, self.Frame)
		    success, self.CurrentFrame = self.videoCapture.read()
		    self.audio_pos = int(((self.Frame/self.fps) * self.speed) * 1000)
		    self.sound.set_time(self.audio_pos) 
		    if(success):
		        self.MyImshow()
		else:
		    event.Skip()  

	def Pause( self, event ):
		if self.PROCESSING_FLAG:
		    self.PAUSE_FLAG = event.GetEventObject().GetValue()
		    if self.PAUSE_FLAG:
		        self.m_timer1.Start(self.FrameTime)
		        event.GetEventObject().SetLabel("Pause")
		        self.sound.pause()	        
		    else:
		        self.m_timer1.Stop()
		        event.GetEventObject().SetLabel("Play")
		        self.sound.pause()
		else:
		    event.Skip()

	def Previous( self, event ):
		l = np.array(self.ts)
		if(self.cont > 0):
		    self.cont -= 1
		    ls = abs(l - self.tsg[self.cont])
		    self.Frame = int(np.argmin(ls)) - self.fps * self.tbg
		    self.audio_pos = int(((self.Frame/self.fps) * self.speed) * 1000)
		    self.gestcode = self.gest[self.cont]
		    self.selection = self.yon[self.cont]
		else:
		    ls = abs(l - self.tsg[0])
		    self.Frame = int(np.argmin(ls)) - self.fps * self.tbg
		    self.audio_pos = int(((self.Frame/self.fps) * self.speed) * 1000)
		    self.gestcode = self.gest[0]
		    self.selection = self.yon[0]
		self.m_slider1.SetValue(int(self.Frame))
		self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, self.Frame)
		self.sound.set_time(self.audio_pos)    
		event.Skip()

	def Next( self, event ):
		self.TEXT_FLAG = True
		l = np.array(self.ts)
		if(self.cont < len(self.tsg) - 1):
		    self.cont += 1
		    ls = abs(l - self.tsg[self.cont])
		    self.Frame = int(np.argmin(ls)) - self.fps * self.tbg
		    self.audio_pos = int(((self.Frame/self.fps) * self.speed) * 1000)
		    self.gestcode = self.gest[self.cont]
		    self.selection = self.yon[self.cont]
		else:
		    ls = abs(l - self.tsg[-1])            
		    self.Frame = int(np.argmin(ls)) - self.fps * self.tbg
		    self.audio_pos = int(((self.Frame/self.fps) * self.speed) * 1000)
		    self.gestcode = self.gest[-1]
		    self.selection = self.yon[-1]
		self.m_slider1.SetValue(int(self.Frame))
		self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, self.Frame)
		self.sound.set_time(self.audio_pos)
		event.Skip()

	def Write( self, event ):
		self.focus = self.m_radioBox1.GetSelection()
		Elem = ""
		Elem = self.gestcode
		if self.focus:
		    Elem += ',No'
		else:
		    Elem += ',Yes'
		if self.selection == 'None':
		    Elem += ',No'
		else:
		    Elem += ',Yes'
		self.AnnotationList.append(Elem)
		if(self.cont == len(self.tsg) - 1):
		    ctypes.windll.user32.MessageBoxW(0, "No more gestures to annotate", "Finished task", 0)
		event.Skip()

	def Save( self, event ):
		f = open(self.write_path, 'w')
		for elem in self.AnnotationList:
		    f.write(elem + "\n")        
		f.close()
		event.Skip()

	def OnTime( self, event ):
		if self.PROCESSING_FLAG:
#		    start_time = time.time()
		    success, self.CurrentFrame = self.videoCapture.read()
		    self.Frame = self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES)
		    if (success):
		        self.MyImshow() 
#		    print("Time taken : ", time.time() - start_time)
		else:
		    event.Skip()
        
    #Functions
    
	def MyImshow(self):
		self.CurrentFrame = cv2.resize(self.CurrentFrame, (self.ImWidth, self.ImHeight), interpolation = cv2.INTER_CUBIC)
		image = cv2.cvtColor(self.CurrentFrame, cv2.COLOR_BGR2RGB)
		vidtext = ""
		if self.TEXT_FLAG:
		    if self.yon[self.cont] == 'None':
		        vidtext = 'No'
		    else:
		        vidtext = 'Yes'
		    cv2.putText(image,vidtext,(10,50),cv2.FONT_HERSHEY_SIMPLEX,2,(200,255,155),5,cv2.LINE_AA)
		    cv2.putText(image,self.gestcode,(10,100),cv2.FONT_HERSHEY_SIMPLEX,1,(200,255,155),1,cv2.LINE_AA)
		pic = wx.Bitmap.FromBuffer(self.ImWidth, self.ImHeight, image) 
		self.m_bitmap1.SetBitmap(pic)
		self.m_slider1.SetValue(int(self.Frame))
        
	def Speed_Change(self, sound, speed = 1.0):
		sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)})  
		return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

if __name__ =='__main__':

    # The size of display area and the path of video file, the annotation file will be in the same dictionary will the video file
    VideoDisplaySize = [1410, 450] 
    app = wx.App()
    frame = MyFrameAHRQ(None)
    frame.Show()
    app.MainLoop() 
    print('Closing :)')
    del app