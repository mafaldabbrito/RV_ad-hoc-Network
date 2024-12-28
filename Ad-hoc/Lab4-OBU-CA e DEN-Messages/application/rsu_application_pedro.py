#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
# Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from socket import MsgFlag
import time, threading
import queue
from application.message_handler import *
import application.app_config as app_conf
import application.app_config_rsu as app_rsu_conf
from application.rsu_commands import *
import ITS_maps as maps
import requests

den_txd = threading.Condition()
web_app_message = threading.Event()
response_timers = {} # Dictionary to store the timers for each message

URL = 'http://127.0.0.1:5000/get_command'

RSU_ID = 1

def in_comm_thread(url: str, in_queue: Queue, starting_flag):
    last_command = None
    while running_flag.is_set():
        try:
            response = requests.get(url)
            response.raise_for_status()
            message = response.json()
            
            if message.get('command') != last_command:
                last_command = message.get('command')
                print(f"Incoming data: {message}")
                in_queue.put(message)
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        time.sleep(5)

def processing_thread(in_queue: Queue, out_queue: Queue, starting_flag):
    while running_flag.is_set():
        try:
            if not in_queue.empty():
                data = in_queue.get()
                
                # Simple direct payload transformation
                parking = False
                outgoing_payload = {
                    'rsu_id': str(RSU_ID),
                    'parking': parking
                }
                
                out_queue.put(outgoing_payload)
            time.sleep(0.1)
        except Exception as e:
            print(f"Processing error: {e}")
            print(f"Error data: {data}")

def out_comm_thread(url: str, out_queue: Queue, starting_flag):
    while running_flag.is_set():
        try:
            if not out_queue.empty():
                payload = out_queue.get()
                print(f"Outgoing data to {url}: {payload}")
                response = requests.post(url, json=payload)
                print(f"Website communication status: {response.status_code}")
            time.sleep(1)
        except Exception as e:
            print(f"Website communication error: {e}")

# For testing purposes, the following variables are used to simulate the message read from the Web app


#-----------------------------------------------------------------------------------------
# Thread: rsu application transmission. In this example user triggers CA and DEN messages. 
#   to be completed, in case RSU sends messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#        ca_service_txd_queue to send CA messages
#        den_service_txd_queue to send DEN messages
#-----------------------------------------------------------------------------------------
def rsu_application_txd(rsu_interface, start_flag,  my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, event_specifics ,spat_service_txd_queue, ivim_service_txd_queue):

     while not start_flag.isSet():
          time.sleep (1)
     if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     while True:
          web_app_message.wait()  # Wait for the event to be set
          web_app_message.clear()  # Clear the event after it is set
          event_type = event_specifics['type']  # Get the event type from the shared variable
          destination = event_specifics['destination']  # Get the destination from the shared variable
          den_event = trigger_event(map.rsu_node, event_type, destination) 
          den_service_txd_queue.put(den_event)
          print ('Sending message of type: ', app_rsu_conf.event_type[event_type])
          if (app_conf.debug_app_den):
               print ('rsu_application_txd - den messsage sent ', den_event)

          # Start a timer for 10 seconds
          event_id = destination
          timer = threading.Timer(10.0, check_response, [event_id])
          response_timers[event_id] = timer
          timer.start()

def check_response(event_id):
     if event_id in response_timers:
          print(f'ERROR: No response received for event {event_id} within 10 seconds')
          del response_timers[event_id]


#-----------------------------------------------------------------------------------------
# Thread: rsu application reception. In this example it does not send ot receive messages
#   to be completed, in case RSU receives messages
#   use: services_rxd_queue to receive messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#-----------------------------------------------------------------------------------------
def rsu_application_rxd(rsu_interface, start_flag, services_rxd_queue, my_system_rxd_queue):
     
     while not start_flag.isSet():
          time.sleep (1)
     if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     
     while True :
          msg_rxd = services_rxd_queue.get()
          response_received = True
          if (msg_rxd['msg_type']=="DEN") and (rsu_interface['node_id'] != msg_rxd['node']):
               if (app_conf.debug_app_den):
                    print ('\n....>rsu_application_rxd - den messsage received ',msg_rxd)
               if (msg_rxd['event']['event_type'] == 'successful'):
                    print('Sucess now i can send a message to the web app')
               
               # Mark the response as received and cancel the timer
               event_id = msg_rxd['event']['destination']
               if event_id in response_timers:
                    response_timers[event_id].cancel()
                    del response_timers[event_id]   
     
             	
             	


#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def rsu_system(rsu_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue):
    
     while not start_flag.isSet():
         time.sleep (1)
     if (app_conf.debug_sys):
         print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     
     
     
def handle_get_request(start_flag, event_specifics):
     last_command = None
     while not start_flag.isSet():
          time.sleep(1)
     
     while True:
          try:
               response = requests.get(URL)
               response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
               message = response.json()
               if message['command'] != last_command:
                    last_command = message['command']
                    if message['command'] == 'lock':
                         event_specifics['type'] = 1  # Locking event
                         web_app_message.set()  # Trigger the event
                    elif message['command'] == 'unlock':
                         event_specifics['type'] = 2  # Unlocking event
                         web_app_message.set()  # Trigger the event
                    event_specifics['destination'] = message['destination']
          except requests.exceptions.RequestException as e:
               print(f"Request failed: {e}")
          time.sleep(5)  # Polling interval
