import pika
from kafka import KafkaProducer
import json

# 1. Konfigurasi & Kirim ke RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='pnb_queue')

message = {"sensor_id": "A1", "temperature": 30.5, "status": "active"}
channel.basic_publish(
    exchange='',
    routing_key='pnb_queue',
    body=json.dumps(message)
)
print(" [x] Sent to RabbitMQ:", message)
connection.close()

# 2. Konfigurasi & Kirim ke Apache Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
producer.send('pnb_topic', value=message)
producer.flush()
print(" [x] Sent to Kafka:", message)