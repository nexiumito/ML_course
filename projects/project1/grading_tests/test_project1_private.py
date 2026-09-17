import copy
import numpy as np
import pytest
from typing import Tuple

import solutions
from conftest import ATOL, RTOL

NUM_OBSERVATIONS = 100
DIM = 3
LAMBDA = 0.1
INITIAL_W = np.zeros((DIM + 1,))
MAX_ITERS = 10000
GAMMA = 0.001  # step size

PARAMETERS = [
    ("least_squares", []),
    ("mean_squared_error_gd", [INITIAL_W.copy(), MAX_ITERS, GAMMA]),
    ("mean_squared_error_sgd", [INITIAL_W.copy(), MAX_ITERS, GAMMA]),
    ("ridge_regression", [LAMBDA]),
    ("logistic_regression", [INITIAL_W.copy(), MAX_ITERS, GAMMA]),
    ("reg_logistic_regression", [LAMBDA, INITIAL_W.copy(), MAX_ITERS, GAMMA]),
]


@pytest.fixture()
def tx_and_y():
    np.random.seed(0)
    x = np.random.rand(NUM_OBSERVATIONS, DIM)
    x = solutions.normalize_data(x)
    tx = np.hstack([np.ones((NUM_OBSERVATIONS, 1)), x])
    y = np.random.rand(
        NUM_OBSERVATIONS,
    )
    return (tx, y)


@pytest.mark.parametrize("function_name,extra_args", PARAMETERS)
def test_run_without_crashing(
    student_implementations, function_name, tx_and_y, extra_args, mocker
):
    mocker.patch("numpy.linalg.inv")
    tx, y = tx_and_y

    if "logistic" in function_name:
        y = (y > 0.5) * 1.0

    fn = getattr(student_implementations, function_name)
    fn(y, tx, *extra_args)
    np.linalg.inv.assert_not_called()


@pytest.mark.parametrize("function_name,extra_args", PARAMETERS)
def test_correct_loss(
    student_implementations,
    function_name: str,
    tx_and_y: Tuple[np.ndarray, np.ndarray],
    extra_args,
):
    tx, y = tx_and_y

    if "sgd" in function_name.lower():
        # Hack to remove stochasticity in SGD, not testing more than GD...
        tx, y = (tx[:1], y[:1])

    if "logistic" in function_name:
        y = (y > 0.5) * 1.0

    # Copy the original arguments such that mutating them in the implementation
    # does not affect other calls.

    fn_solution = getattr(solutions, function_name)
    _, loss_solution = fn_solution(y.copy(), tx.copy(), *copy.deepcopy(extra_args))

    fn = getattr(student_implementations, function_name)
    _, loss = fn(y.copy(), tx.copy(), *copy.deepcopy(extra_args))

    np.testing.assert_allclose(loss, loss_solution, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("function_name,extra_args", PARAMETERS)
def test_correct_weights(
    student_implementations,
    function_name,
    tx_and_y: Tuple[np.ndarray, np.ndarray],
    extra_args,
):
    tx, y = tx_and_y

    if "sgd" in function_name.lower():
        # Hack to remove stochasticity in SGD, not testing more than GD but better than nothing...
        tx, y = (tx[:1], y[:1])

    if "logistic" in function_name:
        y = (y > 0.5) * 1.0

    # Copy the original arguments such that mutating them in the implementation
    # does not affect other calls.

    fn_solution = getattr(solutions, function_name)
    weights_solution, _ = fn_solution(y.copy(), tx.copy(), *copy.deepcopy(extra_args))

    fn = getattr(student_implementations, function_name)
    weights, _ = fn(y.copy(), tx.copy(), *copy.deepcopy(extra_args))

    np.testing.assert_allclose(weights, weights_solution, rtol=RTOL, atol=ATOL)
