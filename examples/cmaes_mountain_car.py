from evox import pipelines, algorithms, problems
from evox.monitors import FitnessMonitor
from evox.utils import TreeAndVector
import jax
import jax.numpy as jnp
from flax import linen as nn

class CarPolicy(nn.Module):
    """A simple model for cartpole"""

    @nn.compact
    def __call__(self, x):
        x = x.at[1].multiply(10)  # normalization
        x = nn.Dense(16)(x)
        x = nn.relu(x)
        x = nn.Dense(3)(x)

        return jnp.argmax(x)


key = jax.random.PRNGKey(42)
model_key, pipeline_key = jax.random.split(key)

model = CarPolicy()
params = model.init(model_key, jnp.zeros((2,)))
adapter = TreeAndVector(params)
monitor = FitnessMonitor()
problem = problems.neuroevolution.Gym(
    env_name="MountainCar-v0",
    policy=jax.jit(model.apply),
    num_workers=16,
    env_per_worker=4,
    controller_options={
        "num_cpus": 0,
        "num_gpus": 0,
    },
    worker_options={"num_cpus": 1, "num_gpus": 1 / 16},
    batch_policy=False,
)
center = adapter.to_vector(params)
# create a pipeline
pipeline = pipelines.StdPipeline(
    algorithm=algorithms.CMA_ES(
        init_mean=center,
        init_stdev=1,
        pop_size=64
    ),
    problem=problem,
    pop_transform=adapter.batched_to_tree,
    fitness_transform=monitor.update,
)
# init the pipeline
state = pipeline.init(pipeline_key)
# run the pipeline for 100 steps
for i in range(100):
    print(monitor.get_min_fitness())
    state = pipeline.step(state)

state, sample_pop = pipeline.sample(state)
# problem._render(state.get_child_state("problem"), adapter.to_tree(sample_pop[0]))

min_fitness = monitor.get_min_fitness()
print(min_fitness)
print(monitor.history)

# 83
# [118.0, 98.0, 98.0, 98.0, 93.0, 93.0, 93.0, 93.0, 93.0, 91.0, 91.0, 88.0, 88.0, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0, 84.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0, 83.0]