import pika
import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Dense, Dropout, LSTM

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

def on_request(ch, method, props, body):
    model = tf.keras.models.load_model("modelforserver.model")
    lost = list(body)
    lost1 = np.array(lost)
    copied_slice = lost1.astype(np.float32)
    copied_slice = copied_slice/255.0
    
    
    prediction2 = model.predict(copied_slice)
    result = np.argmax(prediction2)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=result)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
