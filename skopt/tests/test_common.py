from functools import partial

import numpy as np
from itertools import product

from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_array_less
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_raises

from skopt.benchmarks import branin
from skopt.dummy_opt import dummy_minimize
from skopt.gp_opt import gp_minimize
from skopt.space import Space
from skopt.tree_opt import forest_minimize
from skopt.tree_opt import gbrt_minimize


# dummy_minimize does not support same parameters so
# treated separately
MINIMIZERS = [gp_minimize,]
ACQUISITION = ["LCB", "PI", "EI"]

for est, acq in product(["dt", "et", "rf"], ACQUISITION):
    MINIMIZERS.append(
        partial(forest_minimize, base_estimator=est, acq=acq))
for acq in ACQUISITION:
    MINIMIZERS.append(partial(gbrt_minimize, acq=acq))


def check_minimizer_api(result, n_models):
    assert(isinstance(result.space, Space))
    assert_equal(len(result.models), n_models)
    assert_equal(len(result.x_iters), 7)
    assert_array_equal(result.func_vals.shape, (7,))

    assert(isinstance(result.x, list))
    assert_equal(len(result.x), 2)

    assert(isinstance(result.x_iters, list))
    for n in range(7):
        assert(isinstance(result.x_iters[n], list))
        assert_equal(len(result.x_iters[n]), 2)

        assert(isinstance(result.func_vals[n], float))

    assert_array_equal(result.x, result.x_iters[np.argmin(result.func_vals)])
    assert_almost_equal(result.fun, branin(result.x))


def check_minimizer_bounds(result):
    # no values should be below or above the bounds
    assert_array_less(result.x_iters, np.tile([10, 15], (7, 1)))
    assert_array_less(np.tile([-5, 0], (7, 1)), result.x_iters)


def test_minimizer_api():
    # dummy_minimize is special as it does not support all parameters
    # and does not fit any models
    result = dummy_minimize(branin, [(-5.0, 10.0), (0.0, 15.0)],
                            n_calls=7, random_state=1)

    yield (check_minimizer_api, result, 0)
    yield (check_minimizer_bounds, result)
    assert_raises(ValueError, dummy_minimize, lambda x: x, [[-5, 10]])

    n_calls = 7
    n_random_starts = 3
    n_models = n_calls - n_random_starts
    for minimizer in MINIMIZERS:
        result = minimizer(branin, [(-5.0, 10.0), (0.0, 15.0)],
                           n_random_starts=n_random_starts,
                           n_calls=n_calls,
                           random_state=1)

        yield (check_minimizer_api, result, n_models)
        yield (check_minimizer_bounds, result)
        assert_raises(ValueError, minimizer, lambda x: x, [[-5, 10]])