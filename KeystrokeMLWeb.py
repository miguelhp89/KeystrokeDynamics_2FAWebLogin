#!/usr/bin/python3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.neural_network import MLPClassifier
import joblib
import datetime
#import time


class KeystrokeMLWeb:
    def __init__(self):
        self.data = ""
        self.pressFlightCol = []
        self.holdCol = []
        self.releasePressFlightCol = []
        self.trainData = []
        self.testData = []
        self.predictData = []

    def __call__(self):
        self.data = ""
        self.pressFlightCol = []
        self.holdCol = []
        self.releasePressFlightCol = []
        self.trainData = []
        self.testData = []
        self.predictData = []

    #20210105 MH: Read CSV
    def setDataset(self, path):
        self.data = pd.read_csv(path, header=0)

    #20210105 MH: Create line plot to compare average time keystroke
    def plotKeystrokes(self):
        for ks in self.data.columns:
            if ks.startswith("DD"):
                self.pressFlightCol.append(ks)
            elif ks.startswith("UD"):
                self.releasePressFlightCol.append(ks)
            elif ks.startswith("H"):
                self.holdCol.append(ks)
        
        plot = self.data[self.holdCol]
        plot['subject'] = self.data['subject'].values
        plot = plot.groupby('subject').mean()
        plot.iloc[:6].T.plot(figsize=(10,6), title= 'Hold Time: Tiempo Promedio')

        plot1 = self.data[self.pressFlightCol]
        plot1['subject'] = self.data['subject'].values
        plot1 = plot1.groupby('subject').mean()
        plot1.iloc[:6].T.plot(figsize=(10,6), title= 'Press Flight Time: Tiempo Promedio')

        plot2 = self.data[self.releasePressFlightCol]
        plot2['subject'] = self.data['subject'].values
        plot2 = plot2.groupby('subject').mean()
        plot2.iloc[:6].T.plot(figsize=(10,6), title= 'Release-Press Flight Time: Tiempo Promedio')

    #20210105 MH: Show information about the dataset
    def exploreData(self):
        print("Dataset Information")
        print(self.data.info())
        #print("Dataset Describe")
        #print(self.data.describe())

    #20210105 MH: Evaluates the accuracy prediction level of 3 types of ML classifiers
    def evaluateClassifier(self):
        #20210105 MH: split dataset in train and tes data
        self.trainData, self.testData = train_test_split(self.data, test_size=0.2, random_state=0)
        
        #20210105 MH: asigning train and test data axis
        x_train = self.trainData[self.data.columns[2:]]
        y_train = self.trainData['subject']

        x_test = self.testData[self.data.columns[2:]]
        y_test = self.testData['subject']
        
        #20210105 MH: Evaluating KNN Classifier
        knc = KNeighborsClassifier()
        knc.fit(x_train, y_train)
        y_pred = knc.predict(x_test)
        knc_accuracy = metrics.accuracy_score(y_test, y_pred)
        print("KNN Classifier Accuracy: ", round(knc_accuracy*100,2), "%")

        #20210105 MH: Evaluating Support Vector Linear Classifier
        svc = svm.SVC(kernel='linear')
        svc.fit(x_train, y_train)
        y_pred = svc.predict(x_test)
        svc_accuracy = metrics.accuracy_score(y_test, y_pred)
        print("Support Vector Linear Classifier Accuracy: " , round(svc_accuracy*100,2), "%")
        
        #20210105 MH: Evaluating Multilayer Perceptron Classifier
        mlp = MLPClassifier()
        mlp.fit(x_train, y_train)
        y_pred = mlp.predict(x_test)
        mlp_accuracy = metrics.accuracy_score(y_test, y_pred)
        print("Multilayer Perceptron Classifier Accuracy: " , round(mlp_accuracy*100,2), "%")

    def trainModel(self):
        tCls = input("Enter 0=KNN, 1=Sample Vector Linear, 2=Multilayer Perceptron: ")
        
        if tCls == "0":
            #KNN
            print("0")
        elif tCls == "1":
            #SVL
            print("1")
        elif tCls == "2":
            #MLP
            #20210105 MH: split dataset in train and tes data
            self.trainData, self.testData = train_test_split(self.data, test_size=0.2, random_state=0)
            
            #20210105 MH: asigning train and test data axis
            x_train = self.trainData[self.data.columns[2:]]
            y_train = self.trainData['subject']

            x_test = self.testData[self.data.columns[2:]]
            y_test = self.testData['subject']

            #20210105 MH: Training Multilayer Perceptron Classifier
            mlp = MLPClassifier()
            mlp.fit(x_train, y_train)
            joblib.dump(mlp, './TrainedModels/MLPClassifierTrained.pkl')



        else:
            print("Error: Selected value is not valid!")

    def predictFromFile(self, path):
        self.predictData = pd.read_csv(path, header=0)
        x_pred = self.predictData[self.predictData.columns[2:]]
        
        mlp = joblib.load('00_weblogin/TrainedModels/MLPClassifierTrained.pkl')
        y_pred = mlp.predict(x_pred)

        print("Input keystrokes dynamics: ")
        print(x_pred)
        #time.sleep(2.0)
        print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " Keystrokes dynamics have been evaluated!")
        #time.sleep(2.0)
        print(str(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())) + " Keystrokes dynamics owner: ", y_pred)
        return y_pred[0]
    


