from confluent_kafka import Producer
import json

def create_producer():
    producer = Producer({
        'bootstrap.servers': 'salesync-kafka-controller-0.salesync-kafka-controller-headless.kafka.svc.cluster.local:9092,salesync-kafka-controller-1.salesync-kafka-controller-headless.kafka.svc.cluster.local:9092,salesync-kafka-controller-2.salesync-kafka-controller-headless.kafka.svc.cluster.local:9092',
        # 'bootstrap.servers': 'localhost:9092',
        'security.protocol': 'PLAINTEXT'
    })

    return producer


producer = create_producer()


def send_message(topic, message):
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()