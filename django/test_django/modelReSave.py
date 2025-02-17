import tensorflow as tf

model = tf.saved_model.load("main_model")


# Сохранение модели в формате .h5
from tensorflow import keras

# Создайте новую модель на основе загруженной
new_model = keras.Sequential([
    keras.layers.InputLayer(input_shape=(10,)),
    keras.layers.Lambda(lambda x: model(x))
])

# Сохраните новую модель в формате .keras
new_model.save("main_model.keras")

# Или сохраните в формате .h5
new_model.save("main_model.h5")
