import asyncio
import logging

from aiokafka import AIOKafkaProducer

from src.application.services.outbox_relay import OutboxRelay
from src.infrastructure.messaging.kafka_broker import KafkaMessageBroker, serialize
from src.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
)
from src.infrastructure.persistence.uow import SQLAlchemyUnitOfWork
from src.logging_setup import setup_logging
from src.settings import Settings

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level)
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    logger.info("starting outbox relay")

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=serialize,
    )
    await producer.start()

    broker = KafkaMessageBroker(
        producer=producer,
        topic=settings.kafka_topic_ads,
    )
    relay = OutboxRelay(
        uow_factory=lambda: SQLAlchemyUnitOfWork(session_factory),
        broker=broker,
    )

    try:
        await relay.run()
    finally:
        await producer.stop()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
