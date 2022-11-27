import orjson
import pika
import psycopg2
from psycopg2 import extensions, sql
import os


def main():
    db_connection: extensions.connection = psycopg2.connect(
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASS'],
        host=os.environ['POSTGRES_HOST']
    )
    cursor: extensions.cursor = db_connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS messages_type1 (id SERIAL PRIMARY KEY, data INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages_type2 (id SERIAL PRIMARY KEY, data INTEGER)")

    amqp_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            os.environ['AMQP_HOST'],
            credentials=pika.credentials.PlainCredentials(
                os.environ['AMQP_USER'], os.environ['AMQP_PASS']
            )
        )
    )
    channel = amqp_connection.channel()
    channel.queue_declare(queue='messages')
    print(f"✨ Starting message reading")

    def callback(ch, method, properties, body: bytes):
        print(f"📥 Received {body}")
        message: dict = orjson.loads(body)
        if "type" not in message.keys() or "number" not in message.keys():
            print(f"⚠ Invalid message. Skipping.")
            return

        table = f"messages_type{message['type']}"
        cursor.execute(
            sql.SQL("INSERT INTO {table} VALUES (%s) ON CONFLICT DO NOTHING").format(
                table=sql.Identifier(table)
            ),
            (message["number"],)
        )

    channel.basic_consume(queue='messages', on_message_callback=callback, auto_ack=True)

    print('ℹ Waiting for messages')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('🤚 Stopping the consumer.')
        amqp_connection.close()


if __name__ == '__main__':
    main()
