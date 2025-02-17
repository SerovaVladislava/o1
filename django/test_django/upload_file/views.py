import json
import pickle
import os
from os import path, mkdir

import keras
import numpy as np
import pandas as pd
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse
from django.core.exceptions import ObjectDoesNotExist
from keras_preprocessing.text import tokenizer_from_json
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Keyword
from rest_framework import status

from .helpers import get_lower, text_update_key, onlygoodsymbols
from .serializers import UploadFileSerializer, AuthUserSerializer
from .token import create_token, read_token, ReadTokenException
from main_model.model_weights import ModelWeightManager


class AuthUserView(APIView):
    def post(self, request: Request):
        serializer = AuthUserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            request_body = request.data
            try:
                user: User = User.objects.get(username=request_body["login"])
            except ObjectDoesNotExist:
                return Response(data="User not found", status=404)

            user.save()
            if user.check_password(request_body["password"]):
                payload = {
                    'user_id': user.id
                }

                token = create_token(payload)

                response_body = {
                    'user_id': user.id,
                    'Authorization': token
                }

                return Response(data=response_body, status=200)
            else:
                return Response(data="Unauthorized", status=401)


class UploadFileView(APIView):
    def get(self, request: Request):
        excel_path = "src/excel/output.xlsx"
        response_excel_file = open(excel_path, mode="rb")
        return FileResponse(response_excel_file)

    def post(self, request: Request):
        # Проверка типа весов
        weight_type = request.data.get('weight_type', 'medium')  # По умолчанию используем medium
        if weight_type not in ['light', 'medium', 'heavy']:
            return Response(
                data={"error": "Invalid weight type. Expected 'light', 'medium', or 'heavy'."}, 
                status=400
            )
        
        # Проверка токена
        token = request.headers.get('Authorization')
        try:
            read_token(token)
        except ReadTokenException:
            return Response(
                data={"error": "Unauthorized"}, 
                status=401
            )

        # Валидация данных
        serializer = UploadFileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                data={"error": "Invalid request data", "details": serializer.errors}, 
                status=400
            )

        try:
            # Сохранение Excel файла
            files = request.FILES
            excel_file: InMemoryUploadedFile = files.get('file')
            if not excel_file:
                return Response(
                    data={"error": "No file provided"}, 
                    status=400
                )

            # Создание директории если её нет
            folder_path = "src/excel"
            if not path.isdir(folder_path):
                mkdir(folder_path)
            
            # Сохранение входного файла
            excel_path = path.join(folder_path, excel_file.name)
            with open(excel_path, mode="wb") as new_excel_file:
                new_excel_file.write(excel_file.file.getvalue())

            # Загрузка модели с выбранными весами
            try:
                weight_type = request.data.get('weight_type', 'medium')
                model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main_model')
                weight_manager = ModelWeightManager(model_dir=model_dir)
                model = weight_manager.load_model_with_weights(weight_type)
                if model is None:
                    return Response(
                        data={"error": f"Failed to load model with {weight_type} weights"}, 
                        status=500
                    )
            except Exception as e:
                return Response(
                    data={"error": f"Error loading model: {str(e)}"}, 
                    status=500
                )

            # Обработка данных
            df = pd.read_excel(excel_path)
            if 'Tекст обращения' not in df.columns:
                return Response(
                    data={"error": "Excel file must contain 'Tекст обращения' column"}, 
                    status=400
                )

            # Предобработка текста
            obrashenie = df['Tекст обращения']
            obrashenie = obrashenie.apply(get_lower).apply(text_update_key).apply(onlygoodsymbols)

            # Токенизация
            try:
                with open('tokenizer.json') as f:
                    tokenizer = tokenizer_from_json(json.load(f))
            except Exception as e:
                return Response(
                    data={"error": f"Error loading tokenizer: {str(e)}"}, 
                    status=500
                )

            # Получение категорий
            categories = Category.objects.all()
            category_names = [category.name for category in categories]
            if not category_names:
                return Response(
                    data={"error": "No categories found in database"}, 
                    status=500
                )

            # Предсказание категорий
            obr_t = tokenizer.texts_to_matrix(obrashenie, mode='binary')
            predictions = model.predict(obr_t)
            
            # Получаем индексы и уверенность для каждого предсказания
            predicted_indices = np.argmax(predictions, axis=-1)
            confidence_scores = np.max(predictions, axis=-1)
            
            # Формируем предсказанные категории и добавляем уверенность
            predicted_categories = [category_names[i] for i in predicted_indices]
            df["Категория"] = predicted_categories
            df["Уверенность"] = [f"{score:.2%}" for score in confidence_scores]

            # Сохранение результата
            output_path = path.join(folder_path, "output.xlsx")
            with pd.ExcelWriter(output_path) as writer:
                df.to_excel(writer, index=False)

            return Response(
                data={
                    "message": "File processed successfully",
                    "weight_type": weight_type,
                    "processed_rows": len(df)
                }, 
                status=201
            )

        except Exception as e:
            return Response(
                data={"error": f"Unexpected error: {str(e)}"}, 
                status=500
            )


