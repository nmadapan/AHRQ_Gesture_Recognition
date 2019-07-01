
# coding: utf-8

# In[2]:


import speech_recognition as sr 


# In[3]:


def spch():
    
    mic_name = "Microphone (Realtek High Defini" #Define your microphone

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
            text = r.recognize_sphinx(audio)
            print("you said: ")
            print(text)
            



        except sr.UnknownValueError: 
            print("Google Speech Recognition could not understand audio") 

        except sr.RequestError as e: 
            print("Could not request results from Google speech Recognition service; {0}".format(e)) 


# In[5]:


spch()


# In[19]:




