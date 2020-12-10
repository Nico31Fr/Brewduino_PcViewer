#!/usr/bin/env python

# Affichage des donnees recues du brewduino, par le Bluetooth.

##########
# IMPORT #
##########

import serial
import PySimpleGUI as Sg
import threading
import time
import sys
import os
import glob
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

###########
# GLOBALS #
###########

# couleur du fond de la fenetre
fontdefenetre = '#41B77F'
_RUN_ = True
_GRAPHRUN_ = False


############
# FONCTION #
############


def connect_serial_port(portname, sg_local):
    try:
        seri = serial.Serial(portname, 9600, 8)

    except serial.SerialException:
        error_message = sys.exc_info()
        sg_local.popup_ok("\nErreur de connection au Brewduino :\n", error_message, "\n", title='erreur de connection', icon=icon, font=("Helvetica", 12))
        return False

    seri.reset_input_buffer()
    return seri


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/rfcomm*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/rfcomm*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def receive():
    global tempe
    global setpont
    global pomp
    global heater
    global mode
    global tempo
    global image_cuve
    global ser

    image_cuve = 'ressources/cuvePoffHoff.png'
    ser.reset_input_buffer()
    print("start threat")
    while _RUN_:
        time.sleep(0.1)
        buffer = str(ser.readline())
        buffer = buffer[0:buffer.rfind('|')]
        rx_buffer = buffer.split('|')
        i = 1
        if len(rx_buffer) > 3:
            while i < len(rx_buffer):
                if rx_buffer[i][0:2] == "Tp":
                    tempe = rx_buffer[i][2:]
                elif rx_buffer[i][0:2] == "Sp":
                    setpont = rx_buffer[i][2:]
                elif rx_buffer[i][0:2] == "Po":
                    if rx_buffer[i][2:] == "0":
                        pomp = "Off"
                    else:
                        pomp = "On"
                elif rx_buffer[i][0:2] == "He":
                    if rx_buffer[i][2:] == "0":
                        heater = "Off"
                    else:
                        heater = "On"
                elif rx_buffer[i][0:2] == "Mo":
                    mode = rx_buffer[i][2:]
                elif rx_buffer[i][0:2] == "Te":
                    tempo = rx_buffer[i][2:]
                else:
                    print("> Balise inconnue !")
                i = i + 1
        # print('fin de reception')
        if pomp == "Off" and heater == "Off":
            image_cuve = 'ressources/cuvePoffHoff.png'
        elif pomp == "On" and heater == "Off":
            image_cuve = 'ressources/cuvePonHoff.png'
        elif pomp == "Off" and heater == "On":
            image_cuve = 'ressources/cuvePoffHon.png'
        elif pomp == "On" and heater == "On":
            image_cuve = 'ressources/cuvePonHon.png'


def draw_figure(canvas_local, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas_local)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


########
# INIT #
########


tempe = "0.0"
setpont = "0.0"
pomp = " "
heater = " "
mode = " "
tempo = "00:00:00"
image_cuve = 'ressources/cuvePoffHoff.png'
x = []
y = []
ysp = []

serialportdispo = serial_ports()

# select windows icon compatible file (OS dependant)
if sys.platform.startswith('win'):
    icon = 'Hop.ico'
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    icon = 'Hop.png'
elif sys.platform.startswith('darwin'):
    icon = 'Hop.png'
else:
    raise EnvironmentError('Unsupported platform')

#######
# GUI #
#######

