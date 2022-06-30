import pandas as pd
from sklearn.base import TransformerMixin
import numpy as np


class ArrayExchangeColumn(TransformerMixin):
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
    def __init__(self, cols=None, func=None, new_cols=None, new_cols_prefix=None, inplace=False):
        self.cols = cols
        self.func = func
        if new_cols:
            assert len(cols) == len(new_cols), 'Lists of old and new column names should have the same length.'
            self.new_cols = new_cols
        elif new_cols_prefix:
            self.new_cols = [f'{x}_{new_cols_prefix}' for x in cols]
        else:
            self.new_cols = cols
        self.inplace = inplace

    def fit(self, x, *args, **kwargs):
        return self

    def transform(self, x, *args, **kwargs):
        x_ = x.copy()
        if self.inplace:
            x_.drop(self.cols, axis=1, inplace=True)
        for old_col, new_col in zip(self.cols, self.new_cols):
            x_[new_col] = x[old_col].apply(self.func)
        return x_


class GaussianAbnormal(TransformerMixin):
    def __init__(self, cols=None, std_range=3, upper_only=False):
        """
        Move abnormal values into "mean ± std_range * std" assuming variables satisfying Gaussian distribution.
        :param cols: The columns to perform Gaussian abnormal processing.
        :param std_range: Values outside "mean ± std_range * std" are abnormal ones.
        """
        self.cols = cols
        self.std_range = std_range
        self.lower_bound = None
        self.upper_bound = None
        self.upper_only = upper_only

    def fit(self, x, *args, **kwargs):
        average = np.nanmean(x[self.cols], axis=0)
        stdev = np.nanstd(x[self.cols], axis=0)
        self.lower_bound = dict(zip(self.cols, average - self.std_range * stdev))
        self.upper_bound = dict(zip(self.cols, average + self.std_range * stdev))
        return self

    def transform(self, x, *args, **kwargs):
        x_ = x.copy()
        for col in self.cols:
            x_.loc[x[col] > self.upper_bound[col], col] = self.upper_bound[col]
            if not self.upper_only:
                x_.loc[x[col] < self.lower_bound[col], col] = self.lower_bound[col]
        return x_

    @staticmethod
    def inverse_transform(x, *args, **kwargs): return x


class ForceFloat64(TransformerMixin):
    def __init__(self): pass

    def fit(self, x, *args, **kwargs): return self

    @staticmethod
    def transform(x, *args, **kwargs): return x.astype('float64')