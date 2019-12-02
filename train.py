import sys
sys.path.insert(0, "../meta_material_databank")
sys.path.insert(0, "../SASA")


#standard modules
import os
import random
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import argparse
import pickle
import cProfile
import matplotlib
#NN modules
from tensorflow.keras.layers import Input, Dense, MaxPooling1D, Dropout, Conv1D, GlobalAveragePooling1D, Reshape
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from sklearn.preprocessing import MultiLabelBinarizer
#Self written modules
from crawler import Crawler
from stack import *

MODEL_INPUTS = 128
MODEL_OUTPUTS = 8
MODEL_PREDICTIONS = ["particle_material", "hole"]
BATCH_SIZE = 128
EPOCHS = 10
INIT_LR = 1e-3

#%%

def create_model():
    inp = Input(shape=(MODEL_INPUTS))
    x = Reshape((MODEL_INPUTS, 1)) (inp)
    x = Conv1D(64, 10, activation='relu')(x)
    x = Conv1D(64, 10, activation='relu')(x)
    x = MaxPooling1D(3)(x)
    x = Conv1D(128, 10, activation='relu')(x)
    x = Conv1D(128, 10, activation='relu')(x)
    x = GlobalAveragePooling1D()(x)
    x = Dropout(0.5)(x)
    out = Dense(MODEL_OUTPUTS, activation='sigmoid')(x)

    model = Model(inp, out)
    return model

def batch_generator(batch_dir):
    """
    Just load the batches created by data_gen.py

    """

    x_batches = []
    while True:
        #reset x_batches once are batches are used up
        if len(x_batches) == 0:
            x_batches = os.listdir(f"{batch_dir}/X")

        idx = random.randint(0, len(x_batches)-1)
        batch = x_batches[idx]

        x = np.load(f"{batch_dir}/X/{batch}")
        y = np.load(f"{batch_dir}/Y/{batch}")

        del x_batches[idx]

        yield (x, y)




#%%
if __name__ == '__main__':

    #%% construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--batches", default="data/batches",
    	help="path to directory containing the training batches")
    ap.add_argument("-p", "--params", default="data/params.pickle",
    	help="path to the .pickle file containing the smat parameters")
    ap.add_argument("-m", "--model", default="data/stacker.h5",
    	help="path to output model")
    ap.add_argument("-pl", "--plot", default="data/plot.png",
    	help="path to output accuracy/loss plot")
    args = vars(ap.parse_args())

    #set the matplotlib backend so figures can be saved in the background
    matplotlib.use("Agg")

    print("[INFO] training network...")
    model = create_model()
    opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)
    model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])

    trainGen = batch_generator(args["batches"])
    validationGen = batch_generator("data/validation")
    batch_count = len(os.listdir(f"{args['batches']}/X"))
    validation_count = len(os.listdir("data/validation/X"))

    H = model.fit_generator(
        trainGen,
	    steps_per_epoch=batch_count,
        validation_data=validationGen,
        validation_steps=validation_count,
        epochs=EPOCHS,
        use_multiprocessing=True)

    # save the model to disk
    print("[INFO] serializing network...")
    model.save(args["model"])


    plt.style.use("ggplot")
    plt.figure()
    N = EPOCHS
    plt.plot(np.arange(0, N), H.history["loss"], label="train_loss")
    plt.plot(np.arange(0, N), H.history["val_loss"], label="val_loss")
    plt.plot(np.arange(0, N), H.history["accuracy"], label="train_acc")
    plt.plot(np.arange(0, N), H.history["val_accuracy"], label="val_acc")
    plt.title(f"Training Loss and Accuracy, LR: {INIT_LR}")
    plt.xlabel("Epoch #")
    plt.ylabel("Loss/Accuracy")
    plt.legend(loc="upper left")
    plt.savefig(args["plot"])

    print("[DONE]")


#%%
