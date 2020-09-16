import pika
import uuid
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.keras.models import Sequential

class FibonacciRpcClient(object):

    def size28(self,file):
        
        IMG_SIZE = 28
        img_array = cv2.imread(file,cv2.IMREAD_GRAYSCALE)
        new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        tryimage = new_array.reshape(1,IMG_SIZE,IMG_SIZE)
        print("")
        return bytearray(tryimage)

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=n)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

dbmnist = FibonacciRpcClient().size28("MNIST_EXAMPLE.png")
#print(" [x] Requesting fib(30)")
response = FibonacciRpcClient().call(dbmnist)
print(" [.] Got %r" % response)