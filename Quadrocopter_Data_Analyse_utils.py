import pandas as pd
from sklearn.model_selection import train_test_split
from enum import Enum
import os
import time
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn import neighbors
import time

class State(Enum):
    stehend = 1
    fliegend = 2
    transportierend = 3


RECORD_HEADER = ['Zeitstempel', 'x-accelerometer', 'y-accelerometer',
                 'z-accelerometer', 'x-gyroskop', 'y-gyroskop', 'z-gyroskop', 'State']


def makeCSV_record(file_name, length=0, timestamp=None, x_acc=None, y_acc=None, z_acc=None, x_gyro=None, y_gyro=None, z_gyro=None, state=None):
    start = time.time()
    seperator = ','
    f = open(file_name, 'w+')
    row = seperator.join(RECORD_HEADER) + '\n'
    f.write(row)
    if length > 0:
        # data = [timestamp, x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, state]
        for i in range(length):
            row = seperator.join(map(str, [timestamp[i], x_acc[i], y_acc[i], z_acc[i], x_gyro[i], y_gyro[i], z_gyro[i], state[i]])) + '\n'
            # row = seperator.join(map(str, np.array([timestamp[i], x_acc[i], y_acc[i], z_acc[i], x_gyro[i], y_gyro[i], z_gyro[i], state[i]]))) + '\n'
            f.write(row)
    f.close()
    return time.time()-start


def test_utils():
    # print(State.fliegend)
    # print(repr(State.fliegend))
    # print(State(2))
    # print(State.fliegend.name)
    # print(State.fliegend.value)
    # makeCSV_record('test.csv')
    print('---------------------------------')
    # os.system('cat test.csv')

data = pd.read_csv('Werte_Kombiniert.csv')
train_data = data.drop(columns='Zeitstempel')
train_set, test_set = train_test_split(train_data, test_size = 0.2, random_state=42)
scaler = MinMaxScaler()
def make_classificator():
    global scaler
    global train_data, train_set, test_set, data
    time_current = time.time()
    print('Trainnig data and create a classificator')
    Eingangsdaten = train_data.drop(columns='State').keys()
    Xdf = train_set[Eingangsdaten]
    #Xdf = train_set[train_set.keys()]
    X = scaler.fit_transform(Xdf)
    #y = train_set['State']==State.transportierend.value
    y = train_set['State']
    k = 5
    clf = neighbors.KNeighborsClassifier(n_neighbors=k)
    clf.fit(X,y)
    # Datenaufbereitung
    Xdf_test = test_set[Eingangsdaten]
    X_test = scaler.transform(Xdf_test)
    #y_test = test_set["State"] == State.transportierend.value
    y_test = test_set["State"]
    # Prediction
    y_predict = clf.predict(X_test)
    # Vergleich des Ergebnisses von Vorhersage und tatsaechlicher Klasse
    accuracy = np.mean(y_test == y_predict)
    print('Accuracy: ', accuracy,
          '\nTatsaechliche Klasse:', y_test[:10], '\nvorhergesagte Klasse:', y_predict[:10])
    print('scaler')
    print(scaler)
    print('trained time: ' + str(int((time.time()-time_current)*1000)) + ' ms')
    input("Press Enter to continue...")
    return clf

