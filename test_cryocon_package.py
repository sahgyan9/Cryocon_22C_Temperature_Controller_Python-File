import cryocon_controller as cc

# Create a controller instance for COM5
cryo = cc.Cryocon22C('COM5')

# Connect to the controller
cryo.connect()

# Check if controller is connected
print('Connected:', cryo.connected)

# Read device identity
print('Identity:', cryo.get_identity())

# Read the current set point temperature of Loop 1
print('Set point (Loop 1):', cryo.get_setpoint(1))

# Read current temperature from Channel A
print('Temperature (Channel A):', cryo.read_temperature('A'))

# Disconnect when done
cryo.disconnect()
print('Disconnected')
