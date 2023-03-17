"""
A basic classifier inspired by the Xception architecture: https://arxiv.org/abs/1610.02357
- model implementation used: https://keras.io/examples/vision/image_classification_from_scratch/
"""


import os
import keras
import glob
import random
import itertools
import numpy as np
import tensorflow as tf
from datetime import datetime
from natsort import natsorted
from glob import glob
from keras import layers
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from sklearn.model_selection import train_test_split
from keras.utils.data_utils import Sequence
from keras.utils import to_categorical, normalize


### GLOBALS
IMAGE_SIZE= 244
random_state = 42
DS_LIMIT = 9000
SAVE_DIR = "Models"


def shuffle_data(a, b):
    c = list(zip(a, b))
    random.shuffle(c)

    return zip(*c)


# Xception-Model
def get_model(input_shape, num_classes=2):

    inputs = keras.Input(shape=input_shape)
    x = layers.Conv2D(128, 3, strides=2, padding="same")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    previous_block_activation = x

    for size in [256, 512, 728]:
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

        residual = layers.Conv2D(size, 1, strides=2, padding="same")(
            previous_block_activation
        )
        x = layers.add([x, residual])
        previous_block_activation = x

    x = layers.SeparableConv2D(1024, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    x = layers.GlobalAveragePooling2D()(x)
    
    activation = "softmax"

    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation=activation)(x)
    
    model = keras.Model(inputs, outputs)

    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
        )

    return model



class DatasetGenerator(Sequence):
    def __init__(self, images, labels, img_size=244, channels=3, batch_size=8):
        self.images = images
        self.labels = labels
        self.batch_size = batch_size
        self.img_size = img_size
        self.channels = channels
        self.n_classes = 2

    def load_image(self, x):
        img = tf.io.read_file(x)
        img = tf.io.decode_jpeg(img, channels=self.channels)
        img = tf.slice(img, begin=[0, 0, 0], size=[tf.shape(img)[0], tf.shape(img)[0], self.channels])
        img = tf.image.resize_with_pad(img, target_height=self.img_size, target_width=self.img_size, method=tf.image.ResizeMethod.LANCZOS3)
        img = tf.cast(img, tf.float32)
        img /= 255.0
        return img


    def __len__(self):
        return int(np.ceil(len(self.images) / float(self.batch_size)))


    def __getitem__(self, idx):

        batch_images= self.images[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_labels = self.labels[idx * self.batch_size:(idx + 1) * self.batch_size]

        images = []
        labels = []
        
        for img_path, label in zip(batch_images, batch_labels):
            img = self.load_image(img_path)
            images.append(img)
            labels.append(label)
            
        labels = tf.one_hot(labels, depth=self.n_classes)
                
        return [np.array(images), labels]


if __name__ == "__main__":
    data_root = "Data"

    stamp_images = os.path.join(data_root, "Stamps")
    alpha_stamp_images = os.path.join(data_root, "AlphaNoStamps")
    no_stamp_images = os.path.join(data_root, "NoStamps")

    stamps = natsorted(glob(f"{stamp_images}/*.jpg"))
    alpha_stamps = natsorted(glob(f"{alpha_stamp_images}/*.jpg"))
    no_stamps = natsorted(glob(f"{no_stamp_images}/*.jpg"))

    print(f"Stamp Images: {len(stamps)}, Alpha-Stamp Images: {len(alpha_stamps)}, No-Stamp Images: {len(no_stamps)}")

    ds_stamps = stamps[:DS_LIMIT]
    ds_stamps_labels = np.ones(shape=(len(ds_stamps), ), dtype=np.uint8)

    ds_nostamps = alpha_stamps + no_stamps[:DS_LIMIT-len(alpha_stamps)]
    ds_nostamps_labels = np.zeros(shape=(len(ds_nostamps), ), dtype=np.uint8)

    all_images = list(itertools.chain(*zip(ds_stamps, ds_nostamps)))
    all_labels = list(itertools.chain(*zip(ds_stamps_labels, ds_nostamps_labels)))
    X, y = shuffle_data(all_images, all_labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=random_state)

    print(f"X-Train: {len(X_train)} - y-train: {len(y_train)}")
    print(f"X-Test: {len(X_test)} - y-test: {len(y_test)}")
    print(f"X-Val: {len(X_val)} - y-val: {len(y_val)}")

    now = datetime.now()
    time_stamp = f"{now.year}_{now.month}_{now.day}-{now.hour}-{now.minute}"
    training_out_path = f"{SAVE_DIR}/{time_stamp}"

    
    if not os.path.exists(training_out_path):
        os.makedirs(training_out_path)

    
    xce_model = get_model(input_shape=(244, 244, 1), num_classes=2)
    train_generator = DatasetGenerator(X_train, y_train, channels=1)
    val_generator = DatasetGenerator(X_val, y_val, channels=1)


    epochs = 25

    callbacks_list = [
                  ModelCheckpoint(filepath=f"{training_out_path}/xce_model.h5", monitor='val_loss', verbose=1, save_best_only=True, mode='min'),
                  ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, min_lr=1e-9, verbose=1),
                  EarlyStopping(monitor='val_accuracy', mode='max', patience=10,  restore_best_weights=True)
    ]

    xce_model = get_model(input_shape=(244, 244, 1), num_classes=2)


    train_history = xce_model.fit(
        train_generator,
        epochs=epochs,
        callbacks=callbacks_list,
        validation_data=val_generator,
        shuffle=True
    )


    train_out_file = f"{SAVE_DIR}/{time_stamp}/train_history.txt"

    with open(train_out_file, "w") as f:
        f.write(train_history)
