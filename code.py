import time
import board
import analogio
import usb_midi

# Create USB MIDI object
midi = usb_midi.ports[1]

# Create analog input objects for your potentiometers
potentiometer1 = analogio.AnalogIn(board.GP28)
potentiometer2 = analogio.AnalogIn(board.GP26)

# MIDI control change parameters
midi_channel = 0  # MIDI channel (0-15)

# Control Change numbers (CC#1 and CC#2)
control_change_number1 = 1
control_change_number2 = 2

# Initialize variables for debouncing
debounce_values1 = [0] * 10  # Store the last 10 readings for potentiometer 1
debounce_values2 = [0] * 10  # Store the last 10 readings for potentiometer 2

# Initialize previous MIDI values
prev_midi_value1 = -1
prev_midi_value2 = -1

# Function to create and send MIDI Control Change message
def send_control_change(channel, control_number, value):
    status_byte = 0xB0 | channel  # Control Change status byte
    midi_message = bytes([status_byte, control_number, value])
    midi.write(midi_message)

# Main loop
while True:
    # Read analog values from potentiometers
    raw_pot1_value = potentiometer1.value
    raw_pot2_value = potentiometer2.value

    # Add the current reading to the debounce values lists
    debounce_values1.append(raw_pot1_value)
    debounce_values2.append(raw_pot2_value)

    # Remove the oldest reading from the lists
    debounce_values1.pop(0)
    debounce_values2.pop(0)

    # Calculate the average of the debounce values
    pot1_value = round(sum(debounce_values1) / len(debounce_values1) / 65535, 2)
    pot2_value = round(sum(debounce_values2) / len(debounce_values2) / 65535, 2)

    # Map the normalized values to MIDI values (0-127)
    midi_value1 = int(pot1_value * 127)
    midi_value2 = int(pot2_value * 127)

    # Check if the MIDI values have changed
    if midi_value1 != prev_midi_value1:
        send_control_change(midi_channel, control_change_number1, midi_value1)
        prev_midi_value1 = midi_value1

    if midi_value2 != prev_midi_value2:
        send_control_change(midi_channel, control_change_number2, midi_value2)
        prev_midi_value2 = midi_value2

    # Add a small delay to avoid flooding MIDI messages
    time.sleep(0.1)  # Adjust the delay as needed
