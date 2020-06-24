import paho.mqtt.client as mqtt
import logging
import time
import os
from brokerData import *
from manejo_topics import *

AUDIO='audio/06'    #CFLN Esta variable se utiliza pasa señalar el topic audio
usuarioss='usuarios/06'     #CFLN Esta variable se utiliza pasa señalar el topic usuarios
salasss='salas/06'  #CFLN Esta variable se utiliza pasa señalar el topic de salas
wavy='/subprocess1.wav'     #CFLN Esta variable se utiliza para señalar el archivo de audio
#EDVC b es utilizado para enviar un comando arecord por medio de la libreria os
b = ['arecord', '-D' , 'plughw:1','-d', '-c1' , '-r' , '44100' , '-f' , 'S32_LE' , '-t' , 'wav' , '-V' , 'mono' , '-v' , 'subprocess1.wav']
insert_at = 4   #EDVC esta variable sirve para insertar en la posicion 4 de la lista b la duracion que tomara arecord
proc_args = b[:]    #EDVC una copia de b para poder insertar el valor
emp=''  #CFLN una variable que no tienen texto para eliminar lineas de los archivos de texto
veces=0
reciv = topic()    #JMOC Objeto que maneja la recepcion de mensajes

direccion=os.path.abspath(os.getcwd()) #EDVC Aqui obtenemos la direccion de donde se encuentra este archivo py corriendo

with open("usuario") as f:  #CFLN Abrimos el archivo usuario
    content = f.readlines()     #CFLN obtenemos su contenido
content = [x.strip() for x in content]      #CFLN eliminamos los espacios vacios


logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )


def on_connect(client, userdata, rc):   #CFLN De esta linea a la 45 declaramos las definiciones basicas para mqtt
    logging.info("Conectado al broker")


def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)


def on_message(client, userdata, msg):
    info = msg.topic.split('/')   #JMOC obtiene la informacion del topic
    #JMOC info[0] = indica si es un audio o un text
    #JMOC info[1] =  indica el subtopic del numero de grupo
    #JMOC info[2] =  indica el nombre del sub topic (sala/usuario)
    if info[0] == "audio":    #JMOC Maneja la recepcion del audio
        logging.info(reciv.rep_audio(info[2], msg.payload))            #Llama al metodo para reproducir audio
    else:                           
        logging.info(reciv.chat(info[0], info[2] ,msg.payload))              #Llama el metodo para mostrar mensaje
    
def publishData(topic, value, qos = 0, retain = False):
    client.publish(topic, value, qos, retain)



print("Bienvenido! " + str(content[0]))     #CFLN Damos la bienvenida al usuario
accep=True #CFLN dejamos que accep sea verdadero si content encontro al usuario y asi poder correr la aplicación
usu=str(content[0]) #CFLN como content es una lista, declaramos una variable usu que sera usada a lo largo del programa

with open("salas") as ff: #EDVC Abrimos el archivo que contiene las salas del usuario
    salas_usuario = ff.readlines() #EDVC leemos las lineas y lo guardamos en una lista
    salas_usuario = [xx.strip() for xx in salas_usuario] #EDVC eliminamos espacios vacios en cada elemento
while emp in salas_usuario: salas_usuario.remove(emp)  #EDVC eliminamos las lineas vacias gracias a la variable emp(linea 16)



client = mqtt.Client(clean_session=True) #CFLN iniciamos la sesion
client.on_connect = on_connect 
client.on_publish = on_publish
client.on_message = on_message
client.username_pw_set(MQTT_USER, MQTT_PASS) #CFLN MQTT_USER, MQTT_PASS sale del archivo BrokerData
client.connect(host=MQTT_HOST, port = MQTT_PORT) #CFLN Al igual que MQTT_HOST, MQTT_PORT


qos = 2

usuario_topics=[(usuarioss+'/'+content[0], qos),(AUDIO+'/'+content[0], qos)]  #EDVC Se inicia con los topics que todos los usuarios tienen en comun

for i in salas_usuario:#EDVC Dependiendo de las salas que tenga el usuario 
    usuario_topics.append((salasss+'/'+str(i), qos)) #EDVC agregamos estas a su lista de topics
    usuario_topics.append((AUDIO+'/'+str(i), qos)) 


client.subscribe(usuario_topics) #EDVC Se suscribe a los topics del usuario

