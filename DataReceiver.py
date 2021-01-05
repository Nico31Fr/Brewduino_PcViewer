import serial
import glob
import sys

class DataReceiver:

    def __init__(self):
        pass

    def connect_serial_port(portname):
        try:
            seri = serial.Serial(portname, 9600, 8)

        except serial.SerialException:
            print(sys.exc_info())
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