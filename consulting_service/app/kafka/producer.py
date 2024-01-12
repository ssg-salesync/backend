from confluent_kafka import Producer
import json


def create_producer():
    producer = Producer({
        'bootstrap.servers': 'my-kafka.kafka.svc.cluster.local:9092',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'inter_broker_user',
        'sasl.password': 'aqsA1SGNhS'
    })

    return producer


producer = create_producer()


def send_message(topic, message):
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()
