import threading
import requests
import time
from queue import Queue
import ITS_options as config
#import keyboard

class InCommThread(threading.Thread):
    def __init__(self, url: str, in_queue: Queue):
        super().__init__()
        self.url = url
        self.queue = in_queue
        self.running = True
        self.last_command = None

    def run(self):
        while self.running:
            try:
                response = requests.get(self.url)
                response.raise_for_status()
                message = response.json()
                
                if message.get('command') != self.last_command:
                    self.last_command = message.get('command')
                    
                    print(f"Incoming data: {message}")
                    self.queue.put(message) # Insert into queue
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
            
            time.sleep(5)  # Poll every 5 seconds

    def stop(self):
        self.running = False

class ProcessingThread(threading.Thread):
    def __init__(self, in_queue: Queue, out_queue: Queue):
        super().__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                if not self.in_queue.empty():
                    data = self.in_queue.get() # Read from queue
                    
                    #print(f"Processing data: {data}")

                    # TO DO: Implement payload processing logic
                    # Simple direct payload transformation
                    parking = False
                    outgoing_payload = {
                        'rsu_id': config.RSU_ID,
                        'parking': parking
                    }
                    
                    #print(f"Processed payload: {outgoing_payload}")
                    
                    self.out_queue.put(outgoing_payload) # Insert into queue
                time.sleep(0.1)
            except Exception as e:
                print(f"Processing error: {e}")
                print(f"Error data: {data}")  # Added for debugging

    def stop(self):
        self.running = False

class OutCommThread(threading.Thread):
    def __init__(self, url: str, out_queue: Queue):
        super().__init__()
        self.url = url
        self.queue = out_queue 
        self.running = True

    def run(self):
        while self.running:
            try:
                if not self.queue.empty():
                    payload = self.queue.get()  # Read from queue
                    print(f"Outgoing data to {self.url}: {payload}")
                    response = requests.post(self.url, json=payload)
                    print(f"Website communication status: {response.status_code}")
                time.sleep(1)
            except Exception as e:
                print(f"Website communication error: {e}")

    def stop(self):
        self.running = False

# def main():
    # Create two queues for the processing pipeline
    # in_queue = Queue()
    # out_queue = Queue()

    # Initialize threads
    # in_comm = InCommThread("http://193.236.214.159:8080/get_command", in_queue)
    # processing = ProcessingThread(in_queue, out_queue)
    # out_comm = OutCommThread("http://193.236.214.159:8080/post_command", out_queue)

    # Start threads
    # in_comm.start()
    # processing.start()
    # out_comm.start()

    # print("--- PRESS 'e' TO EXIT ---")
    
    # while True:
    #     if keyboard.is_pressed('e'):
    #         print("Shutting down threads...")
    #         in_comm.stop()
    #         processing.stop()
    #         out_comm.stop()

    #         in_comm.join()
    #         processing.join()
    #         out_comm.join()

    #         print("Threads shut down. Exiting...")
    #         break
    #     time.sleep(0.1)  # Small sleep to prevent high CPU usage

if __name__ == "__main__":
    main()
