import logging
from functools import lru_cache
from kafka import KafkaConsumer, KafkaProducer
from .service_settings import get_settings

service_settings = get_settings()
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_kafka_producer() -> KafkaProducer:
    return KafkaProducer(base_url=service_settings.get_kafka_url())


@lru_cache(maxsize=1)
def get_kafka_consumer(*topics: str, group_id: str) -> KafkaConsumer:
    consumer = KafkaConsumer(
        base_url=service_settings.get_kafka_url(), 
        username=service_settings.KAFKA_USER,
        password=service_settings.KAFKA_AUTH,
        topics=list(topics),
        group_id=group_id
    )
    consumer.rebalance_timeout_ms = 800000
    consumer.max_poll_interval_ms = 800000
    return consumer
