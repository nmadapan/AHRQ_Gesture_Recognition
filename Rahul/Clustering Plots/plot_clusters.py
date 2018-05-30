import pickle
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import itertools
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

# Read pkl object with cluster data
finger_data = None
with open('results_raw_data.pkl', 'rb') as f:
    finger_data = pickle.load(f)
    finger_data = np.array(finger_data, dtype=float)
with open('results_fingers.pkl', 'rb') as f:
    raw_data = pickle.load(f)
    raw_data = np.array(raw_data, dtype=float)

class_names = ["Class " + str(i) for i in range(1,11)]


# Compute confusion matrix
y_test = finger_data[:,0]
y_pred = finger_data[:,1]
cnf_matrix = confusion_matrix(y_test, y_pred)

# Plot non-normalized confusion matrix
plt.figure(figsize=(10, 10), dpi=300)
plot_confusion_matrix(cnf_matrix, classes=class_names,
                      title='Confusion matrix, using finger length data')
plt.savefig('fingers_without_normalization')
# Plot normalized confusion matrix
plt.figure(figsize=(10, 10), dpi=300)
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                      title='Confusion matrix, using finger length data')
plt.savefig('fingers_normalized')


y_test = raw_data[:,0]
y_pred = raw_data[:,1]
cnf_matrix = confusion_matrix(y_test, y_pred)
# Plot non-normalized confusion matrix
plt.figure(figsize=(10, 10), dpi=300)
plot_confusion_matrix(cnf_matrix, classes=class_names,
                      title='Confusion matrix, using hand skeleton data')
plt.tight_layout()
plt.savefig('raw_without_normalization')
# Plot normalized confusion matrix
plt.figure(figsize=(10, 10), dpi=300)
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                      title='Confusion matrix, using hand skeleton data')
plt.tight_layout()
plt.savefig('raw_normalized')


