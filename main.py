import csv
import numpy as np
import tensorflow as tf


class Model:
    def __init__(self, num_input, num_classes):
        self.num_input = num_input
        self.num_classes = num_classes
        self.X = tf.placeholder("float", [None, self.num_input])
        self.Y = tf.placeholder("float", [None, self.num_classes])
        self.model = self.create_model()
        print('Model has been created')

    def create_model(self):
        weights = {
            'h1': tf.Variable(tf.random_normal([self.num_input, 256])),
            'h2': tf.Variable(tf.random_normal([256, 256])),
            'out': tf.Variable(tf.random_normal([256, self.num_classes]))
        }
        biases = {
            'b1': tf.Variable(tf.random_normal([256])),
            'b2': tf.Variable(tf.random_normal([256])),
            'out': tf.Variable(tf.random_normal([self.num_classes]))
        }

        layer_1 = tf.nn.relu(tf.add(tf.matmul(self.X, weights['h1']), biases['b1']))
        layer_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2']))
        out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
        return out_layer

    def train(self, version, data, labels, batch_size, test_data, test_labels):
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.model, labels=self.Y))
        optimizer = tf.train.AdamOptimizer(learning_rate=0.1).minimize(loss)
        correct_pred = tf.equal(tf.argmax(tf.nn.softmax(self.model), 1), tf.argmax(self.Y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

        init = tf.global_variables_initializer()
        saver = tf.train.Saver()

        with tf.Session() as sess:
            sess.run(init)
            data = np.split(data, batch_size)
            labels = np.split(labels, batch_size)
            num_batches = len(data)
            for epoch in range(1, 100 + 1):
                avg_loss, avg_acc = 0, 0
                for batch in range(num_batches):
                    _, cost, acc = sess.run([optimizer, loss, accuracy],
                                            feed_dict={self.X: data[batch], self.Y: labels[batch]})
                    avg_loss += cost
                    avg_acc += acc
                print('Epoch: ' + str(epoch) + ' Accuracy: ' + '{:.3f}'.format(1 - (avg_acc/num_batches))
                      + ' Loss: ' + '{:.4f}'.format(avg_loss/num_batches))

            print('Optimization Finished!')
            print('Testing Accuracy:',
                  sess.run(accuracy, feed_dict={self.X: test_data,
                                                self.Y: test_labels}))
        save_path = saver.save(sess, 'model' + str(version) + '.ckpt')
        print("Model saved in file: %s" % save_path)


class MNIST_Data:
    def __init__(self, train_file, test_file):
        train_x, train_y = [], []
        test_x, test_y = [], []
        with open(train_file) as file:
            reader = csv.reader(file)
            for row in reader:
                label = np.zeros(10)
                label[int(row[0])] = 1
                train_y.append(label)
                train_x.append(list(map(int, row[1:])))
        print('Training Data Loaded from file')

        with open(test_file) as file:
            reader = csv.reader(file)
            for row in reader:
                label = np.zeros(10)
                label[int(row[0])] = 1
                test_y.append(label)
                test_x.append(list(map(int, row[1:])))
        print('Testing Data Loaded from file')

        self.train_x, self.train_y = np.asarray(train_x), np.asarray(train_y)
        self.test_x, self.test_y = np.asarray(test_x), np.asarray(test_y)


def main():
    model = Model(784, 10)
    data = MNIST_Data('mnist_train.csv', 'mnist_test.csv')
    model.train(0, data.train_x, data.train_y, 100, data.test_x, data.test_y)


if __name__ == '__main__':
    main()
