import numpy as np
from fastapi import FastAPI, Form, UploadFile, File
import pandas as pd
from pydantic import BaseModel
from starlette.responses import HTMLResponse 
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import re
import base64
from PIL import Image
import os
import PIL
import glob
from skimage import transform
from PIL import Image as im
from io import BytesIO
import librosa
import librosa.display
import seaborn as sns
import cv2
from sklearn.preprocessing import StandardScaler, OneHotEncoder

app = FastAPI()



def image_pipeline(path): #pipeline for the images
    #using opencv library for face classification
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imageAux = gray.copy()
    faces = faceClassif.detectMultiScale(gray, 1.1, 5)
    count = 0
    for (x,y,w,h) in faces:

        cv2.rectangle(gray, (x,y),(x+w,y+h),(128,0,255),2)
        rostro = imageAux[y:y+h,x:x+w]
        rostro = cv2.resize(rostro,(150,150), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite('face.jpg',rostro)
        count = count + 1
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    #preparing the image for the neural network
    np_image = im.open('face.jpg')
    np_image = np.array(np_image).astype('float32')/255 #preparing the image for the prediction
    np_image = transform.resize(np_image, (48, 48, 1))
    np_image = np.expand_dims(np_image, axis=0)
    return np_image
 


class Image(BaseModel):
    image: str
   
    
    
class Audio(BaseModel):
    audio: str
    
    
@app.post('/predictimage') #prediction on data
def imageCall(img: Image): 
  
    image_decoded = image_pipeline(img.image) #preprocessing of the image
    loaded_model = tf.keras.models.load_model('../codigo_marinaCeballos_TFG/ensemble_image_5_emotions_.h5') #load the saved model
    predictions = loaded_model.predict(image_decoded) #making predictions
    emotion = int(np.argmax(predictions)) #calculate the index of max emotion
    if emotion == 0:  # assigning appropriate name to prediction
        emotion_predicted = 'angry'
    elif emotion == 1:
        emotion_predicted = 'happy'
    elif emotion == 2:
        emotion_predicted = 'sad'
    elif emotion == 3:
        emotion_predicted = 'fear'
    elif emotion == 4:
        emotion_predicted = 'neutral'

    return emotion_predicted #return the emotion into the app 
  
    
   
   
def extract_features(data, sample_rate):
    # ZCR: tasa de cambio de signo de la se?al
    result = np.array([])
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
    result=np.hstack((result, zcr)) # stacking horizontally
    

#     Chroma_stft: a partir de una onda calcula un espectrograma
    stft = np.abs(librosa.stft(data))
    chroma_stft = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
    result = np.hstack((result, chroma_stft)) # stacking horizontally
    

    # MFCC: representan el habla en un espectrograma
    mfcc = np.mean(librosa.feature.mfcc(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mfcc)) # stacking horizontally
    

    # Root Mean Square Value: amplitud media cuadrada
    rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
    result = np.hstack((result, rms)) # stacking horizontally
    
#     print("rms: " + str(rms))

    # MelSpectogram : espectograma
    mel = np.mean(librosa.feature.melspectrogram(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mel)) # stacking horizontally    
    return result
    
    
    
def audio_pipeline(text): #pipeline for the audio
    #decode the audio from basae 64 to wav
    audio_decoded = base64.b64decode(text)
    wav_file = open("temp.wav", "wb")
    wav_file.write(audio_decoded)
    data, sample_rate = librosa.load("temp.wav", duration=2.5, offset=0.6)
    #extract features in order to convert the audio into array for the neural network
    features = extract_features(data, sample_rate)
    x_test  =  np.array(features)
    x_test = np.expand_dims(x_test, axis=0)
    x_test = np.expand_dims(x_test, axis=2)
    return x_test #return the array 
   
@app.post('/predictaudio') #prediction on data
def audioCall(audio: Audio):
    encoder = OneHotEncoder()
    audio_processed = audio_pipeline(audio.audio) #cleaning and preprocessing of the texts
    loaded_model = tf.keras.models.load_model('../codigo_marinaCeballos_TFG/ensemble_audio_5_emotions.h5') #load the saved model
    predictions = loaded_model.predict(audio_processed) #making predictions
    emotion = int(np.argmax(predictions)) #calculate the index of max emotion
    if emotion == 0:  # assigning appropriate name to prediction
        emotion_predicted = 'angry'
    elif emotion == 1:
        emotion_predicted = 'happy'
    elif emotion == 2:
        emotion_predicted = 'sad'
    elif emotion == 3:
        emotion_predicted = 'fear'
    elif emotion == 4:
        emotion_predicted = 'neutral'

    return emotion_predicted #return the emotion into the app
