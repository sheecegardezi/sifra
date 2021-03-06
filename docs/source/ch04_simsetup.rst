.. _simulation-inputs:

**************************
Simulation and Model Setup
**************************

Setting a simulation requires populating two different sets of inputs:

- Simulation scenario configuration
- Infrastructure model configuration

These two sets of input data are contained in two separate files. These files,
their parameters, data layout, and sample input data are presented in the
remainder of this Section. In the course of the discussion it should be useful
to the keep the directory structure of the code in mind::

   .
   ├── docs                        <-- Sphinx documentation files
   │   └── source
   ├── hazard                      <-- Hazard scenario files for networks
   ├── installation                <-- Installation scripts for dev envs
   ├── logs
   ├── models                      <-- Infrastructure models reside here
   ├── output                      <-- Default location for simulation results
   ├── scripts
   ├── sifra                       <-- The core code reside here
   │   └── modelling
   ├── simulation_setup            <-- Scenario configuration files
   ├── tests                       <-- Test scripts + data for sanity checks
   │   ├── historical_data
   │   ├── models
   │   └── simulation_setup
   │
   ├── LICENSE                      <-- License file
   ├── README.md                    <-- Summary documentation
   ├── setup.py                     <-- Package setup file
   └── __main__.py                  <-- Entry point for running the code


.. _simulation-setup-file:

Simulation Setup File
=====================

The code needs a setup file for configuring the model and simulation scenario.
It can be in any of three formats: `ini`, `conf`, or `json`. The code first
converts any setup file to json first before running.
The simulation 'scenario' definition file is located in the following directory
(relative to the root dir of source code)::

    ./simulation_setup/

The following table lists the parameters in the config file, their
description, and representative values.

.. include::
   ./_static/files/model_params__simulation_setup.txt

.. .. csv-table::
   :header-rows: 0
   :widths: 10,50
   :stub-columns: 0
   :file: ./_static/files/scenario_config_parameters.csv


.. _model-definition-file:

Infrastructure Model Definition File
====================================

The system definition files for a infrastructure of type ``<sys_type_A>``
is located in the following directory (relative to the root dir of
source code)::

    ./models/<sys_type_A>/

The system model is defined using an MS Excel spreadsheet file.
It contains five worksheets. The names of the worksheets are fixed.
The function and format of these worksheets are described in the
following subsections:


.. _inputdata__component_list:

List of Components: component_list
----------------------------------

The *component_list* has the following parameters:

.. include::
   ./_static/files/model_params__component_list.txt


.. _inputdata__component_connections:

Connections between Components: component_connections
-----------------------------------------------------

.. include::
   ./_static/files/model_params__component_connections.txt


.. _inputdata__supply_setup:

Configuration of Supply Nodes: supply_setup
-------------------------------------------

.. include::
   ./_static/files/model_params__supply_setup.txt


.. _inputdata__output_setup:

Configuration of Output Nodes: output_setup
-------------------------------------------

.. include::
   ./_static/files/model_params__output_setup.txt


.. _inputdata__comp_type_dmg_algo:

Component Type Damage Algorithms: comp_type_dmg_algo
----------------------------------------------------

.. include::
   ./_static/files/model_params__comp_type_dmg_algo.txt


.. _inputdata__damage_state_def:

Definition of Damage States: damage_state_def
---------------------------------------------

This table documents the physical damage characteristics that are implied
by the damage states used to model the fragility of the system components.

.. include::
   ./_static/files/model_params__damage_state_def.txt

