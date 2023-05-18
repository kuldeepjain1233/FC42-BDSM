import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matlotlib inline

import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score

from sklearn.linear_model import LinearRegression

from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout

def stock():
    # class stock_pred:
    data = pd.read_csv('C:/Users/cycob/Downloads/Google_train_data.csv')
    # tesla.info()
    choose_loc = int(input("Please give the column number where the close field lies: "))

    data["Close"] = pd.to_numeric(data.Close, errors='coerce')
    data = data.dropna()
    trainData = data.iloc[:,choose_loc:choose_loc+1].values

    sc = MinMaxScaler(feature_range=(0,1))
    trainData = sc.fit_transform(trainData)
    d = len(trainData)
    print(d)

    x_train = []
    y_train = []

    for i in range(60, d):
        x_train.append(trainData[i-60:i,0])
        y_train.append(trainData[i,0])

    x_train, y_train = np.array(x_train),np.array(y_train)

    x_train = np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))


    model = Sequential()

    model.add(LSTM(units=100, return_sequences=True, input_shape=(x_train.shape[1],1)))
    model.add(Dropout(0.2))

    model.add(LSTM(units=100, return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(units=100,return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(units=100,return_sequences=False))
    model.add(Dropout(0.2))

    model.add(Dense(units=1))
    model.compile(optimizer='adam',loss="mean_squared_error")

    hist = model.fit(x_train, y_train, epochs=10, batch_size=32, verbose=2)

    # joblib.dump(model,stock_mar)


    testdata = pd.read_csv('C:/Users/cycob/Downloads/Google_test_data.csv')
    choose_loc = 4 
    # input("Please give the column number where the close field lies: ")
    testdata["Close"] = pd.to_numeric(testdata.Close, errors='coerce')
    testdata = testdata.dropna()
    testdata = testdata.iloc[:,choose_loc:choose_loc+1]
    y_test = testdata.iloc[60:,0:].values

    inputclosing = testdata.iloc[:,0:].values
    inputclosing_scaled = sc.transform(inputclosing)
    x_test = []
    length = len(testdata)
    timestep = 60
    for i in range(timestep,length):
        x_test.append(inputclosing_scaled[i-timestep:i,0])
    x_test = np.array(x_test)
    x_test = np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))

    test_pred = model.predict(x_test)

    predicted_price = sc.inverse_transform(test_pred)

    plt.plot(y_test, color = 'red',label='Actual Price')
    plt.plot(predicted_price, color ='green', label='Predicted Price')
    plt.title('Google stock price prediction')
    plt.xlabel('Time')
    plt.ylabel('Stock price')
    plt.legend()
    plt.show()