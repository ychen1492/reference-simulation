from darts.models.physics.geothermal import Geothermal
from darts.models.reservoirs.struct_reservoir import StructReservoir
from darts.models.darts_model import DartsModel
from darts.models.physics.iapws.iapws_property_vec import _Backward1_T_Ph_vec
import numpy as np


class Model(DartsModel):

    def __init__(self, total_time, set_nx, set_ny, set_nz, perms, poro,
                 set_dx, set_dy, set_dz, report_time_step, overburden):
        """The constructor of the model

        :param total_time: the total simulation time
        :type total_time: int
        :param set_nx: the number of grid blocks in x direction
        :type set_nx: int
        :param set_ny: the number of grid blocks in y direction
        :type set_ny: int
        :param set_nz: the number of grid blocks in z direction
        :type set_nz: int
        :param perms: permeability values of each grid
        :type perms: np.ndarray
        :param poro: porosity values of each grid
        :type poro: np.ndarray
        :param set_dx: the cartesian resolution in x direction
        :type set_dx: float
        :param set_dy: the cartesian resolution in y direction
        :type set_dy: float
        :param set_dz: the cartesian resolution in z direction
        :type set_dz: float
        :param report_time_step: the time step which is defined for reporting
        :type report_time_step: int
        :param overburden: the number of overburden layers
        :type overburden: int
        """
        # call base class constructor
        super().__init__()

        self.timer.node["initialization"].start()
        # parameters for the reservoir
        (nx, ny, nz) = (set_nx, set_ny, set_nz)
        self.perm = perms
        self.poro = poro
        # add more layers above the reservoir
        underburden = overburden
        nz += (overburden + underburden)
        overburden_prop = np.ones(set_nx * set_ny * overburden) * 1e-5
        underburden_prop = np.ones(set_nx * set_ny * underburden) * 1e-5
        self.perm = np.concatenate([overburden_prop, self.perm, underburden_prop])
        self.poro = np.concatenate([overburden_prop, self.poro, underburden_prop])
        self.report_time = report_time_step
        # add more layers above or below the reservoir
        self.reservoir = StructReservoir(self.timer, nx=nx, ny=ny, nz=nz, dx=set_dx, dy=set_dy, dz=set_dz,
                                         permx=self.perm, permy=self.perm, permz=0.1 * self.perm, poro=self.poro,
                                         depth=2300)
        well_diam = 0.1524
        well_rad = well_diam / 2
        # add larger volumes
        self.reservoir.set_boundary_volume(yz_minus=1e15, yz_plus=1e15, xz_minus=1e15, xz_plus=1e15)
        self.inj_list = [[50, 20], [110, 20], [170, 20], [230, 20], [50, 80], [110, 80], [170, 80], [230, 80]]
        self.prod_list = [[50, 40], [110, 40], [170, 40], [230, 40], [50, 60], [110, 60], [170, 60], [230, 60]]

        for i, inj in enumerate(self.inj_list):
            self.reservoir.add_well('I' + str(i + 1))
            for k in range(1, self.reservoir.nz):
                self.reservoir.add_perforation(self.reservoir.wells[-1], inj[0], inj[1], k, well_radius=well_rad,
                                               multi_segment=False, verbose=True)

        for p, prod in enumerate(self.prod_list):
            self.reservoir.add_well('P' + str(p + 1))
            for k in range(1,  self.reservoir.nz):
                self.reservoir.add_perforation(self.reservoir.wells[-1], prod[0], prod[1], k, well_radius=well_rad,
                                               multi_segment=False, verbose=True)

        self.uniform_pressure = 200
        self.inj_temperature = 300
        self.prod_temperature = 350

        # rock heat capacity and rock thermal conduction
        hcap = np.array(self.reservoir.mesh.heat_capacity, copy=False)
        rcond = np.array(self.reservoir.mesh.rock_cond, copy=False)
        hcap[self.perm <= 1e-5] = 400 * 2.5  # volumetric heat capacity: kJ/m3/K
        hcap[self.perm > 1e-5] = 400 * 2.5

        rcond[self.perm <= 1e-5] = 2.2 * 86.4  # kJ/m/day/K
        rcond[self.perm > 1e-5] = 3 * 86.4

        self.physics = Geothermal(timer=self.timer, n_points=64, min_p=1, max_p=1000,
                                  min_e=10, max_e=50000, mass_rate=False, cache=False)

        # timestep parameters
        self.params.first_ts = 1e-5
        self.params.mult_ts = 8
        self.params.max_ts = 100

        # nonlinear and linear solver tolerance
        self.params.tolerance_newton = 1e-5
        self.params.tolerance_linear = 1e-7
        self.runtime = total_time

        self.timer.node["initialization"].stop()

    def set_initial_conditions(self):
        """This is to set the initial condition of the reservoir

        :return:
            None
        :rtype:
        """
        # self.physics.set_nonuniform_initial_conditions(self.reservoir.mesh, pressure_grad=100, temperature_grad=30)
        self.physics.set_uniform_initial_conditions(self.reservoir.mesh, uniform_pressure=self.uniform_pressure,
                                                    uniform_temperature=self.prod_temperature)

    # T=300K, P=200bars, the enthalpy is 1914.13 [kJ/kg]
    def set_boundary_conditions(self):
        """This is to set the boundary condition, normally to specify the well control and constraint

        :return:
            None
        :rtype:
        """
        for _, w in enumerate(self.reservoir.wells):
            if 'I' in w.name:
                w.control = self.physics.new_rate_water_inj(5500, self.inj_temperature)
                # w.constraint = self.physics.new_bhp_water_inj(200, self.inj_temperature)
            else:
                w.control = self.physics.new_rate_water_prod(5500)
            #     w.control = self.physics.new_mass_rate_water_inj(417000, 1914.13)
            # else:
            #     w.control = self.physics.new_mass_rate_water_prod(417000)

    def export_pro_vtk(self, file_name):
        """Export vtk data for each time step or given timestep for the given file name

        :param file_name: the name of the vtk output
        :type file_name:
        :return:
            None
        :rtype:
        """
        X = np.array(self.physics.engine.X, copy=False)
        nb = self.reservoir.mesh.n_res_blocks
        temp = _Backward1_T_Ph_vec(X[0:2 * nb:2] / 10, X[1:2 * nb:2] / 18.015)
        press = X[0:2 * nb:2]

        local_cell_data = {'Temperature': temp, 'Pressure': press,
                           'Perm': self.reservoir.global_data['permx']}
        self.export_vtk(local_cell_data=local_cell_data, file_name=file_name)

    def export_data(self):
        """Export the pressure, temperature of the reservoir at each timestep and also export the permeability

        :return:
            pressure of the reservoir, temperature of the reservoir, permeability of the reservoir
        :rtype:
            np.ndarray, np.ndarray, np.ndarray
        """
        X = np.array(self.physics.engine.X, copy=False)
        nb = self.reservoir.mesh.n_res_blocks
        temp = _Backward1_T_Ph_vec(X[0:2 * nb:2] / 10, X[1:2 * nb:2] / 18.015)
        press = X[0:2 * nb:2]
        return press, temp, self.reservoir.global_data['permx']

    def run(self, export_to_vtk=False, file_name='data'):
        """Run the simulation with the option to output the vtk and the vtk file name

        :param export_to_vtk: boolean value to decide if the vtk data is exported
        :type export_to_vtk: bool
        :param file_name: the name of the vtk file
        :type file_name: str
        :return:
            None
        :rtype:
        """
        if export_to_vtk:
            well_loc = np.zeros(self.reservoir.n)
            # well_loc[(self.inj_loc[1] - 1) * self.reservoir.nx + self.inj_loc[0] - 1] = -1
            # well_loc[(self.prod_loc[1] - 1) * self.reservoir.nx + self.prod_loc[0] - 1] = 1

            for inj in self.inj_list:
                well_loc[(inj[1] - 1) * self.reservoir.nx + inj[0] - 1] = -1

            for prod in self.prod_list:
                well_loc[(prod[1] - 1) * self.reservoir.nx + prod[0] - 1] = 1

            self.global_data = {'well location': well_loc}

            nb = self.reservoir.mesh.n_res_blocks
            nv = self.physics.n_vars
            X = np.array(self.physics.engine.X, copy=False)
            tempr = _Backward1_T_Ph_vec(X[0:nb * nv:nv] / 10, X[1:nb * nv:nv] / 18.015)
            local_cell_data = {'Temperature': tempr}

            self.export_vtk(local_cell_data=local_cell_data, global_cell_data=self.global_data)

        # now we start to run for the time report--------------------------------------------------------------
        time_step = self.report_time
        even_end = int(self.runtime / time_step) * time_step
        time_step_arr = np.ones(int(self.runtime / time_step)) * time_step
        if self.runtime - even_end > 0:
            time_step_arr = np.append(time_step_arr, self.runtime - even_end)

        self.export_pro_vtk(file_name)
        for ts in time_step_arr:
            for _, w in enumerate(self.reservoir.wells):
                if 'I' in w.name:
                    w.control = self.physics.new_rate_water_inj(5500, self.inj_temperature)
                    # w.constraint = self.physics.new_bhp_water_inj(200, self.inj_temperature)
                else:
                    w.control = self.physics.new_rate_water_prod(5500)
                #     w.control = self.physics.new_mass_rate_water_inj(417000, 1914.13)

                # else:
                #     w.control = self.physics.new_mass_rate_water_prod(417000)

            self.physics.engine.run(ts)
            self.physics.engine.report()
            if export_to_vtk:
                self.export_pro_vtk(file_name)
