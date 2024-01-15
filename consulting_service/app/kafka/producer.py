from confluent_kafka import Producer
import json


def create_producer():
    producer = Producer({
        # 'bootstrap.servers': 'salesync-kafka.kafka.svc.cluster.local:9092',
        'bootstrap.servers': 'localhost:9092',
        'security.protocol': 'PLAINTEXT'
        # 'sasl.mechanism': 'SCRAM-SHA-256',
        # 'sasl.username': 'user1',
        # 'sasl.password': 'aAlsxk8ihq'
    })

    return producer


producer = create_producer()


def send_message(topic, message):
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()
