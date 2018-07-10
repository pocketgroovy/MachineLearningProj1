# Yoshi Miyamoto ymiyamoto3

import numpy as np

class RTLearner(object):
    def __init__(self, leaf_size, verbose=False):
        self.leaf_size = leaf_size
        self.verbose = verbose


    def addEvidence(self, dataX, dataY):
        self.model = self.build_tree(dataX, dataY)

    def build_tree(self, dataX, dataY):
        if dataX.shape[0] <= self.leaf_size:
            if dataY.shape[0] > 1:
                leaf_data = dataY.mean()
            else:
                leaf_data = dataY[0]
            return np.array([["leaf", str(leaf_data), np.nan, np.nan]])
        else:
            factor_index = np.random.choice(dataX.shape[1])
            sortedX, sortedY = self.get_sorted_data(dataX, dataY, factor_index)
            row_size = sortedX.shape[0]
            split_value, left_tree_data_x, left_tree_data_y, right_tree_data_x, right_tree_data_y = \
                self.split_data(row_size, sortedX, sortedY, factor_index)
            left_tree = self.build_tree(left_tree_data_x, left_tree_data_y)
            right_tree = self.build_tree(right_tree_data_x, right_tree_data_y)
            root = np.array([factor_index, split_value, 1, left_tree.shape[0] +1])
            return np.vstack([root, left_tree, right_tree])


    def get_sorted_data(self, dataX, dataY, max_index):
        sorted_indices = dataX[:, max_index].argsort()
        sortedX = dataX[sorted_indices]
        sortedY = dataY[sorted_indices]
        return sortedX, sortedY


    def split_data(self, row_size, sortedX, sortedY, max_index):
        split_index = row_size / 2
        split_value = (sortedX[split_index - 1, max_index] + sortedX[split_index, max_index]) / 2
        left_tree_data_x = sortedX[:split_index, :]
        left_tree_data_y = sortedY[:split_index]
        right_tree_data_x = sortedX[split_index:, :]
        right_tree_data_y = sortedY[split_index:]
        return split_value, left_tree_data_x, left_tree_data_y, right_tree_data_x, right_tree_data_y


    def query(self, Xtest):
        index = 0
        i = 0
        my_array = np.ndarray(Xtest.shape[0])
        while i < Xtest.shape[0]:
            while self.model[index, 0]!= "leaf":
                factor = int(float(self.model[index, 0]))
                if Xtest[i, factor] <= float(self.model[index, 1]):
                    step = self.model[index, 2]
                else:
                    step = self.model[index, -1]
                step = float(step)
                index = index + int(step)

            leaf = index
            my_array[i] = self.model[leaf, 1]
            i += 1
            index = 0
        return my_array


    def author(self):
        return 'ymiyamoto3'




