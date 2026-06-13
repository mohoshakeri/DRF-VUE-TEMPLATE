import redis
from django.core.management.base import BaseCommand

from project.settings import REDIS_SERVER


class Command(BaseCommand):
    help = "Flush Redis Cache"

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--prefix",
            default=None,
            type=str,
        )

    def handle(self, *args, **options):
        prefix = options["prefix"]

        redis_client = redis.StrictRedis.from_url(REDIS_SERVER)

        if prefix:
            cursor = "0"
            keys_to_delete = []
            while cursor != 0:
                cursor, keys = redis_client.scan(
                    cursor=cursor, match=f"{prefix}*", count=100
                )
                for key in keys:
                    keys_to_delete.append(key)
                if len(keys_to_delete) >= 100:
                    redis_client.delete(*keys_to_delete)
                    keys_to_delete = []
            if keys_to_delete:
                redis_client.delete(*keys_to_delete)
        else:
            redis_client.flushall()

        self.stdout.write(self.style.SUCCESS("Redis Flushed"))
