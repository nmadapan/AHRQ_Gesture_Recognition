
# coding: utf-8

# In[17]:


from fuzzywuzzy import fuzz
import speech_recognition as sr
from IPython.display import clear_output
import pandas as pd


# In[18]:
mic_name = u'Microphone (Logitech Wireless H' #Define your microphone

def spch():

	global mic_name

	sample_rate = 48000

	chunk_size = 2048

	r = sr.Recognizer()

	mic_list = sr.Microphone.list_microphone_names()
	print(mic_list)


	for i, microphone_name in enumerate(mic_list):
		if microphone_name == mic_name:
			device_id = i

	print('Device ID: ', device_id)

	with sr.Microphone(device_index = device_id, sample_rate = sample_rate,
							chunk_size = chunk_size) as source:


		r.adjust_for_ambient_noise(source)
		print("Say your command:")

		audio = r.listen(source)
		print('listened')

		try:
			text = r.recognize_google(audio)

			#print("you said: ")
			#print(text)
			nlp_check(text.lower())



		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")

		except sr.RequestError as e:
			print("Could not request results from Google speech Recognition service; {0}".format(e))


# In[19]:


def mod_spch():
	global mic_name

	sample_rate = 48000

	chunk_size = 2048

	r = sr.Recognizer()

	mic_list = sr.Microphone.list_microphone_names()


	for i, microphone_name in enumerate(mic_list):
		if microphone_name == mic_name:
			device_id = i


	with sr.Microphone(device_index = device_id, sample_rate = sample_rate,
							chunk_size = chunk_size) as source:


		r.adjust_for_ambient_noise(source)
		print("Say your command:")

		audio = r.listen(source)
		print('listened')

		try:
			text = r.recognize_google(audio)

			return text.lower()






		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")

		except sr.RequestError as e:
			print("Could not request results from Google speech Recognition service; {0}".format(e))


# In[20]:


def nlp_check(a):
	cmds = ['scroll','flip','rotate','zoom','switch','move screen','manual contrast','layout','contrast preset']
	r=[]
	if a in cmds:
		print("Your Command:")
		print(a)
		mod(a)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(a,w)
			r.append(ratio)
		m = max(r)
		#print(m)
		if m > 59:
			print("Your Command:")
			j = cmds[r.index(m)]
			print(j)
			mod(j)
		else:
			print("your command not recognized")



# In[21]:


def mod(c):
	mod_select = {'scroll': scrl,'flip':flip,'rotate':rotate,'zoom':zoom,'switch':switch,'move screen':pan,'manual contrast':mctr,'layout':lyt,'contrast preset':cprst}
	f = mod_select.get(c)
	f()


# In[22]:


def scrl():
	print('upside or downside')
	t = mod_spch()
	cmds = ['upside','downside']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 60:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")

def flip():
	print('horizontal or vertical')
	t = mod_spch()
	cmds = ['horizontal','vertical']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 80:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")



def rotate():
	print('clockwise or counterclockwise')
	t = mod_spch()
	cmds = ['clockwise','counterclockwise']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 50:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")


def zoom():
	print('inside or outside')
	t = mod_spch()
	cmds = ['inside','outside']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 80:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")


def switch():
	print('Left or Right')
	t = mod_spch()
	cmds = ['left','right']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 50:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")


def pan():
	print('Left / Right / Upside / Downside')
	t = mod_spch()
	cmds = ['left','right','upside','downside']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 80:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")


def mctr():
	print('increase or decrease')
	t = mod_spch()
	cmds = ['increase','decrease']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.token_sort_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 40:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")


def lyt():
	print('2 panels or 3 panels')
	t = mod_spch()
	cmds = ['two panels','three panels']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 90:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")



def cprst():
	print('first or second')
	t = mod_spch()
	cmds = ['first','second']
	r=[]
	if t in cmds:
		print("Your Command:")
		print(t)
	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(t,w)
			r.append(ratio)
		m = max(r)
		print(m)
		if m > 80:
			print("Your Command:")
			print(cmds[r.index(m)])
		else:
			print("your command not recognized")






# 1. Scroll
# 2. Flip
# 3. Rotate
# 4. Zoom
# 5. Manual Contrast
# 6. Move Screen
# 7. Layout
# 8. Switch
# 9. Contrast Preset

# In[23]:


spch()


# # Tests

# In[70]:


def test():
	itr = 0
	ans ='y'
	c = 0
	acc = 0
	while itr < 5 and ans == 'y':
		spch()
		s = int(input("1-Pass 0-Fail 2-Skip"))

		if s == 1:
			c+=1
			itr+=1
		elif s ==0:
			itr+=1

		ans = input("Do you want to continue (y/n)?")
		print(itr)
		clear_output()

	acc = c / itr
	return acc



