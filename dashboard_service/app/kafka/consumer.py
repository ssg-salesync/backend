from confluent_kafka import Consumer, KafkaException, TopicPartition
import json


def create_consumer():
    consumer = Consumer({
        'bootstrap.servers': 'salesync-kafka-controller-0.salesync-kafka-controller-headless.kafka.svc.cluster.local:9092,salesync-kafka-controller-1.salesync-kafka-controller-headless.kafka.svc.cluster.local:9092,salesync-kafka-controller-2.salesync-kafka-controller-headless.kafka.svc.cluster.local:9092',
        # 'bootstrap.servers': 'localhost:9092',
        # 'security.protocol': 'PLAINTEXT',
        # 'group.id': 'salesync',
        'auto.offset.reset': 'earliest'
    })

    return consumer


def consume_message(topic, req_id, partition=0, offset=0):
    consumer = create_consumer()
    # consumer.subscribe([topic])

    tp = TopicPartition(topic, partition, offset)
    consumer.assign([tp])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                try:
                    msg_dict = json.loads(msg.value().decode('utf-8'))
                    if msg_dict['req_id'] == req_id:
                        response = msg_dict.get('response', '')
                        resp_msg = response.replace('\\', '')
                        return resp_msg
                except json.JSONDecodeError:
                    print(f"Invalid JSON format: {msg.value().decode('utf-8')}")

    finally:
        consumer.close()
