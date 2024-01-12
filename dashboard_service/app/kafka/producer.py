from confluent_kafka import Producer
import json

def create_producer():
    producer = Producer({
        'bootstrap.servers': 'localhost:9092',
        # 'security.protocol': 'SASL_PLAINTEXT',
        # 'sasl.mechanism': 'SCRAM-SHA-256',
        # 'sasl.username': 'admin',
        # 'sasl.password': 'password'
    })

    return producer


producer = create_producer()


def send_message(topic, message):
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()