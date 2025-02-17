import json
import os
import tensorflow as tf
from tensorflow import keras
import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout

class ModelWeightManager:
    def __init__(self, model_dir="."):
        """
        Инициализация менеджера весов
        :param model_dir: директория с моделью (по умолчанию текущая директория)
        """
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "saved_model.pb")
        self.config_path = os.path.join(model_dir, "model_config.json")
        self.weights_dir = os.path.join(model_dir, "weights")
        
        # Создаем директорию для весов если её нет
        if not os.path.exists(self.weights_dir):
            os.makedirs(self.weights_dir)

    def extract_model_architecture(self):
        """Извлекает архитектуру модели и сохраняет её в JSON"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at {self.model_path}")
            
            # Загружаем существующую модель
            print(f"Loading model from {self.model_dir}")
            model = load_model(self.model_dir)
            
            # Получаем и сохраняем конфигурацию
            model_config = model.get_config()
            
            # Сохраняем конфигурацию в JSON
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(model_config, f, ensure_ascii=False, indent=2)
            
            print(f"Model architecture saved to {self.config_path}")
            return model
            
        except Exception as e:
            print(f"Error extracting model architecture: {str(e)}")
            return None

    def create_weight_variations(self, base_model):
        """
        Создает различные версии весов с разной "уверенностью" в предсказаниях
        - light: более консервативные предсказания
        - medium: стандартные предсказания
        - heavy: более уверенные предсказания
        """
        try:
            # Получаем текущие веса
            original_weights = base_model.get_weights()
            
            # Создаем разные версии весов
            # Для последнего слоя (слой с softmax) используем другие коэффициенты
            weight_variations = {}
            
            for weight_type, (hidden_scale, output_scale) in {
                'light': (0.8, 0.5),    # Более осторожные предсказания
                'medium': (1.0, 1.0),    # Оригинальные веса
                'heavy': (1.2, 2.0)     # Более уверенные предсказания
            }.items():
                modified_weights = []
                for i, w in enumerate(original_weights):
                    if i == len(original_weights) - 2:  # Веса последнего слоя
                        modified_weights.append(w * output_scale)
                    else:
                        modified_weights.append(w * hidden_scale)
                weight_variations[weight_type] = modified_weights
            
            # Сохраняем каждую версию весов
            for weight_type, weights in weight_variations.items():
                weight_path = os.path.join(self.weights_dir, f"{weight_type}_weights.h5")
                
                # Создаем временную модель для сохранения весов
                temp_model = keras.models.clone_model(base_model)
                temp_model.set_weights(weights)
                temp_model.save_weights(weight_path)
                
                print(f"Saved {weight_type} weights to {weight_path}")
                
        except Exception as e:
            print(f"Error creating weight variations: {str(e)}")
            raise

    def load_model_with_weights(self, weight_type):
        """
        Загружает модель с определенными весами
        :param weight_type: тип весов ('light', 'medium', 'heavy')
        :return: загруженная модель или None в случае ошибки
        """
        try:
            # Проверяем тип весов
            if weight_type not in ['light', 'medium', 'heavy']:
                raise ValueError("Invalid weight type. Must be 'light', 'medium', or 'heavy'")
            
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at {self.model_path}")
            
            # Загружаем базовую модель
            print(f"Loading base model from {self.model_dir}")
            model = load_model(self.model_dir)
            
            # Загружаем веса
            weight_path = os.path.join(self.weights_dir, f"{weight_type}_weights.h5")
            if not os.path.exists(weight_path):
                raise FileNotFoundError(f"Weights file not found: {weight_path}")
            
            print(f"Loading weights from {weight_path}")
            model.load_weights(weight_path)
            return model
            
        except Exception as e:
            error_msg = f"Error loading model with weights: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

def setup_model_weights():
    """Функция для начальной настройки весов модели"""
    try:
        manager = ModelWeightManager()
        
        # Извлекаем архитектуру модели
        print("Extracting model architecture...")
        base_model = manager.extract_model_architecture()
        if base_model is None:
            raise Exception("Failed to extract model architecture")
        
        # Создаем разные версии весов
        print("Creating weight variations...")
        manager.create_weight_variations(base_model)
        print("Model weights setup completed successfully")
        
    except Exception as e:
        print(f"Error in setup_model_weights: {str(e)}")
        raise

if __name__ == "__main__":
    setup_model_weights()
