from confluent_kafka import Producer
import json

def create_producer():
    producer = Producer({
        'bootstrap.servers': 'kafka.kafka.svc.cluster.local:9092',
        'security.protocol': 'PLAINTEXT'
    })

    return producer


producer = create_producer()


def send_message(topic, message):
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()