# ABAQUS_periodic_boundary_condition_generator
A nifty little GUI for node matching on master-slave surfaces, pairing them and generating lines for use in input file for periodic boundary conditions.

## Prerequisites

* python >= 3.7
* PySimpleGui <https://pysimplegui.readthedocs.io/en/latest/>

## Features
* includes adding strain as displacement of dummy node.
* exclude node sets from constraining equations.
* generates master/slave nodesets and constraining equations.

## Usage
* Should be used top to down step-by-step.
* Surfaces should be defined on part as node sets.
* Excluded node sets should be defined and selected to exclude constraining them.

## Screenshot

![Screenshot](https://github.com/saiwal/ABAQUS_periodic_boundary_condition_generator/blob/dd20b470a6b5c788aa1ff5d00534dc5cb621c141/screenshot.png)
