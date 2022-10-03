import logging
import os

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from app import tasks, serializers

from sheet_task import settings
# Create your views here.
from app.models import DataBase

logger = logging.getLogger('view.logger')


class TelegramViews(APIView):

    def post(self, request):
        logger.info(f'Successfully request {request.data=}')
        return Response(status=status.HTTP_200_OK)




class StartViews(APIView):
    def post(self, request):
        logger.info(f'Successfully request StartViews {request.data=}')
        tasks.write_sheets.apply_async(kwargs={'sheets': settings.SHEETS, 'vers': settings.VERS,
                                                         'scopes': settings.SCOPES,
                                                         'file_credentials': settings.FILE_CREDENTIALS,
                                                         'sheets_id': settings.SPREADSHEET_ID,
                                                         'range_row': settings.SETTING_RANGE_WRITE_HOOK,
                                                         'values': os.environ['VALUES_HOOK_SHEET'],
                                                         })


        tasks.read_and_google_sheets.apply_async(kwargs={'sheets': settings.SHEETS, 'vers': settings.VERS,
                                                               'scopes': settings.SCOPES,
                                                               'file_credentials': settings.FILE_CREDENTIALS,
                                                               'sheets_id': settings.SPREADSHEET_ID,
                                                               'range_row': settings.SETTINGS_RANGE,
                                                               })

        tasks.request_api_cbr.apply_async(kwargs={'currency_id': settings.CURRENCY_ID,
                                                       'url_pattern': settings.URL_PATTERN_CBR})
        return Response(status=status.HTTP_200_OK)



class AdSheetBaseViews(APIView):
    def post(self, request):
        logger.info(f'Successfully request AdSheetBaseViews {request.data=}')
        return Response(status=status.HTTP_200_OK)


class CreateBaseViews(APIView):
    def post(self, request):
        logger.info(f'Successfully request CreateBaseViews {request.data=}')
        return Response(status=status.HTTP_200_OK)


class DeleteBaseViews(APIView):
    def post(self, request):
        DataBase.objects.all().delete()
        logger.info(f'Successfully DELETED BASE {request.data=}')
        return Response(status=status.HTTP_200_OK)


class HomeViews(APIView):
    def post(self, request):
        logger.info(f'Successfully request HomeViews{request.data=}')
        return Response(status=status.HTTP_200_OK)


class SheetViews(APIView):
    def post(self, request):
        logger.info(f'Successfully request HomeViews{request.data=}')
        return Response(status=status.HTTP_200_OK)



class SheetCreateUpdateAPIView(generics.CreateAPIView):
    queryset = DataBase.objects.all()
    serializer_class = serializers.SheetPostSerializer
