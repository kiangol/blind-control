from flask import Flask, render_template, request, redirect
import time
import os
import RPi.GPIO as GPIO

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
gpio_pins = [17, 18, 27, 22]
speed = 0.001
open_steps = 2700
close_steps = 3200


for pin in gpio_pins:
    GPIO.setup(pin, GPIO.OUT)  # Set pin to output
    GPIO.output(pin, False)  # Set pin to low ("False")

StepSequence = list(range(0, 8))
StepSequence[0] = [gpio_pins[0]]
StepSequence[1] = [gpio_pins[0], gpio_pins[1]]
StepSequence[2] = [gpio_pins[1]]
StepSequence[3] = [gpio_pins[1], gpio_pins[2]]
StepSequence[4] = [gpio_pins[2]]
StepSequence[5] = [gpio_pins[2], gpio_pins[3]]
StepSequence[6] = [gpio_pins[3]]
StepSequence[7] = [gpio_pins[3], gpio_pins[0]]


pins = {
    23: {'name': 'Stue', 'state': 'open'},
    24: {'name': 'Soverom 1', 'state': 'closed'},
    25: {'name': 'Soverom 2', 'state': 'open'}
}


@app.route('/set_speed', methods=['POST'])
def set_speed():
    new_speed = request.form['inlineRadioOptions']
    template_data = {
        'pins': pins
    }

    if new_speed == 'option1':
        speed = 0.002
        msg = "Slow"
    elif new_speed == 'option2':
        speed = 0.001
        msg = "Standard"
    elif new_speed == 'option3':
        speed = 0.0008
        msg = "Fast"
    return render_template('index.html', **template_data, status_msg=speed)

def work(number_of_steps, close=False):
    GPIO.setmode(GPIO.BCM)
    gpio_pins = [17, 18, 27, 22]

    for pin in gpio_pins:
        GPIO.setup(pin, GPIO.OUT)  # Set pin to output
        GPIO.output(pin, False)  # Set pin to low ("False")

    StepSequence = list(range(0, 8))
    StepSequence[0] = [gpio_pins[0]]
    StepSequence[1] = [gpio_pins[0], gpio_pins[1]]
    StepSequence[2] = [gpio_pins[1]]
    StepSequence[3] = [gpio_pins[1], gpio_pins[2]]
    StepSequence[4] = [gpio_pins[2]]
    StepSequence[5] = [gpio_pins[2], gpio_pins[3]]
    StepSequence[6] = [gpio_pins[3]]
    StepSequence[7] = [gpio_pins[3], gpio_pins[0]]

    if not close:
        StepSequence.reverse()


    try:
        print(speed)
        stepsDone = 0
        stepsRemaining = number_of_steps
        while stepsRemaining > 0:
            for pinList in StepSequence:
                for pin in gpio_pins:
                    if pin in pinList:
                        GPIO.output(pin, True)
                    else:
                        GPIO.output(pin, False)
                time.sleep(speed)
            stepsRemaining -= 1
            stepsDone += 1
            
    except KeyboardInterrupt:
        StepSequence.reverse()
        while stepsDone > 0:
            for pinList in StepSequence:
                for pin in gpio_pins:
                    if pin in pinList:
                        GPIO.output(pin, True)
                    else:
                        GPIO.output(pin, False)
                time.sleep(speed)
            stepsDone -= 1

    finally:
        GPIO.cleanup()


@app.route('/')
def hello_word():
    template_data = {
        'pins': pins
    }
    return render_template('index.html', **template_data)


@app.route('/<action>/<change_pin>')
def action(action, change_pin):
    print(f"{action} to pin {change_pin}")

    change_pin = int(change_pin)
    # if action != 'stop':
    #     time.sleep(1)
    pins[change_pin]['state'] = action
    
    template_data = {
        'pins': pins
    }

    current_status = '...'

    if action == 'open':
        current_status = 'opening...'
        work(open_steps, close=False)
    if action == 'close':
        current_status = 'closing...'
        work(close_steps, close=True)
    if action == 'stop':
        GPIO.cleanup()
        current_status = 'stopping...'


    return render_template('index.html', **template_data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
