from confluent_kafka import Consumer, KafkaException
import json


def create_consumer():
    consumer = Consumer({
        'bootstrap.servers': 'salesync-kafka-pro-controller-0.salesync-kafka-pro-controller-headless.kafka.svc.cluster.local:9092,salesync-kafka-pro-controller-1.salesync-kafka-pro-controller-headless.kafka.svc.cluster.local:9092,salesync-kafka-pro-controller-2.salesync-kafka-pro-controller-headless.kafka.svc.cluster.local:9092',
        # 'bootstrap.servers': 'localhost:9092',
        # 'security.protocol': 'PLAINTEXT',
        'group.id': 'salesync',
        'auto.offset.reset': 'earliest'
    })

    return consumer


def consume_message(topic):
    consumer = create_consumer()
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                print(f"Received message: {msg.value().decode('utf-8')}")
                return json.loads(f"Received message: {msg.value().decode('utf-8')}")
    finally:
        consumer.close()