import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f" [x] Received from RabbitMQ: {message}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='pnb_queue')

channel.basic_consume(
    queue='pnb_queue',
    on_message_callback=callback,
    auto_ack=True
)

print(' [*] Waiting for messages from RabbitMQ. To exit press CTRL+C')
channel.start_consuming()