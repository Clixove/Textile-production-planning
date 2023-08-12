import numpy as np
from sklearn.base import TransformerMixin, BaseEstimator
from scipy.optimize import linprog


class DEA(TransformerMixin, BaseEstimator):
    def __init__(self, input_cols=None, output_cols=None):
        self.input_cols = input_cols
        self.output_cols = output_cols
        self.input_mat = None
        self.output_mat = None
        self.ni = len(input_cols)
        self.no = len(output_cols)

    def fit(self, x, *args):
        self.input_mat = x[self.input_cols].values
        self.output_mat = x[self.output_cols].values
        return self

    def predict(self, x):
        n = x.shape[0]
        x_out = x[self.output_cols].values
        efficients = np.zeros(shape=n)
        for i in np.arange(n):
            opt = linprog(
                c=np.hstack([-x_out[i, :], np.zeros(shape=self.ni)]),
                A_ub=np.hstack([self.output_mat, -self.input_mat]),
                b_ub=np.zeros(shape=self.output_mat.shape[0]),
                A_eq=np.hstack([np.zeros(shape=(1, self.no)), self.input_mat[i:i + 1, :]]),
                b_eq=np.array([1.]),
            )
            efficients[i] = - opt.fun
        return efficients
