import pandas as pd
from sklearn.base import TransformerMixin
import numpy as np


class ArrayToVariable(TransformerMixin):
    def __init__(self, col_order=None, col_names=None):
        self.col_order = col_order
        self.col_names = col_names

    def fit(self, x, *args, **kwargs):
        return self

    def transform(self, x, *args, **kwargs):
        x_ = x[:, self.col_order]
        if self.col_names:
            assert len(self.col_names) == len(self.col_order), \
                'The length of column names should be the same as the width of the matrix.'
            x_ = pd.DataFrame(data=x_, columns=self.col_names)
        return x_


class DropColumn(TransformerMixin):
    def __init__(self, cols=None):
        self.cols = cols

    def fit(self, x, *args, **kwargs):
        return self

    def transform(self, x, *args, **kwargs):
        return x.drop(self.cols, axis=1)


class ApplyColumn(TransformerMixin):
    def __init__(self, cols=None, func=None, new_cols=None):
        self.cols = cols
        self.func = func
        assert len(cols) == len(new_cols), 'Lists of old and new column names should have the same length.'
        self.new_cols = new_cols

    def fit(self, x, *args, **kwargs):
        return self

    def transform(self, x, *args, **kwargs):
        x_ = x.copy()
        for old_col, new_col in zip(self.cols, self.new_cols):
            x_[new_col] = x[old_col].apply(self.func)
        return x_


class GaussianAbnormal(TransformerMixin):
    def __init__(self, cols=None, std_range=3):
        """
        Move abnormal values into "mean ± std_range * std" assuming variables satisfying Gaussian distribution.
        :param cols: The columns to perform Gaussian abnormal processing.
        :param std_range: Values outside "mean ± std_range * std" are abnormal ones.
        """
        self.cols = cols
        self.std_range = std_range
        self.lower_bound = None
        self.upper_bound = None

    def fit(self, x, *args, **kwargs):
        mean_ = np.nanmean(x, axis=0)
        std_3 = self.std_range * np.nanstd(x, axis=0)
        self.lower_bound = mean_ - std_3
        self.upper_bound = mean_ + std_3
        return self

    def transform(self, x, *args, **kwargs):
        x_ = x.copy()
        x_[self.cols] = x[self.cols].clip(lower=self.lower_bound, upper=self.upper_bound, axis=1)
        return x_


class ForceFloat64(TransformerMixin):
    def __init__(self): pass

    def fit(self, x, *args, **kwargs):
        return self

    @staticmethod
    def transform(x, *args, **kwargs):
        return x.astype('float64')
