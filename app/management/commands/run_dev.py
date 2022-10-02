import logging
import os
from urllib.parse import urlparse
from django.core.management import call_command
import requests
from django.core.management import BaseCommand
from pyngrok import ngrok

from sheet_task import settings


logger = logging.getLogger('bot.logger')


def send_webhook(url):
    url += '/telegram_webhook/'
    response = requests.post(
        url=settings.TELEGRAM_API_URL + 'setWebhook',
        json={
            'url': url,
        },
    )
    return response




class Command(BaseCommand):
    help = 'ngrock connect and runserver'

    def handle(self, *args, **options):

        if not os.environ.get('PUBLIC_URL'):
            if settings.DEBUG:
                # create tunnel from somewhere to local server
                https_tunnel = ngrok.connect(
                    addr='8000',
                    bind_tls=True
                )
                public_url = https_tunnel.public_url
                # add new temporary host to allowed hosts
            else:
                public_url = settings.PUBLIC_URL
            os.environ['PUBLIC_URL'] = public_url
            self.stdout.write(self.style.SUCCESS(f'Successfully poll {public_url=}'))
            response = send_webhook(public_url)
            if settings.DEBUG:
                logger.info(f'Telegram setWebhook response {response}')
        settings.ALLOWED_HOSTS.append(urlparse(os.environ['PUBLIC_URL']).netloc)
        call_command('runserver', '8000')