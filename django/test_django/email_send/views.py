from django.core.mail import send_mail
from django.conf import settings
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from upload_file.models import Category

class EmailSendView(APIView):
    def post(self, request):
        try:
            # Чтение последнего output файла
            excel_path = "src/excel/output.xlsx"
            df = pd.read_excel(excel_path)
            
            # Группировка данных по категориям, сохраняя подкатегории
            grouped_data = df.groupby('Категория')[['Категории', 'Tекст обращения']].apply(lambda x: list(zip(x['Категории'], x['Tекст обращения']))).to_dict()
            
            # Получение всех категорий с email адресами
            categories = Category.objects.filter(email__isnull=False)
            
            emails_sent = 0
            for category in categories:
                if category.name in grouped_data:
                    # Формирование текста письма
                    messages = grouped_data[category.name]
                    email_body = f"Обращения для категории {category.name}:\n\n"
                    for i, (subcategory, message) in enumerate(messages, 1):
                        email_body += f"{i}. Подкатегория: {subcategory}\n   Обращение: {message}\n\n"
                    
                    # Отправка email
                    send_mail(
                        subject=f'Обращения по категории: {category.name}',
                        message=email_body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[category.email],
                        fail_silently=False,
                    )
                    emails_sent += 1
            
            return Response({
                'status': 'success',
                'message': f'Отправлено {emails_sent} email сообщений'
            }, status=status.HTTP_200_OK)
            
        except FileNotFoundError:
            return Response({
                'status': 'error',
                'message': 'Файл output.xlsx не найден'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)