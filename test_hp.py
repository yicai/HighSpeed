from hyperopt import hp, fmin, rand, tpe, space_eval
from functools import  partial


def q(args):
    x, y = args
    return x**2 + y**2

space = [hp.uniform('x', 0, 1), hp.normal('y', 0, 1)]
#best = fmin(q, space, rand, tpe, space_eval)
best = fmin(q, space, algo=rand.suggest, max_evals=10)
print(space_eval(space, best))
print(best)

algo = partial(tpe.suggest, n_startup_jobs=10)
best = fmin(q, space, algo=algo, max_evals=20)
print(space_eval(space, best))
print(best)