
import json
import time
import logging
from media_service.kafka_settings import get_kafka_consumer

from kafka import get_kafka_consumer
from .handle_event import update_user_anwser
from src.decorators import retry_on_exception

logger = logging.getLogger(__name__)


RETRY_TOPIC = "jobs-retry"


class EventsEngine:
    def __init__(self, topic: str):
        # self.consumer = get_kafka_consumer(topic, RETRY_TOPIC) # Add retry topic later
        self.consumer = get_kafka_consumer(topic)
        self.producer = None
        batch = []
        last_poll_time = time.time()
        MAX_BATCH_SIZE = 10

        self.running = False
        self.event_handlers = {
            "update_user_anwser": update_user_anwser,
        }

    def start(self):
        logger.info("Starting Events Engine...")
        self.consumer.start()
        self.running = True

        logger.info("Started Events Engine Successfully")

    def stop(self):
        logger.info("Stopping Events Engine...")
        self.running = False
        self.consumer.stop()

        logger.info("Stopped Events Engine Successfully")

    def consume(self):
        try:
            for message in self.consumer.consume():
                if not self.running:
                    break

                self.process_event(message)

        except KeyboardInterrupt:
            logger.info("Events engine interrupted by user.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.stop()

    @retry_on_exception(max_retries=3)
    def process_event(self, message):
        event_dict = json.loads(message)
        logger.info(f"Received message: {event_dict}")

        # Process the event
        event_type = 'update_user_anwser'  # we have only one event type for now

        handler = self.event_handlers.get(event_type)
        if not handler:
            logger.error(f"Error No handler for event type: {event_type}")
            return

        handler(event_dict)

    def health_check(self) -> bool:
        return self.running

    @retry_on_exception(max_retries=3)
    def process_batch(self, batch):
        if batch:
            print(f"Processing batch of {len(batch)} messages...")
            for msg in batch:
                try:
                    # Process your message here
                    print(f"  Key: {msg.key()}, Value: {msg.value().decode('utf-8')}")
                except Exception as e:
                    print(f"Error processing message: {e}")
                # Handle exception (e.g., log, retry, move to DLQ)

            # Commit the offsets after processing the batch
            self.consumer.commit(asynchronous=False)

    batch = []
    last_poll_time = time.time()
    MAX_BATCH_SIZE = 10 # Maximum size of batch. Can be configured according to needs.

    try:
        while True:
            msg = consumer.poll(1.0) # Poll every second
            if msg is None:
                 # No message, check if we need to process existing batch
                 if (time.time() - last_poll_time >= 0.5 and len(batch) > 0):
                     process_batch(batch)
                     batch = []
                     last_poll_time = time.time()
                 continue
            elif msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                     print('%% %s [%d] reached end at offset %d\n' %
                           (msg.topic(), msg.partition(), msg.offset()))
                else:
                    print(f"ERROR: {msg.error()}")
                continue

            batch.append(msg)

            if len(batch) >= MAX_BATCH_SIZE or time.time() - last_poll_time >= 0.5 :
                 process_batch(batch)
                 batch = []
                 last_poll_time = time.time()
    except KeyboardInterrupt:
        pass
    finally:
         consumer.close()
