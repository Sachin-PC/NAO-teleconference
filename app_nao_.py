
#!/usr/bin/env python
# coding: utf-8

# In[90]:

from naoqi import ALProxy
import speech_recognition as sr
import time
import os
import paramiko
import Tkinter 
import argparse
from playsound import playsound
import wave
import pyaudio


def setParameter(tts, speech_speed, pitch):
	tts.setParameter("speed", speech_speed)
	tts.setParameter("pitchShift", pitch)



def saySomething(tts, sentence):
	tts.say(sentence)


#def speech2text2speech(tts):


def recognize_speech_from_mic(recognizer, microphone):
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    print("Start Speaking")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print(type(audio))
	# set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }
    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,update the response object accordingly
    try:
    	print("HI")
    	print(type(audio))
    	response["transcription"] = recognizer.recognize_google(audio)
        #response["transcription"] = recognizer.recognize_google(audio)
        #response["transcription"]= response["transcription"].encode("ascii")
        print(response["transcription"])   
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"
    return response


def startRecording(record):
	print('start recording...')
	record_path = '/home/nao/record.wav'
	record.startMicrophonesRecording(record_path, 'wav', 16000, (0,0,1,0))
	time.sleep(5)
	record.stopMicrophonesRecording()
	print 'record over'

def event_of_streaming():
	ssh = paramiko.SSHClient() 
	ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
	ssh.connect("10.42.0.18", username="nao", password="Naonao123*")
	command = "gst-launch-0.10 pulsesrc ! audioconvert ! vorbisenc ! oggmux ! tcpserversink port=5678"
	ssh.exec_command(command)
	os.system("vlc tcp://10.42.0.18:5678/")
	time.sleep(10)
	ssh.send('\x03')
	ssh.close()


def mode1():
	setParameter(tts, 100, 1)
	saySomething(tts, "HI! I'm connected")

def mode2():
	global recognizer, microphone
	response = recognize_speech_from_mic(recognizer,microphone)
	setParameter(tts, 90, 1)
	if(response["transcription"] != None):
		saySomething(tts, str(response["transcription"]))
	else:
		saySomething(tts, str(response["error"]))

def mode3():
	saySomething(tts, "Do you have any questions?")
	startRecording(record)
	ssh = paramiko.SSHClient() 
	ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
	ssh.connect("10.42.0.18", username="nao", password="Naonao123*")
	sftp = ssh.open_sftp()
	sftp.get('/home/nao/record.wav', '/home/seekr/Desktop/NAO/recordTest.wav')
	sftp.close()
	ssh.close()
	playsound('/home/seekr/Desktop/NAO/recordTest.wav')

def mode4():
	saySomething(tts, "I'm connecting you to Gods")
	event_of_streaming()

def mode5():
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 10
	WAVE_OUTPUT_FILENAME = "voice_human.wav"
	audio = pyaudio.PyAudio()
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
	                rate=RATE, input=True,
	                frames_per_buffer=CHUNK)
	print("recording...")
	frames = []
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    frames.append(data)
	print("finished recording")
	# stop Recording
	stream.stop_stream()
	stream.close()
	audio.terminate()
	 
	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()

	ssh = paramiko.SSHClient() 
	ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
	ssh.connect("10.42.0.18", username="nao", password="Naonao123*")
	sftp = ssh.open_sftp()
	sftp.put('/home/seekr/Desktop/NAO/all_functions/voice_human.wav', '/home/nao/voice.wav')
	sftp.close()
	ssh.close()

	record_path = '/home/nao/voice.wav'
	saySomething(tts, "now next voice is of human!")
	startRecording(record)
	# ----------> playing the recorded file <----------
	fileID = aup.playFile(record_path, 0.7, 0)

def button_call():
	return

def main(robot_IP, robot_PORT=9559, robot_mode=0):
	global tts, audio, record, aup, recognizer, microphone 
	# ----------> Connect to robot <----------
	tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
	audio = ALProxy("ALAudioDevice", robot_IP, robot_PORT)
	record = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)
	aup = ALProxy("ALAudioPlayer", robot_IP, robot_PORT)
	recognizer = sr.Recognizer()
	microphone = sr.Microphone()
	root = Tkinter.Tk()
	root.title("Speak_NAO")
	label = Tkinter.Label(root, fg="dark green")
	label.config(text= "press the button to see the magic!")
	label.pack()

	btn1 = Tkinter.Button(root, text="NAO say!", width=20, command=button_call)
	btn2 = Tkinter.Button(root, text="say something!", width=20, command=button_call)
	btn3 = Tkinter.Button(root, text="walkie-talkie!", width=20, command=button_call)
	btn4 = Tkinter.Button(root, text="voice streaming!", width=20, command=button_call)
	btn5 = Tkinter.Button(root, text="human voice!", width=20, command=button_call)

	btn1.pack()
	btn2.pack()
	btn3.pack()
	btn4.pack()
	btn5.pack()

	toggle_btn1 = Tkinter.Button(root, text="quit!", fg = "red", width=20, command= root.destroy)
	toggle_btn1.pack()
	root.mainloop()			
	


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.42.0.18",
                        help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("--mode", type=int, default=0,help="Mode of Robot")
    args = parser.parse_args()
    main(args.ip, args.port, args.mode)























