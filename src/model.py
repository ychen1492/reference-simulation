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
        nz += (overburden+underburden)
        overburden_prop = np.ones(set_nx * set_ny * overburden) * 1e-5
        underburden_prop = np.ones(set_nx * set_ny * underburden) * 1e-5
        self.perm = np.concatenate([overburden_prop, self.perm, underburden_prop])
        self.poro = np.concatenate([overburden_prop, self.poro, underburden_prop])
        self.report_time = report_time_step
        # add more layers above or below the reservoir
        self.reservoir = StructReservoir(self.timer, nx=nx, ny=ny, nz=nz, dx=set_dx, dy=set_dy, dz=set_dz,
                                         permx=self.perm, permy=self.perm, permz=0.1*self.perm, poro=self.poro,
                                         depth=2300)

        # add larger volumes
        self.reservoir.set_boundary_volume(yz_minus=1e15, yz_plus=1e15, xz_minus=1e15, xz_plus=1e15)
        # given the x spacing 4500m, the distance between injection well and boundary is 2400m
        # well spacing is 1300m
        # add well's locations
        injection_well_x = int(2400/set_dx)
        production_well_x = injection_well_x + int(1300/set_dx)
        self.iw = [injection_well_x, production_well_x]
        self.jw = [int(set_ny/2), int(set_ny/2)]

        self.well_index = 100

        # add well
        self.reservoir.add_well("INJ")
        # add perforations to the payzone
        start_index = overburden + 1
        end_index = nz - underburden + 1
        for n in range(start_index, end_index):
            self.reservoir.add_perforation(well=self.reservoir.wells[-1], i=self.iw[0], j=self.jw[0], k=n,
                                           well_index=self.well_index, multi_segment=False)

        # add well
        self.reservoir.add_well("PRD")
        # add perforations to te payzone 
        for n in range(start_index, end_index):
            self.reservoir.add_perforation(self.reservoir.wells[-1], i=self.iw[1], j=self.jw[1], k=n,
                                           well_index=self.well_index, multi_segment=False)

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
                w.control = self.physics.new_rate_water_inj(7500, self.inj_temperature)
                # w.constraint = self.physics.new_bhp_water_inj(200, self.inj_temperature)
            else:
                w.control = self.physics.new_rate_water_prod(7500)
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
            # injection well
            well_loc[(self.jw[0] - 1) * self.reservoir.nx + self.iw[0] - 1] = -1
            # production well
            well_loc[(self.jw[1] - 1) * self.reservoir.nx + self.iw[1] - 1] = 1
            self.global_data = {'well location': well_loc}
            self.export_vtk(file_name, global_cell_data=self.global_data)

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
                    w.control = self.physics.new_rate_water_inj(7500, self.inj_temperature)
                    # w.constraint = self.physics.new_bhp_water_inj(200, self.inj_temperature)
                else:
                    w.control = self.physics.new_rate_water_prod(7500)
                #     w.control = self.physics.new_mass_rate_water_inj(417000, 1914.13)
                    
                # else:
                #     w.control = self.physics.new_mass_rate_water_prod(417000)
                 
            self.physics.engine.run(ts)
            self.physics.engine.report()
            if export_to_vtk:
                self.export_pro_vtk(file_name)