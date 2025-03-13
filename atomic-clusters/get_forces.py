from potentials.gupta import Gupta
from read_xyz import read_xyz_file

path = 'atomic-clusters/examples/feconi.xyz'
atoms, coords = read_xyz_file(path)

gupta = Gupta(atoms)

energy = gupta.gradient(coords)
print(energy)