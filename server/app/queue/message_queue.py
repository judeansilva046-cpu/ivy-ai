"""
Message Queue System for Task Management
RabbitMQ integration for distributed task processing
"""
import json
import asyncio
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, asdict
from datetime import datetime
import aio_pika
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class QueueMessage:
    """Queue message structure"""
    id: str
    type: str
    priority: int = 5  # 1-10, higher = more urgent
    payload: Dict[str, Any] = None
    created_at: str = None
    retry_count: int = 0
    max_retries: int = 3
    dead_letter: bool = False

    def to_json(self) -> str:
        """Convert to JSON"""
        data = asdict(self)
        data['created_at'] = self.created_at or datetime.utcnow().isoformat()
        return json.dumps(data)

    @staticmethod
    def from_json(json_str: str) -> 'QueueMessage':
        """Create from JSON"""
        data = json.loads(json_str)
        return QueueMessage(**data)


@dataclass
class TaskMessage(QueueMessage):
    """Task message for agent/tool execution"""
    agent_id: str = None
    tool_id: str = None
    user_id: str = None
    parameters: Dict = None
    timeout: int = 30


@dataclass
class ChatMessage(QueueMessage):
    """Chat message for processing"""
    conversation_id: str = None
    user_id: str = None
    content: str = None
    agent_id: str = None


class MessageQueue:
    """RabbitMQ message queue"""

    def __init__(self, url: str = "amqp://guest:guest@localhost/"):
        self.url = url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchanges: Dict = {}
        self.queues: Dict = {}
        self.handlers: Dict[str, Callable] = {}

    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

    async def declare_queue(self, name: str, durable: bool = True):
        """Declare a queue"""
        queue = await self.channel.declare_queue(
            name,
            durable=durable,
            auto_delete=False
        )
        self.queues[name] = queue
        logger.info(f"Queue declared: {name}")
        return queue

    async def declare_exchange(
        self,
        name: str,
        exchange_type: str = "topic",
        durable: bool = True
    ):
        """Declare an exchange"""
        exchange = await self.channel.declare_exchange(
            name,
            aio_pika.ExchangeType.TOPIC,
            durable=durable
        )
        self.exchanges[name] = exchange
        logger.info(f"Exchange declared: {name}")
        return exchange

    async def publish(
        self,
        queue_name: str,
        message: QueueMessage,
        exchange_name: str = None,
        routing_key: str = None
    ):
        """Publish message to queue"""
        try:
            msg_body = message.to_json().encode()
            msg = aio_pika.Message(
                body=msg_body,
                content_type="application/json",
                priority=message.priority
            )

            if exchange_name and routing_key:
                exchange = self.exchanges.get(exchange_name)
                if exchange:
                    await exchange.publish(msg, routing_key=routing_key)
            else:
                queue = self.queues.get(queue_name)
                if queue:
                    await queue.put(msg)

            logger.info(f"Message published to {queue_name}: {message.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish: {e}")
            return False

    async def consume(
        self,
        queue_name: str,
        handler: Callable,
        auto_ack: bool = True
    ):
        """Consume messages from queue"""
        try:
            queue = self.queues.get(queue_name)
            if not queue:
                logger.error(f"Queue not found: {queue_name}")
                return

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        msg_data = QueueMessage.from_json(message.body.decode())
                        await handler(msg_data)

                        if auto_ack:
                            await message.ack()

                    except Exception as e:
                        logger.error(f"Handler error: {e}")
                        if not auto_ack:
                            await message.nack(requeue=True)

        except Exception as e:
            logger.error(f"Consumer error: {e}")

    async def publish_task(
        self,
        task_id: str,
        agent_id: str,
        parameters: Dict,
        priority: int = 5
    ):
        """Publish task for execution"""
        message = TaskMessage(
            id=task_id,
            type="task_execution",
            agent_id=agent_id,
            parameters=parameters,
            priority=priority,
            created_at=datetime.utcnow().isoformat()
        )

        return await self.publish("tasks", message)

    async def publish_chat(
        self,
        message_id: str,
        conversation_id: str,
        user_id: str,
        content: str,
        agent_id: str = None
    ):
        """Publish chat message"""
        message = ChatMessage(
            id=message_id,
            type="chat_message",
            conversation_id=conversation_id,
            user_id=user_id,
            content=content,
            agent_id=agent_id,
            created_at=datetime.utcnow().isoformat()
        )

        return await self.publish("chats", message)

    async def register_handler(
        self,
        message_type: str,
        handler: Callable
    ):
        """Register message handler"""
        self.handlers[message_type] = handler
        logger.info(f"Handler registered: {message_type}")


# Singleton instance
_message_queue = None


async def get_message_queue() -> MessageQueue:
    """Get message queue singleton"""
    global _message_queue
    if _message_queue is None:
        _message_queue = MessageQueue()
        await _message_queue.connect()
    return _message_queue


async def initialize_queues():
    """Initialize all queues"""
    queue = await get_message_queue()

    # Declare queues
    await queue.declare_queue("tasks", durable=True)
    await queue.declare_queue("chats", durable=True)
    await queue.declare_queue("notifications", durable=True)
    await queue.declare_queue("analytics", durable=True)

    # Declare exchanges
    await queue.declare_exchange("events", "topic")
    await queue.declare_exchange("tasks", "topic")

    logger.info("Message queues initialized")
