#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 18:20:34 2022

@author: acad
"""
import PySimpleGUI as sg
import sys
import numpy as np

def makewin():
    sg.ChangeLookAndFeel('GreenTan')         # Add a touch of color

    # All the stuff inside your window.

    layout = [[sg.Multiline('Enter input file',size=(55, 2), key='-inp-'), sg.Input(key='-FILE-', visible=False, enable_events=True), sg.FileBrowse()],
              [sg.B('get COORDS',key='-coord-')],
              [sg.Text('_'  * 100, size=(74, 1))],
              [sg.Text('Master surface name',size=(25,1)), sg.InputText(key='-msurf-')],
              [sg.B('Generate master nodes',key ='-msndgen-')],
              [sg.Text('Slave surface name',size=(25,1)), sg.InputText(key='-ssurf-')],
              [sg.B('Generate slave nodes', key='-slndgen-')],
              [sg.B('Pair nodes',key='-pair-')],
              [sg.Text('_'  * 27, size=(27, 1)),sg.Text('Write node sets', size=(16, 1)),sg.Text('_'  * 27, size=(27, 1))],
              [sg.B('Nset master'), sg.B('Nset slave')],
              [sg.Text('_'  * 30, size=(30, 1)),sg.Text('Parameters', size=(10, 1)),sg.Text('_'  * 30, size=(30, 1))],
              [sg.Text('DOF (1,2 or 3)', size=(25, 1)) ,sg.InputText(' ', key='-dof-')],
              [sg.Text('N (no. of eqs.(3))', size=(25, 1)) ,sg.InputText(' ', key='-N-')],
              [sg.Text('Am coeff. (1)', size=(25, 1)) ,sg.InputText(' ', key='-Am-')],
              [sg.Text('As coeff. (-1)', size=(25, 1)) ,sg.InputText(' ', key='-As-')],
              [sg.Text('Au coeff. (-1,0,1)', size=(25, 1)) ,sg.InputText(' ', key='-Au-')],
              [sg.Text('ndummy (dummy node label)', size=(25, 1)) ,sg.InputText(' ', key='-ndummy-')],
              [sg.Text('  ', size=(55, 1)), sg.B('Write to File',key='-write-')],
              [sg.Exit()],
              [sg.StatusBar(' ',key='-status-'), sg.ProgressBar(100, s=(20,20), key='-prog')]]
    return sg.Window('ABAQUS PBC maker', layout)

def main():

    window = makewin()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if values['-FILE-']:
            window['-inp-'].Update(values['-FILE-'])
            fn = values['-FILE-']
            if event == '-coord-':
                coords = getcoord(fn)
                window['-status-'].update('coords obtained')
            if event == '-msndgen-':
                msnds = getnd(fn,values['-msurf-'])
                window['-status-'].update('master nodes obtained')
            if event == '-slndgen-':
                slnds = getnd(fn,values['-ssurf-'])
                window['-status-'].update('slave nodes obtained')
            if event == '-pair-':
                coord_pair = pairnodes(msnds,slnds,coords)
            if event == '-write-':
                writetof(values,coord_pair)
            if event =='Nset master':
                writend(coord_pair, values['-msurf-'])
            if event =='Nset slave' :
                    writend(coord_pair, values['-ssurf-'])
    window.close()

def getcoord(fn):
    file = open(fn)
    lines = file.readlines()
    c1 = 0
    corin = 0
    cornd = 0
    coord= []
    for line in lines:
        if line.find("*Node") >= 0:
            corin = c1 + 1
            continue
        if corin > 0:
            if line.find("*") >=0:
                cornd = c1
                break
            (nd, nx, ny, nz) = line.split(',')
            coord.append(list((nd, nx, ny, nz)))
        c1 = c1 + 1
    coords = []
    for i in coord:
        i = [x.strip(' ') for x in i]
        i = [x.strip('\n') for x in i]
        i = [float(j) for j in i]
        coords.append(i)
    return (coords)

def getnd(fn, surf):
    file = open(fn)
    lines = file.readlines()
    ctr = 1
    msstr = 0
    msstp = 0
    msnd = []
    lin = "*Nset, nset=" + surf
    for line in lines:
        if line.find(lin) >= 0 :
            msstr = ctr + 1
            continue
        if msstr > 0:
            msnd.append(line)
            #msnd.write(line)
            if line.find("*") >= 0 :
                msstp = ctr
                break
        ctr = ctr + 1
    msnd.pop()
    print(surf+" surface nodes start on line",msstr)
    print(surf+" surface nodes end on line",msstp)
    msnds = []
    tmp = []
    for i in msnd:
        tmp.append(i.strip())
    flatten(tmp)
    msnd = []
    for i in tmp:
        ele = i.split(',')
        for e in ele:
            msnd.append(int(e))
    return(msnd)

def pairnodes(msnds,slnds,coords):
    ln = len(slnds)
    msnds = [[i, 0, 0, 0] for (i) in msnds]
    slnds = [[i, 0, 0, 0] for (i) in slnds]
    ci = 0
    for i in msnds:
        cj = 0
        for j in coords:
            if msnds[ci][0] == coords[cj][0]:
                msnds[ci][1] = coords[cj][1]
                msnds[ci][2] = coords[cj][2]
                msnds[ci][3] = coords[cj][3]
                break
            cj = cj + 1
        ci = ci + 1
    ci = 0
    for i in slnds:
        cj = 0
        for j in coords:
            if slnds[ci][0] == coords[cj][0]:
                slnds[ci][1] = coords[cj][1]
                slnds[ci][2] = coords[cj][2]
                slnds[ci][3] = coords[cj][3]
                break
            cj = cj + 1
        ci = ci + 1
    coord_mas = [u + v for u, v in zip(msnds, slnds)]
    coord_pair = [[0,0,0,0,0,0,0,0]]*ln
    ci = 0
    disp = 20
    for i in coord_mas:
        cj = 0
        for j in coord_mas:
            dis = np.sqrt((j[7]-i[3])**2+(j[6]-i[2])**2+(j[5]-i[1])**2)
            if dis <= disp:
                pair_in = cj
                disp = dis
            cj = cj + 1
        coord_pair[ci][0] = coord_mas[ci][0]
        coord_pair[ci][1] = coord_mas[ci][1]
        coord_pair[ci][2] = coord_mas[ci][2]
        coord_pair[ci][3] = coord_mas[ci][3]
        coord_pair[ci][4] = coord_mas[pair_in][4]
        coord_pair[ci][5] = coord_mas[pair_in][5]
        coord_pair[ci][6] = coord_mas[pair_in][6]
        coord_pair[ci][7] = coord_mas[pair_in][7]
        ci = ci + 1
    print(coord_pair)
    return coord_pair

def writetof(values, coord_pair):

    eqfile = values['-msurf-'] + "_" + values['-ssurf-'] + "_" + values['-dof-'] + "_" + "constraints.txt"
    eqs = open(eqfile, 'w+')
    dof = values['-dof-']
    N = values['-N-']
    Am = values['-Am-']
    Au = values['-Au-']
    As = values['-As-']
    ndummy = values['-ndummy-']
    for i in coord_pair:
        ndm = int(i[0])
        nds = int(i[4])
        eqs.write("*EQUATION\n")
        eqs.write(N+'\n')
        eqs.write("master_"+repr(ndm)+", "+ dof +", "+ Am+'\n')
        eqs.write("slave_"+repr(nds)+", "+ dof +", "+ As+'\n')
        eqs.write(ndummy+ ", "+ dof +", "+ Au+'\n')
    eqs.close()

def writend(coord_pair, surf):
# write nodesets master
    ndsetms = open(surf+"_nodesets.txt", 'w+')
    for i in coord_pair:
        ndsetms.write("*Nset, nset=master_"+repr(int(i[0]))+", instance = Part-1-1"+'\n')
        ndsetms.write(repr(int(i[0]))+","+'\n')



def flatten(nasted_list):
    """
    input: nasted_list - this contain any number of nested lists.
    ------------------------
    output: list_of_lists - one list contain all the items.
    """

    list_of_lists = []
    for item in nasted_list:
        list_of_lists.extend(item)
    return list_of_lists


if __name__ == '__main__':
    main()