class CategoryUpdateView(APIView):
    def get(self, request: Request):
        """
        Получение всех категорий из базы данных.
        """
        categories = Category.objects.all()
        category_names = [category.name for category in categories]
        return Response(data={"categories": category_names}, status=status.HTTP_200_OK)

    def post(self, request: Request):
        """
        Получение одной категории и её почты по имени или удаление категории по имени.
        Ожидается, что в теле запроса будет имя категории и флаг для удаления.
        """
        category_name = request.data.get('category_name', None)
        category_email = request.data.get('email', None)  # Получение почты категории
        delete_flag = request.data.get('delete', False)  # Флаг для удаления категории

        if not category_name:
            return Response(data="Category name is required.", status=status.HTTP_400_BAD_REQUEST)

        if delete_flag:
            try:
                category = Category.objects.get(name=category_name)
                category.delete()
                return Response(data=f'Category "{category_name}" deleted successfully.', status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response(data="Category not found.", status=status.HTTP_404_NOT_FOUND)
        
        if category_email:
            category, created = Category.objects.get_or_create(name=category_name, email=category_email)
            if created:
                return Response(data=f'Category "{category_name}" created successfully.', status=status.HTTP_201_CREATED)
            else:
                return Response(data=f'Category "{category_name}" already exists.', status=status.HTTP_200_OK)

        try:
            category = Category.objects.get(name=category_name)
            response_data = {
                'name': category.name,
                'email': category.email
            }
            return Response(data=response_data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response(data="Category not found.", status=status.HTTP_404_NOT_FOUND)           
    

class KeywordUpdateView(APIView):
    def get(self, request: Request):
        """
        Получение всех ключевых слов из базы данных.
        """
        keywords = Keyword.objects.all()
        keyword_list = [keyword.word for keyword in keywords]
        return Response(data={"keywords": keyword_list}, status=status.HTTP_200_OK)

    def post(self, request: Request):
        """
        Обновление ключевых слов в базе данных.
        Ожидается, что в теле запроса будет список ключевых слов.
        """
        keywords_data = request.data.get('keywords', [])

        if not isinstance(keywords_data, list):
            return Response(data="Invalid data format. Expected a list of keywords.", status=status.HTTP_400_BAD_REQUEST)

        # Обработка добавления или обновления ключевых слов
        for keyword_word in keywords_data:
            keyword, created = Keyword.objects.get_or_create(word=keyword_word)
            if created:
                print(f'Keyword "{keyword_word}" created')
            else:
                print(f'Keyword "{keyword_word}" already exists')

        # Удаление ключевых слов, которые не были в списке
        existing_keywords = Keyword.objects.all()
        for keyword in existing_keywords:
            if keyword.word not in keywords_data:
                keyword.delete()
                print(f'Keyword "{keyword.word}" deleted')

        return Response(data="Keywords updated successfully.", status=status.HTTP_200_OK)