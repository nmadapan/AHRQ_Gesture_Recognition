# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 04:41:40 2019

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

###########################################################################
## Class MyFrame3
###########################################################################

class MyFrame3 ( wx.Frame ):
    
    self.ImWidth = VideoDisplaySize[0] 
	self.ImHeight = VideoDisplaySize[1] 
	self.wildcard1='Video Files(*.avi)|*.avi|All Files(*.*)|*.*' 
    self.wildcard2='Video Files(*.mov)|*.mov|All Files(*.*)|*.*' 
	self.AnnotationList = []
	self.video_path1 = ''
	self.video_path2 = ''
	self.write_path = ''
	self.sync_window = 50
	self.ts1 = []
	self.ts2 = []

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1448,815 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer20 = wx.BoxSizer( wx.VERTICAL )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer23 = wx.BoxSizer( wx.VERTICAL )

		bSizer25 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Video File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		bSizer25.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.vidtxt1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.vidtxt1.Enable( False )

		bSizer25.Add( self.vidtxt1, 1, wx.ALL, 5 )

		self.selectbtn1 = wx.Button( self, wx.ID_ANY, u"Select", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer25.Add( self.selectbtn1, 0, wx.ALL, 5 )


		bSizer23.Add( bSizer25, 1, wx.EXPAND, 5 )

		bSizer26 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_bitmap7 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer26.Add( self.m_bitmap7, 1, wx.ALL|wx.FIXED_MINSIZE, 5 )


		bSizer23.Add( bSizer26, 8, wx.EXPAND, 5 )

		bSizer29 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slider4 = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizer29.Add( self.m_slider4, 1, wx.ALL, 5 )


		bSizer23.Add( bSizer29, 1, wx.EXPAND, 5 )

		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer23.Add( bSizer12, 1, wx.EXPAND, 5 )


		bSizer21.Add( bSizer23, 1, wx.EXPAND, 5 )

		bSizer24 = wx.BoxSizer( wx.VERTICAL )

		bSizer27 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Video File", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		bSizer27.Add( self.m_staticText3, 0, wx.ALL, 5 )

		self.vidtxt2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.vidtxt2.Enable( False )

		bSizer27.Add( self.vidtxt2, 1, wx.ALL, 5 )

		self.selectbtn2 = wx.Button( self, wx.ID_ANY, u"Select", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer27.Add( self.selectbtn2, 0, wx.ALL, 5 )


		bSizer24.Add( bSizer27, 1, wx.EXPAND, 5 )

		bSizer28 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_bitmap6 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.m_bitmap6, 1, wx.ALL|wx.FIXED_MINSIZE, 5 )


		bSizer24.Add( bSizer28, 8, wx.EXPAND, 5 )

		bSizer30 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slider5 = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		bSizer30.Add( self.m_slider5, 1, wx.ALL, 5 )


		bSizer24.Add( bSizer30, 1, wx.EXPAND, 5 )


		bSizer21.Add( bSizer24, 1, wx.EXPAND, 5 )

		bSizer17 = wx.BoxSizer( wx.VERTICAL )


		bSizer21.Add( bSizer17, 1, wx.EXPAND, 5 )


		bSizer20.Add( bSizer21, 10, wx.EXPAND, 5 )

		bSizer18 = wx.BoxSizer( wx.VERTICAL )

		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

		self.pausebtn1 = wx.ToggleButton( self, wx.ID_ANY, u"Pause", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pausebtn1.SetValue( True )
		bSizer22.Add( self.pausebtn1, 1, wx.ALL, 5 )


		bSizer18.Add( bSizer22, 1, wx.EXPAND, 5 )

		bSizer19 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

		self.Prevbtn = wx.Button( self, wx.ID_ANY, u"Previous Gesture", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.Prevbtn, 1, wx.ALL, 5 )

		self.Nextbtn = wx.Button( self, wx.ID_ANY, u"Next Gesture", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.Nextbtn, 1, wx.ALL, 5 )


		bSizer19.Add( bSizer14, 2, wx.EXPAND, 5 )

		bSizer15 = wx.BoxSizer( wx.HORIZONTAL )

		m_radioBox1Choices = [ u"Yes", u"No" ]
		self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, u"Focus Shift", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 3, wx.RA_SPECIFY_COLS )
		self.m_radioBox1.SetSelection( 0 )
		bSizer15.Add( self.m_radioBox1, 0, wx.ALL, 5 )

		self.wrtbtn = wx.Button( self, wx.ID_ANY, u"Write", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15.Add( self.wrtbtn, 0, wx.ALL, 5 )


		bSizer19.Add( bSizer15, 1, wx.EXPAND, 5 )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		self.savebtn = wx.Button( self, wx.ID_ANY, u"Save", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		bSizer16.Add( self.savebtn, 0, wx.ALL, 5 )


		bSizer19.Add( bSizer16, 0, wx.EXPAND, 5 )


		bSizer18.Add( bSizer19, 1, wx.EXPAND, 5 )


		bSizer20.Add( bSizer18, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer20 )
		self.Layout()
		self.m_timer1 = wx.Timer()
		self.m_timer1.SetOwner( self, 1 )
		self.m_timer2 = wx.Timer()
		self.m_timer2.SetOwner( self, 2 )

		self.Centre( wx.BOTH )

		# Connect Events
		self.selectbtn1.Bind( wx.EVT_BUTTON, self.Load1 )
		self.m_slider4.Bind( wx.EVT_SCROLL, self.OnScroll1 )
		self.selectbtn2.Bind( wx.EVT_BUTTON, self.Load2 )
		self.m_slider5.Bind( wx.EVT_SCROLL, self.OnScroll2 )
		self.pausebtn1.Bind( wx.EVT_TOGGLEBUTTON, self.Pause1 )
		self.Prevbtn.Bind( wx.EVT_BUTTON, self.Previous )
		self.Nextbtn.Bind( wx.EVT_BUTTON, self.Next )
		self.wrtbtn.Bind( wx.EVT_BUTTON, self.Write )
		self.savebtn.Bind( wx.EVT_BUTTON, self.Save )
		self.Bind( wx.EVT_TIMER, self.OnTime1, id=1 )
		self.Bind( wx.EVT_TIMER, self.OnTime2, id=2 )
        
        #Set Flags
        
		self.PAUSE_FLAG1 = False
		self.PROCESSING_FLAG1 = False
		self.PAUSE_FLAG2 = False
		self.PROCESSING_FLAG2 = False

	def __del__( self ):
        self.m_timer1.Stop()
		self.m_timer2.Stop()
		pass


	# Virtual event handlers, overide them in your derived class
	def Load1( self, event ):
        dlg1 = wx.FileDialog(self, message='Open Video File',
                            defaultDir='',
                            defaultFile='',
                            wildcard1=self.wildcard1,
                            style=wx.FD_OPEN)
        
		if dlg1.ShowModal() == wx.ID_OK:  #Do something
		    self.AnnotationList = []
		    self.video_path1 = dlg1.GetPath()
		    dlg1.Destroy()
		    fpath1 = self.video_path1.split('.')
		    self.write_path = fpath1[0] + '_annot.txt'
		    print(self.write_path)
            # read timestamp
		    try:
		        self.ts_path1 = fpath1[0] + 'ts.txt' #if the file is named as xxx_depthts or rgbts
		        print(self.ts_path1)
		        f = open(self.ts_path1, 'r+')
		    except FileNotFoundError:
		        self.ts_path1 = fpath1[0][:-5] + 'skelts.txt' #if the file is named as xxx_skelts
		        f = open(self.ts_path1, 'r+')
		    finally:
		        for line in f.readlines():
		            self.ts1.append(float(line))
		        f.close()
                
		    self.PROCESSING_FLAG1 = True
		    self.videoCapture1 = cv2.VideoCapture(self.video_path1)
		    if(self.videoCapture1 == None):
		        wx.SafeShowMessage('start', 'Open Failed')
		        return
		    self.TotalFrame1 = self.videoCapture1.get(cv2.CAP_PROP_FRAME_COUNT)
		    self.fps1 = self.videoCapture1.get(cv2.CAP_PROP_FPS)
		    self.FrameTime1 = 1000 / self.fps1  #In miliseconds
		    self.TotalTime1 = self.TotalFrame1*self.FrameTime1
		    self.m_slider4.SetMax(int(self.TotalFrame1))
		    self.m_timer1.Start(self.FrameTime1)
		    self.vidtxt1.SetValue('Video Loaded : ' + self.video_path1)
		    self.index = 0
		event.Skip()

	def OnScroll1( self, event ):
        if self.PROCESSING_FLAG1:
		    self.Frame1 = self.m_slider4.GetValue()
            #synchronize video2 by 1: set the current frame position and scroall2 for video2
		    if self.PROCESSING_FLAG2:
		        self.Frame2 = self.sync_ts(mode = 1)
		        self.m_slider5.SetValue(int(self.Frame2))
		        self.videoCapture2.set(cv2.CAP_PROP_POS_FRAMES, self.Frame2)
		    self.videoCapture1.set(cv2.CAP_PROP_POS_FRAMES, self.Frame1)
		    success1, self.CurrentFrame1 = self.videoCapture1.read()
		    if(success1):
		        self.MyImshow1()
		else:
		    event.Skip()  

	def Load2( self, event ):
        dlg2 = wx.FileDialog(self, message='Open Video File',
                            defaultDir='',
                            defaultFile='',
                            wildcard2=self.wildcard2,
                            style=wx.FD_OPEN)
        
		if dlg2.ShowModal() == wx.ID_OK:  #Do something
		    self.video_path2 = dlg2.GetPath()
		    dlg2.Destroy()
		    self.PROCESSING_FLAG2 = True
            
            # read timestamp
		    fpath2 = self.video_path2.split('.')
		    try:
		        self.ts_path2 = fpath2[0] + 'ts.txt'
		        f = open(self.ts_path2, 'r+')
		    except FileNotFoundError:
		        self.ts_path2 = fpath2[0][:-5] + 'skelts.txt'
		        f = open(self.ts_path2, 'r+')
		    finally:
		        for line in f.readlines():
		            self.ts2.append(float(line))
		        f.close()
                
		    self.videoCapture2 = cv2.VideoCapture(self.video_path2)
		    if(self.videoCapture2 == None):
		        wx.SafeShowMessage('start', 'Open Failed')
		        return
		    self.TotalFrame2 = self.videoCapture2.get(cv2.CAP_PROP_FRAME_COUNT)
		    self.fps2 = self.videoCapture2.get(cv2.CAP_PROP_FPS)
		    self.FrameTime2 = 1000 / self.fps2  #In seconds
		    self.TotalTime2 = self.TotalFrame2*self.FrameTime2
		    self.m_slider5.SetMax(int(self.TotalFrame2))
		    self.m_timer2.Start(self.FrameTime2)
		    self.vidtxt2.SetValue('Video Loaded : ' + self.video_path2)
		event.Skip()

	def OnScroll2( self, event ):
        if self.PROCESSING_FLAG2:
		    self.Frame2 = self.m_slider5.GetValue()
		    self.videoCapture2.set(cv2.CAP_PROP_POS_FRAMES, self.Frame2)
            #synchronize video1 and 2: set the current frame position and scroall1 for video1
		    if self.PROCESSING_FLAG1:
		        self.Frame1 = self.sync_ts(mode = 0)
		        self.m_slider4.SetValue(int(self.Frame1))
		        self.videoCapture1.set(cv2.CAP_PROP_POS_FRAMES, self.Frame1)
		    success2, self.CurrentFrame2 = self.videoCapture2.read()
		    if(success2):
		        self.MyImshow2()
		else:
		    event.Skip()    

	def Pause1( self, event ):
        if self.PROCESSING_FLAG1:
		    self.PAUSE_FLAG1 = event.GetEventObject().GetValue()
		    if self.PAUSE_FLAG1:
		        self.m_timer1.Stop()
		        event.GetEventObject().SetLabel("Play")
		    else:
		        self.m_timer1.Start(self.FrameTime1)
		        event.GetEventObject().SetLabel("Pause")
		else:
		    event.Skip()
		if self.PROCESSING_FLAG2:
		    self.PAUSE_FLAG2 = event.GetEventObject().GetValue()
		    if self.PAUSE_FLAG2:
		        self.m_timer2.Stop()
		        event.GetEventObject().SetLabel("Play")
		    else:
		        self.m_timer2.Start(self.FrameTime2)
		        event.GetEventObject().SetLabel("Pause")
		else:
		    event.Skip()

	def Previous( self, event ):
		event.Skip()

	def Next( self, event ):
		event.Skip()

	def Write( self, event ):
        Elem = ""  
		self.focus = self.m_radioBox1.GetSelection()
		Elem = self.combot_1.GetValue()
		if self.focus:
		    Elem += ',No'
		else:
		    Elem += ',Yes'
		self.AnnotationList.append(Elem)
		event.Skip()

	def Save( self, event ):
        f = open(self.write_path, 'w')
		for elem in self.AnnotationList:
		    f.write(elem + "\n")        
		f.close()
		event.Skip()

	def OnTime1( self, event ):
        if self.PROCESSING_FLAG1:
		    success1, self.CurrentFrame1 = self.videoCapture1.read()
		    self.Frame1 = self.videoCapture1.get(cv2.CAP_PROP_POS_FRAMES)
		    if (success1):
		        self.MyImshow1() 
		else:
		    event.Skip()

	def OnTime2( self, event ):
        if self.PROCESSING_FLAG2:
		    success2, self.CurrentFrame2 = self.videoCapture2.read()
		    self.Frame2 = self.videoCapture2.get(cv2.CAP_PROP_POS_FRAMES)
		    if (success2):
		        self.MyImshow2()
		else:
		    event.Skip()
            
    #Functions
    
	def MyImshow1(self):
		self.CurrentFrame1 = cv2.resize(self.CurrentFrame1, (self.ImWidth, self.ImHeight), interpolation = cv2.INTER_CUBIC)
		image1 = cv2.cvtColor(self.CurrentFrame1, cv2.COLOR_BGR2RGB)
		pic1 = wx.Bitmap.FromBuffer(self.ImWidth, self.ImHeight, image1) 
		self.m_bitmap7.SetBitmap(pic1)
		self.m_slider4.SetValue(int(self.Frame1))
        
	def MyImshow2(self):
        
		self.CurrentFrame2 = cv2.resize(self.CurrentFrame2, (self.ImWidth, self.ImHeight), interpolation = cv2.INTER_CUBIC)
		image2 = cv2.cvtColor(self.CurrentFrame2, cv2.COLOR_BGR2RGB)
		pic2 = wx.Bitmap.FromBuffer(self.ImWidth, self.ImHeight, image2) 
		self.m_bitmap6.SetBitmap(pic2)
		self.m_slider5.SetValue(int(self.Frame2))
        
	def sync_ts(self, mode = 0):
		'''
		Description:
    		Synchronize two lists of time stamps.
    	Input arguments:
    		frame_num: current frame number
            mode: if mode == 0: synchronize right by left
                  if mode == 1: left by right 
    	Return:
    		* A synchronized frame number
		'''	
		if mode:
		    frame_num = int(self.Frame1)
		    if frame_num > self.sync_window and frame_num < self.TotalFrame2 - self.sync_window:
		        l = np.array(self.ts2[frame_num - self.sync_window : frame_num + self.sync_window + 1])
		        l = abs(l - self.ts1[frame_num])
		        sync_frame = frame_num - self.sync_window + int(np.argmin(l))
		    elif frame_num < self.sync_window:
		        sync_frame = frame_num
		    else:
		        sync_frame = self.Frame2
		else:
		    frame_num = int(self.Frame2)
		    if frame_num > self.sync_window and frame_num < self.TotalFrame1 - self.sync_window:
		        l = np.array(self.ts1[frame_num - self.sync_window : frame_num + self.sync_window + 1])
		        l = abs(l - self.ts2[frame_num])
		        sync_frame = frame_num - self.sync_window + int(np.argmin(l))
		    elif frame_num < self.sync_window:
		        sync_frame = frame_num
		    else:
		        sync_frame = self.Frame1            
		return sync_frame
    
if __name__ =='__main__':

    # The size of display area and the path of video file, the annotation file will be in the same dictionary will the video file
    VideoDisplaySize = [705, 460] #For Taurus
#    VideoDisplaySize = [960, 700] #For Taurus Simulator  
    app = wx.App()
    frame = MyFrame3(None)
    frame.Show()
    app.MainLoop()
    
    print("closing correctly")    
    del app

