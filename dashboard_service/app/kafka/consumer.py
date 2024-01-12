from confluent_kafka import Consumer, KafkaException
import json


def create_consumer():
    consumer = Consumer({
        'bootstrap.servers': 'my-kafka.kafka.svc.cluster.local:9092',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanåism': 'SCRAM-SHA-256',
        'sasl.username': 'admin',
        'sasl.password': 'password',
        'group.id': 'salesync',
        'auto.offset.reset': 'earliest'
    })

    return consumer


def consume_message(topic, req_id):
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
                # print(f"Received message: {msg.value().decode('utf-8')}")
                msg_value = msg.value().decode('utf-8')
                msg_dict = json.loads(msg_value)
                if msg_dict['req_id'] == req_id:
                    return msg.value().decode('utf-8')
    finally:
        consumer.close()
