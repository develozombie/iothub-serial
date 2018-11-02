################################################################################
# Desarrollado por Jose Yapur - joyapu@microsoft.com 
# Para iniciar el proyecto debes conectar tu arduino por serial
# Luego en te ubicas en la carpeta donde esta este script y debes ejecutar:
# pip install azure-iothub-device-client
# lee detalladamente todos los comentarios para su correcto funcionamiento
# luego ejecutas este script: python lee-serial.py
################################################################################
import sys
import serial
import logging
import datetime
import time
import os
import threading
import random
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

# Aca debes copiar la cadena conexión que generamos al crear el dispositivo
# Recuerda que puedes obtenerlo desde el panel de Azure y luego en la opcion IoT Devices
CONNECTION_STRING = "HostName=servicio.azure-devices.net;DeviceId=nombre;SharedAccessKey=codigo"
# PUERTO_ARDUINO debe contener el valor de puerto serial que estas usando para tu Arduino
PUERTO_ARDUINO = '/dev/cu.usbmodem14101'
# BAUDIOS_ARDUINO debe contener los baudios que definiste en la apertura del serial
BAUDIOS_ARDUINO = 115200
# Usaremos el protocolo MQTT
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000

################################################################################
# Aca defines la estructura del mensaje
# Por ejemplo, si tienes un modulo de temperatura y humedad entonces
# El MSG_TXT sera: MSG_TXT = "{\"temperatura\": %s,\"humedad\": %s}"
################################################################################
MSG_TXT = "{\"temperatura\": %s,\"humedad\": %s}"

def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub respondio con el mensaje de status: %s" % (result) )

def iothub_client_init():
    # Crea el cliente de IoT Hub
    client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
    return client

def iothub_client_telemetry_run():
    # Inicia el proceso de caputa de información por serial de Arduino y
    # lo envía al IoT Hub
    try:
        client = iothub_client_init()
        print ( "IoT Hub dispositivo enviando telemetría, presiona Ctrl-C para salir" )
        arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS_ARDUINO, timeout=.1)
        while True:
            t = time.time()
            ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
            # Leemos la informacion recibida por el puerto serial
            raw = arduino.readline()
            # Lo imprimimos en consola
            print("Mensaje {} recibido a las {}".format(raw,ts))
            ###########################################################################
            # En esta seccion configuramos las variables de los valores
            # Que recibimos de Arduino
            temperature = raw
            humidity = raw
            ###########################################################################
            # Estos valores son pasados en el msg_txt_formatted como parametros
            # Estos valores se escribiran en la variable global MSG_TXT que se 
            # definió al inicio
            ###########################################################################    
            msg_txt_formatted = MSG_TXT % (temperature, humidity)
            message = IoTHubMessage(msg_txt_formatted)
            # Enviamos el mensaje y lo imprimimos.
            print( "Sending message: %s" % message.get_string() )
            client.send_event_async(message, send_confirmation_callback, None)

    except IoTHubError as iothub_error:
        print ( "Error inesperado %s de IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient envio detenido" )

if __name__ == '__main__':
    print ( "IoT Hub Bienvenido - Envío de Telemetría" )
    print ( "Presiona Ctrl-C para salir" )
    iothub_client_telemetry_run()                
 
