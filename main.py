import json
import cognitive_face as CF
import sys
from PIL import Image, ImageDraw, ImageFont

#import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
#from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw

SUBSCRIPTION_KEY = os.environ['COGNITIVE_SERVICE_KEY']
BASE_URL = os.environ['FACE_ENDPOINT']
PERSON_GROUP_ID = 'modelo-famosos'
CF.BaseUrl.set(BASE_URL)
CF.Key.set(SUBSCRIPTION_KEY)

#Solo hay que crearlo la primera vez
def crear_grupo(nombre_grupo):
    CF.person_group.create(PERSON_GROUP_ID,nombre_grupo)

def crear_persona(nombre,datos):
    #Crear una persona
    response = CF.person.create(PERSON_GROUP_ID, nombre, datos)
    #En response viene el person_id de la persona que se ha creado
    #Para tener el id de la nueva persona que se creó
    person_id = response['personId']
    #print(person_id)
    print(person_id)
    return person_id

def entrenar_modelo(fotos, id_persona):
    for foto in fotos:
        f = open(foto, 'r+b')
        CF.person.add_face(f, PERSON_GROUP_ID, id_persona)
    CF.person_group.train(PERSON_GROUP_ID)
    response = CF.person_group.get_status(PERSON_GROUP_ID)
    status = response['status']
    print(status)


#crear_grupo("famosos-1")
#julia_imagenes = [file for file in glob.glob('imagenes/*.jpg') if file.startswith("imagenes\julia")]

#id_persona_creada = crear_persona("Julia","Actriz")
#entrenar_modelo(julia_imagenes,"43d107ef-f38a-40d1-96be-1c503accf69e")


def detectar_emociones(foto):
    data = open(foto, 'rb')

    #headers = {'Ocp-Apim-Subscription-Key': KEY} Se puede usar este header cuando usa un url de internet y en lugar de data usa json{url: url(entre comillas)}
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY} #Funciona porque tiene el content  type
    params = {
        'returnFaceAttributes': 'emotion',
    }
    face_api_url = BASE_URL+'detect'
    response = requests.post(face_api_url, params=params,
                            headers=headers, data=data)
    json_detected = response.json()
    
    face_ids = [d['faceId'] for d in json_detected]
    identified_faces = CF.face.identify(face_ids, PERSON_GROUP_ID)
    
    for identified in identified_faces:
        candidates_list = identified['candidates']
        print("Candidates",candidates_list)
        if candidates_list != []:
            candidates = candidates_list[0]
            persona = candidates['personId']
            persona_info = CF.person.get(PERSON_GROUP_ID, persona)
            person_name = persona_info['name']
            
            emociones = {}
            for resp in json_detected:
                if resp['faceId'] == identified['faceId']:
                    faceRectangle = resp['faceRectangle']
                    width = faceRectangle['width']
                    top = faceRectangle['top']
                    height = faceRectangle['height']
                    left = faceRectangle['left']
                    emociones = resp['faceAttributes']['emotion']
                    print("EMOCIONES",emociones)
                    break
            image=Image.open(foto)
            draw = ImageDraw.Draw(image)
            draw.rectangle((left,top,left + width,top+height), outline='red')
            font = ImageFont.truetype('Roboto-Regular.ttf', 20)
            draw.text((0,0), person_name, font=font,  fill="black")
            #emociones = detectar_emociones(foto)
            y = 20
            font_emotion = ImageFont.truetype('Roboto-Regular.ttf', 15)
            for e in emociones:
                if emociones[e] > 0.0:
                    emocion = traducir_sentimiento(e)
                    draw.text((10, y), emocion, font=font_emotion,  fill="black")
                    draw.text((70, y), str(round(emociones[e]*100,2))+"%", font=font_emotion,  fill="black")
                    y += 20
            image.show()
            return
    '''for j in json_detected:
        face_id
        emotions = j['faceAttributes']['emotion']
        return emotions'''


def traducir_sentimiento(emocion):
    switcher = {
        'anger': 'enojo',
        'contempt': 'desprecio',
        'disgust': 'disgusto',
        'fear':'miedo',
        'happiness':'felicidad',
        'neutral' : 'neutral',
        'sadness': 'tristeza',
        'surprise': 'sopresa'
    }
    return switcher.get(emocion,"Invalido")
    
detectar_emociones('imagenes/prueba6.JPG')

        
