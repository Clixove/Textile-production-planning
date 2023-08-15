import numpy as np
from scipy.optimize import linprog
from sklearn.base import TransformerMixin
import contextlib
import joblib
from tqdm import tqdm


# Reference: https://stackoverflow.com/questions/24983493/tracking-progress-of-joblib-parallel-execution
@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """
    Context manager to patch joblib to report into tqdm progress bar given as argument
    """
    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()
# Reference end.


class DEA(TransformerMixin):
    def __init__(self, input_cols=None, output_cols=None):
        self.input_cols = input_cols
        self.output_cols = output_cols
        self.input_mat = None
        self.output_mat = None
        self.n = None
        self.n_input_var = len(input_cols)
        self.n_output_var = len(output_cols)

    def fit(self, x, *args):
        self.input_mat = x[self.input_cols].values
        self.output_mat = x[self.output_cols].values
        self.n = x.shape[0]
        return self

    def transform(self, x):
        n = x.shape[0]
        output_mat = x[self.output_cols].values
        z_input = np.zeros(shape=self.n_input_var)
        inequality_left = np.hstack([self.output_mat, - self.input_mat])
        inequality_right = np.zeros(shape=self.n)
        z_output = np.zeros(shape=(1, self.n_output_var))
        equality_right = np.array([1.])

        def parallel_dea(i):
            opt = linprog(
                c=np.hstack([- output_mat[i, :], z_input]),
                A_ub=inequality_left, b_ub=inequality_right,
                A_eq=np.hstack([z_output, self.input_mat[i:i + 1, :]]), b_eq=equality_right,
                method='highs'
            )
            return - opt.fun

        with tqdm_joblib(tqdm(total=n)):
            solution = joblib.Parallel(n_jobs=-1)(joblib.delayed(parallel_dea)(i) for i in range(n))
        return np.maximum(np.minimum(solution, 1), 0)
