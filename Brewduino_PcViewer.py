#!/usr/bin/env python

# Affichage des donnees recues du brewduino, par le Bluetooth.

##########
# IMPORT #
##########

import threading
import time
from brew_tools import brew_maths
import PySimpleGUI as Sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from DataReceiver import *

###########
# GLOBALS #
###########


_RUN_ = True
_GRAPHRUN_ = False


############
# FONCTION #
############

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

serialportdispo = DataReceiver.serial_ports()

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

# _______________________________ tab Info --------------------------------------------------------------------------
# tab info - colonne info
layout_col1 = [[Sg.Text(' ', size=(13, 1))],
               [Sg.Text('Temperature :', font=("Helvetica", 16), size=(13, 2), justification='right'),
                Sg.Text(' ', font=("Helvetica", 16), size=(5, 2), key='_TEMPERATURE_', justification='right'),
                Sg.Text('°', font=("Helvetica", 16), size=(5, 2))],
               [Sg.Text('Consigne :', font=("Helvetica", 16), size=(13, 2), justification='right'),
                Sg.Text(' ', font=("Helvetica", 16), size=(5, 2), key='_SETPOINT_', justification='right'),
                Sg.Text('°', font=("Helvetica", 16), size=(5, 2))],
               [Sg.Text('pompe :', font=("Helvetica", 16), size=(13, 2), justification='right'),
                Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_POMP_')],
               [Sg.Text('Heater :', font=("Helvetica", 16), size=(13, 2), justification='right'),
                Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_HEATER_')],
               [Sg.Text('Mode :', font=("Helvetica", 16), size=(13, 2), justification='right'),
                Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_MODE_')],
               [Sg.Text('Tempo :', font=("Helvetica", 16), size=(13, 2), justification='right'),
                Sg.Text(' ', font=("Helvetica", 16), size=(8, 2), key='_TEMPO_')],
               [Sg.Text(' ', size=(13, 1))]
               ]
layout_frame_col1 = [[Sg.Frame('Infos', layout_col1, font=("Helvetica", 12))]]

# tab info - colonne systeme
layout_col2 = [[Sg.Image('ressources/cuvePoffHoff.png', key='_IMAGE_', pad=((50, 50), (50, 50)))]]
layout_frame_col2 = [[Sg.Frame('Système', layout_col2, font=("Helvetica", 12))]]

# tab info - colonne graphique
layout_col3 = [[Sg.Canvas(key="_CANVAS_")],
               [Sg.Button(" Start ", font=("Helvetica", 12), key='_GRAPHBUTTON_'),
                Sg.Button(" Reset ", font=("Helvetica", 12), key='_RESETBUTTON_')]]
layout_frame_col3 = [[Sg.Frame('Courbes', layout_col3, font=("Helvetica", 12))]]

# tab info - connection Bluetooth + 3 col + logo
layout_info = [
    [Sg.Image('ressources/bluethoot_off.png', size=(25, 25), key="_IMAGEBTCONNECT_"), Sg.Text('', pad=(0, 20)),
     Sg.Combo(serialportdispo, font=("Helvetica", 12), size=(15, 0), key="_INSERIALPORT_",
              tooltip='selectionner le port a utiliser', readonly=True),
     Sg.Button("Connecter", font=("Helvetica", 12), key='_BTBUTTON_')],
    [Sg.Column(layout_frame_col1), Sg.Column(layout_frame_col2), Sg.Column(layout_frame_col3)],
    [Sg.Image('ressources/process_0.png', pad=((150, 350), (20, 20))), Sg.Image('Hop_BW.png'),
     Sg.Text('V0.1', font=("Helvetica", 8), pad=((0, 0), (30, 0)))]]

# -------------------------------------------- tab Outils -----------------------------------------------------------
layout_outils_col1 = [[Sg.Text("", font=("Helvetica", 14))],
                 # frame Ajustement de la densité
                 [Sg.Frame(title="Ajustement de la densitée", font=("Helvetica", 14), layout=[
                     [Sg.Text("", font=("Helvetica", 14))],
                     [Sg.Text("Volume de moût (L) : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(size=(5, 1), justification="Right", key="_VolMout_", font=("Helvetica", 14))],
                     [Sg.Text("Densité actuelle : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(default_text="1.0", size=(5, 1), justification="Right", key="_DensiteMout_",
                               font=("Helvetica", 14))],
                     [Sg.Text("Densité souhaité : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(default_text="1.0", size=(5, 1), justification="Right", key="_DensiteMoutCible_",
                               font=("Helvetica", 14))],
                     [Sg.Text("Volume d'eau ajusté : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(disabled=True, size=(5, 1), justification="Right", key="_AjustResult_",
                               font=("Helvetica", 14), disabled_readonly_background_color="grey")],
                     [Sg.Text("", font=("Helvetica", 14))],
                     [Sg.Button("Calculer", key="_bouttonCalculerAjust_", font=("Helvetica", 12),
                                pad=((80, 0), (0, 0)))]])],
                 [Sg.Text("", font=("Helvetica", 14))],
                 # calcul du volume d'alcool
                 [Sg.Frame(title="calcul du volume d'alcool", font=("Helvetica", 14), layout=[
                     [Sg.Text("", font=("Helvetica", 14))],
                     [Sg.Text("Densité Initiale : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(default_text="1.0", size=(5, 1), justification="Right", key="_DI_",
                               font=("Helvetica", 14))],
                     [Sg.Text("Densité Finale : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(default_text="1.0", size=(5, 1), justification="Right", key="_DF_",
                               font=("Helvetica", 14))],
                     [Sg.Text("Volume d'alcool : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(disabled=True, size=(5, 1), justification="Right", key="_ResultAcool_",
                               font=("Helvetica", 14), disabled_readonly_background_color="grey")],
                     [Sg.Text("", font=("Helvetica", 14))],
                     [Sg.Button("Calculer", key="_bouttonCalculerAlcool_", font=("Helvetica", 12),
                                pad=((80, 0), (0, 0)))]])],
                 [Sg.Text("", font=("Helvetica", 14))],
                 ]

layout_outils_col2 = [[Sg.Text("", font=("Helvetica", 14))],
                 # frame Ajustement mesure en temperature
                 [Sg.Frame(title="Ajustement mesure de densitée", font=("Helvetica", 14), layout=[
                     [Sg.Text("", font=("Helvetica", 14))],
                     [Sg.Text("mesure densité : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(size=(5, 1), justification="Right", key="_MesDensite_", font=("Helvetica", 14))],
                     [Sg.Text("T° de mesure (°C) : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(size=(5, 1), justification="Right", key="_TempMessure_", font=("Helvetica", 14))],
                     [Sg.Text("T° de calibration (°C) : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(default_text="21", size=(5, 1), justification="Right", key="_TempCal_",
                               font=("Helvetica", 14))],
                     [Sg.Text("mesure corrigé : ", font=("Helvetica", 12), size=(20, 1), justification="Right"),
                      Sg.Input(disabled=True, size=(5, 1), justification="Right", key="_MessCorrigeResult_",
                               font=("Helvetica", 14), disabled_readonly_background_color="grey")],
                     [Sg.Text("", font=("Helvetica", 14))],
                     [Sg.Button("Calculer", key="_bouttonCalculerCorrection_", font=("Helvetica", 12),
                                pad=((80, 0), (0, 0)))]])],
                 [Sg.Text("", font=("Helvetica", 14))],
                 ]

layout_outils_frame_col1 = [[Sg.Frame('', layout_outils_col1, font=("Helvetica", 12), relief="flat", vertical_alignment="top")]]
layout_outils_frame_col2 = [[Sg.Frame('', layout_outils_col2, font=("Helvetica", 12), relief="flat", vertical_alignment="top")]]

layout_outils = [[Sg.Column(layout_outils_frame_col1), Sg.Column(layout_outils_frame_col2)]]

# Layout global
layout = [[Sg.TabGroup([[Sg.Tab('  Info  ', layout_info), Sg.Tab(' Outils ', layout_outils)]], font=("Helvetica", 14))]]

# Create the Window
window = Sg.Window('Brewduino', layout, default_element_size=(10, 1), font=('Helvetica', 25), icon=icon, finalize=True)

canvas_elem = window['_CANVAS_']
canvas = canvas_elem.TKCanvas
# draw the initial plot in the window
fig = Figure(figsize=(6, 3.7))
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
        ser = DataReceiver.connect_serial_port(values['_INSERIALPORT_'])
        if not ser:
            Sg.popup_ok("\nErreur de connection au Brewduino ", title='erreur de connection', icon=icon,
                        font=("Helvetica", 12))
        elif ser:
            decoderthread = threading.Thread(target=DataReceiver.receive, daemon=True)
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
    elif event == "_bouttonCalculerAjust_":
        try:
            result = brew_maths.adjust_gravity_volume(float(window["_VolMout_"].Get()),
                                                      float(window["_DensiteMout_"].Get()),
                                                      float(window["_DensiteMoutCible_"].Get()))
            window["_AjustResult_"].update('%.2f' % result)
        except Exception:
            window["_AjustResult_"].update("")

    elif event == "_bouttonCalculerAlcool_":
        try:
            result = (float(window["_DI_"].Get()) - float(window["_DF_"].Get())) * 131.25
            window["_ResultAcool_"].update('%.2f' % result)
        except Exception:
            window["_ResultAcool_"].update("")
    elif event == "_bouttonCalculerCorrection_":
        try:
            Dlue = float(window["_MesDensite_"].Get()) * 100
            Te = float(window["_TempMessure_"].Get())
            Tc = float(window["_TempCal_"].Get())
            result = Dlue + 0.00352871 * (Te - Tc) ** 2 + 0.225225 * (Te - Tc)
            result = result / 100
            window["_MessCorrigeResult_"].update('%.3f' % result)
        except Exception:
            window["_MessCorrigeResult_"].update("")

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
