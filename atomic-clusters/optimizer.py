import scipy.optimize as spo
from autograd import elementwise_grad as egrad
from potentials.gupta import Gupta
from read_xyz import read_xyz_file
from write_xyz import write_xyz_file

file = "feconi.xyz"
path = f'atomic-clusters/examples/'
atoms, coords = read_xyz_file(f"{path}{file}")

gupta = Gupta(atoms)
potential = lambda x: gupta.potential(x.reshape(len(coords), 3))

sol = spo.minimize(
                potential,
                coords.flatten(),
                method='L-BFGS-B',
                jac=egrad(potential),
                options={
                    "gtol": 1e-8,
                    "maxiter": 1000,
                    "disp": False,
                })

new_coords = sol.x.reshape(-1, 3)
energy = sol.fun

write_xyz_file(f'{path}opt-{file}', atoms, new_coords, energy)
