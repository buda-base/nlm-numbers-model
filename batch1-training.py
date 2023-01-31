import os
import cv2
import random
import numpy as np
from glob import glob
import tensorflow_hub as hub
import tensorflow as tf
from keras import models
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, LearningRateScheduler, EarlyStopping

from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input

IMAGE_SHAPE = (244, 244)
BATCH_SIZE = 32
data_root = "/home/data"
train_dir = f"{data_root}/train/"
valid_dir = f"{data_root}/valid/"
test_dir = f"{data_root}/test/"

model_out_dir = "/content/drive/MyDrive/TrainingData/Tibetan/NLM/Models"
checkpoint_path = f"{model_out_dir}/NLM_StampClassifier_vgg16.h5"

train_datagen = ImageDataGenerator(rescale=1/255.)
valid_datagen = ImageDataGenerator(rescale=1/255.)

print("Training images:")
train_ds = train_datagen.flow_from_directory(train_dir,
                                               target_size=IMAGE_SHAPE,
                                               batch_size=BATCH_SIZE,
                                               class_mode="categorical")

print("Validation images:")
valid_ds = train_datagen.flow_from_directory(valid_dir,
                                              target_size=IMAGE_SHAPE,
                                              batch_size=BATCH_SIZE,
                                              class_mode="categorical")


base_model = VGG16(weights="imagenet", include_top=False, input_shape=(244, 244, 3))
base_model.trainable = False

flatten_layer = Flatten()
dense_layer_1 = Dense(50, activation='relu')
dense_layer_2 = Dense(20, activation='relu')
prediction_layer = Dense(2, activation='softmax')


vgg16_model2 = models.Sequential([
    base_model,
    flatten_layer,
    dense_layer_1,
    dense_layer_2,
    prediction_layer
])

vgg16_model2.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

callbacks_list = [
                  ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min'),
                  ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-9, verbose=1),
                  EarlyStopping(monitor='val_accuracy', mode='max', patience=5,  restore_best_weights=True)
]

vgg16_history = vgg16_model2.fit(
    train_ds, epochs=5, 
    steps_per_epoch=len(train_ds), 
    validation_data=valid_ds, 
    validation_steps=len(valid_ds), 
    callbacks=callbacks_list, shuffle=True)

vgg16_model2.save("/content/drive/MyDrive/TrainingData/Tibetan/NLM/Models/VGG16")