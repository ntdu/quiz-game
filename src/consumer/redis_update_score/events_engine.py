
import json
import logging
from core import constants
from src.dj_project.kafka import get_kafka_consumer
from src.callback_func.noti_consumer_v3 import handle_send_noti_event
from src.apps.notification.decorators import retry_on_exception

logger = logging.getLogger(constants.CONSOLE_LOGGER)


RETRY_TOPIC = "jobs-retry"


class EventsEngine:
    def __init__(self, topic: str):
        # self.consumer = get_kafka_consumer(topic, RETRY_TOPIC) # Add retry topic later
        self.consumer = get_kafka_consumer(topic)
        self.producer = None

        self.running = False
        self.event_handlers = {
            "send_noti": handle_send_noti_event,
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
        event_type = 'send_noti'  # we have only one event type for now

        handler = self.event_handlers.get(event_type)
        if not handler:
            logger.error(f"Error No handler for event type: {event_type}")
            return

        handler(event_dict)

    def health_check(self) -> bool:
        return self.running
