import tensorflow as tf
from utils import parser_cfg_file

class AFD_RNN(object):

    def __init__(self):
        net_config = parser_cfg_file('./config/rnn_net.cfg')
        self.time_step = int(net_config['time_step'])
        self.class_num = int(net_config['class_num'])
        self.num_units = int(net_config['num_units'])
        self.senor_data_num = int(net_config['senor_data_num'])
        self.batch_size = int(net_config['batch_size'])

    def build_net_graph(self):
        self.x = tf.placeholder(tf.float32, [None, self.time_step, self.senor_data_num])

        self._add_input_layer()
        self._add_rnn_layer()
        predict = self._add_output_layer()

        return predict

    def _add_input_layer(self):
        input_x = tf.reshape(self.x, [-1, self.senor_data_num])
        weights_x = self._get_variable_weights([self.senor_data_num, self.num_units], 'input_weights')
        biases_x = self._get_variable_biases([self.num_units], 'input_biases')

        self.x_output = tf.reshape(tf.add(tf.matmul(input_x, weights_x), biases_x),
                                   [-1, self.time_step, self.num_units])


    def _add_rnn_layer(self):
        self.x_output = tf.unstack(self.x_output, axis=1)
        lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(self.num_units)
        self.cell_state = lstm_cell.zero_state(self.batch_size, dtype=tf.float32)

        # outputs shape =[batch_size, max_time, cell_state_size]
        # LSTM final_state shape = [2, batch_size, cell_state_size]
        self.cell_outputs, self.final_state = tf.nn.static_rnn(lstm_cell,
                                                               self.x_output,
                                                               initial_state=self.cell_state)

    def _add_output_layer(self):
        outputs = tf.reshape(self.cell_outputs, [-1, self.num_units])
        weights_outputs = self._get_variable_weights([self.num_units, self.class_num], 'outputs_weights')
        biases_outputs = self._get_variable_biases([self.class_num], 'outputs_biases')

        return tf.reshape(tf.add(tf.matmul(outputs, weights_outputs), biases_outputs),
                          [self.time_step, self.batch_size, self.class_num])

    def _get_variable_weights(self, shape, name):
        return tf.Variable(tf.truncated_normal(shape, stddev=0.1), dtype=tf.float32, name=name)

    def _get_variable_biases(self, shape, name):
        return tf.Variable(tf.constant(0.1, shape=shape), dtype=tf.float32, name=name)