Sg.theme('GreenMono')  # Add a touch of color
# All the stuff inside your window.
layout_col1 = [[Sg.Text('Temperature :', font=("Helvetica", 16), size=(15, 2), justification='right'), Sg.Text(' ', font=("Helvetica", 16), size=(5, 2), key='_TEMPERATURE_', justification='right'), Sg.Text('°', font=("Helvetica", 16), size=(0, 2))],
               [Sg.Text('Consigne :', font=("Helvetica", 16), size=(15, 2), justification='right'), Sg.Text(' ', font=("Helvetica", 16), size=(5, 2), key='_SETPOINT_', justification='right'), Sg.Text('°', font=("Helvetica", 16), size=(0, 2))],
               [Sg.Text('pompe :', font=("Helvetica", 16), size=(15, 2), justification='right'), Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_POMP_')],
               [Sg.Text('Heater :', font=("Helvetica", 16), size=(15, 2), justification='right'), Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_HEATER_')],
               [Sg.Text('Mode :', font=("Helvetica", 16), size=(15, 2), justification='right'), Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_MODE_')],
               [Sg.Text('Tempo :', font=("Helvetica", 16), size=(15, 2), justification='right'), Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_TEMPO_')]
               ]
layout_frame_col1 = [[Sg.Frame('Infos', layout_col1, font=("Helvetica", 12), size=(120, 60))]]

layout_col2 = [[Sg.Image('ressources/cuvePoffHoff.png', key='_IMAGE_')]]
layout_frame_col2 = [[Sg.Frame('Système', layout_col2, font=("Helvetica", 12))]]

layout_col3 = [[Sg.Canvas(key="_CANVAS_")],
               [Sg.Button(" Start ", font=("Helvetica", 12), key='_GRAPHBUTTON_'), Sg.Button(" Reset ", font=("Helvetica", 12), key='_RESETBUTTON_')]]
layout_frame_col3 = [[Sg.Frame('Courbes', layout_col3, font=("Helvetica", 12), size=(120, 20))]]

layout = [[Sg.Image('ressources/bluethoot_off.png', size=(25, 25), key="_IMAGEBTCONNECT_"), Sg.Text('', pad=(0, 20)), Sg.Combo(serialportdispo, font=("Helvetica", 12), size=(15, 0), key="_INSERIALPORT_", tooltip='selectionner le port a utiliser', readonly=True), Sg.Button("Connecter", font=("Helvetica", 12), key='_BTBUTTON_')],
          [Sg.Column(layout_frame_col1), Sg.Column(layout_frame_col2), Sg.Column(layout_frame_col3)],
          [Sg.Text('', pad=(360, 10)), Sg.Image('Hop_BW.png'), Sg.Text('V0.1', font=("Helvetica", 8), pad=((0, 0), (30, 0)))]]

# Create the Window
window = Sg.Window('Brewduino', layout, default_element_size=(10, 1), font=('Helvetica', 25), icon=icon, finalize=True)

canvas_elem = window['_CANVAS_']
canvas = canvas_elem.TKCanvas
# draw the initial plot in the window
fig = Figure(figsize=(4, 3))
ax = fig.add_subplot(111)
ax.set_ylabel("température")
ax.set_xticks([])
ax.locator_params(nbins=4)
fig_agg = draw_figure(canvas, fig)

########
# MAIN #
########

while True:
    event, values = window.read(timeout=1000)

    if event == Sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    elif event == "_BTBUTTON_":
        ser = connect_serial_port(values['_INSERIALPORT_'], Sg)
        if ser:
            decoderthread = threading.Thread(target=receive, daemon=True)
            window['_IMAGEBTCONNECT_'].update('ressources/bluethoot_on.png')
            window['_BTBUTTON_'].update(disabled=True)
            decoderthread.start()
    elif event == "_GRAPHBUTTON_":
        _GRAPHRUN_ = True
        window['_GRAPHBUTTON_'].update(disabled=True)
    elif event == "_RESETBUTTON_":
        x.clear()
        y.clear()
        ysp.clear()

    window['_TEMPERATURE_'].update(tempe)
    window['_SETPOINT_'].update(setpont)
    window['_POMP_'].update(pomp)
    window['_HEATER_'].update(heater)
    window['_MODE_'].update(mode)
    window['_TEMPO_'].update(tempo)
    window['_IMAGE_'].update(image_cuve)
    if _GRAPHRUN_:
        x.append(time.strftime('%H:%M:%S', time.gmtime()))
        y.append(float(tempe.replace(',', '.')))
        ysp.append(float(setpont.replace(',', '.')))
        ax.cla()  # clear the subplot
        ax.plot(x, y, color='purple', label='temperature cuve')
        ax.plot(x, ysp, color='red', label='consigne')
        ax.legend()
        ax.set_xticks([])
        fig_agg.draw()

# fermeture
window.close()
_RUN_ = False
