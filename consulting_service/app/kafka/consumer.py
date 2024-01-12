from confluent_kafka import Consumer, KafkaException
import json


def create_consumer():
    consumer = Consumer({
        'bootstrap.servers': 'my-kafka.kafka.svc.cluster.local:9092',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'inter_broker_user',
        'sasl.password': 'aqsA1SGNhS',
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