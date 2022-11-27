import time

import pika
import random
import orjson
import os


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            os.environ['AMQP_HOST'],
            credentials=pika.credentials.PlainCredentials(
                os.environ['AMQP_USER'], os.environ['AMQP_PASS']
            )
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='messages')
    print(f"✨ Starting message spamming")

    while True:
        try:
            body = orjson.dumps({'type': random.choice((1, 2)), 'number': random.randint(0, 100)})
            print(f"📩 Sending {body}")
            channel.basic_publish(
                exchange='',
                routing_key='messages',
                body=body
            )
            time.sleep(1)
        except KeyboardInterrupt:
            break

    print("🤚 Closing connection.")
    connection.close()


if __name__ == '__main__':
    main()
