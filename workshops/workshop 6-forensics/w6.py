from sklearn.neighbors import KNeighborsClassifier
from sklearn import datasets, linear_model
import pandas as pd
import numpy as np 
import mnist
from sklearn.model_selection import KFold
from sklearn.datasets import load_iris
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
from tensorflow.keras.utils import to_categorical
from tensorflow import keras

def readData():
    iris = datasets.load_iris()
    print(type(iris.data), type(iris.target))
    X = iris.data
    Y = iris.target
    df = pd.DataFrame(X, columns=iris.feature_names)
    print(df.head())

    return df 

def makePrediction():
    iris = datasets.load_iris()
    knn = KNeighborsClassifier(n_neighbors=6)
    knn.fit(iris['data'], iris['target'])
    X = [
        [5.9, 1.0, 5.1, 1.8],
        [3.4, 2.0, 1.1, 4.8],
    ]
    prediction = knn.predict(X)
    print(prediction)    

def doRegression():
    diabetes = datasets.load_diabetes()
    diabetes_X = diabetes.data[:, np.newaxis, 2]
    diabetes_X_train = diabetes_X[:-20]
    diabetes_X_test = diabetes_X[-20:]
    diabetes_y_train = diabetes.target[:-20]
    diabetes_y_test = diabetes.target[-20:]
    regr = linear_model.LinearRegression()
    regr.fit(diabetes_X_train, diabetes_y_train)
    diabetes_y_pred = regr.predict(diabetes_X_test)


def doDeepLearning():
    

    (train_images, train_labels), (test_images, test_labels) = keras.datasets.mnist.load_data()



    train_images = (train_images / 255) - 0.5
    test_images = (test_images / 255) - 0.5


    train_images = np.expand_dims(train_images, axis=3)
    test_images = np.expand_dims(test_images, axis=3)

    num_filters = 8
    filter_size = 3
    pool_size = 2

    model = Sequential([
    Conv2D(num_filters, filter_size, input_shape=(28, 28, 1)),
    MaxPooling2D(pool_size=pool_size),
    Flatten(),
    Dense(10, activation='softmax'),
    ])

    # Compile the model.
    model.compile(
    'adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'],
    )

    # Train the model.
    model.fit(
    train_images,
    to_categorical(train_labels),
    epochs=3,
    validation_data=(test_images, to_categorical(test_labels)),
    )

    model.save_weights('cnn.weights.h5')

    predictions = model.predict(test_images[:5])

    print(np.argmax(predictions, axis=1)) # [7, 2, 1, 0, 4]

    print(test_labels[:5]) # [7, 2, 1, 0, 4]

def k_fold_cv_mlp(n_splits):
  
  iris_data = load_iris()
  X_data = pd.DataFrame(iris_data.data, columns=iris_data.feature_names)
  ## to numpy
  X=  X_data.to_numpy()
  y = iris_data.target


  kf = KFold(n_splits)
  folds = []

  for train_index, test_index in kf.split(X):
      folds.append((train_index, test_index))


  # Initialize machine learning model, MLP
  model = MLPClassifier(hidden_layer_sizes=(256,128,64,32),activation="relu",random_state=1)

  # Initialize a list to store the evaluation scores
  scores = []
  ## Initialize fold index
  fold_index = 0

  
  # Iterate through each fold
  for train_indices, test_indices in folds:
      X_train, y_train = X[train_indices], y[train_indices]
      X_test, y_test = X[test_indices], y[test_indices]


      fold_index += 1
      print(f"Fold {fold_index}:")
     
      # scale data
      sc_X = StandardScaler()
      X_train_scaled=sc_X.fit_transform(X_train)
      X_test_scaled=sc_X.transform(X_test)

      # Train the model on the training data
      model.fit(X_train_scaled, y_train)

      # Make predictions on the test data
      y_pred = model.predict(X_test_scaled)

      # Calculate the accuracy score for this fold
      fold_score = accuracy_score(y_test, y_pred)
      print(f"Fold test score {fold_score}:")

      # Append the fold score to the list of scores
      scores.append(fold_score)

  # Calculate the mean accuracy across all folds
  mean_accuracy = np.mean(scores)
  print("K-Fold Cross-Validation Scores:", scores)
  print("Mean Accuracy:", mean_accuracy)

if __name__=='__main__': 
    data_frame = readData()
    makePrediction() 
    doRegression() 
    my_k_fold = input('Type in k for cross valdation: ') 
    my_k_fold = int(my_k_fold)
    k_fold_cv_mlp(my_k_fold)
    doDeepLearning() 
