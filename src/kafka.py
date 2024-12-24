
import logging
from core import constants
from confluent_kafka import Consumer, Producer


logger = logging.getLogger(constants.CONSOLE_LOGGER)


class KafkaConsumer:
    def __init__(self, base_url: str, username: str, password: str, topics: list[str], group_id: str):
        logger.info(f"KafkaConsumer Init {base_url=} {username=} {topics=} {group_id=}")
        config = {
            'bootstrap.servers': base_url,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'partition.assignment.strategy': 'roundrobin',
        }

        if username and password:
            config.update({
                'security.protocol': 'SASL_PLAINTEXT',
                'sasl.mechanisms': 'PLAIN',
                'sasl.username': username,
                'sasl.password': password,
            })

        self.consumer = Consumer(config)
        self.topics = topics

    def start(self):
        self.consumer.subscribe(self.topics)

    def stop(self):
        self.consumer.close()

    def consume(self):
        try:
            while True:
                message = self.consumer.poll(timeout=1.0)
                if message is None:
                    continue

                if message.error():
                    logger.error(f"Kafka error: {message.error()}")
                    continue

                yield message.value().decode('utf-8')

        except KeyboardInterrupt:
            logger.info("Kafka consumer interrupted by user.")
        except Exception as e:
            logger.error(f"Kafka consumer Unexpected error: {e}")
        finally:
            self.stop()


class KafkaProducer:
    # Just for testing purpose
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': 'localhost:9092',
        })

    def delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush()."""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce(self, topic, key, value):
        try:
            self.producer.produce(topic, key=key, value=value, callback=self.delivery_report)
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")

    def flush(self):
        self.producer.flush()
