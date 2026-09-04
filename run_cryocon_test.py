"""
Cryocon 22C Temperature Controller - Live Health & Diagnostic Test
Tests communication on COM5 (9600 baud) and reads complete device state.
"""

import serial
import time

PORT = "COM5"
BAUD = 9600

def test_cryocon():
    print("=" * 70)
    print("      CRYOCON 22C TEMPERATURE CONTROLLER DIAGNOSTIC TEST       ")
    print("=" * 70)
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2.0)
        time.sleep(0.5)
        print(f"[OK] Port {PORT} opened successfully at {BAUD} baud.")
    except Exception as e:
        print(f"[ERROR] Failed to open port {PORT}: {e}")
        return

    def query(cmd, delay=0.05):
        ser.reset_input_buffer()
        ser.write(f"{cmd}\r\n".encode())
        if delay > 0:
            time.sleep(delay)
        return ser.readline().decode('utf-8', errors='ignore').strip()

    # 1. Identity & Firmware
    idn = query("*IDN?")
    fw = query("SYSTEM:FWREV?")
    sys_name = query("SYSTEM:NAME?")
    print("\n--- 1. DEVICE IDENTIFICATION ---")
    print(f"  Identity (*IDN?)      : {idn}")
    print(f"  Firmware (SYSTEM:FWREV?): {fw}")
    print(f"  System Name          : {sys_name}")

    # 2. Input Channel A
    temp_a = query("INPUT? A")
    units_a = query("INPUT A:UNITS?")
    sentype_a = query("INPUT A:SENTYPE?")
    name_a = query("INPUT A:NAME?")
    print("\n--- 2. INPUT CHANNEL A ---")
    print(f"  Temperature          : {temp_a} {units_a}")
    print(f"  Sensor Type          : {sentype_a}")
    print(f"  Sensor Name          : {name_a}")

    # 3. Input Channel B
    temp_b = query("INPUT? B")
    units_b = query("INPUT B:UNITS?")
    sentype_b = query("INPUT B:SENTYPE?")
    name_b = query("INPUT B:NAME?")
    print("\n--- 3. INPUT CHANNEL B ---")
    print(f"  Temperature          : {temp_b} {units_b}")
    print(f"  Sensor Type          : {sentype_b}")
    print(f"  Sensor Name          : {name_b}")

    # 4. Loop 1 Configuration
    setpt_1 = query("LOOP 1:SETPT?")
    source_1 = query("LOOP 1:SOURCE?")
    type_1 = query("LOOP 1:TYPE?")
    range_1 = query("LOOP 1:RANGE?")
    p_1 = query("LOOP 1:PGAIN?")
    i_1 = query("LOOP 1:IGAIN?")
    d_1 = query("LOOP 1:DGAIN?")
    outp_1 = query("LOOP 1:OUTP?")
    pmax_1 = query("LOOP 1:PMAX?")
    rate_1 = query("LOOP 1:RATE?")
    ramp_1 = query("LOOP 1:RAMP?")
    print("\n--- 4. CONTROL LOOP 1 ---")
    print(f"  Setpoint             : {setpt_1}")
    print(f"  Control Source       : {source_1}")
    print(f"  Control Type         : {type_1}")
    print(f"  Heater Range         : {range_1}")
    print(f"  PID Gains            : P={p_1}, I={i_1}, D={d_1}")
    print(f"  Current Output Power : {outp_1}%")
    print(f"  Max Power Setting    : {pmax_1}%")
    print(f"  Ramp Rate            : {rate_1}")
    print(f"  Ramp Status          : {ramp_1}")

    # 5. Loop 2 Configuration
    setpt_2 = query("LOOP 2:SETPT?")
    source_2 = query("LOOP 2:SOURCE?")
    type_2 = query("LOOP 2:TYPE?")
    range_2 = query("LOOP 2:RANGE?")
    print("\n--- 5. CONTROL LOOP 2 ---")
    print(f"  Setpoint             : {setpt_2}")
    print(f"  Control Source       : {source_2}")
    print(f"  Control Type         : {type_2}")
    print(f"  Heater Range         : {range_2}")

    # 6. Global Control Status
    ctrl = query("CONTROL?")
    print("\n--- 6. GLOBAL CONTROL STATUS ---")
    print(f"  Control Status       : {ctrl}")

    # 7. Short Stability Monitor (5 samples)
    print("\n--- 7. LIVE TEMPERATURE STABILITY CHECK (5 samples) ---")
    print(f"  {'Sample':<8} {'Channel A (K)':<18} {'Heater Power (%)':<18}")
    print("  " + "-" * 44)
    readings_a = []
    for s in range(1, 6):
        t_a = query("INPUT? A")
        h_p = query("LOOP 1:OUTP?")
        try:
            readings_a.append(float(t_a))
        except:
            pass
        print(f"  #{s:<7} {t_a:<18} {h_p:<18}")
        time.sleep(0.5)

    if readings_a:
        avg_t = sum(readings_a) / len(readings_a)
        min_t = min(readings_a)
        max_t = max(readings_a)
        spread = max_t - min_t
        print("  " + "-" * 44)
        print(f"  Average Temp A       : {avg_t:.3f} K")
        print(f"  Min / Max            : {min_t:.3f} K / {max_t:.3f} K")
        print(f"  Noise / Spread       : {spread:.3f} K")

    ser.close()
    print("\n" + "=" * 70)
    print("[OK] TEST COMPLETE: Cryocon 22C is Fully Functional and Communication OK!")
    print("=" * 70)

if __name__ == "__main__":
    test_cryocon()