# In[32]:


test()


# In[75]:


def test_s():
	a = test()
	results.append(a)
def test_f():
	a = test()
	results.append(a)
def test_r():
	a = test()
	results.append(a)
def test_z():
	a = test()
	results.append(a)
def test_mc():
	a = test()
	results.append(a)
def test_ms():
	a = test()
	results.append(a)
def test_l():
	a = test()
	results.append(a)
def test_sw():
	a = test()
	results.append(a)
def test_cp():
	a = test()
	results.append(a)
def test_rt():
	a = test()
	results.append(a)


# Scroll

# In[77]:


results=[]
test_s()


# Flip

# In[78]:


test_f()


# Rotate

# In[79]:


test_r()


# Zoom

# In[80]:


test_z()


# Manual Contrast

# In[81]:


test_mc()


# Move Screen

# In[82]:


test_ms()


# Layout

# In[83]:


test_l()


# Switch

# In[84]:


test_sw()


# Contrast Preset

# In[85]:


test_cp()


# Random Test
# 1. Scroll
# 2. Flip
# 3. Rotate
# 4. Zoom
# 5. Manual Contrast
# 6. Move Screen
# 7. Layout
# 8. Switch
# 9. Contrast Preset

# In[86]:


test_rt()


# In[87]:


results


# In[106]:


df = pd.read_excel('results.xlsx')

c = list(df.columns)
df2 = pd.DataFrame([results], columns=c)

df = df.append(df2)
df.to_excel("results.xlsx")


# In[48]:


def t1():
#     r_t1 = [0]*12
	cd = ['scroll','flip','rotate','zoom','switch','move screen','manual contrast','layout','contrast preset','clockwise','two panels','left','right']
	for i in range(0,3):
		print("Round:"+str(i+1))

		j =0
		c='y'
		while j < 13 and c =='y':
			print(str(j+1)+". " + cd[j])
			t = mod_spch()
			nlp_t1(t)

			s = int(input("1-Pass 0-Fail 2-repeat"))
			if s==1:
				r_t1[j]+=1
				j+=1
			elif s==0:
				r_t1[j]+=0
				j+=1

			c = input("Do you want to continue (y/n)?")
			clear_output()


def nlp_t1(a):
	cmds = ['scroll','flip','rotate','zoom','switch','move screen','manual contrast','layout','contrast preset','clockwise','two panels','left','right']
	r=[]
	if a in cmds:
		print("Your Command:")
		print(a)

	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(a,w)
			r.append(ratio)
		m = max(r)

		if m > 59:
			print("Your Command:")
			j = cmds[r.index(m)]
			print(j)

		else:
			print("your command not recognized")



def t2():
#     r_t1 = [0]*12
	cd = ['upside','downside','horizontal','vertical','counterclockwise','inside','outside','increase','decrease','three panels','first','second']
	for i in range(0,3):
		print("Round:"+str(i+1))

		j =0
		c='y'
		while j < 12 and c =='y':
			print(str(j+1)+". " + cd[j])
			t = mod_spch()

			nlp_t2(t)

			s = int(input("1-Pass 0-Fail 2-repeat"))
			if s==1:
				r_t2[j]+=1
				j+=1
			elif s==0:
				r_t2[j]+=0
				j+=1

			# c = input("Do you want to continue (y/n)?")
			clear_output()


def nlp_t2(a):
	cmds = ['upside','downside','horizontal','vertical','counterclockwise','inside','outside','increase','decrease','three panels','first','second']
	r=[]
	if a in cmds:
		print("Your Command:")
		print(a)

	else:
		for w in cmds:
			ratio = fuzz.partial_ratio(a,w)
			r.append(ratio)
		m = max(r)

		if m > 65:
			print("Your Command:")
			j = cmds[r.index(m)]
			print(j)

		else:
			print("your command not recognized")




# In[51]:


r_t1 = [0]*13
t1()


# In[52]:


r_t2 = [0]*12
t2()


# In[53]:


r_t1[:] = [x / 3 for x in r_t1]
r_t2[:] = [x / 3 for x in r_t2]


# In[54]:


r_t1


# In[55]:


results = []
results = r_t1 + r_t2


# In[56]:


df = pd.read_excel('results.xlsx')

c = ['scroll','flip','rotate','zoom','switch','move screen','manual contrast','layout','contrast preset','clockwise','two panels','left','right','upside','downside','horizontal','vertical','counterclockwise','inside','outside','increase','decrease','three panels','first','second']
df2 = pd.DataFrame([results], columns=c)

df = df.append(df2)
df.to_excel("results.xlsx")

