# sheet_task

Приложение зеркально получает от Google Sheets изменение данных (POST)  
-на старте (POST \start)(CELERY) читает данные из Google Sheets и записывает в базу-формируя репликант листа  
-опрашивает CBR(https://www.cbr.ru/)(CELERY) на данные даты содержащиеся в листе курсы валют и записывает в базу  
-записывает(CELERY) в Google Sheets в лист settigs url webhook для получения измененных ячеек через POST запросы через endpoint(sheet_webhook/)  

Что не успел, но нужно:  
-перенести данные относящиеся к работе Google Sheets настроек в settings.ini:  
-full рефакторинг  
-тестировать  
