from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time
import os
from picamera2 import Picamera2, Preview
from io import BytesIO
import pigpio
app = Flask(__name__)

# Ustawienie trybu pinów GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Wyłączenie ostrzeżeń GPIO

# Definicja pinów
pin_en2 = 37 #Numeracja pinu RaspberryPi
pin_in3 = 13 #Numeracja pinu RaspberryPi
pin_in4 = 15 #Numeracja pinu RaspberryPi
pin_en = 22 #Numeracja pinu RaspberryPi
pin_in1 = 16 #Numeracja pinu RaspberryPi
pin_in2 = 18 #Numeracja pinu RaspberryPi
pin_servo = 17 #Numeracja pinu RaspberryPi
camera = Picamera2()
config = camera.preview_configuration.sensor.output_size = (1332, 990)
camera.configure("preview")
camera.start()
photos_folder = os.path.expanduser('/home/daniel/Desktop/static')
photos = sorted([filename for filename in os.listdir(photos_folder) if filename.endswith('.jpg')])
print(photos)

# Ustawienie pinów jako wyjścia
GPIO.setup(pin_en, GPIO.OUT)
GPIO.setup(pin_in1, GPIO.OUT)
GPIO.setup(pin_in2, GPIO.OUT)
GPIO.setup(pin_en2, GPIO.OUT)
GPIO.setup(pin_in3, GPIO.OUT)
GPIO.setup(pin_in4, GPIO.OUT)

# Ustawienie PWM
pwm = GPIO.PWM(pin_en, 1000)  # 1000 Hz (częstotliwość sygnału PWM)
pwm2 = GPIO.PWM(pin_en2, 1000)  # 1000 Hz (częstotliwość sygnału PWM)
pwm.start(0)  # Wartość wypełnienia PWM: 0 (silnik zatrzymany)
pwm2.start(0)  # Wartość wypełnienia PWM: 0 (silnik zatrzymany)

# Inicjalizacja pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Nie można połączyć się z pigpio. Upewnij się, że daemon pigpio jest uruchomiony.")
    exit()

# Funkcja do obracania kół
def rotate(direction, speed, speedturn):
    if direction:
        GPIO.output(pin_in1, GPIO.HIGH)
        GPIO.output(pin_in2, GPIO.LOW)
        GPIO.output(pin_in4, GPIO.HIGH)
        GPIO.output(pin_in3, GPIO.LOW)
    else:
        GPIO.output(pin_in1, GPIO.LOW)
        GPIO.output(pin_in2, GPIO.HIGH)
        GPIO.output(pin_in4, GPIO.LOW)
        GPIO.output(pin_in3, GPIO.HIGH)
    
    pwm.ChangeDutyCycle(speed)
    pwm2.ChangeDutyCycle(speedturn)  # Zmiana prędkości obrotowej silnika

def turnLeft(speed, speedturn):
    GPIO.output(pin_in1, GPIO.HIGH)
    GPIO.output(pin_in2, GPIO.LOW)
    GPIO.output(pin_in4, GPIO.LOW)
    GPIO.output(pin_in3, GPIO.HIGH)
    
    pwm.ChangeDutyCycle(speed)
    pwm2.ChangeDutyCycle(speedturn)

def turnRight(speed, speedturn):
    GPIO.output(pin_in1, GPIO.LOW)
    GPIO.output(pin_in2, GPIO.HIGH)
    GPIO.output(pin_in4, GPIO.HIGH)
    GPIO.output(pin_in3, GPIO.LOW)
    
    pwm.ChangeDutyCycle(speed)
    pwm2.ChangeDutyCycle(speedturn)

# Funkcja do obracania serwo
def takepicture(base_name):
    # Zakres dla serwomechanizmu to od 500 do 2500 mikrosekund
    center = 1500
    left = 2500
    right = 500
    
    pi.set_servo_pulsewidth(pin_servo, center)
    time.sleep(2)
    camera.start_and_capture_files(f'/home/daniel/Desktop/static/{base_name}.jpg')
    
    pi.set_servo_pulsewidth(pin_servo, left)
    time.sleep(2)
    camera.start_and_capture_files(f'/home/daniel/Desktop/static/Lewo{base_name}.jpg')
    
    pi.set_servo_pulsewidth(pin_servo, center)
    time.sleep(2)
    
    pi.set_servo_pulsewidth(pin_servo, right)
    time.sleep(2)
    camera.start_and_capture_files(f'/home/daniel/Desktop/static/Prawo{base_name}.jpg')
    
    pi.set_servo_pulsewidth(pin_servo, center)
    time.sleep(0.5)
    pi.set_servo_pulsewidth(pin_servo, 0)  # Wyłączenie sygnału PWM na serwo

@app.route('/')
def index():
    return render_template('strona.html')

@app.route('/forward')
def forward():
    rotate(GPIO.HIGH, 100, 100)
    return 'Poruszam się do przodu'

@app.route('/backward')
def backward():
    rotate(GPIO.LOW, 100, 100)
    return 'Poruszam się do tyłu'

@app.route('/left')
def left():
    turnLeft(100, 100)
    return 'Poruszam się w lewo'

@app.route('/right')
def right():
    turnRight(100, 100)
    return 'Poruszam się w prawo'

@app.route('/stop')
def stop():
    pwm.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    return 'Silnik zatrzymany'

@app.route('/takePhoto', methods=['POST'])
def takePhoto():
    base_name = request.form['photo_name']
    takepicture(base_name)
    return 'Zdjęcie zrobione'


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0')
    finally:
        GPIO.cleanup()  # Czyszczenie ustawień GPIO po zakończeniu
        pi.stop()  # Zatrzymanie pigpio