client.loop_start()
while accep: #EDVC Iniciamos el menu
    try:
        while True:
            logging.info("Desea enviar un audio? 1=SI") #EDVC   Mostramos el menu al usuario
            logging.info("Desea enviar un mensaje? 2=SI")
            logging.info("Desea enviar salir? 3=SI")
            respu=int(input())
            if(respu==1):
                if os.path.exists("subprocess1.wav"):
                    os.remove("subprocess1.wav")
                print("Ingrese la duracion del mensaje (no mayor a 30 seg)") #EDVC  Si enviara un audio le pedimos que sea menor a 30 segundos
                dura=int(input())
                if(dura<=30.0): #EDVC si la duracion es menor permitimos que grabe
                    if(veces>0):
                        proc_args.pop(4)
                    veces=veces+1
                    proc_args[insert_at:insert_at] = [str(dura)] #EDVC agregamos a proc_args(linea 15) la duracion que ingreso el usuario en su posicion insert_at(linea 14)
                    os.popen(" ".join(proc_args)).readlines() #EDVC por medio de OS ejecutamos pro_args
                                
                    logging.info("\n Este audio es para una sala o alguien? 1=Sala 2=Alguien") #EDVC Una vez grabado el audio le pedimos al usuario que indique a quien es
                    elec=int(input())
                    if(elec==1):
                        logging.info("Estas son sus salas:")
                        logging.info(str(salas_usuario))
                        logging.info("Escriba la sala receptora ej(06S01):") #EDVC Si eligio una sala le pedimos que indique cual es
                        sal=str(input())
                        f = open('subprocess1.wav', 'rb') #EDVC abrimos el archivo de audio creado anteriormente
                        publishData(AUDIO+'/'+sal,f.read()) #EDVC publicamos el audio al topic AUDIO +  la sala destinatoria
                        f.close() #EDVC cerramos el archivo de audio
                        logging.info("Esperando que el servidor autorize que se envie el audio...") #EDVC le indicamos al usuario que el servidor esta enviando su audio
                    elif(elec==2):
                        logging.info("Escriba el carnet receptor:") #EDVC Si eligio un carnet le pedimos que indique cual es
                        cardes=str(input())
                        f = open('subprocess1.wav', 'rb')
                        publishData(AUDIO+'/'+cardes,f.read()) #EDVC publicamos el audio al topic AUDIO +  el carnet destinatorio
                        f.close()
                        logging.info("Esperando que el servidor autorize que se envie el audio...")


                else:
                    logging.info("No es posible enviar mas de 30seg!") #EDVC si el usuario ingreso una duracion mayor a 30seg le decimos que no es posible hacer el envio
                
            elif(respu==2):
                logging.info("El mensaje es para una sala o alguien? 1=alguien 2=Sala") #EDVC Si el usuario quiere enviar un mensaje le indicamos si es para alguien o un sala
                res=int(input())
                if(res==1):
                    logging.info("Escriba el carnet del receptor:") #EDVC Si eligio un carnet le pedimos que indique cual es
                    carn=int(input())
                    logging.info("Escriba su mensaje: ") #EDVC luego le pedimos que ingrese el mensaje
                    men=str(input())
                    publishData(usuarioss+'/'+str(carn),men) #EDVC Publicamos en el topic usuarioss(linea 9) + el carnet ingresado
                elif(res==2):
                    logging.info("Estas son sus salas:") #EDVC Si eligio una sala le pedimos que indique cual es
                    logging.info(str(salas_usuario))
                    logging.info("Escriba la sala receptora ej(06S01):")
                    salaa=str(input())
                    if salaa in salas_usuario: #EDVC Si el usuario pertenece a la sala que ingrese permitimos que escriba el mensaje
                        logging.info("Escriba su mensaje: ")
                        men=str(input())
                        publishData(salasss+'/'+str(salaa),men) #EDVC Hacemos el publish a la sala indicada
                    else:
                        logging.info("Usted no esta suscrito a esta sala!") #EDVC Si no esta suscrito le indicamos al usuario
            elif(respu==3):
                break #EDVC Si el usuario indico que quiere salir hacemos break del while loop
           

    except KeyboardInterrupt:
        logging.warning("Desconectando del broker...") #EDVC Si ocurre un error desconectamos al usuario del servidor

    finally:
        client.loop_stop()  #EDVC cuando el usuario sale del while loop paramos el thread del cliente
        client.disconnect() #EDVC lo desconetamos
        logging.info("Desconectado del broker. Saliendo...") #EDVC y le indicamos que salio
        break #EDVC finalmente salimos del while accep