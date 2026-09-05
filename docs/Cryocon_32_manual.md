# **User's Guide Model 32 & 32B Cryogenic Temperature Controller** 

**CRYO** GENIC **CON** TROL SYSTEMS, INC. 

P.O. Box 7012 Rancho Santa Fe, CA 92067 Tel:  (858) 756-3900 Fax: (858) 759-3515 www.cryocon.com 

 Copyright 2008 - 2011 Cryogenic Control Systems, Inc. All Rights Reserved. 

##### Printing History 

Edition 6f, April 1, 2011 

##### Certification 

Cryogenic Control Systems, Inc. (Cryo-con) certifies that this product met its published specifications at the time of shipment. Cryo-con further certifies that its calibration measurements are traceable to the United States National Institute of Standards and Technology (NIST). 

##### Warranty 

This product is warranted against defects in materials and workmanship for a period of one year from date of shipment. During this period Cryo-con will, at its option, either repair or replace products which prove to be defective. 

For products returned to Cryo-con for warranty service, the Buyer shall prepay shipping charges and Cryo-con shall pay shipping charges to return the product to the Buyer. 

However, the Buyer shall pay all shipping charges, duties, and taxes for products returned to Cryo-con from another country. 

##### Warranty Service 

For warranty service or repair, this product must be returned to a service facility designated by Cryo-con. 

##### Limitation of Warranty 

The foregoing warranty shall not apply to defects resulting from improper or inadequate maintenance by the Buyer, Buyer supplied products or interfacing, unauthorized modification or misuse, operation outside of the environmental specifications for the product, or improper site preparation or maintenance. 

The design and implementation of any circuit on this product is the sole responsibility of the Buyer. Cryo-con does not warrant the Buyer's circuitry or malfunctions of this product that result from the Buyer's circuitry. 

In addition Cryo-con does not warrant any damage that occurs as a result of the Buyer's circuit or any defects that result from Buyersupplied products. 

##### Notice 

Information contained in this document is subject to change without notice. 

Cryo-con makes no warranty of any kind with regard to this material, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. 

Cryo-con shall not be liable for errors contained herein or for incidental or consequential damages in connection with the furnishing, performance, or use of this material. No part of this document may be photocopied, reproduced, electronically transferred, or translated to another language without prior written consent. 

##### Trademark Acknowledgement 

CalGen<sup></sup> and Cryo-Con<sup></sup> are registered trademarks of Cryogenic Control Systems, Inc. All other product and company names are trademarks or trade names of their respective companies. 

##### Safety 

The Model 32 does not contain any user serviceable parts. Do not open the enclosure. Do not install substitute parts or perform any unauthorized modification to the product. For service or repair, return the product to Cryo-con or an authorized service center. 

Model 32 / 32B User's Manual 

## Table of Contents 

|Preparing the controller for use..................................................................1|
|---|
|Supplied Items. ...................................................................................1|
|Verify the AC Power Line Voltage Selection.........................................1|
|Apply Power to the Controller...............................................................1|
|Installation............................................................................................3|
|Initial Setup and Configuration.............................................................4|
|Options and Accessories......................................................................7|
|Returning Equipment...........................................................................9|
|A Quick Start Guide....................................................................................11|
|A Quick Start Guide to the User Interface............................................11|
|Front Panel Operation................................................................................17|
|The Keypad..........................................................................................17|
|The VFD Display..................................................................................22|
|Front Panel Menu Operation......................................................................27|
|Instrument Setup Menus......................................................................27|
|Specifications, Features and Functions......................................................51|
|Specification Summary........................................................................51|
|Input Channels.....................................................................................55|
|Control Outputs....................................................................................64|
|Remote Interfaces................................................................................67|
|Rear Panel Connections......................................................................68|
|Mechanical, Form Factors and Environmental.....................................74|
|Basic Setup and Operating Procedures......................................................77|
|Configuring a sensor............................................................................77|
|Adding a New Sensor Type..................................................................77|
|Autotuning............................................................................................80|
|Temperature Ramping.........................................................................85|
|Cryocooler Signature Subtraction.........................................................87|
|Using an external power booster..........................................................90|
|<br>Using Thermocouple Sensors..............................................................92|
|CalGenCalibration Curve Generator.................................................96|
|System Shielding and Grounding Issues....................................................101<br>|
|Grounding Scheme..............................................................................101|

iii 

#### Model 32 / 32B User's Manual 

|Cryo-con Utility Software............................................................................103|
|---|
|Installing the Utility Software................................................................103|
|Connecting to an Instrument................................................................104|
|Using the Interactive Terminal..............................................................105<br>|
|Downloading or Uploading a Sensor Calibration Curve........................106|
|Using the Real-Time Strip Charts.........................................................110|
|Data Logging........................................................................................111|
|Remote I/O command HELP................................................................113<br>|
|CalGen Calibration Curve Generator....................................................114|
|The Vapor Pressure Calculator............................................................117|
|Downloading Instrument Firmware ......................................................118|
|Instrument Calibration................................................................................123|
|Cryo-con Calibration Services..............................................................123|
|Calibration Interval...............................................................................123|
|Minimum Required Equipment.............................................................124|
|The Basic Calibration Sequence..........................................................124|
|Calibration of Silicon Diodes................................................................129|
|Calibration of DC resistors...................................................................130|
|Calibration of AC resistors....................................................................130|
|Remote Operation......................................................................................131|
|Remote Interface Configuration...........................................................131|
|Introduction to Remote Programming..................................................133|
|SCPI Status Registers.........................................................................134|
|Remote Commands.............................................................................137|
|Remote Command Summary...............................................................203|
|EU Declaration of Conformity.....................................................................211|
|Appendix A: Installed Curves......................................................................213|
|Factory Installed Curves.......................................................................213|
|Sensor Curves on CD..........................................................................215|
|Appendix B: Troubleshooting Guide...........................................................217|
|Error Displays.......................................................................................217|
|Control Loop and Heater Problems......................................................218|
|Temperature Measurement Errors.......................................................220|
|Remote I/O problems...........................................................................221<br>|
|General problems................................................................................222|
|Appendix C: Application Note on Signal Dither...........................................223|
|Using Dither in Digital Control Loops....................................................223|
|Appendix D: Tuning Control Loops.............................................................227|
|<br>Introduction..........................................................................................227|
|Various methods for obtaining PID coefficients....................................227|
|Manual Tuning Procedures..................................................................228|
|Appendix E: Sensor Calibration Curve Tables............................................231|
|Cryocon S700 Silicon Diode.................................................................231|

iv 

Model 32 / 32B User's Manual 

## Index of Tables 

|Table 1: Model 32 Instrument Accessories.................................................7|
|---|
|Table 2: Cryogenic Accessories..................................................................8|
|Table 3: Input Sensor Selections................................................................12|
|Table 4: Loop #1 Output Summary.............................................................13<br>|
|Table 5: Control Type Summary..................................................................14|
|Table 6: Keypad key functions....................................................................21<br>|
|Table 7: Temperature Units.........................................................................24|
|Table 8: Display Configurations..................................................................29<br>|
|Table 9: Input Channel Setup Menus..........................................................31|
|Table 10: Control Loop Setup Menus..........................................................34<br>|
|Table 11: User Configurations Menu...........................................................39|
|Table 12: System Functions Menu..............................................................41<br>|
|Table 13: PID table Menu...........................................................................45|
|Table 14: PID Table Edit Menu...................................................................46<br>|
|Table 15: Sensor Setup Menu....................................................................47|
|Table 16: Calibration Curve Menu...............................................................49|
|Table 17: Voltage Bias Selections...............................................................56<br>|
|Table 18: NTC Resistor Measurement Accuracy........................................56|
|Table 19: Supported Sensor Configurations...............................................57|
|Table 20:  PTC Resistor Sensor Configuration...........................................58|
|Table 21:  NTC Resistor Sensor Configuration...........................................58<br>|
|Table 22: Sensor Performance for Diodes and Pt Sensors.........................60|
|Table 23: Sensor Performance for NTC sensors........................................61|
|Table 24: Sensor Performance for Thermocouple Sensors........................62|
|Table 25: Loop 1 Heater output ranges.......................................................64|
|Table 26. AC Power Line Fuses..................................................................69|
|Table 27: Input Connector Pin-out..............................................................70|
|Table 28:  Dual Sensor Cable Color Codes................................................71<br>|
|Table 29: Thermocouple Types...................................................................73|
|Table 30:  RS-232 DB-9 Connector Pinout.................................................73|
|Table 31: Sensor Setup Menu....................................................................78|
|Table 32: Autotune Menu............................................................................83|
|Table 33: First CalGenMenu, Diode Sensor............................................97|
|Table 34: CalGenMenu, 2-point Diode Sensor........................................98|
|<br>Table 35: CalGenNew Curve Menu.........................................................99|
|Table 36: Recommended GPIB Host Setup Parameters............................131|
|Table 37: Remote Command Summary......................................................209|
|Table 38: Factory Installed Sensors............................................................213|
|Table 39: S700 Cable Color Codes.............................................................232|

v 

Model 32 / 32B User's Manual 

## Index of Figures 

|Figure 1: Rack Mount Kit............................................................................3|
|---|
|Figure 2:  Model 32 Front Panel Layout......................................................17|
|Figure 3:  Model 32 Rear Panel Layout......................................................68|
|Figure 4: Proper Assembly of the Input Connector ....................................70|
|Figure 5: Diode and Resistor Sensor Connections.....................................71|
|Figure 6: Thermocouple Input Connector...................................................72|
|Figure 7: RS-232 Null Modem Cable..........................................................74|
|Figure 8: Instrument Calibration Screen.....................................................125|

vi 

Model 32 / 32B User's Manual 

vii 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

## Preparing the controller for use. 

The following steps help you verify that the controller is ready for use. 

### Supplied Items. 

Verify that you have received the following items with your controller. If anything is missing, contact Cryogenic Control Systems, Inc. directly. 

- Model 32/32B Cryogenic Temperature Controller. 

- User’s Manual (PN 3038-029). 

- Cryo-con software CD (PN 4034-029). 

- Connector kit (PN 4038-015) consisting of: Two DIN-5 input connectors (PN 04-0436) A Dual banana plug heater connector (PN 04-0433) A Terminal block plug Loop 2 connector (PN 04-0301). 

- Detachable 120VAC Line Cord (04-0310). 

- Certificate of Calibration. 

### Verify the AC Power Line Voltage Selection. 

The AC power line voltage is set to the proper value for your country when the controller is shipped from the factory. Change the voltage setting if it is not correct. The settings are: 100, 120 220, or 240 VAC. For 230 VAC operation, use the 220 VAC setting. 

On the rear panel of the instrument, the AC voltage selection can be seen on the power entry module. If the setting is incorrect, please refer to section Fuse Replacement and Voltage Selection to change it. 

### Apply Power to the Controller 

Connect the power cord and turn the controller on by pressing the **Power** key for a minimum of 0.5 Seconds. The front panel will show a Power Up display with the model number and firmware revision. 

While the Power Up display is shown, the controller is performing a self-test procedure that verifies the proper function of internal data 

  

and program memories, remote interfaces and input/output channels. If an error is detected during this process, the controller will freeze operation with an error message display. In this case, turn the unit off and refer to Appendix B: Troubleshooting Guide. 

1 

Model 32 / 32B User's Manual Preparing the controller for use. 

**Caution:** Do not remove the instrument’s cover or attempt to repair the controller. There are no user serviceable parts, jumpers or switches inside the unit. Further, there are no software ROM chips, trim pots, batteries or battery-backed memories. All firmware installation and instrument calibration functions are <u>performed externally via the remote interfaces.</u> 

After about five seconds, the self-test will complete and the controller will begin normal operation. 

2 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

### Installation 

#### General 

The Model 32 can be used as a bench top instrument, or mounted in an equipment rack. In either case, it is important to ensure that adequate ventilation is provided. 

Cooling airflow enters through the side holes and exhausts out the fan on the rear panel. It is important to allow at least ½” of clearance on the left and right sides and to ensure that the exhaust path of the fan is not blocked. 

#### Rack Mounting 

You can rack mount the controller in a standard 19-inch rack cabinet using the optional rack mount kit. Instructions and mounting hardware are included with the kit. 

4034-032 Single instrument shelf rack mount kit. 4034-031 Dual instrument shelf rack mount kit. 

Since the controller is an industry standard size, you can mount any similar size instrument next to it in the rack. 

**Figure 1: Rack Mount Kit** Note that the rack mount extends the height of the controller from 2U (3½”) to 3U (5¼”). 

To mount the controller, first remove the plastic feet and instrument bail on the bottom of the unit. 

Next, lay the controller 

on the shelf and slide forward to line up with the front cutout. 

Use four #6-1/4” screws to secure the controller using the same threaded holes as the plastic feet used. 

**Warning:** When rack mounting, do not use screws that protrude into the bottom of instrument more than ¼”. Otherwise, they can touch internal circuitry and damage it. 

3 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

### Initial Setup and Configuration 

Before attempting to control temperature, the following instrument parameters should be checked: 

1. The Loop #1Heater resistance setting should match the actual heater resistance that you are going to use. Choices are 50 Ω and 25 Ω . A heater resistance of less than 25 Ω should use the 25 Ω setting. Using the 50 Ω setting with a heater resistance much less than 50 Ω may cause the instrument to overheat and disengage the control loops. 

Set the heater resistance by pressing the **Loop 1** key and refer to the Control Loop Setup menu section. 

2. The Loop #1 heater range should be set to a range where the maximum output power will not damage your equipment. To set this parameter, press the **Loop 1** key and refer to the Control Loop Setup menu section. 

3. The controller has an over-temperature disconnect feature that monitors a selected input and will disconnect both control loops if the specified temperature is exceeded. This feature should be enabled in order to protect your equipment from being over heated. To enable, press the **Sys** key and refer to the System Functions Menu section. 

4 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

#### Factory Default Setup 

A controller with factory default settings will have an operational display like the one shown here. The dash ( **-** ) or dot ( **.** ) characters indicate that there is no sensor connected.     

Note that, in some cases, there will be an erratic temperature display when no sensor is connected. This is not an error condition. The high input impedance of the controller’s input preamplifier causes erratic voltage values when unconnected. 

Input Channel factory defaults are: Sensor Units: Kelvin. Sensor Type: LS DT-670 (Lakeshore DT-670 Curve 11 Silicon Diode) Bias Type: DC Alarm Enables: Off 

To change these, press the **ChA** or **ChB** key and refer to the Input Channel Setup Menu section. Control Loop factory defaults are: Setpoint: 100K P gain: 5.0, I gain: 28.0 Seconds, D gain: 8.0, Manual output power, Pman: 5% Control input channel: A for Loop 1, B for Loop 2 Loop 1 Range: Low Control Type: Manual Heater Resistance:25 Ω To change these, press the **Loop 1** or **Loop 2** key and refer to the Control Loop Setup menu section. 

Instrument setup factory defaults are: Display Filter Time Constant: 2.0 Seconds. Display Resolution: 3 digits. Over Temperature Disconnect: Off Remote Interface: RS-232, RS-232 Baud Rate: 9600. IEEE-488 (GPIB) Address: 12 AC Power Line Frequency: 60Hz Cryocooler Filter: Off Control on power-up: OFF 

To change these, press the **Sys** key and refer to the System Functions Menu section. 

 **NOTE:** Factory defaults may be restored at any time by use of the following sequence: 1) Turn power to the Model 32 OFF. 2) Press and hold the **Enter** key while turning <u>power back ON.</u> 

5 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

#### Model Identification 

The model number of all Cryo-con controllers is identified on the front and rear panel of the instrument as well as in various instrument displays. 

- **Model 32** – Basic controller with two standard input channels. Outputs are Loop #1: 50Watt 3-range linear heater and Loop 2: 0-5Volt analog output. 

- **Model 32B** – Controller with two standard input channels. Outputs are Loop 1: 50Watt 3-range linear heater and Loop 2: Ten Watt linear heater. 

The only option that can be ordered with a Model 32 or 32B is a single thermocouple input for sensor ‘B’. These variations are: 

- **Model 32B-T** Model 32B with one standard input plus one universal thermocouple input. 

- **Model 32-T** Model 32 with one standard input plus one universal thermocouple input. 

#### Ordering Information 

|**Standard**|**Model 32B**|**Description**|
|---|---|---|
|Model 32|Model 32B|Controller with two standard multi-function sensor<br>input channels.|
|Model 32-T|Model 32B-T|Controller with one standard input and one<br>universal thermocouple input.|

#### **Technical Assistance.** 

Trouble shooting guides and user’s manuals are available on our web page at http://www.cryocon.com. 

Technical assistance may be also be obtained by contacting Cryo-con as follows: 

Cryogenic Control Systems, Inc. PO Box 7012 Rancho Santa Fe, CA 92067 

Telephone: (858) 756-3900x100         FAX: (858) 759-3515 e-mail:  techsupport@cryocon.com 

For updates to LabVIEW  drivers, Cryo-con utility software and product documentation, go to our web site and select the Download area. 

#### <u>Current Firmware Revision Level</u> 

As of December, 2006 the current firmware revision level for the Model 32 series is 6.10. 

#### <u>Current Hardware Revision Level</u> 

As of December, 2006, the current hardware revision level for the Model 32 series is H. Hardware cannot be upgraded in the field. 

6 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

### Options and Accessories Instrument Accessories 

|**Cryo-con**<br>**Part #**|**Description**|
|---|---|
|**4034-031**|Two instrument shelf rack mount kit|
|**4034-032**|One instrument shelf rack mount kit|
|**04-0420**|RS-232 Null Modem Cable, 6’. (Required for downloading<br>firmware to the instrument products)|
|**4034-035**|Shielded IEEE-488.2 Interface Bus Cable, 6'6”|
|**4039-010**|Cable Assembly, 10 Pin to Modular Test Dewar|
|**4039-009**|Cable Assembly, 19 Pin to Modular Test Dewar|
|**04-0310**|AC Power Cord|
|**4038-036**|Loop 1 / Loop 2 connector kit|
|**4038-033**|Din-5 Sensor Input Connector|
|**3038-029**|Additional User’s Manual/CD|

**Table 1: Model 32 Instrument Accessories** 

7 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

#### Cryogenic Accessories 

|**Cryo-con**<br>**Part #**|**Description**|
|---|---|
|**S700**|S700 series Silicon Diode Temperature Sensors.<br>Temperature range: 1.4 to 495K|
|**CP-100**|CP-100 series Ceramic Wound RTD, 100Ω|
|**GP-100**|GP-100 series Glass Wound RTD, 100Ω|
|**CPX-100**|CPX-100 series Thin Film Platinum RTD, 100Ω|
|**CPX-1K**|CPX-1K series Thin Film Platinum RTD, 1,000Ω|
|**3039-015**|Cartridge Heater, Silicon free, 25Ω/ 25 Watt,<br>1/4”x 1 1/8”. Temperature range to 1,600K|
|**3039-016**|Cartridge Heater, Silicon free, 50Ω/ 50 Watt,<br>1/4”x 1 1/8. Temperature range to 1,600K|
|**4039-011**|Pre-cut Nichrome wire heater w/connectors, 25Ω|
|**4039-012**|Pre-cut Nichrome wire heater w/connectors, 50Ω|
|**4039-013**|Pre-cut Nichrome wire heater w/connectors, Custom.<br>Specify length or resistance.|
|**3039-006**|Bulk Nichrome Heater Wire, 32AWG,<br>Polyamideinsulation, 100’|

**Table 2: Cryogenic Accessories** 

8 

Model 32 / 32B User's Manual 

Preparing the controller for use. 

### Returning Equipment 

If an instrument must be returned to Cryo-con for repair or recalibration, a Return Material Authorization (RMA) number must first be obtained from the factory. This may be done by Telephone, FAX or e-mail. 

When requesting an RMA, please provide the following information: 

1. Instrument model and serial number. 

2. User contact information. 

3. Return shipping address. 

4. If the return is for service, please provide a description of the malfunction. 

If possible, the original packing material should be retained for reshipment. If not available, consult factory for packing assistance. 

Cryo-con’s shipping address is: 

Cryogenic Control Systems, Inc. 17279 La Brisa Street Rancho Santa Fe, CA 92067 

9 

A Quick Start Guide 

Model 32 / 32B User's Manual 

## A Quick Start Guide 

### A Quick Start Guide to the User Interface. 

Pressing the **Power** key will toggle the controller's AC power on and off. This key must be pressed and held for two seconds before power will toggle. 

Pressing the **Stop** key will immediately disengage both control loops. Pressing the **Control** key will engage them. 

#### The Home Status Display 

Pressing the **Home** key will return the screen to the Home Display from anywhere in the sub-menus. The Home Display is the primary display for instrument status information. 

Several Home Displays are available so that the user can see desired information without additional clutter. To scroll through the available displays, press the or key. 

#### Accessing the heater setpoint 

To instantly access the setpoint for either control loop, press the **Set Pt** key. 

#### Configuring a temperature sensor 

Configuring an input sensor from the front panel is performed by using the Input Channel Setup Menu. To access this menu for input A, press the **ChA** key, or for input B, the **ChB** key. 

The first line of this menu is used to change the sensor units. It shows the selected input channel, the current temperature (in real time) and the current units. An example is shown here.  

 

To change the sensor units, use the right and left arrow keys ( or ) to scroll through the available options. When the desired units are shown,  press the **Enter** key to make the selection. The display will now show the current temperature with the new units. 

Next, go to the sensor selection field by pressing the down arrow ( ) key.  This field is  used to select the actual sensor type. In the example shown here, the input channel is currently configured for a standard Platinum 100 sensor. Use the right and left arrow keys ( or ) to scroll through the available options. When the desired sensor is shown, press the **Enter** key to make the selection. A summary of sensor selections is shown here: 

11 

A Quick Start Guide 

Model 32 / 32B User's Manual 

|**Sensor**|**Description**|
|---|---|
|**None**|Input disabled|
|**Cryocon S700**|Cryo-con S700 series Silicon Diode. Range: 1.4 to 495K.|
|**LS DT-670**|Lakeshore Silicon Diode Curve 11 for DT-670 series diodes. Range:<br>1.4 to 500K.|
|**LS DT-470**|Lakeshore Silicon Diode Curve 10 for DT470 series diodes. Range:<br>1.4 to495K.|
|**CD-12A Diode**|Cryo Industries CD-12A Silicon Diode. Range: 1.4 to 325K.|
|**SI 410 Diode**|Scientific Instruments,Inc. 410 Diode Curve. Range: 1.5 to 450K..|
|**Pt100 385**|DIN43760 standard 100ΩPlatinum RTD. Range: 23 to 1023K, 1mA<br>excitation.|
|**Pt1K 385**|1000Ωat 0°C Platinum RTD using DIN43760 standard calibration<br>curve. Range: 23 to 1023K.|
|**Pt10K 385**|10KΩat 0°C Platinum RTD. Temperature coefficient 0.00385, Range:<br>23to475K.|
|**RhFe 27, 1mA**|Rhodium-Iron resistor,27 Ohms at 0<sup>o</sup>C. 1mA DC excitation.|
|**RO-105 AC**|Scientific Instruments Inc. RO-105 Ruthenium Oxide sensor with<br>constant-voltage AC excitation.|
|**RO-105 DC 10μA**|Scientific Instruments Inc. RO-105 Ruthenium Oxide sensor with<br>constant-current 10μA DC excitation.|
|**RO-600 AC**|Scientific Instruments Inc. RO-600 Ruthenium Oxide sensor with<br>constant-voltageAC excitation..|
|**User Sensor 1**|User supplied sensor #1.|
|**User Sensor 2**|User supplied sensor #2.|
|**User Sensor 3**|User supplied sensor #3.|
|**User Sensor 4**|User supplied sensor #4.|

**Table 3: Input Sensor Selections.** 

Before one of the user-supplied sensors can be used, the sensor’s calibration curve and configuration data must be installed. This is best done by using Cryo-con’s utility software. 

This completes the process of configuring an input channel. Press the **Home** key to return to the Home Status display. 

#### Configuring the Loop #1 Output 

Before using the Loop #1 (main heater) control output, it is essential that the proper load resistance and output range be selected. This is done using the Control Loop Setup menu as follows: 

- Press the **Loop 1** key to go to the Control Loop Setup menu for Loop #1. 

- Use the up arrow and down arrow keys  ( and )  to scroll to the Htr Resistance field. An example is shown here:  Ω 

12 

A Quick Start Guide 

Model 32 / 32B User's Manual 

- Use the left and right arrow keys ( or ) to select between a 50 Ohm and a 25 Ohm heater and then press the **Enter** key. 

- Use the up arrow and down arrow keys  ( and ) to scroll  

- to the Range field and then select Hi, Mid or Low. Be sure 

to select a range that does not exceed the ratings of your cryostat. A summary of full-scale output power for the various ranges is given here: 

|**R**|**Max. Output Po**|**wer**|
|---|---|---|
|**ange**|**25**Ω|**50**Ω|
|**Hi**|25 Watts|50 Watts|
|**Mid**|2.5 Watts|5.0 Watts|
|**Low**|0.25 Watts|0.50 Watts|

**Table 4: Loop #1 Output Summary** 

Next, the control type should be set by scrolling to the Type field and selecting the desired loop operating mode. 

 

13 

A Quick Start Guide 

Model 32 / 32B User's Manual 

A summary of control types is given here: 

|**Type**|**Description**|
|---|---|
|**Off**|Control loop is disabled.|
|**Man**|Manual control mode. Here, a constant heater output power is<br>applied. The Pman field selects the output power as a<br>percentage of full-scale.|
|**Table**|PID control mode where the PID coefficients are generated from<br>a stored, user supplied PID table.|
|**PID**|Standard PID control.|
|**RampP**|Temperature ramp control. Uses PID control to perform a<br>temperature ramp.|

**Table 5: Control Type Summary** 

**Caution:** The Model 32 has an automatic control-on-power-up feature. If enabled, the controller will automatically begin controlling temperature whenever AC power is applied. For a complete description of this function, please see the SYS-Auto Ctl function in the **System Functions menu** section. 

14 

A Quick Start Guide 

Model 32 / 32B User's Manual 

#### Configuring the Loop #2 Output 

The second control loop of a Model 32B controller is a fixed 10 Watt output that is matched to a 50 Ω resistive load. Therefore, there are no load resistance or range settings to configure. 

On the standard Model 32, the second control loop is a zero to 10 Volt output that is intended to drive a booster supply or other voltage controlled device. It is not a heater output. 

All other configuration settings are identical for both Loop #1 and Loop #2. 

**Caution:** The Model 32 has an automatic control-on-power-up feature. If enabled, the controller will automatically begin controlling temperature whenever AC power is applied. For a complete description of this function, please see the SYS-Auto Ctl function in the **System Functions menu** section. 

#### Restoring Factory Defaults 

Factory default settings may be restored with the following simple procedure: 

1. Turn AC power OFF. 

2. Press and hold the Enter key while turning AC power back ON. Keep the key pressed until you see the power-up display indicating that defaults have been restored. 

 **NOTE:** Factory defaults may be restored at any time by use of the following sequence: 1) Turn power to the Model 32 OFF. 2) Press and hold the **Enter** key while turning <u>power back ON.</u> 

15 

A Quick Start Guide 

Model 32 / 32B User's Manual 

#### Forcing a Firmware Download 

The Model 32 may be powered up in a mode where it will wait for a firmware update via the serial port. This is not normally necessary because the Cryo-con utility software will set this mode when a firmware update is being processed. However, if the instrument has crashed during a firmware download or has otherwise become corrupted, following this procedure will set the firmware download mode: 

1. Turn AC power OFF. 

2. Press and hold the STOP key while turning the AC power back ON. Keep the key pressed until the firmware download display is seen. The initial firmware download screen  is shown here.  

3. Use the Utility Software package to download new firmware over the RS-232 port.  Instructions are detailed in the section: “Downloading Instrument Firmware” 

16 

Front Panel Operation 

Model 32 / 32B User's Manual 

## Front Panel Operation 

The user interface of the Model 32 Cryogenic Temperature Controller consists of a two line by 20 character Vacuum Florescent display and a keypad. All features and functions of the instrument are accessed via this simple and intuitive menu-driven interface. 

**Figure 2:  Model 32 Front Panel Layout** 

### The Keypad 

#### Function Keys 

The Function Keys on the Model 32 are **Power** , **Stop** , **Control** , **Home** , and **Enter** as shown here: 

The **Power** key is used to turn AC power to the controller on or off. Note that this key must be pressed and held for one second in order to toggle AC power. 

 **Note:** The Model 32 uses a smart power on/off scheme. When the power button on the front panel is pressed to turn the unit off, the instrument's configuration is copied to flash memory and restored on the next power up. If the front panel button is not used to toggle power to the instrument, the user should configure the controller and cycle power from the front panel button one time. This will ensure that the proper setup is restored when AC power is applied. 

17 

Front Panel Operation 

Model 32 / 32B User's Manual 

The **Stop** and **Control** keys are used to disengage or engage the instrument’s output control loops. Pressing **Control** will immediately turn on all enabled heater outputs and pressing **Stop** will turn them both off.   To enable or disable an individual loop, go to the Control Loop Setup menu and select the desired ‘Type’. 

The **Home** key is used to take the display to one of the Home Status displays. These displays show the full status of the instrument. 

Generally, pressing the **Home** will take the display up one level in the Setup Menu tree and the Home Status displays are at the root level. 

The **Enter** key is functional only in the Setup Menus and is used to enter numeric data or make a selection. 

#### Navigation Keys 

Navigation through the displays and menus of the Model 32 is accomplished with the cursor keys and . 

The and keys are used to scroll the display up or down through all of the lines available on a given menu. 

When the display is showing one of the Home Status displays, the and keys are used to scroll through the four available display formats. When the display is in any of the Setup menus, these keys are used to scroll through the various lines of the menu. 

18 

Front Panel Operation 

Model 32 / 32B User's Manual 

#### The Keypad and Setup Menu Keys 

The keypad keys on the far right side of the instrument serve a dual function. When numeric data is required, these keys are used as a standard keypad where the numbers are printed on the keys. Otherwise, they are used to go directly to the Setup Menu printed over the top of the key. 

When used as Setup Menu keys, their function is identified by a label printed just above the key and is as follows: 

**ChA** -Go to the Input Channel A setup menu. 

**ChB** -Go to the Input Channel B setup menu. 

**Loop 1** -Go to the Loop 1, or primary heater output, setup menu. 

**Loop 2** - Go to the Loop 2, or secondary heater output, setup menu. 

**Auto Tune** - Go to the auto-tuning menu for either loop. 

**Config** -Go to the User Configurations menu. 

- **Sensors** - Go to the Sensors configuration menu, including sensor calibration curves. 

**PID Table** - Go to the PID tables setup menu. 

- **Sys** - Go to the System Functions menu. This includes fields for Remote Input / Output, Display filters and the Over Temperature Disconnect feature. 

- **Display** - Go to the Display setup menu. This allows configuration of the front panel display from a list of options 

**Alarm** - Go to the Alarm Status menu. 

**Set Pt** - Set the setpoint values for both control loops. 

#### The Selection Keys and Enumeration Fields 

Enumeration fields are display fields where the value is one of several specific choices. For example, the Heater Range field in the Loop 1 setup menu may contain one of only three possible values: HIGH, MID and LOW. There are many enumeration fields that contain only the values ON and OFF. 

An enumeration field is always indicated by the character in the last column of the display. 

To edit an enumeration field, place the cursor at the desired field by using the Navigation keys. Then, use the or key to scroll through all of the possible choices in sequence. 

19 

Front Panel Operation 

Model 32 / 32B User's Manual 

When a field has been changed, a block cursor will flash over the symbol. Each time the or key is pressed, the field value will scroll forward or backward through all of the available choices. 

To select the displayed value, press the **Enter** key. To cancel selection without updating the field, press the **Esc** key. The cursor will then return to the symbol. 

#### The Keypad Keys and Numeric Data Fields 

A numeric data field is indicated by a pound-sign ( **#** ) in the last column of the display. 

The Keypad Keys are used to enter data into numeric fields. These keys are: the numerals **0** through **9** , the period key ( **.** ) and the **+/-** key. 

When the cursor is positioned to a field that requires numeric data, the Keypad Keys become hot and pressing one of them will result in the field being selected and numeric entry initiated. This is indicated by a flashing cursor. 

When the **Enter** key is pressed, numeric data in the selected field will be checked for range and the instrument’s database will be correspondingly updated. 

If the numeric entry is outside of the required range, an error is indicated by the display of the previous value of the field. 

Once the entry of numeric data has started, it can be aborted by pressing the **Esc** or **Home** key. This will cause the field to be de-selected and its value will be unchanged. 

 **Note:** Up to 20 digits may be entered in a numeric field. When digit entry has exceeded the display field width, additional characters will cause the display to scroll from right to left. When entry is complete, the updated display field may not show all of the digits entered because of limited field width, however, the digits are retained to the full precision of the controller's internal 32 bit floating <u>point format.</u> 

20 

Front Panel Operation 

Model 32 / 32B User's Manual 

#### Summary of keypad functions 

|**Key**|**Function**|**Description**|
|---|---|---|
||**Power**|Toggle power. Must be held in for two seconds in order to<br>toggle ACpower.|
||**Stop**|Disengage all control loops.|
||**Control**|Engage all control loops.|
||**Home**|Go to the Home Status Display.|
||**Enter**|Enter data / make a selection.|
||**Esc**|Scroll Display UP. If in a selection mode, abort entry and<br>return to the Home Status Display.|
|||Scroll DisplayDOWN.|
|||Scroll to NEXT selection.|
|||Scroll to PREVIOUS selection.|
|**.**|**Display**|Go to the Display Setup menu.|
|±|**Set Pt**|Change the setpoint value for either control loop.|
|**o**|**Alarm**|Go to the Alarm Status menu.|
|**1**|**ChA**|Sensor input A setupmenu.|
|**2**|**ChB**|Sensor input B setupmenu.|
|**3**|**LOOP 1**|Primarycontrol loopsetup,Loop1.|
|**4**|**Config**|User configuration save and restore.|
|**5**|**Sys**|System functions menu.|
|**6**|**Loop 2**|Loop2 setupmenu.|
|**7**|**Sensors**|Sensor data and calibration curve menu.|
|**8**|**PID Table**|PID table menu.|
|**9**|**Auto Tune**|Autotune menu.|

**Table 6: Keypad key functions.** 

21 

Front Panel Operation 

Model 32 / 32B User's Manual 

#### The LED indicators and Audible Alarm 

There are three LED indicators located just below the main display as shown here: 

The Green **Control** LED is illuminated whenever either of the control loops are engaged and actively controlling temperature.  To disengage the loops, press the **Stop** key. 

The Red **Alarm** LED is illuminated whenever a user programmed has been triggered. To clear the alarm, the enabled event that is asserting the alarm must be disabled. 

The Green **Remote** LED can be turned on or off under program control by the remote interface. Use of this LED by a computer connected to the instrument is optional. 

### The VFD Display 

#### Home Status Displays 

At the top of the instrument’s menu tree are the home status displays. They can be selected from anywhere in the instrument’s menu tree by pressing the **Home** key. 

The list of display configurations is accessed by pressing the **Display** key: 

1. Dual Input Status (default) 

2. Loop 1 Status 

3. Loop 2 Status 

4. Dual Loop Status 

5. Ch A Statistics 

6. Ch B Statistics 

Select the desired configuration and press the **Enter** to return to the Home display. 

#### <u>Dual Input Status Display</u> 

This is the factory default display. It shows the status and current input temperature for both control loops. 

Input channel A is shown on the left and channel B on the right. 

    

22 

Front Panel Operation 

Model 32 / 32B User's Manual 

The second line of the display shows the Loop Status Display. Directly above each Loop Status is a temperature for the controlling input channel. In the example here, Loop 1 is being controlled by input channel A and Loop 2 is being controlled by input channel B. Please note that either loop may be controlled by either input. The display will be adjusted to show the control loop directly below the controlling input channel. 

The next example shows the control inputs reversed, Loop 1 controlling in the low power range and Loop 2 off. 

#### <u>Loop 1 and Loop 2 Status Displays</u> 

These displays show the current status of a selected single control loop. Information includes the controlling input channel, temperature, setpoint, heater status and heater bar chart. 

In the example shown here for Loop 2, the loop is controlling from input B with 30% output power and the setpoint is 17.0000K. 

    

   

#### <u>Dual Loop Status</u> 

The Dual Loop Status display is similar to the Dual Input Status display described above. However, on this display, control loop #1 is always on the left side and loop #2 is always on the right. 

#### <u>Channel A and B Statistics Display</u> 

The Channel A and B statistics displays show the selected input channel temperature, the slope of the temperature history, the minimum and maximum temperatures. 

  

The slope of the temperature history (M) is given in Display Units per Minute. In this example, Display Units are Kelvin. 

#### Temperature Displays 

A typical Input Channel Temperature Display is shown here. It consists of the input channel designator, a Temperature reading and the current temperature units. 

The input channel designator is a superscripted A or B. 

The temperature is a seven-character field and is affected by  the Display Resolution setting in the **Sys** menu. This setting may be 1, 2, 3 or Full. Settings of 1, 2, or 3 indicate the number of digits to the right of the decimal point to display whereas the Full setting causes the display to be left justified in order to display the maximum number of significant digits possible. 

 

23 

Front Panel Operation 

Model 32 / 32B User's Manual 

The Display Resolution setting does not affect the internal accuracy of arithmetic operations. It is generally used to eliminate the display of unnecessary digits that are beyond the sensor’s actual resolution. 

If the Input Channel has been disabled, a blank display is shown. 

Temperature units are selected in the individual input channel setup menus, **ChA** or **ChB** . Temperature Units may be K, C or F. When Sensor Units (S) is selected, the raw input readings are displayed. These will be in Volts or Ohms. 

<!-- Start of picture text -->
K Kelvin<br>C Celsius<br>F Fahrenheit<br>Ω Ohms<br>V Volts<br><!-- End of picture text -->

**Table 7: Temperature Units** 

#### <u>Sensor Fault Display</u> 

A sensor fault condition is identified by a temperature display of seven dash ( **-** ) characters as shown here. The sensor is open, disconnected or shorted. 

 

#### <u>Temperature Out of Range Display</u> 

If a temperature reading is within the measurement range of the instrument but is not within the specified Sensor Calibration Curve, a display of seven dot ( **.** ) characters is shown. 

<!-- Start of picture text -->
<br><!-- End of picture text -->

 **Note:** In some cases, there will be an erratic temperature display when no sensor is connected. This is not an error condition. The high input impedance of the controller’s input preamplifier causes erratic voltage values when left unconnected. 

24 

Front Panel Operation 

Model 32 / 32B User's Manual 

#### Loop Status Displays 

|When t<br>shown.<br>The firs<br>either a<br>The Lo<br>|he Model 32 is not controlling temperature, the statu<br> <br>t character of the Loop Status Display is always the<br>superscripted 1 or 2 corresponding to Loop 1 or Lo<br>op number will be followed by the heater status as fo<br>|s of the Loop output is<br>loop number, which will be<br>op 2.<br>llows:|
|---|---|---|
|1.|**-OFF-**Indicates that heater output is functional<br>and the control loop is off or disabled.||
||<br>For the primary heater, Loop 1, the range is also sh<br>be either**Hi**,**Mid**or**Low**. The range is set in the**L**<br>For the secondary output, or Loop 2, the range will<br>Model 32B, or**10V**for a Model 32.|own. Range settings may<br>**oop 1**menu.<br>be shown as**10W**for a|
|2.|**Overtemp**indicates that the controller’s Internal Te<br>shut off the heater. This fault is usually the result|mperature Monitor circuit|
||<br>of a shorted heater, or use of a heater with<br>significantly less resistance than the selected<br>load resistance.||
|3.|**Readback**indicates that the Current Readback Mo<br>the heater. This monitor compares the actual|nitor circuit has shut down|
||heater output Current with the indicated output<br>Current and asserts a fault condition if there is a<br>difference. This fault is usually the result of a<br>broken heater cable or an open heater.||
|4.|**SensorFLT**indicates that the heater was shut dow<br>the on the controlling input channel. This is usually<br>sensor or sensor cables. None: A sensor fault will<br>not shut down the heaters if the loop is in Manual<br>output mode.|n by a fault condition on<br>caused by an error in the<br>|
|5.|**OTDisconn**indicates that the heater output was di<br>Temperature Disconnect Monitor. This monitor is c<br>functions to disable the heater if a specified over te<br>exists on a selected input channel. See the**Sys**|sconnected by the Over<br>onfigured by the user and<br>mperature condition is|
||menu for information on how to configure and<br>use this important feature.||

25 

Front Panel Operation 

Model 32 / 32B User's Manual 

If the Model 32 is controlling temperature (loop ON), the heater status display shows the loop output as a percentage of full scale. 

This example shows the Heater Status for Loop 2 in a Model 32B controller. The unit is in control mode and is outputting 30% of full scale output current. This means that the output power is (30%)^2, or 9% of 10 Watts. 

###  

#### The Loop Bar Chart Display 

The Loop Bar Chart is a 50-segment bar chart that shows the measured output of a selected loop output. 

The bar is composed of ten blocks with five segments. Therefore, output current can be read to an accuracy of 2%. 

Note that the bar chart does not have a loop number indicator. 

Some examples are: 

<!-- Start of picture text -->
Loop ON, zero output: <br>Loop OFF: <br>Loop ON, 50% output: <br><!-- End of picture text -->

 **Note** : The Model 32 uses an independent circuit to read current actually flowing through the load. The heater bar graph shows this measured current. If the unit is controlling temperature, but the bar graph indicates zero current flow, an error condition exists, possibly an open heater. 

26 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

## Front Panel Menu Operation 

### Instrument Setup Menus 

The various instrument setup menus are accessed by pressing one of the Setup Menu keys. The display must be in ‘Home Status’ in order for these keys to be active. 

The user may exit a Setup Menu and return to the Home Status display at any time by pressing the **Home** key. 

The first one, or more characters on a line identify the specific menu. For example, the first character of every line in the Loop 1 setup menu is the loop identifier, which is a superscripted 1. 

Menus contain several lines, so the display must be scrolled by using the and keys. 

The last character of each line in a setup menu is the format indicator. The indicator will be blank until the cursor is moved to the line. 

Format indicators are: 

- #  - Numeric entry is required 

- Enumeration entry using the and keys. 

- The line is selected by pressing the **Enter** key. 

#### The Setpoint Menu 

The setpoint menu is accessed by pressing the **Set Pt** key. This gives one-key access to the setpoints for both control loops. The following 2-line menu will be shown.  

  

The pound sign (#) character at the end of the top line is the cursor. Use the and keys. to move the cursor between control loop 1 and 2. The location of the cursor is remembered so that it will point to the same loop each time. 

To enter a new setpoint, use the numeric keys and then press the **Enter** key. This will update the setpoint on the selected control loop and return the display to the Home display. 

Press the **Home** key to exit the menu without update. 

27 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### The Alarm Status Display Menu 

The current status of the temperature alarms may be viewed by pressing the **Alarm** key. A display like this one will be shown: 

 Alarms are set for each input  channel using the Input Channel Setup menu described below. 

When an alarm is asserted, the Alarm LED on the front panel will light. Pressing the **Alarm** key will display all of the alarms. Status is shown as follows: 

**—** No alarm **LO** Low temperature alarm **HI** High temperature alarm 

The letter L at the end of the line indicates that the alarm is latched. A latched alarm is asserted when the alarm condition is set. It stays asserted until it is manually cleared by the user. 

 **Note:** To clear a latched alarm, first press the **Alarm** key to view the alarms and then press the Home key to clear the latch and return to the **Home** display. 

28 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### The Display Configuration Menu 

The display configuration menu is accessed by pressing the **Display** key. When accessed, the menu will appear as a list of possible configurations. The cursor, indicated by a character, will be located at the current configuration. Use the and keys to move up and down the list. 

Display configurations are: 

|**Dual Input**<br>**Status**|(Default). Input channel status. Displays temperature of both<br>input channels and the status of any control loop assigned to<br>the inputs.|
|---|---|
|**Loop 1 Status**|Detailed status of control loop #1. Temperature of controlling<br>input channel, setpoint, heater status and bargraph.|
|**Loop 2 Status**|Detailed status of control loop #2. Temperature of controlling<br>input channel, setpoint, heater status and bargraph.|
|**Dual Loop**<br>**Status**|Control loop status. Displays the status of both control loops on<br>the second line of the display. On the first line the temperature<br>of the controllinginput is shown.|
|**Ch A Statistics**|Temperature statistics for input channel A. Shows current<br>temperature, maximum, minimum and accumulation time. For<br>additional statistical information, refer to theInput Channel<br>Setup Menu.<br>Note: Pressingthe**Enter**keywill reset the statistics.|
|**Ch B Statistics**|Temperature statistics for input channel A. Shows current<br>temperature, maximum, minimum and accumulation time. For<br>additional statistical information, refer to theInput Channel<br>Setup Menu.<br>Note: Pressingthe**Enter**keywill reset the statistics.|

**Table 8: Display Configurations** 

Select the desired configuration and press the **Enter** to return to the Home display. Refer to the section “Home Status Displays” for more information. 

29 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### Input Channel Setup Menu 

The Input Channel Setup menus are selected by pressing the **ChA** or **ChB** keys from a Home Status Display. These menus contain all of the user-configurable parameters for a selected sensor input channel. 

The first character on each line of these menus is always the input identifier, which is a superscripted A or B for Input A or Input B. 

Use the and keys to move up and down the list. 

||**ChA, ChB Setup **|**Menu**<br>|
|---|---|---|
|1||Input channel units. Temperature is<br>displayed on the left and is in the selected<br>units. Selections are K, C, F or S. Here, S<br>selects primitive sensor units. When S is<br>selected, the actual sensor units of Volts<br>or Ohms will be displayed.|
|2||Sensor type selection. Allows selection of<br>any user or factory installed sensor. The<br>I20 shown indicates that the current<br>sensor is factory installed sensor #20.|
|3||Selecting this field by pressing the Enter<br>key will take the display to the CalGen<br>screen.|
|4||Setpoint for the High Temperature alarm.<br>Use the keypad for numeric entry and<br>then press the Enter key.|
|5||High temperature alarm enable.<br>Selections are Yes or No.|
|6||Setpoint for the Low Temperature alarm.|
|7||Enables latching alarms on the selected<br>input channel.|
|8||Enables the internal audio alarm to sound<br>on any enabled alarm condition.|
|9||Enables or disables latching alarm<br>conditions. A latched alarm is cleared by<br>pressing the Alarm key followed by Home<br>key.|
|10||Continuously displays the Maximum<br>temperature on this input channel.<br>Pressing the**Enter**key resets.|
|11||Continuously displays the Minimum<br>temperature on this input channel.<br>Pressing the**Enter**key resets.|
|12||Displays the accumulation time for the<br>input channel statistics. Pressing the<br>**Enter**key resets.|

30 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

|13<br>|**ChA, ChB Setup Me**<br>|**nu(cont)**<br>Displays the variance of the input channel<br>temperature over the accumulation time.<br>Pressing the**Enter**key resets the<br>accumulation time.|
|---|---|---|
|14<br>||Displays the slope, or rate of change, of<br>the input temperature over the<br>accumulation time. Pressing the**Enter**key<br>resets the accumulation time.|
|15<br>||Displays the offset of the input temperature<br>over the accumulation time. The M and b<br>statistics are the slope and offset of a<br>straight-line fit to the input channel<br>temperature. Pressing the**Enter**key<br>resets the accumulation time.|
|16<br>||Selects sensor bias type. Applies only to<br>resistor sensors that use constant-voltage<br>excitation. All others show N/A. Choices<br>are: 10mV , 3mV and 1.0mV|

**Table 9: Input Channel Setup Menus.** 

#### **Temperature Units** 

Enumeration, Default: K 

The Temperature Units field (line 1) assigns the units that are used to display temperature for the input channel. Options are K for Kelvin, C for Celsius, F for Fahrenheit and S for sensor units. Note that if the S option is selected, the actual sensor units will be displayed when the field is deselected. Available sensor units are V for Volts and Ω for Ohms. 

Use the or key to scroll through all of the options. When the desired units are displayed, press the **Enter** key to make the selection. The display will now show the current temperature with the new units. 

**Sensor Type Selection** Enumeration Line 2 selects the Sensor type for the input channel. When this field is selected, the scroll keys are used to scroll through all of the available sensor types. Factory installed sensors appear first and then user sensors. For a list of both factory and user sensors, refer to Appendix A. 

New user sensor types and calibration curves are added using the **Sensors** menu. 

#### **CalGen™** 

Selection of the CalGen  field initiates the calibration curve generator feature. This feature is described in the section “CalGen Calibration Curve Generator”. 

31 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### **Setting a Temperature Alarm** 

The Alarm lines are used to setup alarm conditions. The Model 32 allows alarm conditions to be assigned independently to any of the input channels. 

High temperature and low temperature alarms may be entered and enabled. Note that there is a 0.25K hysteresis in the assertion of high and low temperature alarms. 

Alarm conditions are indicated on the front panel by the Alarm LED and various display fields. They are also reported via the remote interfaces. 

When the audible alarm is enabled, a high-pitched buzzer will sound when an alarm condition is asserted. 

The Model 32 supports latched alarms. These are alarms that remain asserted even after the condition that caused the alarm has been cleared. To clear a latched alarm, first press **Alarm** to view the Alarm Status Display and then press the **Home** key to clear. 

#### **Input Channel Statistics** 

The Model 32 continuously tracks temperature history on each input channel. The Input Statistics shown in this menu provides a summary of that history. 

The channel history is reset whenever the channel is initialized and can also be reset by pressing the **Enter** key while the cursor is on any of the statistics lines. 

The **Accum** line shows the length of time that the channel history has been accumulating. It is in units of Minutes. 

The **Minimum** and **Maximum** temperature lines show the temperatures from during the accumulation time. Values are shown in the currently selected display units. 

**S2** is the temperature variance, which is computed as standard deviation squared. 

The **M** and **b** fields display the slope and the offset of the LMS best-fit straight line to the temperature history data. 

**Bias Voltage Selection** Enumeration, Default: 10mV 

The Model 32 supports constant-voltage AC excitation for resistor sensors. Other sensors, including diodes, are supported by DC constant-current excitation. 

Sensor type ACR indicates an AC resistor sensor that uses constant-voltage bias. Here, the Bias Voltage field will show selections of 10.0mV, 3.3mV and 1.0mV to indicate the voltage that is held on the sensor. The Model 32 has an autoranging current source that will maintain the selected voltage. 

For sensor types other than ACR, the Bias Voltage field will show N/A for not applicable. 

Additional information on excitation voltages and currents is given in the section “Input Channels”. 

32 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### The Control Loop Setup Menu 

The control loop setup menus are selected by pressing the **Loop 1** or **Loop 2** key from a Home Status Display. These menus contain all of the user-configurable parameters for the selected control loop. 

The **Loop 1** menu is used to perform the setup of the primary 25/50 Watt heater output. This display was designed to provide all of the information required to tune heater parameters and is, therefore rather complex. 

The **Loop 2** menu is used to perform the setup of the secondary output. For a standard Model 32, this is a zero to 10 Volt output. For a Model 32B this is a 10 Watt current source. 

The first character on each line of the control loop setup menu is always the loop identifier, which is a superscripted 1 or 2 for Loop 1 or Loop 2. 

33 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

||**Loop #1, Loop #2 Set**|**up Menu**|
|---|---|---|
|1|<br>|Numeric setpoint entry. The<br>temperature of the controlling input is<br>shown on the left and is continuously<br>updated. Use the keypad to enter a new<br>setpoint and then press the Enter key.<br>Control loop setpoints may also be<br>accessed from the**Set Pt**key.|
|2||Proportional gain, or P term for PID<br>control.|
|3||Integrator gain term, in Seconds, for<br>PID control.|
|4||Derivative gain term, in inverse-<br>Seconds, for PID control.|
|5||Output power, as a percent of full scale,<br>when controlling in the Manual mode.|
|6||Control input channel, ChA or ChB|
|7||Output power range. For loop 1, this will<br>be HI, Mid or Low. For loop 2 on a<br>Model 32, it will be10V and for a Model<br>32B, it will be 10W.|
|8||Control Type. Selections are: Off, Man,<br>PID, RampT, RampP and Table.|
|9||Power limit as a percent of full scale.<br>On loop 1, this limit only applies to the<br>HI range.|
|10||Maximum value allowed for the setpoint<br>on this loop.|
|11||Table number for control in Table mode.<br>The Model 32 has six PID tables<br>numbered from zero through five.|
|12|Ω|Sets the heater load resistance.<br>Selections are 25 and 50.|
|13||Ramp rate in temperature units per<br>minute.|

**Table 10: Control Loop Setup Menus.** 

34 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### **Setpoint** 

Numeric Entry 

The first line of this menu the user can change the setpoint, while still viewing the temperature of the controlling source channel. This allows the user to view the temperature without leaving the setup menu. 

 **Note:** Entry of a setpoint can be overridden by the Maximum Setpoint field described below. The instrument will not accept an entry that exceeds the maximum. 

Control loop setpoints may also be entered by using the **Set Pt** key. 

**Control Loop PID values** Numeric Entry 

The Pgain, Igain and Dgain lines correspond to the Proportional, Integral and Derivative coefficients of the control loop. Pman is the output power that will be applied to the load if the manual control mode is selected. 

Values for the Proportional, or P, gain term range from zero to 1000. This is a unitless gain term that is applied to the control loop. Gain is scaled to reflect the actual heater range and the load resistance. 

Integrator gain values range from zero to 10,000. The units of this term are Seconds. A value of zero turns the integration function off. 

Derivative gain values have units of inverse Seconds and may have values from zero to 1000. A value of zero turns the Derivative control function off. 

The Pman field is only used when the heater output is in manual control mode. The value is in percent of full-scale output power (Watts) and may have values from zero to 100%. 

 **Note:** The Model 32 expresses heater output values in terms of percent of full-scale output power. The actual power, in Watts, applied to the load is proportional to the square-root of output current. 

**Control Source Input Channel** Enumeration, Default: Loop #1- ChA Loop #2- ChB The input filed selects the control loop source input. Any input channel may be selected. 

35 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

**Control Loop Range** Enumeration, Default: Loop #1- Low 

The Range field selects the full-scale output for the selected control loop. 

For Loop #1, settings are HI, MID and LOW. The actual full-scale output power is determined by this setting along with the load resistance. See the Heater Output Ranges Table for more information. 

The full-scale output range for Loop #2 is fixed and cannot be changed by using the Range field. For a Model 32, the output is a 0 to 10Volt voltage source. For the Model 32B, the output is a 10 Watt linear current source. 

**Control Types** Enumeration 

The Type filed selects the actual control algorithm used for the selected loop. Selections are: Off, PID, Man, Table and RampP. 

Loop control modes are: 

1. **Man** for Manual control mode. Here, a constant heater output power is applied when the unit is controlling temperature. The Pman field selects the output as a percentage of full-scale. 

2. **Table** . This is a PID control mode where the PID coefficients are generated from a stored PID table based on setpoint. 

3. **PID** for standard PID control. 

4. **Off** . In this mode, the controller will not apply power on this output channel. Note that the Model 32 is a dual-loop controller. The Off control mode is used if regulation is desired only on the other channel. 

5. **RampP** . This is a temperature ramp mode. When a ramp operation is complete, the controller will revert to standard PID mode control at the final setpoint. 

For more information on control algorithms, refer to the Heater Control Types table above. 

For more information on temperature ramps, refer to the section on Temperature Ramping below. 

36 

Model 32 / 32B User's Manual 

Front Panel Menu Operation 

**Output Power Limit** Numeric entry, Default: 100% 

The Power Limit field defines the maximum output power that the controller is allowed to output. It is a percent of the maximum allowed output. Maximum value is 100% and minimum is 15%. 

For Loop #1, the Power Limit is applied to the HI range only. For lower power levels on this loop, select either the MID or LOW range. 

For Loop #2, the Power Limit is always applied. 

 **Note:** Output Power Limit is an important cryostat protection feature. The user is encouraged to apply it. 

**Maximum Setpoint** Numeric Entry, Default: 1000K 

The Maximum Setpoint field is used to prevent the casual user from inadvertently entering a temperature that might damage the cryostat. 

Maximum value is 10,000K and minimum is 0K. 

Setpoint values use the temperature units selected for the controlling input channel. See the section on Temperature Displays. 

 **Note:** The Maximum Setpoint selection is an important cryostat <u>protection feature. The user is encouraged to apply it.</u> 

**PID Table Index** Numeric entry, Default: 0 

The PID Table index line is used to identify the number of the user supplied PID Table that will be used when the Table control mode is selected. The Model 32 will store up to six PID Tables. They are numbered zero through five. 

37 

Model 32 / 32B User's Manual 

Front Panel Menu Operation 

#### **Heater Resistance** 

Enumeration, Default: 25 Ω 

The heater resistance field is an enumeration that sets the value of the heater load resistance. Choices are 50 Ω and 25 Ω . When 50 Ω is selected, the heater will output a maximum of 50 Volts at 1.0 Ampere or 50 Watts. When 25 Ohms is selected, the maximum heater voltage is 25 Volts and the output power is 25 Watts. 

For additional information, please refer to the Heater Ranges table above. 

**Warning:** It is necessary to set the Load resistance field to the actual value of the heater load resistance being used. If an incorrect value is selected, output power indications will be incorrect and non-linear heater operation may result. If the actual heater resistance is less than selected, the heater may overheat resulting in an automatic over temperature shutdown. 

#### **Ramping Rate** 

Numeric entry, Default: 0.10/min 

When performing a temperature ramp, the Ramp field defines the ramp rate. Units are display units per minute. In the default case, this means Kelvin per minute. 

For more information on temperature ramps, refer to the section on Temperature Ramping below. 

38 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### User Configurations Menu 

The User Configurations Menu is displayed by pressing the **Config** key. It is used to save or restore up to four instrument setups. Each setup saves the entire state of the Model 32 including setpoints, heater configurations, input channel data etc. 

||**User Configurations**|**Menu**|
|---|---|---|
|1||Selects the user configuration. The<br>Model 32 has four configurations<br>available.|
|2||Pressing the**Enter**key saves the<br>instrument setup to the selected<br>configuration number.|
|3||Pressing the**Enter**key restores a<br>saved configuration.|

**Table 11: User Configurations Menu** 

To save or restore a setup, select the desired configuration number on line 1. Then, move the cursor to either Save or Restore and press the **Enter** key. 

When a configuration has been saved, the menu shown here will be displayed indicating that the current instrument setup has been written to 

  

the controller’s FLASH memory and may be retrieved by using the Restore function. 

If the user attempts to restore an invalid configuration, an error display is shown. This is usually caused by attempting to restore a configuration that was never saved.  

 

When a configuration is successfully restored, the display shown here is shown. After a one or 

two seconds, the controller will automatically perform a power-up reset with the restored data. 

39 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### The System Functions Menu 

This menu is accessed by pressing the **Sys** key from the Home Status Display. It is used to set many of the instrument’s parameters including display resolution, I/O port settings etc. 

||**System Functions**|**Menu**|
|---|---|---|
|1||Sets the display time constant in<br>seconds. Selections range from 0.5S to<br>64S|
|2||Sets the resolution. Selections are: 1, 2,<br>3 or Full.|
|3||Enables or disables Cold Junction<br>Compensation for Thermocouple<br>sensors. Only shown when the<br>thermocouple option is present.|
|4||Offset, in<sup>o</sup>C, applied to thermocouple<br>Cold Junction Compensation. Only<br>shown when the thermocouple option is<br>present.|
|5||Display brightness. Selections are 0,1,2<br>and 3|
|6||Sets the Over Temperature Disconnect<br>enable. Selections are On or Off.|
|7||Sets the Over Temperature Disconnect<br>source input channel. Selections are<br>ChA or ChB.|

40 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

||**System Functions Men**|**u(cont.)**|
|---|---|---|
|8||Sets the Over Temperature Disconnect<br>setpoint temperature.|
|9||Selects the port for remote I/O.<br>Selections are RS232 or GPIB.|
|10||Sets GPIB I/O address. It is a numeric<br>entry with a range of 1 to 31. Default is<br>12.|
|11||Sets RS-232 port baud rate. Selections<br>range from 300 to 38K baud.|
|12||Advanced configuration: Number of<br>taps in the synchronous filter. Normally<br>set to a value of 7.|
|13||AC line frequency. Select 50 or 60Hz.|
|14||Power Up Mode. Off for normal<br>operation. On to engage the control<br>loops 10 seconds after power has been<br>turned on.|
|15||Remote I/O: Last command received.|
|16||Remote I/O: Last response.|

**Table 12: System Functions Menu** 

#### **Display Time Constant** 

Enumeration, Default: 2 Seconds 

The SYS-Display TC field is used to set the display time-constant. This is an enumeration field that sets the time constant used for all temperature displays. Choices are 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0 and 64 Seconds. 

The time-constant selected is applied to all channels and is used to smooth data in noisy environments. The filtering only applies to displayed data; it is not used by the control loops. 

41 

Model 32 / 32B User's Manual 

|Front Panel Menu Operation|
|---|

#### **Display Resolution** 

Enumeration, Default: 3 

The Display Resolution line (SYS-Display RS) is used to set the temperature resolution of the front panel display. Settings of 1, 2 or 3 will fix the number of digits to the right of the decimal point to the specified value. A setting of FULL will left-justify the display to show maximum resolution possible. 

Note that the Display Resolution setting only formats the display as a user convenience. The internal resolution of the Model 32 is not affected by this setting. 

**Display Brightness** Enumeration, Default: 2 

The SYS-Brightness field is used to control the brightness of the display. Selections are 0, 1, 2 and 3 with 0 being the brightest. This control does not take effect until the next power-up. 

#### **Over Temperature Disconnect** 

The Over Temperature Disconnect (OTD) feature is configured using the OTD- lines. This feature allows the user to specify an over temperature condition on any of the input channels. 

Whenever an over temperature condition exists on the selected channel, the heaters outputs are disconnected and the Loop Status indicator is set to "OTDisconn". 

Both loops are disconnected when an over temperature condition exists. A mechanical relay is used so that the load is protected, even if the condition was caused by a fault in the controller’s output circuitry. 

The OTD must first be configured to monitor one of the input channels. Note that the OTD feature is completely independent of control loop function and may monitor any input. 

Next, an OTD Setpoint must be specified. This is the temperature at which an over temperature shut down will be asserted. Temperature units are taken from the source input channel. 

Finally, the OTD function must be enabled. 

**Important** : The Over Temperature Disconnect is an important cryostat protection feature. The user is encouraged to apply it. 

42 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### **Remote I/O Port Configuration** 

The RIO- lines are used to configure the Remote I/O interfaces including the GPIB and RS-232. 

Note that ‘GPIB’ is used to indicate the controller’s IEEE-488.2 interface. 

Port Select (RIO-Port) is an enumeration field that sets the active remote port. The controller can only have one active port at a given time. Inactive ports are disabled. Choices are RS-232 and GPIB. The factory default is RS-232. 

The address line (RIO-Address) is a numeric field that may have a value between 1 and 31. The factory default is address 12. This field is used by the GPIB interface to select individual instruments. It is the user’s responsibility to configure the bus structure with unique addresses for each connected instrument. 

RS232 Rate is an enumeration of the RS-232 baud rate. Choices are 300, 1200, 2400, 4800, 9600, 19k for 19,200 and 38K for 38,400. 

**Synchronous Filter Configuration** Numeric Entry Default: 7 The Synchronous Filter is used to subtract synchronous noise from the input channel. An example of synchronous noise is the thermal signature of a cryocooler. 

The default value of 7 taps is used for a line-frequency synchronous cryocooler. Values go from 1 (off) to 25 taps with 25 corresponding to 2.5 seconds of filtering. 

This is an advanced setup function. Unless you are familiar with the synchronous noise source that you are trying to remove, leave this field at its default value of 7. 

When the number of taps is changed, the control loops will have to be re-tuned because this filter affects the PID values. 

**AC Line Frequency Selection** Enumeration, Default: 60Hz Select the AC power line frequency. Choices are 50 or 60 Hz. This function only affects the operation of the Synchronous Filter described above. 

**Power-up in Control Mode.** Default: Off The SYS-Auto Ctl: field sets the power up mode of the controller’s loops. Choose ‘Off’ for normal operation where the control loops are engaged by pressing the **Control** key and disengaged by pressing the **Stop** key. When SYS-Auto Ctl is ON, the controller will power up, then after ten seconds, will automatically engage the control loops. 

#### **Remote I/O transactions** 

The last two lines of the SYS menu are the Remote I/O input and output lines. These are used to assist in debugging programs that use the controller over one of its remote interfaces. The remote input line ( **>** ) shows the last complete command received and parsed by the controller. The remote output line ( **<** ) shows the response that the command generated. 

43 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### PID Tables Menu 

The Model 32 can store four user generated PID tables. Each table may have up to sixteen setpoint zones. 

Each setpoint zone in a table requires the entry of a setpoint along with corresponding values for P, I, D and full scale heater range. 

When controlling in the Table mode, the Model 32 will derive control loop PID coefficients and heater range by interpolation of the PID Table zones based on that zone’s setpoint. 

PID Tables can be used with both control loops. 

Building a table from the front panel requires the entry of several numeric values. For this reason, the user may want to consider using one of the remote interfaces. 

The start, and top level, of this process is the PID Tables menu. Two menu screens below this are used to enter numeric data. Here is an overview of the process: 

1. The PID Tables menu is used to select the PID Table number (zero through three). 

2. Once the table is identified, selecting the EDIT PID TABLE line will take the menu used to edit individual lines of the selected table. 

3. To enter or edit an entry, set the desired entry index and enter the zone data on the following lines. 

4. The last line of this menu is used to save the table when line entry is complete. 

When a table is saved, it is automatically conditioned so that it can be used directly by the control loop software. The conditioning deletes all entries with setpoint values of zero or less and sorts the table based on setpoint. Therefore, an entry may be deleted by setting the setpoint to any negative number. 

44 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### <u>The PID Table Menu</u> 

The PID Table Menu is accessed by pressing the **PID Table** key from the Home Display. 

The first three characters of each line on the initial PID Table menu are a two-digit index followed by a single vertical bar. The index identifies the currently selected table and will change whenever the table number is updated. 

|||**PID Table Men**|**u**|
|---|---|---|---|
|1|||Sets the PID table number for editing.<br>Selections are 0 to 3.|
|2|||Displays the number of zones in the<br>selected PID table. Note. This number<br>is generated from the selected table<br>and cannot be changed in this menu.|
|3|||Pressing the Enter key on this line will<br>take the display to the second level<br>menu where the selected table is<br>entered.|

**Table 13: PID table Menu** 

The first line (01|) is the table index. This field is used to select a table for editing. 

Below this is N, the number of valid entries in the table. This number was generated when the user entered table and cannot be changed using this menu. 

45 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### <u>The PID Table Edit Menu</u> 

The EDIT PID TABLE line is selected to enter and edit zones within the selected table. This will take the display to the PID Table Edit Menu shown below. 

The first four characters of the PID Table Edit Menu show the selected table index followed by TWO vertical bars. 

||**PID Table Edit M**|**enu**|
|---|---|---|
|1<br>||Sets the line number index to edit /<br>view. Values are 0 through 15.|
|2<br>||Line setpoint entry.|
|3<br>||Line P gain  entry.|
|4<br>||Line I gain  entry.|
|5<br>||Line D  gain  entry.|
|6<br>||Sets the heater range. This entry is<br>ignored by Loop 2.|
|7<br>||Save the table and exit by pressing the<br>Enter key. Exit without saving by<br>pressing the**Esc**or**Home**key.|

**Table 14: PID Table Edit Menu** 

Pressing the **Esc** key from this menu will abort the line entry process and return the display to the PID Table Menu above. Any edits made to the line will be lost. 

When an index is selected, all of the lines on this menu will be updated to show the selected index. Any data in the selected index will be displayed on the following lines. 

The following data can be entered into the PID zone: Setpoint (SP), Proportional gain (P), Integral gain (I), Derivative gain (D) and heater range. Note: the heater range entry is ignored for Loop 2. 

To delete a zone from the PID Table, enter zero or a negative number in the setpoint field. These entries will be rejected when the table is conditioned and stored in Flash memory. 

Save the entire table by scrolling to the last line, SaveTable&Exit, then press the **Enter** key. 

46 

Front Panel Menu Operation 

Model 32 / 32B User's Manual 

#### Sensor Setup 

The Sensor Setup menu is used to view and edit user temperature sensor data. 

#### <u>The Sensor Setup Menu</u> 

Pressing the **Sensor** key from the Home Status Display accesses the Sensor Setup Menu. 

Definition of a sensor requires entering configuration data on this screen followed by entering a calibration curve. 

The first three lines of the Sensor Setup Menu show the Sensor Index followed by a ‘greater than’ (>) character.  This > character indicates the first level of the Sensor Setup menu. 

||**Sensor Setup Me**|**nu**|
|---|---|---|
|1||Sets the Sensor Index. Scroll through<br>choices until the desired sensor is<br>displayed and press**Enter**.|
|2||Sets the Sensor Type, which includes<br>voltage range and excitation. Selections<br>are described in the Sensor Type table<br>above.|
|3||Sets the sensor Temperature<br>Coefficient and Calibration Curve<br>Multiplier.|
|4||Sets Units of the sensor’s Calibration<br>Curve. Choices are: Ohms, Volts and<br>LogOhm.|
|5||Pressing Enter will display the next level<br>menu where the sensor’s Calibration<br>Curve data may be viewed and edited.|

**Table 15: Sensor Setup Menu** 

The first line on this menu is the sensor table index. Selecting this field will allow scrolling through all of the sensors configured in the unit, including user sensors. The index is displayed along with the sensor name. 

Note: the sensor name may be entered via any of the Remote I/O interfaces, but may not be changed from the front panel. 

Sensor Type is an enumeration of all of the basic sensor types supported by the Model 32. Choices are shown in the **Supported Sensor Configurations** table above. 

The **Multiplier** field is a floating-point numeric entry and is used to specify the sensor's temperature coefficient and to scale the calibration curve. Negative multipliers imply that the sensor has a negative temperature coefficient. The absolute value of the multiplier scales the calibration curve. For example, the curve for a Platinum sensor that has 100 Ω of resistance at 0 ° C may be used with a 1000 Ω 

47 

Model 32 / 32B User's Manual Front Panel Menu Operation 

sensor by specifying a multiplier of 10.0. Also note that the temperature coefficient field is only used when the unit is controlling temperature based on the sensor units of Volts or Ohms. 

**Units** is an enumeration field that identifies the primitive units used by the sensor’s calibration curve. Choices are Volts, Ohms and LogOhm. LogOhm selects the base ten logarithm of ohms and is useful with sensors whose resistance vs. temperature curve is logarithmic. 

Selecting the ‘EDIT CAL CURVE’ field will cause the screen to go to the Calibration Curve menu for the selected sensor. Here, the calibration curve may be viewed or edited. 

#### <u>The Calibration Curve menu</u> 

The Calibration Curve menu is the first screen used in the process of building a sensor calibration curve. Note that these curves can have up to 200 points requiring the entry of 400 floating point numeric values. For lengthy curves, you may want to consider using one of the remote interfaces. Cryocon provides a free PC utility that will upload or download curves that can be created by a text editor. 

The entry of a sensor calibration curve is essentially identical to the process used to enter PID Tables. The procedure for entering or editing a calibration curve is summarized as follows: 

1. The sensor’s calibration curve is accessed from the Sensor Setup menu detailed above. 

2. Data points in the selected curve are entered by first entering the entry index, then values for sensor readings vs. corresponding Temperature. 

3. When all data points have been entered, the SaveCurve&Exit field is selected to save the curve. 

Once complete, the controller will condition the curve by rejecting invalid entries, then sorting the curve in order of ascending sensor unit values. Therefore, an entry may be deleted by placing a zero or negative number in either the temperature field. 

The first four characters of a Calibration Curve Menu show the two-digit sensor index followed by either the sequence >>. 

48 

Model 32 / 32B User's Manual 

Front Panel Menu Operation 

||**Calibration Curve**|**Menu**|
|---|---|---|
|1||Sets the current index to an entry within<br>the current table. Values are 0 to 159.<br>When the**Enter**key is pressed, the<br>following lines will display any data<br>corresponding to the selected entry.|
|2||Temperature. Units are always in<br>Kelvin.|
|3||Sensor reading. Units are taken from<br>the Sensor Setup menu described<br>above.|
|4||Pressing Enter will display the next level<br>menu where the sensor’s Calibration<br>Curve data may be viewed and edited.|

**Table 16: Calibration Curve Menu** 

#### The Auto Tune Menu 

The Model 32 can automatically tune both control loops. For a complete description of the autotune process including configuration of the tuning menus, refer to the section titled autotuning. 

49 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

## Specifications, Features and Functions 

### Specification Summary 

#### **User Interface** 

**_Display Type_** _:_ 20 x 2 character VFD, 9mm character height. **_Number of Inputs Displayed:_** Two. 

**_Keypad_** _:_ Sealed Silicon Rubber. **_Temperature Display_** _:_ Six significant digits, autoranged. **_Display Update Rate:_** 0.5 Seconds. **_Display Units:_** K, C, F or native sensor units. 

**_Display Resolution:_** User selectable to seven significant digits. 

#### **Input Channels** 

There are two input channels, each of which may be independently configured for any of the supported sensor types. 

**_Sensor Connection_** _:_ 4-wire differential. DIN-5 input connectors mate with either DIN-5 or DIN-6 plugs. Connections are described in the “Sensor Connections” section. 

#### **_Supported Sensors_** _:_ Include: 

|**Type**|**Excitation**|**Temperature Range**|
|---|---|---|
|**Cernox**|Constant-Voltage AC|0.3 to 420K|
|**Ruthenium Oxide**|Constant-Voltage AC|200mK to 273K|
|**Thermistors**|Constant-Voltage AC|70 to 325K|
|**Rhodium-Iron**|1mA DC|1.4 to 800K|
|**Germanium**|Constant-Voltage AC|0.3K to 100K|
|**Carbon Glass**|Constant-Voltage AC|1.4K to 325K|
|**Silicon Diode**|10µA DC|1.4 to 475K|
|**Platinum RTD**|1mA DC|14 to 1200K|
|**GaAlAs Diode**|10µA DC|25K to 325K|
|**Thermocouple**|None|Option,>1.4K|

51 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

**_Sensor Selection_** _:_ Front Panel or remote interface. There are no internal jumpers or switches. 

**_Sensor Resolution_** _:_ Sensor Dependent. See Sensor Performance Data table. 

**_Sensor Excitation_** _:_ Constant current mode: 1mA, 100 µ A or 10 µ A. Constant voltage mode: 10mV, 3.333mV and 1.0mV RMS. Excitation Current: 1.0mA to 10nA in steps of 5% of power. 

**_Resistance Measurement type:_** Ratiometric bridge. 

**_Resistance Range:_** Constant-voltage, Maximum resistance:  10mV = 1M Ω , 3.3mV  = 430K Ω , 1.0mV = 100K Ω . 

**_AC Excitation Frequency:_** Resistor sensors in constant-voltage mode: 1.25Hz bipolar square wave. 

**_Sample Rate_** _:_ 10Hz per channel in all measurement modes. 

**_Measurement Resolution_** _:_ Sensor Dependent. See Sensor Performance Data table. 

**_Digital Resolution_** _:_ 24 bits. 

**_Measurement Drift_** _:_ <15ppm/<sup>o</sup> C. 

**_Measurement Filter:_** 0.5, 1, 2, 4, 8, 16, 32 and 64 Seconds. 

**_Calibration Curves_** _:_ Built-in curves for industry standard sensors plus four user curves with up to 200 entries each. Interpolation is performed using a Cubic Spline. 

**_CalGen_**<sup></sup> **_:_** Calibration curve generator fits any diode, thermocouple or resistor sensor curve at 1, 2 or 3 user specified temperature points. 

**_Thermocouples:_** Factory installed option on one channel only. 

**Input Connector:** Universal mini-spade type thermocouple connector with screw terminals for direct connection to thermocouple wires. **Input Range:** ±80mV, Resolution: 0.4µV. **Electronic Accuracy:** ±1.0µ V  ± 0.05%. **Installed Types:** K, E, T and Chromel-AuFe (0.07%) plus four user supplied curves. **Cold Junction Compensation:** Internal, enable/disable. 

52 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### **Control Outputs** 

**_Number of Loops:_** Two. 

**_Control Input:_** Either sensor input. **_Loop Update Rate:_** 10Hz per loop. 

**_Control Type:_** PID table, Enhanced PID, Ramp or Manual. 

**_Autotune:_** Minimum bandwidth PID loop design. 

**_PID Tables:_** Two user PID tables available for storage of Setpoint vs. PID and heater range. Up to 16 entries/table. 

**_Setpoint Accuracy:_** Six+ significant digits. 

**_Fault Monitors:_** Control loops are disconnected upon detection of a control sensor fault or excessive internal temperature. 

**_Over Temperature Disconnect:_** Heater may be relay disconnected from user equipment when a specified temperature is exceeded on any selected input. 

#### **Loop #1 Primary Heater Output** 

**_Type_** _:_ Short circuit protected linear current source. Maximum compliance is 50V. **_Connection:_** Dual Banana Plug. 

**_Ranges_** _:_ Three output ranges of 1.0A, 0.33A and 0.10A full-scale, which correspond to 50W, 5.0W and 0.5W when used with a 50 Ω load. 

**_Load Resistance_** _:_ 25 Ω or 50 Ω . Heaters down to 10 Ω can be used with the 25 Ω range. 

**_Minimum Load:_** 10 Ω in 25 Ω setting, 40 Ω in 50 Ω setting. 

**_Digital Resolution_** _:_ 1.0PPM of full-scale, corresponding to 20 bits. 

**_Readback_** _:_ Heater output power, Heatsink temperature. 

#### **Loop #2 Output, Standard Model 32** 

**_Type_** _:_ Voltage output, 0 to 10  Volts. Input impedance: 500 Ω . 

**_Connection:_** Two-pin, 3.5mm detachable terminal block. 

**_Digital Resolution_** _:_ 1.0PPM of full-scale, corresponding to 20 bits. 

#### **Loop #2 Heater Output, Model 32B** 

**_Type_** _:_ 10 Watt, short circuit protected linear current source. Maximum output is 0.4A at 25V. 

**_Load Resistance_** _:_ 62.5 Ω (10Watts), 50 Ω (8Watts), 25 Ω (4 Watts) or 10 Ω (1.6 Watts). 

**_Digital Resolution_** _:_ 1.0PPM of full-scale, corresponding to 20 bits. 

**_Readback_** _:_ Heater output power. 

53 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### **Status Outputs** 

**_Audible and Visual Alarms_** _:_ Independent audible and visual alarms. 

**_Status reported via Remote Interface_** _:_ Sensor fault, Heater over temperature fault. 

#### **Remote Interfaces** 

Remote interfaces are electrically isolated to prevent ground loops. 

**_RS-232:_** Serial port is an RS-232 standard null modem. Rates are 300, 1200, 4800, 9600, 19,200 and 38,400 Baud. 

**_IEEE-488 (GPIB):_** Full IEEE-488.2 compliant. 

**_Language:_** Remote interface language is IEEE SCPI compliant. National Instruments LabVIEW  drivers available for all interfaces. 

#### **User Setups** 

Two User Setups are available that save and restore the complete configuration of the instrument. 

#### **Firmware** 

Internal firmware and all data tables are maintained in FLASH type memory and may be upgraded via the remote interface ports. Instrument firmware updates are available on the Internet. 

#### **General** 

**_Ambient Temperature_** _:_ 25<sup>°o</sup> C ± 5<sup>o</sup> C for specified accuracy. 

**_Mechanical_** _:_ 8.5”W x 3.5”H x 12”D. One half-width 2U rack. Instrument bail standard, rack mount kit optional. 

**_Weight_** _:_ 9 Lbs. 

**_Enclosure:_** Aluminum Extrusion. Machined Aluminum front and rear panels. 

**_Power Requirement_** _:_ 100, 120, 220 or 240VAC +5% -10%. 50 or 60Hz, 150VA max. 

54 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

### Input Channels 

There are two independent, multi-purpose input channels; each of which can separately be configured for use with any supported sensor. 

The Sensor Type is selected by the user via the microprocessor. Values of excitation current, voltage gain etc. will be determined by the microprocessor and used to automatically configure the channel. There are no internal jumpers or switches. 

#### Constant-Current Sensor Excitation 

Cryogenic sensors including Diode and Platinum devices require a constant-current excitation. To support this, the Model 32 has a constant-current excitation mode with three selectable outputs of 10 µ A, 100 µ A and 1.0mA DC. 

The maximum compliance of the constant-current source is 2.45V. 

Temperature is measured with diode type sensors by providing a 10 µ A excitation current and reading the resulting voltage. 

The Model 32 uses a Ratiometric bridge technique to measure resistor sensors. Here, the measurement is the ratio between the sensor resistance and an internal calibration standard resistance. This effectively cancels the DC drift and electronic noise associated with the internal voltage reference and constant-current source circuitry. 

Resistor sensors may use any of the three constant-current settings. 

#### Constant-Voltage Sensor Excitation 

A unique feature of the Model 32 is the constant-voltage excitation mode where current applied to the sensor is autoranged in order to maintain a constant RMS voltage level across the sensor. 

A constant-voltage excitation is necessary since the resistance thermometers used below about 10K exhibit a negative temperature coefficient. Therefore, a constantvoltage measurement will reduce the power dissipation in the sensor as temperature decreases. By maintaining a low power levels, sensor self-heating errors that occur at very low temperatures are minimized. 

In the constant-voltage mode, sensor excitation is a 1.25Hz bipolar square-wave. This provides DC offset cancellation without loss of signal energy. 

55 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

Available voltage selections are 10.0mV, 3.33mV and 1.0mV RMS. The maximum and minimum sensor resistance that can be read is a function of the selected voltage bias. Power dissipation in the sensor is computed by: 

|selections are 10.0mV,<br>mV RMS. The maximum|**Re**<br>|**sistance Rang**<br>|**e Table**<br>|
|---|---|---|---|
|nsor resistance that can<br>tion of the selected|**Voltage**<br>**Bias**|**Min.**<br>**Resistance**|**Max.**<br>**Resistance**|
||**10.0mV**|10Ω|1.0MΩ|
|n in the sensor is|**3.33mV**|4Ω|250KΩ|
|2|**1.0mV**|1Ω|100KΩ|
|_sensor_<br>_bias_<br>_d_<br>_R_<br>_V_<br>_P_<br><br>=|**Table**|**17: Voltage Bias S**|**elections**|

Excitation current sources used with constant-voltage bias are calibrated from 1.0mA to 0.1uA so that the accuracy of resistance measurement will be ± 0.1%. Accuracy will steadily degrade at lower excitation currents down to the minimum available output current of 10nA where the accuracy of resistance measurement is about ± 0.7%. 

The tradeoff in measurement accuracy vs. minimum sensor excitation current is taken for two reasons: 

1. The sensitivity of NTC resistor sensors is extremely high in the low temperature end of their range. Therefore the reduced measurement accuracy does not degrade temperature measurement accuracy. 

2. The low current settings are required since sensor self-heating at low temperature is a very significant source of errors. 

In order to minimize large jumps in self-heating, the Model 32 uses current sources to cover the 1.0mA to 10nA in steps of 5% power. 

|**Resistance**|**Measurement Ac**|**curacy**|
|---|---|---|
|**Voltage Bias**|±**0.1%**|±**0.7%**|
|**10.0mV**|10Ω- 100KΩ|1.0MΩ|
|**3.33mV**|3.3Ω- 43KΩ|430KΩ|
|**1.0mV**|1Ω- 10KΩ|100KΩ|

**Table 18: NTC Resistor Measurement Accuracy** 

56 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Supported Sensor Types 

A complete list of the sensor types supported by the Model 32 is shown below: 

|**Sensor Type**|**Max. Voltage/**<br>**Resistance**|**Bias**<br>**Type**|**Excitation**<br>**Current**|**Typical Use**|
|---|---|---|---|---|
|**Diode**|2.5V|CI|10µA|Silicon Diode,GaAs Diode.|
|**ACR**|1Ωto 1MΩ|CV|1.0mA to<br>10nA|NTC resistors including Ruthenium<br>Oxide,Cernox|
|**R250K10UA**|250KΩ|CI|10µA|NTC resistors including Ruthenium<br>Oxide,Cernox.|
|**R125K10UA**|125KΩ|CI|10µA|NTC resistors including Ruthenium<br>Oxide,Cernox.|
|**R62K10UA**|62KΩ|CI|10µA|NTC resistors including Ruthenium<br>Oxide,Cernox.|
|**R16K10UA**|16KΩ|CI|10µA|PTC/NTC Resistors.|
|**R8K10UA**|8KΩ|CI|10µA|PTC/NTC Resistors.|
|**R6K100UA**|6KΩ|CI|100µA|Platinum 1000|
|**R2K100UA**|2KΩ|CI|100µA|Platinum 1000|
|**R625R1MA**|625Ω|CI|1.0mA|Pt 100 > 800K.|
|**R312R1MA**|312Ω|CI|1.0mA|Pt 100 < 800K.|
|**R125R1MA**|125Ω|CI|1.0mA|Rhodium-Iron|
|**TC80**|78mV|--|0|80mV thermocouple|
|**TC40**|39mV|--|0|40mV thermocouple|
|**Snone**|0|--|0|Disable Input Channel|

**Table 19: Supported Sensor Configurations** 

Bias types are: 

**CI** – Constant Current sensor excitation. 

**CV** – Constant Voltage sensor excitation. Voltages of 10.0mV, 3.3mV and 1.0mV RMS may be selected. Excitation current autoranges from 1.0mA to 10nA in order to maintain the selected voltage. 

#### <u>Silicon Diode Sensors</u> 

Silicon Diode sensors (2-volt diodes) are configured with a 10 µ A current source excitation and a 2.5 Volt unipolar input voltage range. 

<u>Gallium-Arsenide Diode Sensors</u> 

Gallium-Arsenide Diodes, or 6-Volt Diodes, can be used down to a minimum temperature of about 25K. This limitation is imposed by the fact that the controller’s maximum input voltage is 2.25 Volts. 

Gallium-Arsenide sensors do not fit standard calibration curves, therefore, the user must provide a sensor-specific curve before using this type sensor. 

To use diodes, Gallium-Arsenide select the Diode input sensor type. 

57 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### <u>PTC Resistor Sensor (RTDs)</u> 

The Model 32 supports all types of Positive-Temperature-Coefficient (PTC) resistive sensors. Various combinations of excitation current and full-scale input voltage allow the user to trade off accuracy vs. sensor self heating. 

The Supported Sensor Configurations table above gives a complete list of combinations that can be selected. 

Standard calibration curves are provided for DIN43760 and IEC751 Platinum sensors. While these curves are based on a 100 Ω sensor, they may easily be extended to other resistance values by using the Multiplier field of the sensor setup. 

A table of recommended setups for various types of PTC resistor sensors is shown here: 

|**Type**|**Sensor Type**|**Sensor Excitation**|**TC**|**Calibration**<br>**Units**|
|---|---|---|---|---|
|**Platinum, 100**Ω|R625R1MA|1.0mA, AC/DC|(+)|Ohms|
|**Platinum, 1000**Ω|R6K100UA|100µA,AC/DC|(+)|Ohms|
|**Platinum, 10K**Ω**, < 425K**|R16K10UA|10µA,AC/DC|(+)|Ohms|
|**Rhodium-Iron**|R125R1MA|1.0mA, AC/DC|(+)|Ohms|

**Table 20:  PTC Resistor Sensor Configuration** 

#### <u>NTC Resistor Sensor Devices</u> 

The Model 32 also supports almost all types of Negative-Temperature-Coefficient (NTC) resistive sensors. Using AC, constant-voltage excitation, these sensors can be used down to extremely low temperatures. 

Examples of NTC resistor sensors include: Ruthenium Oxide, Cernox  , Carbon Glass  , Germanium and Thermistors. 

Calibration tables may be entered either directly in Ohms or in (base 10) Log of Ohms. 

A table of recommended setups for various types of NTC resistors sensors is shown here: 

|**Type**|**Sensor Type**|**Sensor Excitation**|**TC**|**Calibration**<br>**Units**|
|---|---|---|---|---|
|**Carbon Glass**|ACR|1.0 to 10.0mV AC|(-)|LogOhm|
|**Germanium**|ACR|1.0 to 10.0mV AC|(-)|LogOhm|
|**Cernox**|ACR|1.0 to 10.0mV AC|(-)|LogOhm|
|**Ruthenium Oxide**|ACR|1.0 to 10.0mV AC|(-)|LogOhm|
|**Thermistors**|ACR|1.0 to 10.0mV AC|(-)|LogOhm|

**Table 21:  NTC Resistor Sensor Configuration** 

58 

Model 32 / 32B User's Manual Specifications, Features and Functions 

#### <u>Thermocouple Sensors</u> 

The Model 32 can be ordered with optional thermocouple support. 

Thermocouple inputs on the Model 32 feature: 

- Universal thermocouple input supports all types including user-supplied. 

- High accuracy built-in Cold Junction compensation. 

- Open sensor detection. 

For more information on using thermocouples, please refer to the sections Thermocouple Sensor Connections and  Using Thermocouple Sensors. 

59 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Sensor Performance Summary 

|**Sensor Type**|**Silico**|**n Diode**|**100**Ω <br>**DIN**|**Platinum**<br>**43760**|**1000**Ω<br>**DIN**|**Platinum**<br>**43760**|**10K**Ω**P**<br>**DIN4**|**latinum**<br>**3760**|
|---|---|---|---|---|---|---|---|---|
|**Input**<br>**Configuration**|2.5V, 1|0µA|625Ω,|1.0mA|3125Ω|, 100µA|16KΩ, 1|0µA|
|**Sensor Sensitivity**|300K:<br>77K:<br>4.2K|2.4mV/K<br>1.9mV/K<br>30mV/K|800K:<br>300K:<br>77K:<br>30K:|0.36Ω/K<br>0.39Ω/K<br>0.42Ω/K<br>0.19Ω/K|600K:<br>300K: <br>77K:<br>30K:|3.7Ω/K<br> 3.9Ω/K<br>4.2Ω/K<br>1.9Ω/K|300K:<br>77K:<br>30K:|39Ω/K<br>42Ω/K<br>19Ω/K|
|**Measurement**<br>**Accuracy**|300K:<br>77K:<br>4.2K:|21µV<br>23µV<br>44µV|800K:<br>300K:<br>77K:<br>30K:|2.4mΩ<br>2.4mΩ<br>1.2mΩ<br>1.2mΩ|600K:<br>300K: <br>77K:<br>30K:|38mΩ<br> 38mΩ<br>4.7mΩ<br>4.7mΩ|300K:<br>77K:<br>30K:|380mΩ<br>50mΩ<br>50mΩ|
|**Temperature**<br>**Measurement**<br>**Accuracy**|300K:<br>77K:<br>4.2K:|8.7mK<br>12mK<br>1.6mK|800K:<br>300K:<br>77K:<br>30K:|6.7mK<br>6.2mK<br>2.8mK<br>9.8mK|600K: <br>300K: <br>77K:<br>30K:|6.2mK<br> 6.2mK<br>2.8mK<br>9.8mK|300K:<br>77K:<br>30K:|6.2mK<br>2.8mK<br>9.8mK|
|**Measurement**<br>**Resolution**|300K:<br>77K:<br>4.2K:|7.4µV<br>7.4µV<br>15µV|800K:<br>300K:<br>77K:<br>30K:|1.8mΩ<br>1.8mΩ<br>460µΩ<br>460µΩ|600K: <br>300K: <br>77K:<br>30K:|15mΩ<br> 15mΩ<br>1.8mΩ<br>1.8mΩ|300K:<br>77K:<br>30K:|150mΩ<br>18mΩ<br>1.8mΩ|
|**Temperature**<br>**Resolution**|300K:<br>77K:<br>4.2K:|3.0mK<br>3.8mK<br>500µK|800K:<br>300K:<br>77K:<br>30K:|5.1mK<br>4.7mK<br>1.1mK<br>2.4mK|600K: <br>300K: <br>77K:<br>30K:|4mK<br> 4mK<br>0.5mK<br>1.0mK|300K:<br>77K:<br>30K:|4mK<br>0.5mK<br>1.0mK|
|**Control Stability**|300K:<br>77K:<br>4.2K:|3.0mK<br>3.8mK<br>500µK|800K:<br>300K:<br>77K:<br>30K:|5.1mK<br>4.7mK<br>1.1mK<br>2.4mK|600K: <br>300K: <br>77K:<br>30K:|4mK<br> 4mK<br>0.5mK<br>1.0mK|300K:<br>77K:<br>30K:|4mK<br>0.5mK<br>1.0mK|
|**Power Dissipation**|4.2K:<br>77K:|17µW<br>12µW|30K:<br>77K:|3.7µW<br>20µW|30K:<br>77K:|370nW<br>2.0µW|30K:<br>77K:|37nW<br>200nW|
|**Magneto-**<br>**resistance**|Very|Large|Mo|derate|Mo|derate|Mod|erate|

**Table 22: Sensor Performance for Diodes and Pt Sensors.** 

60 

Specifications, Features and Functions 

Model 32 / 32B User's Manual 

|**Sensor Type**|**Ruthenium**<br>**Oxide**<sup>**2**</sup>|**Carbon**|**Glass**<sup>**2**</sup>|**Cer**|**nox**<sup>**2**</sup>|
|---|---|---|---|---|---|
|**Example Sensor**|**RX102A**|**CGR**|**-1-500**|**CX**|**-1050**|
|**Sensor Sensitivity**|1.0K: 1260Ω/K<br>4.2K: 80.3Ω/K<br>20K: 3.96Ω/K|1.4K:<br><br>4.2K:<br>77K:<br>300K:|520KΩ/K<br>422Ω/K<br>0.1Ω/K<br>0.01Ω/K|1.4K:<br>4.2K:<br>77K:<br>300K:|240KΩ/K<br>2290Ω/K<br>2.15Ω/K<br>0.16Ω/K|
|**Measurement**<br>**Accuracy**|1.0K: 1.9Ω<br>4.2K: 1.4Ω<br>20K: 1.09Ω|1.4K:<br>4.2K:<br>77K:<br>300K:|728Ω<br>0.58Ω<br>14mΩ<br>0.02Ω|1.4K:<br>4.2K:<br>77K:<br>300K:|675Ω<br><br>5.1Ω<br>161mΩ<br> 40mΩ|
|**Temperature**<br>**Measurement**<br>**Accuracy**|1.0K: 1.9mK<br>4.2K: 17mK<br>20K: 275mK|1.4K:<br>4.2K:<br>77K:<br>300K|1.4mK<br>1.4mK<br>150mK<br>: 2.1K|1.4K:<br>4.2K:<br>77K:<br>300K:|2.2mK<br>2.2mK<br>75mK<br> 295mK|
|**Measurement**<br>**Resolution**|2.0K: 11mΩ<br>4.2K: 11mΩ<br>20K: 11mΩ|4.2K:<br>77K:<br>300K:|11mΩ<br>0.2mΩ<br> 0.2mΩ|4.2K:<br>77K:<br>300K:|46mΩ<br>1.8mΩ<br> 0.5mΩ|
|**Temperature**<br>**Resolution**|2.0K: 32µK<br>4.2K: 0.13mK<br>20K: 2.9mK|4.2K:<br>77K:<br>300K:|30µK<br>1.2mK<br> 12mK|4.2K:<br>77K:<br>300K:|50µK<br>0.85mK<br> 3.5mK|
|**Control Stability**|2.0K: 0.15mK<br>4.2K: 0.15mK<br>20K: 2.9mK|4.2K:<br>77K:<br>300K:|0.15mK<br>35mK<br> 250mK|4.2K:<br>77K:<br>300K:|0.15mK<br>0.15mK<br> 35mK|
|**Power Dissipation**|1.0K: 42nW<br>4.2K: 73nW|1.4K:<br>4.2K:|962pW<br>171nW|1.4K:<br>4.2K:|1.1nW<br>20nW|
|**Magneto-**<br>**resistance**|<2% for H<2T|Mod|erate|<1% f|or H<2T|
||210mV Const|ant-Voltag|e bias|||

**Table 23: Sensor Performance for NTC sensors.** 

61 

Model 32 / 32B User's Manual Specifications, Features and Functions 

|**Sensor Type**|**Ty**|**pe K**<sup>1</sup>|**Typ**|**e E**<sup>1</sup>|**Ty**|**pe T**<sup>1</sup>|**C-Au**|**Fe .07%**<sup>1</sup>|
|---|---|---|---|---|---|---|---|---|
|**Input Range**|80|mV|80|mV|4|0mV|4|0mV|
|**Sensor**<br>**Sensitivity**|300K:<br>1500K:|41µV/K<br> 36µV/K|300K:<br>1200K:|61µV/K<br>76µV/K|300K: <br>600K:|41µV/K<br> 60µV/K|300K: <br>600K:|22.4µV/K<br> 23.4µV/K|
|**Measurement**<br>**Accuracy**|300K:<br>1500K:|0.6µV<br> 6.7µV|300K:<br>1200K:|0.6µV<br>9.0µV|300K:<br>600K:|0.5µV<br>4.0µV|300K:<br>600K:|0.5µV<br>2.0µV|
|**Temperature**<br>**Measurement**<br>**Accuracy**|300K:<br>1500K:|15mK<br> 190mK|300K:<br>1200K:|11mK<br>122mK|300K:<br>600K:|12mK<br>75mK|300K:<br>600K:|17mK<br>90mK|
|**Measurement**<br>**Resolution**|300K:<br>1500K:|0.5µV<br> 0.5µV|300K:<br>1200K:|0.5µV<br>0.5µV|300K:<br>600K:|0.4µV<br>0.4µV|300K:<br>600K:|0.4µV<br>0.4µV|
|**Temperature**<br>**Resolution**|300K:<br>1500K:|11mK<br> 13mK|300K:<br>1200K:|11mK<br>13mK|300K:<br>600K:|12mK<br>73mK|300K:<br>600K:|12mK<br>73mK|
|**Control Stability**|300K:<br>1500K:|110mK<br> 100mK|300K:<br>1200K:|56mK<br>55mK|300K:<br>600K:|60mK<br>56mK|300K:<br>600K:|66mK<br>65mK|
|**Magneto-**<br>**resistance**|Very|Large|Very|Large|Ver|y Large|Ver|y Large|
|1Includes error from|internal c|old junctio|n compens|ation|||||

**Table 24: Sensor Performance for Thermocouple Sensors** 

62 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Factory Installed Sensors 

For a listing of factory installed sensors, refer to Appendix A. 

#### CalGen Calibration Curve Generator 

The CalGen  feature is used to generate new calibration curves for Silicon Diode, Thermocouple or Platinum sensors. This provides a method for obtaining higher accuracy temperature measurements without expensive sensor calibrations. 

Curves can be generated from any user-selected curve and are written to a specified internal user calibration curve area. 

The CalGen  function may be performed in the instrument by using the front panel. Alternatively, the feature is also implemented in the Model 32 utilities software. 

#### Input Channel Statistics 

Input temperature statistics are continuously maintained on each input channel. This data may be viewed in real time on the Input Channel menu, or accessed via any of the remote I/O ports. 

Statistics are: Minimum Temperature. Maximum Temperature. Temperature Variance. Slope and Offset of the best-fit straight line to temperature history. Accumulation Time 

The temperature history may be cleared using a reset command provided. 

#### Electrical Isolation and Input Protection 

The input channel measurement circuitry is electrically isolated from other internal circuits. However, the common mode voltage between an input sensor connection and the instrument's ground should not exceed ± 40V. 

Sensor inputs and outputs are provided with protection circuits. The differential voltage between sensor inputs should not exceed ± 15V. 

#### Thermal EMF and AC Bias Issues 

DC offsets can build up in cryogenic temperature measurement systems due to Thermocouple effects within the sensor wiring. Careful wiring can minimize these effects. However, in a few systems, measurement errors induced by thermal EMFs can result in unacceptable measurement errors. These cases will require the use of an AC bias, or chopped sensor excitation, in order to remove DC offsets. 

#### <u>Sensor Wiring</u> 

Diode and Platinum RTD type sensors use a DC measurement scheme. Therefore, the only effective method of minimizing Thermocouple (DC) offsets is to wire temperature sensors so that connections between dissimilar metals are grouped together. For example, the connection between sensor leads and cryostat wiring should be kept close together. This way, the Thermocouple junctions formed by the connection will have equal-but-opposite voltages and will cancel each other. 

63 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

Frequently, sensor leads are made from the same material as the cryostat wires. Therefore, there is no significant Thermocouple formed by this connection. 

In a four-wire measurement scheme, only connections in the voltage sense lines can cause measurement errors. So, the sense wires should have adjacent contacts in a multi-pin connector in order to minimize any temperature difference between them. 

Usually, the ‘connection to copper’ in a cryostat is made at the top of the cryostat. After this point, Thermal EMFs cannot be generated. 

#### <u>AC Excitation</u> 

When a sensor type of ACR, or AC Resistance, is selected, the Model 32 uses a 1.25Hz square-wave sensor excitation. This eliminates DC offsets by computing the sensor resistance at two different excitation points. This method will not work diode sensors. 

### Control Outputs 

#### Control Loop #1, Primary Heater Output 

The Loop #1 heater output is a short circuit protected linear current source. This output is heavily regulated and RFI filtered. External filters should not be necessary. 

Automatic shutdown circuitry is provided that will protect the heater output stage from excessive temperature. Here, the heater output will be turned off until the output stage returns to its Safe Operating Area (SOA), then the output will be returned to normal operation. 

Load resistance values of either 25 Ω or 50 Ω may be selected. Using a 25 Ω load, the heater will be automatically configured to have a compliance voltage of 25V. With a 50 Ω load, the compliance voltage is 50V. In either case, the maximum output current is 1.0A. 

There are three output ranges, which are manually selected in PID mode and automatically selected in the PID Table control mode. The ranges are High, Medium and Low. 

|**Range**|**Compliance**<br>**25**Ω|**Voltage**<br>**50**Ω|**Full-Scale**<br>**Current**|**Max. Output Po**<br>**25**Ω|**wer**<br>**50**Ω|
|---|---|---|---|---|---|
|**High**|25|50|1.0A|25 Watts|50 Watts|
|**Medium**|25|50|0.333A|2.5 Watts|5.0 Watts|
|**Low**|25|50|0.100A|0.25 Watts|0.50 Watts|

**Table 25: Loop 1 Heater output ranges.** 

Care must be taken to ensure that the proper load resistance is selected. Connection to a 25 Ω load while a 50 Ω is selected will result in overheating and eventual automatic heater shutdown. Conversely, connection to a 50 Ω load while setting a 25 Ω load will result in only one half of the indicated heater power being dissipated in the load. 

Load resistance and Full Scale Output Range are selected via the front panel, or any of the remote interfaces. 

64 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

Heater output power displays are based on the heater read-back circuitry which measures output current independently of the actual heater circuitry. Thus, heater fault conditions can be detected and their corresponding alarms asserted. 

The temperature of the internal heater heat sink is continuously monitored used to generate over temperature fault conditions that will result in shut down of the control loop. 

The absolute resolution of output heater current is 0.0015% of full scale (Sixteen bits). However, this resolution is significantly extended through the use of a dither signal that is applied to the Digital-to-Analog Converter and averaged by analog filtering in the output stage. The resulting output is an interpolation between the available quantization levels. See Appendix C: Application Note on Signal Dither for details. 

 **Note:** Heater output displays are given as a percentage of output power, not output current. In order to compute actual output power, multiply this percentage by the full-scale power of the selected range. However, to compute actual output current, you must first take the square root of the percentage and then multiply by the full-scale current. 

Connection to the heater output is made on the rear panel using the banana-plug block provided. 

**Caution:** The Model 32 has an automatic control-on-power-up feature. If enabled, the controller will automatically begin controlling temperature whenever AC power is applied. For a complete description of this function, please see the SYS-Auto Ctl function in the **System Functions menu** section. 

#### Control Loop #2, Secondary Heater Output 

For a standard Model 32, control loop 2 is a voltage output with a 600 Ω output impedance. Range is zero to 10.0 Volts. 

In the Model 32B, control loop 2 is a constant current source similar to the Loop 1 heater. It has a single output range of zero to 450mA and a compliance of 25V. This will result in an output power of 10 Watts into a 50 Ω load. 

The absolute resolution of Loop 2 is 0.0015% of full scale (Sixteen bits). However, this extended through the use of a dither signal. See Appendix C: Application Note on Signal Dither for details. 

Connection to the Analog Output is made on the rear panel using the pluggable terminal block provided. 

65 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Control Types 

There are four control types available in the Model 32. They are Manual, PID, PID Table and Ramp. All modes are available on both control loops. 

Manual mode operation allows setting the output power manually as a percentage of full-scale power. 

PID control allows feedback control using an enhanced PID algorithm that is implemented using 32-bit floating point Digital Signal Processing techniques. Enhancements include: 

1. Implementation of a user settable damping factor that can be used to minimize overshoot to a new setpoint without affecting the PID loop operation. 

2. Noise filtering on the derivative term. The D term will provide better control stability, but is often not used because, without filtering, it can make the control loop too sensitive to noise. 

3. Integrator wind up compensation. While slewing to a new setpoint, the integrator in the PID loop can build up to a very large value. If no compensation is applied, overshoot and time to stability at the new setpoint can be delayed for an extremely long time. This is especially true in cryogenic environments where process time constants can be very long. 

4. Dithering and filtering the outputs in order to increase output resolution and improve control stability. 

The PID Table control mode is a PID control loop just as described above. However, it is used to look up P,I,D and heater range values based on the specified setpoint. This is useful where a process must operate over a wide range temperature range since optimum PID values usually change with temperature. 

To use the Table mode effectively, the user must first characterize the cryogenic process over the range of temperature that will be used, then generate PID and heater range values for various temperature zones. This is usually done using the autotune capability. Once the information is placed into a PID Table, the Model 32 will control in Table mode by interpolating optimum PID values based on setpoint. 

The Model 32 allows for the entry of four independent PID Tables. Each table may contain up to 16 temperature zones. 

In the Ramp control mode, the controller will approach a new setpoint at a user specified rate. When this setpoint is reached, the controller will revert to PID control. 

66 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Alarm Outputs 

Alarm outputs include a LED indicator, an audible alarm, on-screen display and remote reporting. 

Alarms may be asserted based on high temperature, low temperature, input sensor fault or heater fault conditions. 

There is a 0.25K hysteresis built into the high and low temperature alarms. 

### Remote Interfaces 

IEEE-488.2 and RS-232 interfaces are standard. All functions and read-outs available from the instrument may be completely controlled by any of these interfaces. 

The Serial port is an RS-232 standard null modem with male DB9 connector. Rates are 300, 1200, 4800, 9600, 19,200 and 38,400 Baud. 

The GPIB is fully IEEE-488.2 compliant. Connection is made at the rear panel using the IEEE-488 standard connector. 

The programming language used by the Model 32 is identical for all interfaces and is SCPI language compliant. The Standard Command Protocol for programmable Instruments (SCPI) is a sub section of the IEEE-488.2 standard and is a tree structured ASCII command language that is commonly used to program laboratory instruments. 

67 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

### Rear Panel Connections 

The rear panel of the Model 32 is shown here: 

**Figure 3:  Model 32 Rear Panel Layout** 

#### AC Power Connection 

The Model 32 requires single-phase AC power of 50 to 60 Hz. 

**Caution** : _Protective Ground:_ To minimize shock hazard, the instrument is equipped with a three-conductor AC power cable. Plug the power cable into an approved three-contact electrical outlet or use a three-contact adapter with the grounding wire (green) firmly connected to an electrical ground (safety ground) at the power outlet. 

The power jack and mating plug of the power cable meet Underwriters Laboratories (UL) and International Electrotechnical Commission (IEC) safety standards. 

User-replaceable fuses are incorporated in the Power Entry Module. 

68 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Fuse Replacement and Voltage Selection 

Access to the Model 32's fuses and voltage selector switch is made by using a screwdriver to open fuse drawer in the power entry module. A slot is provided above the voltage selector window for this purpose. 

The fuse and voltage selection drawer cannot be opened while the AC power cord is connected. 

Voltage selection is performed by rotating the selector cams until the desired voltage shows through the window shown. 

There are two fuses that may be removed by pulling out the fuse modules below the voltage selector. Fuses are specified according to the AC power line voltage used: 

|**Line Voltage**|**Fuse**|**Example**|
|---|---|---|
|**100VAC, 120VAC**|2.0A slow-blow|Littlefuse 313 002|
|**220VAC, 240VAC**|1.0A slow-blow|Littlefuse 313 001|

**Table 26. AC Power Line Fuses** 

69 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### Sensor Connections 

All sensor connections are made at the rear panel of the Model 32 using the two DIN5 receptacles provided. 

#### <u>Standard Four Wire Sensor Connections</u> 

Silicon Diode and all resistor type sensors should be connected to the Model 32 using the four-wire method. It is strongly recommended that sensors be connected using shielded, twisted pair wire. Wires are connected as shown below and the shield should be connected to the metal backshell of the connector. 

|**Pin**|**Function**|
|---|---|
|**1**|Excitation(-),I-|
|**2**|Sense(-),V-|
|**3**|Do not connect|
|**4**|Sense(+),V+|
|**5**|Excitation(+),I+|

**Table 27: Input Connector Pin-out** 

**Caution** : To ensure proper 

low noise operation, cable shields should be connected to the metal backshell of the connector.  A metal clip is provided with the connector for this purpose. Please refer to the section on shielding and grounding for further information. 

**Figure 4: Proper Assembly of the Input Connector** 

 **Note:** The input connectors on the Model 32 will mate with either DIN-5 or DIN-6 plugs. Wiring is identical. If a DIN-6 plug is used, Pin 6 is not connected. Do not connect to pin 3 of either connector. 

70 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

Recommended color codes for a sensor cable are as follows: 

|**Color Code**|**Signal**|**Pin**|
|---|---|---|
|**White**|Excitation(+)|5|
|**Green**|Excitation(-)|1|
|**Red**|Sense(+)|4|
|**Black**|Sense(-)|2|

**Table 28:  Dual Sensor Cable Color Codes** 

The cable used is Belden 8723. This is a dual twisted pair cable with individual shields and a drain wire. The shields and drain wire are connected to the DIN-5’s connector's metal backshell in order to complete the shielding connection. 

A four-wire connection is recommended in order to eliminate errors due to lead resistance. Cryogenic applications often use fine wires made from specialty metals that have low heat conduction. This results in high electrical resistance and, therefore, large measurement errors if the four-wire scheme is not used. 

Four-wire connection to Diode and Resistive type sensors is diagrammed below: 

**Figure 5: Diode and Resistor Sensor Connections** 

71 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

<u>Cryo-con S700 Silicon Diode Connections</u> The S700BB is a Silicon Diode temperature sensor. Connection is made using a color-coded four-wire, 36 AWG cryogenic ribbon cable. 

Wires may be separated by dipping in Isopropyl Alcohol and then wiping clean. 

Insulation is Formvar™ and is difficult to strip. Techniques include use of a mechanical stripper, scrapping and passing the wire over a low level flame. 

|**Ribbon**|**Cable**|**Color Codes**|
|---|---|---|
|**V+**||Clear|
|**V-**||Green|
|**I+**||Black|
|**I-**||Red|

#### <u>Thermocouple Sensor Connections</u> 

Thermocouple sensors require the factory installed thermocouple option. All thermocouple connections must be made at the sensor input connector since this connector is thermally anchored to an internal sensor that is used for Cold Junction compensation. 

Thermocouple sensors are connected to the Model 32 by use of the special connector provided with the controller. Sensor connection is made at the screw terminals. Proper polarity of the sensor wires is required. Polarity is marked on the input connector and a summary of common thermocouple polarities is given in the table below. The input connector should have its backshell and rubber grommet installed in order to prevent local air currents from generating errors in the cold junction circuitry. 

It is recommended that the Thermocouple sensor be electrically isolated, or floating, from any surrounding circuits or grounds. This will ensure the highest possible measurement accuracy. 

**Figure 6: Thermocouple Input Connector** 

72 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

Additional discussion on Thermocouple and grounding issues can be found below in the “Using Thermocouple Sensors” section below. 

|**Type**|**Color**|**(+) Terminal**|**(-)Terminal**|
|---|---|---|---|
|**E**|Purple|Chrome|Constantan|
|**K**|Yellow|Chrome|Aluminum|
|**T**|Blue|Copper|Constantan|
|**U**|White|Copper|Copper|

**Table 29: Thermocouple Types** 

#### Loop #1 Heater Connections 

Rear panel Primary Heater Output (Loop #1) connections are made using the two-pin banana plug shown here. Pin One of this block (HI) is the positive output and Pin Two (Lo) is the ground return. The shield of the output cable should be connected to the third (uninsulated) banana plug. 

#### Loop #2 Output Connections 

Rear panel connections to the Loop #2 output are made using the two-pin pluggable 0.200" terminal block shown above. Pin One of this block (left hand pin) is the positive (+) output and Pin Two is the return (-). The shield of the output cable may be connected to Pin Two. 

The two-pin heater terminal block plug is an Augat part number 2ESDV-02. It is available from Cryo-con as part number 04-0301. 

#### IEEE-488.2 Connections 

Rear panel connection to the IEEE-488.2 is performed using the GPIB connector. 

GPIB cables are available in various lengths. However, only shielded type assemblies should be used. Many of the molded GPIB cables are actually unshielded and can introduce excessive noise into your instrumentation environment. 

#### RS-232 Connections 

The Model 32 uses a Female DB-9 connector for RS-232 serial communications. The pin-out of this connector is as follows: 

<!-- Start of picture text -->
Pin Function<br>1 NC<br>2 RXD, Receive data<br>3 TXD, Transmit data<br>4 NC<br>5 Ground<br>6 NC<br>7 NC<br>8 NC<br>9 NC<br><!-- End of picture text -->

**Table 30:  RS-232 DB-9 Connector Pinout** 

73 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

The cable used to connect the Model 32 to a computer serial port is a Dual Female Null Modem cable. An example is Digikey Inc. part number AE1033-ND. 

The wiring diagram for this cable is shown below. Note that communication with the Model 32 only requires connection of pins 2, 3 and 5. All other connections are optional. 

**Figure 7: RS-232 Null Modem Cable** 

### Mechanical, Form Factors and Environmental 

#### Display 

The display is a two line by twenty-character dot matrix VFD. 

#### Enclosure 

The Model 32 enclosure is standard 2-U half-width 17-inch rack-mountable type that may be used either stand-alone or incorporated in an instrument rack. 

Dimensions are: 8.5"W x 3.5"H x 12"D. Weight is 9 Lbs. 

An instrument bail and feet are standard. Rack Mount kits are available from Cryocon for both single instrument or side-by-side dual configurations. A rack mount kit is optional. 

#### AC Power 

The Model 34 requires single-phase AC power of 50 to 60 Hz. Voltages are set by the line voltage selector in the Power Entry Module on the rear panel. 

Line voltage selections are: 100, 120, 220 or 240VAC. Tolerance on voltages is +10% to  -5% for specified accuracy and -10% for reduced full-scale heater output in the highest output range. 

Protective Ground: To minimize shock hazard, the instrument is equipped with a three-conductor AC power cable. Plug the power cable into an approved three-contact electrical outlet or use a three-contact adapter with the grounding wire (green) firmly connected to an electrical ground (safety ground) at the power outlet. 

74 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

The power jack and mating plug of the power cable meet Underwriters Laboratories (UL) and International Electrotechnical Commission (IEC) safety standards. 

Power requirement is 25 Watts plus the power being provided to the heater load. 

The power cord will be a standard detachable 3-prong type. 

User-replaceable fuses are incorporated in the Power Entry Module. See the section titled Fuse Replacement / Voltage Selection. 

 **Note:** The Model 32 uses a smart power on/off scheme. When the power button on the front panel is pressed to turn the unit off, the instrument's setup is copied to flash memory and restored on the next power up. If the front panel button is not used to toggle power to the instrument, the user should configure it and cycle power from the front panel button one time. This will ensure that the proper setup is restored when AC power is applied. 

#### Environmental and Safety Concerns. <u>Safety</u> 

The Model 32 protects the operator and surrounding area from electric shock or burn, mechanical hazards, excessive temperature, and spread of fire from the instrument. 

- Keep Away From Live Circuits: Operating personnel must not remove instrument covers. There are no internal user serviceable parts or adjustments. Refer instrument service to qualified maintenance personnel. Do not replace components with power cable connected. To avoid injuries, always disconnect power and discharge circuits before touching them. 

- Cleaning: Do not submerge instrument. Clean exterior only with a damp cloth and mild detergent only. 

- Grounding: To minimize shock hazard, the instrument is equipped with a three-conductor AC power cable. Plug the power cable into an approved three-contact electrical outlet only. 

75 

Model 32 / 32B User's Manual 

Specifications, Features and Functions 

#### <u>Safety Symbols</u> 

#### <u>Environmental Conditions</u> 

Environmental conditions outside of the conditions below may pose a hazard to the operator and surrounding area: 

- Indoor use only. 

- Altitude to 2000 meters. 

- Temperature for safe operation: 5 °C to 40 °C. 

- Maximum relative humidity: 80% for temperature up to 31 °C decreasing linearly to 50% at 40 °C. 

- Power supply voltage fluctuations not to exceed ±10% of the nominal voltage. 

- Over voltage category II. 

- Pollution degree 2. 

- Ventilation: The instrument has ventilation holes in its side covers. Do not block these holes when the instrument is operating. 

- Do not operate the instrument in the presence of flammable gases or fumes. Operation of any electrical instrument in such an environment is a definite safety hazard. 

76 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

## Basic Setup and Operating Procedures. 

### Configuring a sensor 

Before connecting a new sensor to the Model 32, the instrument should be configured to support it. Most common sensors are factory installed; others require a simple configuration sequence. 

A complete list of sensors installed at the factory is shown in Appendix A. To configure the instrument for one of these sensors, proceed as follows: 

1. To install the sensor on Input Channel A, press the **ChA** key. For Channel B, press the **ChB** key. This will take you to the Input Channel Setup menu for the selected channel. The first line of this display will show the current temperature in real-time and allow you to select the desired display units. Press the or keys to sequence through the available options and press the **Enter** key to make the selection. 

2. Press the key to go down to the Sen: filed. Here, you will use the or key to scroll through all of the sensor types available. When the desired sensor is displayed, press the **Enter** key to configure the instrument. 

Select **None** to disable the input channel. 

At the end of the factory-installed sensors, four user-installed selections will be shown. The default name for these is User Sensor N. However, this name can be changed to give a better indication of the sensor type that is connected. 

For most sensor types, installation is now complete and the Home key can be pressed to return to the Home Status display. The exceptions are NTC resistor sensors that use constant-voltage AC excitation. With these types of sensors, you will need to scroll down to the Bias Voltage field and select the desired constant-voltage excitation level. 

 **Note:** NTC resistor sensors require the selection of a Bias Voltage. Selections are 10mV, 3.3mV and 1.0mV. Generally, 10mV works well for most sensors down to about 1K. Below that, the lower settings may be used to minimize errors from sensor selfheating. However, use of a lower voltage limits the maximum resistance range and significantly increases measurement noise. 

Once sensor configuration is complete, review the section on Sensor Connections to connect the sensor to the instrument. 

### Adding a New Sensor Type 

This procedure identifies how to add a new sensor type to the controller. If the desired sensor is already installed as a factory installed sensor or previously installed user sensor, this procedure is not required. These sensors can be simply assigned to an 

77 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

input channel by using the Input Channel Setup Menu described above. 

Adding a new sensor to the Model 32 is a two-step process. First, the sensor type must be defined using the Sensor Setup Menu. Next, the sensor’s calibration curve must be entered by using the Calibration Curve Menu. 

Note that, if the new sensor has a lengthy calibration curve, entry from the front panel may be tedious. In these cases, the user may consider entering the sensor via the remote interfaces using the controller’s utility software. 

To add a sensor using one of the remote interfaces, please refer to the Remote I/O section command syntax etc. 

||Sensor Setup|
|---|---|
||**Sensor Setup Menu**|
|**1**||
|**2**||
|**3**||
|**4**||
|**5**||

**Table 31: Sensor Setup Menu** 

The new sensor type is defined using the Sensor Setup Menu. The first line of this menu includes the Sensor Index (18) and the name (User Sensor 3). This line may be scrolled through all of the available sensor types, including factory-installed sensors. Press **Enter** to select the displayed sensor. 

In order to install a new sensor, one of the four user sensors should be selected. 

Next, the Type of sensor must be defined. Choices include Silicon Diodes, various resistors and thermocouples. This selection will identify the excitation current and voltage input range that the controller must use to interface with the sensor. Selections are given in Table 2 above. 

The Multiplier field specifies a multiplier that is applied to the sensors calibration curve. The sign of this field indicates the temperature coefficient. This coefficient is only used when the user is attempting to control on sensor units, such as Ohms or Volts. 

Most commonly, the multiplier field contains a value of plus or minus 1.0. This causes the controller to apply the sensor calibration curve directly, without first scaling it. Further, a negative value will indicate that the sensor has a negative temperature coefficient and a positive value will indicate a positive coefficient. 

Diode sensors will generally have a Multiplier of –1.0 since their temperature coefficient is negative and no scale is applied to the calibration curve. 

78 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

100 Ω Platinum sensors will use a Multiplier of 1.0. However, if a 1000 Ω sensor is used with a calibration curve for 100 Ω sensors, a Multiplier of 10.0 should be used. 

‘Units’ is an enumeration field that identifies the basic units used by the sensor’s calibration curve. Choices are Volts, Ohms and LogOhm. LogOhm selects the base ten logarithm-of-ohms and is useful with sensors whose fundamental resistance vs. temperature curve is logarithmic. 

The LogOhm selection is only used with Negative-Temperature-Coefficient resistor sensors, where it acts to improve the accuracy of interpolation. 

The N field is the number of valid points in the calibration curve and is generated from the entries made during the editing process. 

Selecting the ‘EDIT CAL CURVE’ field will cause the screen to go to the Calibration Curve menu for the selected sensor. Here, the calibration curve may be entered or edited. 

#### Calibration Curve Entry 

Once a sensor type is defined, the calibration curve for that sensor may be entered. This may be done by using the Calibration Curves Menu described above, or, using any of the remote I/O ports, or using the Model 32 Utility Software package. 

One very efficient way to enter a new calibration curve is to use the instrument’s CalGen  feature to generate a new curve from an existing one. Operation of this feature is described below. 

79 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

### Autotuning 

#### The Autotune Process 

The Model 32 performs autotuning by applying a generated waveform to the heater output and analyzing the resulting changes in process temperature. This is used to develop a process model, then a PID solution. 

It is important to note that there is a range of PID combinations that will provide accurate control for a given process. Further, process modeling is a statistical method that is affected by noise and system non-linearity. 

As a result, multiple autotuning of the same process may yield different results. However, if the process model has not corrupted, any of the generated results will provide equally stable temperature control. 

For further explanation, the different PID solutions generated by autotuning will vary only in the resultant closed loop bandwidth. Low bandwidth solutions will be slower to respond to changes in setpoint or load disturbances. High bandwidth solutions will result be responsive but can exhibit overshoot and damped oscillation. 

The Model 32 attempts to generate minimum overshoot solutions since many cryogenic temperature control applications require this. If the process is noisy, bandwidth will be minimized as much as possible. If the process is very quiet, a more aggressive solution will be generated subject to the minimum overshoot requirement. 

The autotune algorithm will produce a heater output waveform in order to force the process model to converge. In general, a large amplitude waveform will provide the best possible signal-to-noise ratio, resulting in a faster and more accurate solution. 

However, it is important in some systems that the user constrains the amplitude and duration of the heater output waveform by using the DeltaP and Timeout parameters. 

Small values for DeltaP will force the use of small changes in heater power. This will make the process model more susceptible to corruption by noise. 

Large values of DeltaP will allow the use of large heater power swings, but this may also drive the process into non-linear operation, which will also corrupt the tuning result. Worse, it may allow application of too much heater power and may cause an over temperature condition. 

Experience indicates that most cryogenic systems will autotune properly using a DeltaP of 10% whereas a noisy system will require 20% or more. A common example of a noisy cryogenic system is one where a Silicon Diode sensor is used with a setpoint near room temperature. 

#### System Noise and Tuning Modes 

Three modes of autotuning may be selected. They are: P only, PI and PID. 

Using P only autotuning will result in the maximum value for P that will not cause oscillation. The process temperature will stabilize at some point near the setpoint. 

Using PI or PID control will result in stable control at the setpoint. 

80 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

The Derivative, or D, term in PID is used to make the controller more responsive to changes in setpoint or thermal load. It does not affect the control accuracy when the system has stabilized. However, derivative action, by it's nature, amplifies noise. Therefore, PID autotuning and control should only be used with very quiet systems. PI control should be used with all others. 

Sensor type has a significant impact on measurement noise. 

The Model 32 uses a ratiometric technique to measure resistor sensors such as Thermistors, Platinum RTDs, Carbon Glass  etc. This effectively cancels most of the measurement noise and allows effective use of PID control. 

Voltage mode sensors, which include diodes and thermocouples, cannot benefit from ratiometric measurement, Therefore, PI control is recommended. 

It is a very common mistake to attempt PID control using a Diode sensor above 70K. This is the least sensitive region of the sensor so measurement noise is very high. PI control is recommended. 

Below about 20K, the sensitivity of the Diode increases significantly and PID control may be used effectively. 

#### Pre-Tuning and System Stability. 

Before autotuning can be initiated by the controller, the system must be stable in terms of both temperature and heater output power. This requires the user to perform a basic pre-tuning operation before attempting the first autotune. 

The goal of pre-tuning is to stabilize the process at a temperature near the desired setpoint so that the tuning algorithm can use this as a baseline to model the process. 

Cryogenic systems will usually require different PID values at different setpoint temperatures. Therefore, the pre-tuning process should result in a temperature near the desired setpoint. 

Pre-tuning does NOT require that the user establish stable control at the target setpoint. This is the job of the autotuning algorithm and is much more difficult than the stability required by pre-tuning. 

One method of pre-tuning is to use PID control with a small initial value for P and zero for I and D. This will result in stability at a temperature of the setpoint minus some constant offset. Increasing the P value will reduce the offset amount. When P is too large, the system will oscillate. 

Another pre-tuning technique is to Manual control mode with some fixed value of output power. When the system becomes stable at a temperature corresponding to the set heater power level, a system characterization process is performed using that temperature as an initial setpoint. 

#### System Characterization. 

System characterization is the process of using autotune to generate optimal PID coefficients for each setpoint over a wide range of possible setpoints. 

81 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

The characterization process is performed once. Then, the setpoints and corresponding generated PID values are transferred to an internal PID table. Thereafter, the system is efficiently controlled by using the Table control mode. 

#### Autotune Setup and Execution 

The Autotune menu for either control loop is accessed by pressing the **Auto Tune** key from the Home Operate Screen. 

Upon entry, the autotune state variable will be set to Idle and the P, I and D fields on the bottom of the display will be blank. 

As described above, various setup conditions must be met before autotune can be performed: 

1. The Model 32 must be in Control mode. 

2. Both the output power and the process temperature must be stable. The user must stabilize the process before the autotune function can accurately model it. If the process is not stable, erroneous values of P, I and D will be generated. 

3. The input control channel units must be in temperature, not sensor units of Volts or Ohms. This is because PID control is a linear process and sensor output is generally non-linear. Note that the Model 32 can be manually tuned using sensor units but autotuning cannot be performed. 

82 

Model 32 / 32B User's Manual Basic Setup and Operating Procedures. 

||**Autotune**|**Menu**<br>|
|---|---|---|
|1||<br>Sets the loop number for autotuning.<br>Each control loop must be tuned<br>separately. Choices are Loop 1 and<br>Loop 2. The selected loop is displayed<br>in all following lines of this menu.|
|2||<br>Sets the maximum power delta allowed<br>during the tuning process. Value is a<br>percent of full-scale output power for<br>the selected loop.|
|3||<br>Sets autotuning mode. Choices are P,<br>PI or PID. PI is recommended for most<br>systems.|
|4||<br>Sets the autotune timeout in seconds. If<br>the process model has not converged<br>within this time, tuning is aborted.|
|5||Real-time display of the temperature on<br>the input channel being tuned.|
|6||<br>Pressing Enter will initiate the autotune<br>sequence.|
|7||Autotune status. Display only|
|8||Proportional gain term generated by<br>autotune. This field will be blank until a<br>successful autotune is completed.|
|9||Integral gain term generated by<br>autotune. This field will be blank until a<br>successful autotune is completed.|
|10||Derivative gain term generated by<br>autotune. This field will be blank until a<br>successful autotune is completed.|
|11||<br>Pressing**Enter**cause the controller to<br>transfer the generated PID coefficients<br>to the selected loop, initiate control with<br>the new parameters and exit to the<br>Home Operate Display.|

**Table 32: Autotune Menu** 

The Delta P field is in percent and is the maximum change in output power that the controller is allowed to apply during the modeling process. A value of 100% will allow use full-scale power increments. A value of 20% will use a maximum power increment of ± 20% of the current heater output. 

The Mode field tells autotune to generate coefficients for P only, PI only, or PID. Choices are: P--, PI- and PID. 

The Timeout field is in units of Seconds and indicates the maximum period of time that the process model will run before aborting. This value should be set to at least two or three times the estimated maximum time constant of the process. 

83 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

 **Note:** Depending on the setup configuration, the autotune algorithm may apply full-scale heater power to the process for an extended time. Therefore, care should be taken to ensure that autotune does not overheat user equipment. If overheating is a concern, the Over Temperature Disconnect Monitor should be configured to disconnect the heater and abort the autotune process when an input temperature exceeds the specified maximum. 

The autotune sequence is initiated by selecting the Go field. If the initialization of process modeling is successful, the status display line will change from idle to Running. If initialization is not successful, one of the above listed conditions has not been met. 

When the tuning process is successfully completed, a status of Complete will be indicated and the values of P, I and D will be updated with the generated values. To accept these values and save them as the loop PID coefficients, select the Save&Exit field. To reject the values and exit, press the **ESC** key. 

Autotune may always be aborted by pressing the **ESC** key. 

An unsuccessful autotune will be indicated by one of the following status lines: 

1. Failed. This indicates that the process model did not converge or that PID values could not be generated from the result. 

2. Aborted. Autotune was aborted by user intervention such as pressing the Stop key. 

84 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

### Temperature Ramping 

#### Operation 

The Model 32 will perform a temperature ramp function using a specified ramp rate and target setpoint. Once placed in a ramping control mode, a ramp is initiated by changing the setpoint. The unit will then progress to the new setpoint at the selected ramp rate. Upon reaching the new setpoint, ramp mode will be terminated and standard PID type regulation will be performed. 

Ramping may be independently performed on control loop. 

The procedure for temperature ramping is as follows: 

1. Set the Ramp Rate in the Heater Configuration Menu. This parameter specifies the ramp rate in Units Per Minute, where Units are the measurement units of the input channel controlling the heater. For example, if the input channel units are Kelvin, the ramp rate is in K/min. 

2. Select a ramping Control Mode. There are two types: 1) RampP, which will perform a ramp using the current PID parameters, and 2) RampT, which will ramp using PID parameters derived from a specified PID Table. The RampP mode will perform a ramp, and then perform temperature regulation using the standard PID mode. The RampT function will perform a ramp, then perform regulation using the PID Table control mode. 

3. Press CONTROL. Now, the controller will begin temperature regulation at the current setpoint. 

4. Enter a new setpoint. The controller will enter ramping mode, and ramp to the target setpoint at the specified rate. 

5. When the new setpoint is reached, ramping mode will terminate and temperature regulation will begin at the new setpoint. 

6. Entry of a different setpoint will initiate another ramp. 

As a variation on the above procedure: 

1. The controller may be regulating temperature in any available control mode. This mode can be changed to a ramping mode without exiting the control loop. This will not result in a ‘glitch’ in heater output power. 

2. Once a ramp mode is selected, ramping is performed, as above, by changing the setpoint. 

The current status of the ramp function may be seen on the Operate Screen. When a ramp is active, the word RMP will appear in the control loop status displays. It may also be queried via any of the remote ports using the LOOP 1:RAMP? Command. 

85 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

#### Ramping Algorithm 

The ramp algorithm uses a basic PID type control loop and continuously varies the setpoint until the specified temperature is reached. This means that the PID control loop will continuously track the moving setpoint. The result is that there will be small time lag between the target ramp and the actual temperature. 

Although not normally a problem, the ramp time lag may be minimized by using aggressive PID values. This is accomplished by increasing P, decreasing I and setting D to zero. 

#### Ramping Parameters and Setup 

The Ramp Rate is set on the Control Loop Setup menu. Note that the ramp rate on Loop 1 is independent of the rate on Loop 2. 

A ramping control mode must also be set. Ramping modes are RampP or RampT. These modes are also selected in the Control Loop Setup menu. 

#### Summary 

To perform a temperature ramp, proceed as follows: 

1. Set the control loop P, I and D parameters to allow stable control at both ends of the desired ramp. This is usually done by using ‘slow’ PID values (Low values for P, high for I and zero for D). 

2. Set the Ramp Rate in the Heater Configuration Menu. Set the setpoint to the starting value for the ramp. 

3. Press CONTROL. Now, the controller will begin temperature regulation at the current setpoint. 

4. Enter a new setpoint. The controller will enter ramping mode, and ramp to the target setpoint at the specified rate. The word RMP will appear in the control loop menu. 

5. When the new setpoint is reached, ramping mode will terminate and temperature regulation will begin at the new setpoint. 

86 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

### Cryocooler Signature Subtraction 

Cryocoolers often have a thermal signature that is associated with the mechanical cooling process. At the low end of their temperature range, this signature can have amplitudes of one or more Kelvin. 

Since the thermal signature is related to the mechanical cooling process, it is low frequency and has an irregular shape that is rich in harmonics. With most coolers, the frequency will be a sub-multiple of the AC line frequency around 2Hz and the shape will be a narrow spike followed by a long lull. 

If a conventional PID control loop is connected to a cryocooler, the thermal signature will disrupt the loop and degrade the accuracy of control. If a fast PID loop is used, it will attempt to track the signature, which usually results in placing a waveform on the loop output heater that causes control performance to degrade even further. 

In still other systems, the thermal signature of the cryocooler will be outside of the PID control loop bandwidth enough to cause a phase reversal that actually amplifies the signature causing the entire system to become unstable. These systems will oscillate with a sine-wave at a very low frequency. 

Faced with a significant thermal signature, users are generally required to de-tune the PID loop and live with the resulting inaccurate control. Here, there is still the possibility of instability. 

The Model 32 uses digital time-synchronous filter to actively subtract the cooler’s signature, resulting in much higher control accuracy and loop responsiveness. 

With the Synchronous Filter enabled, the controller will synchronously subtract the thermal signal from the input temperature signal. Since synchronous subtraction is used to eliminate the undesired signature, there is no phase-shift or loss of signal energy, as would be the case if a classical notch or low-pass filter is used. 

Subtraction is performed ahead of the PID control loop. Therefore, the input to the loop contains only the baseline temperature signal. 

Using the Input Signature Subtraction filter gives much higher temperature measurement accuracy and allows the use of aggressive, high precision control. It is applicable to virtually any cryocooler system. 

87 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

#### Synchronous Filter Setup 

To use the synchronous filter, two parameters must be set: 

- The AC Line Frequency setting must correspond to the actual power input AC frequency. The filter uses this to synchronize to the cooler. 

- The Synchronous Filter Taps parameter must be set for the specific cryocooler type. This parameter gives the filter a starting point for the number of filter taps required to perform an accurate subtraction. Determination of a proper setting may require some experimentation. 

To set the AC Line Frequency, go to the **Sys** menu and scroll down to the field _AC Line_ field. Then, select  60 or 50 Hz as required.  

To set the Synchronous Filter Taps parameter, enter a number between 1 and 25 into the _Sync Filt. Taps_ field. A setting of 1 turns the filter off. 

For most cryocoolers, a setting of 7 is used since this is the most common submultiple of the AC line frequency used. 

 **Note:** If you are not using a cryocooler, please leave the _Sync Filt. Taps_ field set at the default of 7. 

 **Note:** If you change the setting the _Sync Filt. Taps_ setting, you will need to re-tune the PID control loop. 

#### Viewing a Cryocooler Thermal Signature 

In order to view a cryocooler’s thermal signature and experiment with the synchronous filter, the Cryo-con Utility Software may be used. 

In the Data Logging menu, set the _interval_ field to the minimum allowed value of 0.1 Seconds and then open a strip chart. Use the manual settings on the strip-chart to zoom in on the temperature. You should be able to see the signature with the chart set to the base temperature plus or minus about 0.5K. 

In order to see the cooler signature, you will need to set the _Sync Filt. Taps_ field to zero. This will disable the removal of the signature. From here, you can enter various values in order to see the affect of the synchronous filter. 

Shown here is an example of a Cryomech PT403 pulse-tube refrigerator with a very low heat-capacity load. The first part of the graph is with the synchronous filter turned off and the second part shows a setting of 7 taps. 

88 

Model 32 / 32B User's Manual 

Basic Setup and Operating Procedures. 

In most cases, a tap setting may be found that completely eliminates the signature. 

89 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

### Using an external power booster 

Some systems require more power than the Model 32 can provide, or require a higher power secondary control loop. An auxiliary DC power supply or amplifier can be used for this purpose. 

Programmable power supplies that can be programmed by an input voltage or current can be interfaced to either control loop of the Model 32. 

Both control loops of the Model 32B are unipolar current source outputs. This means that they will not have the ‘zero voltage’ drift problems that bipolar voltage source outputs exhibit. 

Since both loops are current-source outputs, a programming resistor may be required to develop the voltage needed by the booster supply. 

To use a booster supply with the Loop #1 output, setup the controller as follows: 

1. Set the Loop 1 Load Resistance to 25 Ω by using the Heater Configuration Menu. 

2. On the Heater Setup Menu, set the Heater Range to Low. This will cause the loop to output a full-scale programming current of 0.1A. 

3. If the booster supply requires a voltage input, the loop output will need a programming resistor to set the full-scale programming voltage. This resistor can be installed across the input terminals of the power supply. 

4. Connect the Loop #1 output to the booster supply to the programming input of the booster supply and set up the supply according to the manufacturer’s documentation. 

**Example:** Many programmable power supplies require a zero to 10 Volt programming voltage. The value of the programming resistor is: 

R = 10-Volts / 0.1mA = 100 Ohms. 

Also note that the resistor must be capable of dissipating power: 

Watts = 10-Volts * 0.1mA = 1.0-Watts. 

90 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

Using a booster supply with Loop #2 of a Model 32 is simple since the loop outputs 0 to 10-Volts and can be connected directly to most programmable power supplies. However, Loop #2 of a Model 32B is more difficult since it is designed to output 10Watts. 

To use a booster supply with the Loop #2 of the Model 32B setup as follows: 

1. Loop #2 of a Model 32B outputs 450mA at up to 25-Volts. Therefore, to generate a zero to 10-Volt output, you must use a 25-Ohm programming resistor that can dissipate at least 10-Watts. Therefore, this resistor will get very hot during normal operation. 

2. Connect the Loop #2 output to the booster supply’s programming and set up the supply according to the manufacturer’s documentation. 

91 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

### Using Thermocouple Sensors 

Thermocouple sensors have low sensitivity and are very susceptible to electrical noise. Therefore, they are often difficult to apply. In order to obtain the best possible measurement accuracy, the recommendations given here should be carefully applied. 

#### Direct Connection 

The Model 32 supports direct connection to Thermocouple sensors by using a software based Cold Junction Compensation scheme as follows: 

1. The sensor input connection on the rear panel of the instrument is thermally anchored to a temperature sensor that is used for Cold Junction Compensation. 

2. The Cold Junction Temperature is continuously monitored and converted to a Cold Junction Voltage by a performing a ‘reverse lookup’ of the sensor’s calibration curve. 

3. When a sensor reading is taken, the Cold Junction Voltage is subtracted from the measured voltage. The result is used to compute actual sensor temperature by using a ‘forward lookup’ on the sensor’s calibration curve. 

It is important that Thermocouple sensors be connected directly to the input connector as described in the section below. For example, if the thermocouple wires were first connected to Copper wires, then to the Model 32 input, the Cold Junction Compensation cannot function properly and measurement errors will result. 

The Cold Junction Compensation function may be turned On or Off for each input channel. This is done by using the “CJcomp” field of the Input Channel Setup Menu. 

#### Adding New Thermocouple Types 

New thermocouple types may be added to the Model 32 by adding a new user sensor type and corresponding calibration curve. This procedure is described in the section below titled Adding a New Sensor. 

Since the software Cold Junction Compensation technique used by the Model 32 depends on the thermocouple's calibration curve, it is important to note that the temperature range of the curve must include room temperature. 

#### Cold Junction Compensation Errors 

Cold Junction Compensation is required for any instrument to measure thermocouple sensors accurately. The most accurate method for performing this is by using an external ‘Ice Bath’ setup. However, this is often impractical. 

Cold Junction Compensation in the Model 32 controller is performed by a circuit that measures the temperature of the input connector pins. This reading is then used to look up a compensating voltage from the thermocouple’s calibration curve 

The back-shell of the input connector should always be installed. This will minimize errors caused by local air currents. 

92 

Model 32 / 32B User's Manual 

Basic Setup and Operating Procedures. 

#### Offset Calibration 

Offset calibration is used to calibrate the Cold Junction Compensation circuit and is recommended when a thermocouple is first installed or any time a thermocouple is changed. 

An appropriate curve must be selected and Cold Junction Compensation must be enabled before calibration can be started. 

1. Connect the thermocouple. 

2. Locate the controller away from drafts as these may affect compensation. 

3. Allow the instrument to warm up for at least ½ hour without moving or handling the sensor. 

4. Insert the thermocouple into the ice-bath, liquid nitrogen, liquid helium, or other know fixed temperature. The temperature should be close to the measurement temperature that requires best accuracy. 

5. Read the displayed temperature in units of K or C, then subtract the known actual temperature from the reading to determine the CJ offset value. 

6. Enter the CJ offset value into the controller by going to the SYS menu and scrolling down to the CJ offset field. This completes the procedure. 

Check the calibration by verifying that the correct temperature is being read. 

#### Calibration Errors 

Variation in the manufacture of thermocouple wire and it’s annealing over time can cause errors in temperature measurement. 

Instruments that measure temperatures above about 0<sup>o</sup> C will usually allow the user to correct calibration errors by adjusting an offset in order to zero the error at room temperature. Unfortunately, in cryogenic applications, thermocouples lose sensitivity at low temperatures so a single offset voltage correction is insufficient. For example, if calibration errors for a Type K thermocouple are zeroed at room temperature, a reading near Liquid Nitrogen temperatures may have an error of 5K. 

Correction of Calibration Errors over a wide range of temperature can be made by using the Model 32’s CalGen  feature. Here, the controller should be stabilized at both temperature extremes. Then, CalGen  will generate a new sensor calibration curve that best fits the two points to the actual sensor voltage readings. 

Often, CalGen is be done by taking a reading at room temperature, then a second reading with the sensor in Liquid Nitrogen. Since a thermocouple’s sensitivity is relatively constant above room temperature, this procedure will give good accuracy over a wide range of temperature. 

#### AC Power Line Noise Pickup 

AC power noise pickup is indicated by temperature measurements that are significantly in error. In extreme cases, there may be no valid measurements at all. 

93 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

Thermocouples have relatively high resistance leads, and each lead is made from a different material. Therefore, they are much more sensitive to AC pickup than sensors using copper wires. 

A ground loop will cause significant AC coupling into the sensor. However, if the connection procedures described above are carefully followed, ground loops through the sensor leads will be avoided. 

When a grounded sensor is used, a poor quality ground may have sufficient AC voltage to exceed the input range of the controller. This can often be corrected by running a copper connection from a point near the sensor ground and the chassis ground of the controller. Defective building wiring or insufficient grounding is usually the root cause of this type problem. 

Most common AC noise pickup problems are caused by capacitive or magnetic coupling into the sensor wires. Again, the thermocouple’s high resistance leads make this type coupling very efficient. General recommendations to minimize coupling include: 

1. Minimize the length of thermocouple wires. For example, use a thermocouple Module near the sensor to convert the thermocouple wires to copper as soon as possible. 

2. Twist the wires. Twisted wire for various types of thermocouples is available from several vendors. 

3. Avoid running sensor wires near, or parallel to AC power lines. 

4. Use the largest diameter sensor wires possible (Lowest AWG). This will reduce the lead resistance and, therefore, reduce coupling. However, in many cryogenic applications, wire size must be kept small because thermocouple wire is a good heat conductor. 

#### Connecting Grounded Thermocouples 

For best performance, thermocouple sensors should be floating. This will ensure that no noise currents can flow in the sensor leads and that no common-mode noise voltage will be directly coupled into the controller. 

If a thermocouple must be grounded, the ground point should be a good earth ground that has the same potential as the earth ground of the instrument. If the ground point is floating or only loosely connected to earth ground, significant noise pickup can result. 

Since floating thermocouples will always give the best accuracy, they should be electrically insulated by using small Sapphire washers. 

Assuming that a grounded thermocouple is properly connected, the controller should operate properly. If this is not the case, the problem can usually be tracked to the ground connection made at the sensor relative to the ground at controller. 

The ground potential at the thermocouple sensor must fall within the ± 5 volt input range of the controller. 

94 

Model 32 / 32B User's Manual Basic Setup and Operating Procedures. 

Usually, the voltage difference between the sensor ground and the controller’s ground is an AC power line signal. It can be seen with a battery powered AC voltmeter connected between the controller’s chassis and a ground point near the sensor. 

If there is a significant voltage difference, a safety hazard may be present. Building wiring should be tested before proceeding. 

A voltage difference caused by a loose, or non-existent, ground reference can be corrected by: 

1. Establishing a good quality ground point that the controller and sensor grounds are both connected to. 

2. Running a ground strap. The preferred connection of the ground strap would be from a ground point near the sensor to the Third-Wire ground connection of the controller’s AC power cord. If this is not available, the strap can be connected to the controller’s chassis. 

95 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

### CalGen  Calibration Curve Generator. 

The CalGen  feature is used to generate new calibration curves for Silicon Diode, thermocouple or Platinum sensors. This provides a method for obtaining higher accuracy temperature measurements without expensive sensor calibrations. 

Most Cryo-con  temperature controllers support CalGen directly on the instrument. However, the utility software package implements the same algorithm and can be used with virtually any instrument capable of measuring temperature. 

Curves can be generated from any user selected sensor calibration curve and are written to a specified internal user curve location. 

For Diode sensors, the user may specify one, two or three data points. CalGen will generate the new curve based on fitting the input curve to the user specified points. 

Platinum or thermocouple calibration curves require one or two data points. The generated curve will be a best fit of the input curve to the two specified input points. 

Since CalGen fits a sensor calibration curve to measured data, any errors in the Model 32's measurement electronics are also effectively cancelled. 

 **Note:** CalGen  is re-entrant. Therefore, the user can enter or exit the CalGen  menus at any time without loss of previously captured data points. For example, a data point may be captured near 300K, next, the user may exit the CalGen  process in order to stabilize the controller near 77K. When the CalGen  menu is reentered for curve generation, the point captured at 300K is still valid. 

#### CalGen  Initial Setup 

Generation of a calibration curve using CalGen  requires the measurement various temperature points. Therefore, an input channel must be configured with the correct sensor before the CalGen  process can start. 

To initiate the curve generation, select the CalGen field on the Input Channel Setup menu. This will take the screen to a sub-menu for the specific sensor type. 

 **Note:** Before CalGen can be initiated, there must be a valid temperature reading on the selected input channel. If this is not the case, selecting the CalGen  field will cause the display of an error message. 

When the input channel has a valid reading, CalGen will determine if the sensor is a Diode, Platinum, or a thermocouple sensor. Further, the calibration curve of the selected input sensor will be used as the input to the curve generation process. 

96 

Basic Setup and Operating Procedures. 

Model 32 / 32B User's Manual 

#### Using CalGen  With Diode Sensors 

Options for generating Diode calibration curves are: 

1. One point near 300K. The portion of a Diode Sensor curve above 30K will be fit to a user-specified point near 300K. This is a two-point fit where the 30K point is taken from the existing calibration curve. The portion of the curve below 30K is unaffected. 

2. Two points: 300K and 77K. Here, two user-specified points are taken to fit the diode curve region above 30K. The entire curve is offset to match the 77K point, then, the >30K region is fit to the two points. 

3. Three points: 300K, 77K and 4.2K. Two points above 30K are fit as in the selection above. Then, a third point is used to fit a single point in the highsensitivity region below 20K. 

4. One point near 4.2K. This is a two-point fit where the 20K point is taken from the existing calibration curve. The portion of the curve above 20K is unaffected. 

For a Diode Sensor, a sub-menu will be displayed that allows the user to select the number of points desired for the CalGen  fit. 

||**First C**|**alGen****Men**|**u, Diode Sensor**|
|---|---|---|---|
|1|||<br>Pressing the**Enter**key will select curve<br>generation with a single point near<br>300K.|
|2|||<br>Pressing the**Enter**key will select curve<br>generation at two points where both<br>points must be > 50K.|
|3|||<br>Pressing the**Enter**key will select curve<br>generation three points: Two above 50K<br>and one near 4.2K.|
|4|||<br>Pressing the**Enter**key will select curve<br>generation with a single point near<br>4.2K.|

**Table 33: First CalGen**  **Menu, Diode Sensor** 

From this screen, select the desired number of points. For example, select ‘2 point’. This will take the display to the two-point curve generator screen shown here. 

97 

Model 32 / 32B User's Manual 

Basic Setup and Operating Procedures. 

**CalGen**  **Menu, 2-point Diode Sensor** 

|1||The exact temperature at a point near<br>300K is entered here. Note: if CalGen<br>has not been used on this channel<br>before, the word Capture will appear.<br>Otherwise, the last captured sensor<br>reading will appear.|
|---|---|---|
|2||Pressing the**Enter**key will capture the<br>existing unit reading and associate it<br>with the 300K point. The value will be<br>displayed on line 1 above.|
|3||The exact temperature at a point near<br>77K is entered here.|
|4||Pressing the**Enter**key will capture the<br>existing unit reading and associate it<br>with the 77K point. The value will be<br>displayed on line 3 above.|
|5||Pressing the**Enter**key will initiate the<br>generation of a new curve.|

**Table 34: CalGen**  **Menu, 2-point Diode Sensor** 

The two temperature points, one near 300K and the other near 77K may be entered in any order. 

To enter the 300K-point, change the field 300.000 to the exact required temperature. Then, allow the temperature measurement to stabilize. When the measurement is stable, select the Capture field next to the temperature field. This will cause the Model 32 to capture the sensor reading and associate it with the specified temperature. 

When a sensor reading has been captured, the actual reading will be displayed in place of the word Capture. Note that the user may capture a new reading by selecting this field again, even if it already contains a reading. 

The Unit field of this screen will display the actual sensor reading in real time. This will allow the user to determine when the unit is stable at the required temperature. 

Next, the second temperature must be entered in the same way as before. 

98 

Model 32 / 32B User's Manual 

Basic Setup and Operating Procedures. 

When both temperature points have been entered, the user may select the New Curve field in order to generate the new curve. This will cause the display of a menu like the one shown here: 

||**CalGen**|**New Curve**|**Menu**|
|---|---|---|---|
|1|||Sets the curve number for the<br>generated curve. Numeric entry. Note:<br>only the user curves can be written.|
|2|||Pressing the**Enter**key will cause the<br>generation of a new curve. The curve<br>will be stored at the curve number<br>specified on line 1.|

**Table 35** : **CalGen**  **New Curve Menu** 

From this screen, the user must select the target user curve for the generated curve. 

Finally, select the Save field in order to generate the curve and store it in the selected user location. 

Note: The CalGen process may be aborted by pressing the **Esc** or **Home** key. 

#### Using CalGen  With Platinum and Thermocouple Sensors 

The calibration curve generation procedure for Platinum or Thermocouple sensors is the same as for the diode sensors described above. However, Platinum sensor curves are generated using two user specified points. Therefore, the selection of the number of points is not required. 

99 

Model 32 / 32B User's Manual 

System Shielding and Grounding Issues 

## System Shielding and Grounding Issues 

### Grounding Scheme 

The grounding scheme used in all of Cryo-con’s instruments is based on a SinglePoint-Ground and is designed to minimize ground-loop and noise pickup by assuming that the Sensor and Heater elements are electrically floating, but the remote interfaces are not. 

#### The Single-Point-Ground 

The internal Single-Point-Ground is the voltage reference point for the instrument’s grounding scheme. All circuits are designed so that no current will normally flow through the connections to this ground. Therefore, it provides a good quality, low impedance path to ground for any undesired currents that are coupled into the equipment. 

#### AC Power Entry 

AC Power enters the instrument directly into a power entry module. This provides fusing, line voltage selection and RFI filtering. 

The Building Ground, often referred to as “Earth-Ground”, “Shield-Ground” or “ThirdWire-Ground” is connected to the shield of the Power Entry RFI filter, then to the instrument’s Single-Point-Ground.  Since the grounding and shielding scheme depends on having a good quality ground, this Earth-Ground connection is extremely important. Noise and ground loop problems are often traced to how this connection is made. 

If your facility does not provide a building ground, it is strongly recommended that one be fabricated. 

#### Sensor Connection 

For best performance, all sensors connected to the instrument should be electrically isolated (floating) from any other grounds. 

Sensors used in cryogenic thermometry are often high impedance. For example, a Silicon Diode temperature sensor will have about 160K ohms of impedance at 5K. Because of this, a very efficient antenna can develop around the sensor and its connections. Requiring these sensors to be floating and providing a low impedance path to ground is the most effective way to eliminate noise pickup from this antenna effect. 

To ensure that the instrument’s grounding scheme is working effectively: 

1. Make sure that the sensors are floating. 

2. Make sure that the input cable shields are connected to the connector’s metal backshell using the shield clip provided with the connector. 

3. Make sure that the Third-Wire-Ground is good quality and not conducting current. 

101 

Model 32 / 32B User's Manual 

System Shielding and Grounding Issues 

#### Control Loops 

The circuitry in the Control Loop Area provides power to external heater elements. The grounding of this area is identical to the Sensor Area described above. Note however that heater elements usually have very low impedance. Therefore, noise pickup issues are not near the problem that they are in the Sensor Area. 

#### Digital Circuits 

The digital circuits of the Model 32 cannot assume that its external connections are floating. Therefore, it is connected to the Single-Point-Ground through a ResistorCapacitor network in order to prevent ground loops. 

RS-232 and GPIB connections bring a ground return connection from the host computer. This means that the Digital area must be at the same voltage as the host’s circuit board ground; Otherwise, ground loop currents will flow from the host, through the instrument and back into the Earth-Ground. 

An R-C network is used to eliminate common-mode voltages from the unit’s power supply, but also has a high enough impedance to reduce ground-loop current flow. 

Further, since it is isolated from the other areas of the circuit, no current carrying paths can flow through the more sensitive analog circuits. 

#### <u>The RS-232 Connection</u> 

The RS-232 connection is a three-wire serial communication scheme. Two wires carry signals and the third carries a ground reference. 

When either of these interfaces is connected to a Cryo-con controller, the voltage of the digital area is established by the ground reference of the connected interface. 

Because of the internal R-C network connection to ground, little if any current can flow back through the system grounds. 

#### <u>The GPIB Connection</u> 

The GPIB is a 24-wire communications protocol that has six control signal grounds, one data signal ground and one shield ground. 

In the Cryo-con controller, the control and signal grounds are connected together and used to establish the ground reference potential for the digital area. 

The Shield ground connection is connected to the instrument’s Single-Point-Ground through a jumper. The jumper is available since some manufacturers connect the GPIB shield ground to their circuit board ground and, therefore, ground loops are established through the shields. Removing the jumper will break this ground. 

102 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

## Cryo-con Utility Software 

Cryo-con provides a PC compatible utility software package with all instruments. This is available on CD, or on the Internet. 

Utility software can be used to control and configure any Cryo-con instrument via the RS-232, LAN, USB or IEEE-488 interface. It runs under all versions of the Windows operating system. This software provides several useful functions, including: 

1. Real-time strip charts of temperature. 

2. Data Logging. This function allows the user to record data from the instrument at a specified sample rate. The resulting file is compatible with most spreadsheet and data analysis software. 

3. Download or upload sensor calibration curves. The software will accept curves in Cryo-con .CRV, Lakeshore .340 or Scientific Instrument’s .txt format. In fact, it will read almost any table of temperature vs. sensor units. 

4. Cryo-con’s CalGen  function is implemented. This function allows the user to fit an existing sensor calibration curve to one- two- or three user-specified points. The result is a high accuracy sensor calibration at low cost. 

5. Upload and download PID tables to a Cryo-con temperature controller. These tables can be generated by using a simple text editor and downloaded to the controller. 

6. Configuration of any of the instrument’s remote interfaces. 

7. Flexible ‘Help’ interface that documents all instrument remote commands with a cut-and-paste type interface. 

8. ‘Interactive Mode’ provides interactive communication with the instrument over any of the remote interfaces. 

9. Instrument calibration using a simple step-by-step menu driven process. 

10. Uploading and downloading instrument firmware. Updates may be obtained on CD, or on the Internet. 

### Installing the Utility Software 

From a CD, the utility software package does not require installation. It can be executed from the CD directly by running the UTILITY.EXE program. 

When the software is downloaded off of the Internet, it is in a self-extracting ZIP format and must first be un-zipped onto hard disk. 

103 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

### Connecting to an Instrument 

The desired remote interface connection may be selected by clicking **Comm>Port Select** from the main menu. 

Select the desired communications port and then click **OK** .. 

Click on the **Connect** button of the shortcut menu bar or on **Comm->Connect** from the main menu to connect to the instrument. 

104 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

After a short delay, the connect LED should light and the instrument type will be displayed. Also, most of the grayed-out fields on the menu bars should activate. 

### Using the Interactive Terminal 

The Utility Software’s Interactive Terminal mode allows the user to send commands to the instrument and view the response. 

Terminal mode is selected by selecting **Comm>Interact** from the main menu or **Interact** from the shortcut bar. This will result in the display shown below. 

To interact with the instrument, type a remote command into the dialog box and click **Send** . The command will be transmitted to the instrument and a response, if any, will be displayed on the background window. 

To exit terminal mode, click the **Quit** button on the dialog box. 

105 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

### Downloading or Uploading a Sensor Calibration Curve 

Sensor calibration curves may be transferred between the PC and the instrument by using the Calibration Table menu. 

To download a curve (send it from the PC to the instrument), either select “Sensor Curve Download” from the shortcut bar or **Operations>Sensor Curve>Download** 

from the main menu. This will cause a file selection dialog box to appear as follows: 

From this screen, the desired calibration curve is selected. Cryo-con calibration curves have the file extension of .CRV. Lakeshore curves with the extension .340 may also be selected. Scientific Instruments .txt files may be downloaded by first selecting a file type of *.* and then selecting the desired calibration curve file. 

Cryo-con .CRV files are ASCII text files that may be edited by any text editor. 

106 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

After selecting the file and clicking on **Open** , the selected file will be read and the Edit Curve Header dialog box will appear. This box contains information extracted from the curve file header that can be modified, if desired, before the curve is downloaded. 

“Sensor Name” is any 15-character string and is only used to identify the sensor. 

Sensor type can be selected from a pull-down menu or entered directly. Note that different models of Cryo-con instruments support different types of sensors. Therefore, it is important to enter a sensor type that is supported by the specific product. If the instrument receives a sensor type that it does not support, the ‘Diode’ type is selected. The section titled “Supported Sensor Configurations” gives complete information on sensor types. 

The Multiplier field is used to select the sign of the sensor’s temperature coefficient. A value of –1 selects a Negative-Temperature-Coefficient sensor while a value of 1 selects a Positive-Temperature-Coefficient. 

The Unit field selects the units used in the calibration curve. Choices are: Volts, Ohms or LogOhm. 

Checking the ‘Save as .crv’  will save the curve to disk as a Cryo-con .crv file. 

107 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

The sensor curve may be viewed as a graph by clicking the ‘Display Curve’ button. An example plot is shown here: 

After completing any desired changes in the “Edit Curve Header” dialog box, click ‘Accept’ to proceed. Then the, curve number dialog box will appear: 

A user calibration curve should be entered here. For the Model 32, user curves are 1 through 4. For the Model 34 and Model 62, user curves are 1 through 12. 

108 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

When ‘OK’ is selected, the sensor calibration curve will be downloaded to the instrument. During the transfer, curve data points will be displayed in the window’s main pane. Upon completion, the Download Complete dialog box will appear: 

Dismiss this dialog box to complete the download process. 

To upload a calibration curve, use the same procedure and select **Upload** . This will transfer a curve from the instrument to the PC. 

109 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

#### **Downloading or Uploading a PID Table** 

A PID table may be transferred to the instrument by selecting **PID Table>Download** from the main menu toolbar. 

PID tables are transferred from the instrument to the PC by using **PID Table>Upload** . 

From this point, the sequence is identical to the calibration curve transfer process described above. 

### Using the Real-Time Strip Charts 

The real-time strip chart feature of the Utility Software lets the user continuously display any combination of input channels on the computer display. 

This function is initiated by selecting the **View** command on the Utility Software’s main toolbar, then selecting the desired channels to monitor. 

A strip chart will be displayed for each channel selected. The dialog box will show the channel’s Input Identifier, Name String and a chart of current temperature. 

The update rate of the chart is locked to the program’s Data Logging Interval. The section below details how to set this value. 

110 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

### Data Logging 

The Utility Software will perform data logging on all of the instruments input and control output channels. The result is a disk file in Comma-Separated-Value, or CSV format. This format is compatible with any data analysis or charting software including Microsoft Excel. 

To initiate data logging, select the **Data Logging** button from the Utility Software’s main menu. The Data Logging Setup dialog box will now appear. 

On this dialog box, check the desired channels and set an Interval value in Seconds. The minimum interval is 0.1 Second. 

111 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

When the **Start** button is clicked, a file selection dialog box will be shown. 

From this dialog box, enter a file name and select the directory where data logging 

results will be saved. 

As soon as the **Save** button is clicked, the software will begin continuous data logging to the specified file. 

While data logging is in progress, a dialog box will be displayed that allows the user to stop logging. When this **Stop** button is clicked, logging is stopped and the log file is closed. 

112 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

### Remote I/O command HELP 

Help for the remote interfaces and remote commands is available by clicking on the **HELP>Contents** button from the Utility Software’s main menu. 

A standard HELP screen will be shown that is indexed and searchable. 

113 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

### CalGen Calibration Curve Generator. 

The CalGen  feature is used to generate new calibration curves for Silicon Diode or resistor sensors. This provides a method for obtaining higher accuracy temperature measurements without expensive sensor calibrations. 

Most Cryo-con  temperature controllers support CalGen  directly on the instrument. However, the utility software package implements the same algorithm and can be used with virtually any instrument capable of measuring temperature. 

New Curves can be generated from any user selected sensor calibration curve and are written to a specified file. 

For Diode sensors, the user may specify one, two or three data points. CalGen will generate the new curve based on fitting the input curve to the user specified points. 

Platinum or other resistor calibration curves require one or two data points. The generated curve will be a best fit of the input curve to the two specified input points. 

Since CalGen fits a sensor calibration curve to measured data, any errors in the instrument’s measurement electronics are also effectively cancelled. 

#### CalGen  Initial Setup 

To start the CalGen  process, either select **CalGen**  from the shortcut bar, or select Operations>CalGen from the main menu. This will initiate the process of generating a new sensor curve. 

#### Using CalGen With Diode Sensors 

Options for generating Diode calibration curves are: 

5. One point near 300K. The portion of a Diode Sensor curve above 30K will be fit to a user-specified point near 300K. This is a two-point fit where the 30K point is taken from the existing calibration curve. The portion of the curve below 30K is unaffected. 

6. Two points: 300K and 77K. Here, two user-specified points are taken to fit the diode curve region above 30K. The entire curve is offset to match the 77K point, then, the >30K region is fit to the two points. 

7. Three points: 300K, 77K and 4.2K. Two points above 30K are fit as in the selection above. Then, a third point is used to fit a single point in the highsensitivity region below 20K. 

8. One point near 4.2K. This is a two-point fit where the 20K point is taken from the existing calibration curve. The portion of the curve above 20K is unaffected. 

#### Using CalGen  With Resistor Sensors 

The calibration curve generation procedure for Platinum or other resistor sensors is the same as for the diode. However, these sensor curves are generated using two user specified points. Therefore, the selection of the number of points is not required. 

114 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

#### Example CalGen  Procedure 

A complete procedure for calibrating a diode sensor at three points is shown here. Before the procedure can be started, the instrument must be connected and have a valid sensor connected. 

The CalGen  procedure will require the user to stabalize the input temperature at three user-selected points. It will capture data at each of these points and then generate a new curve from that data. 

When a 3-point CalGen is started for a Silicon Diode sensor, the reference curve must first be selected. This is the curve that will be rotated and shifted to fit the selected points. 

115 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

When the curve has been selected, the following dialog box will appear: 

The process requires you to completely fill out this dialog box by selecting a temperature and then copying the voltage (or resistance) reading corresponding to that temperature from the instrument. 

Note that the Vapor Pressure button will take the user to a convenient calculator that will compute the temperature of various cryogens from the current barometric pressure. 

Once the dialog box has been completed, click OK to proceed. 

To finish the process, you will be prompted to save the modified calibration curve to a file. Once complete, the file can be transferred to any Cryo-con  instrument. 

116 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

### The Vapor Pressure Calculator. 

The Vapor Pressure Calculator is a convenient aid that computes the actual temperature of most cryogens given the current barometric pressure. It can be launched directly off of the utility disk by executing “Vapor Pressure Calculator.exe” or from the CalGen  dialog as shown above. 

A typical calculation is shown here: 

You must select the Substance from a drop-down list and then select the barometric pressure and temperature units. 

117 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

Substance selections are shown here: 

### Downloading Instrument Firmware 

A primary feature common to all of Cryo-con’s instruments is the ability to download new firmware. Firmware must be matched to the product’s model number and hardware revision level. For that reason, please contact Cryo-con via e-mail or telephone for the most recent firmware. 

Firmware updates include the addition of new features as well as bug fixes. Installing a new revision writes to all of the available FLASH type memory in the instrument. Therefore, existing calibration curves, instrument setups and PID tables are reset to factory defaults. If user information, such as sensor calibration curves, has been installed, it is recommended that these be uploaded to the computer before new firmware is installed. This way, they can be re-installed after the new firmware. 

Firmware download does NOT erase the instrument’s calibration data. 

Note that FLASH memory is inherently non-volatile and may be re-written in excess of 100,000 times. Therefore, the user need not be concerned about excessive re-writing. 

118 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

 **Note:** Firmware can only be downloading using the RS-232 serial interface. It cannot be downloaded via the GPIB. Therefore, make sure that you have a null-modem RS-232 cable attached to the controller and that the Utility Software is configured to use RS232 at a baud rate of 9600. Do NOT use baud rates above 9600 since the firmware update speed is limited by the programming speed of the flash memories. 

**Caution** : To protect the instrument from casual downloads and possible corruption, the Utility software must be executed with a command line argument of –f for a firmware download and –d for a firmware upload. The utility disk contains a shortcut named UtilityFD that contains these command line arguments. 

119 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

To download new firmware, select **Firmware>Download** from the Utility Software’s main menu. If the Download item is grayed-out, you must exit the utility software and re-start it with the correct command line switches as noted in the caution above. Selecting a firmware download will result in the display of a file selection dialog box as shown below: 

In this dialog box, firmware file names are coded as shown below: 

#### **MmmRev.BIN** 

Where mm is the Model Number, eg: 32, 34, 62 etc. and Rev is the revision code in the format XrXX where the lower case r indicates a <u>period character. The file extension is always BIN.</u> 

From the file dialog box, find and select the desired firmware file. Then click on the Open button in order to initiate the firmware download. 

Firmware download will be initiated immediately after the Open button is clicked. Once download has started, you should not attempt to stop it. 

120 

Model 32 / 32B User's Manual 

Cryo-con Utility Software 

When a firmware download has successfully started, the VFD display will continuously display the number of records transmitted as shown here. There are 1008 records in a complete  firmware download. The process should  take about 15 minutes. 

The PC screen will show a bar-graph of progress during download. 

When the download is complete, the controller will freeze and the PC will display a ‘Download Complete’ dialog box. 

**Caution** : When a firmware download is complete, the controller should automatically reset within 10 seconds. Do not unplug it. When the reset process is complete, hold down the **Enter** key and power-cycle the instrument from the front panel. The new firmware should boot up. 

If a non-recoverable communications error occurs during firmware download, the controller will power up in an error mode where it is looking for a new firmware transfer on the serial port. The VFD screen will display the transfer display shown above. In this case, repeat the above procedure until the entire firmware transfer sequence works correctly. 

 **NOTE:** Factory defaults may be restored at any time by use of the following sequence: 1) Turn power to the Model 32 OFF. 2) Press and hold the **Enter** key while turning <u>power back ON.</u> 

 **NOTE:** The firmware download mode of the Model 32 may be forced by the following sequence 1) Turn power to the Model 32 OFF. 2) Press and hold the **Stop** key while turning power back ON. This sequence is intended for use when the controller is not operational and will not accept remote commands to place it in the download mode. 

121 

Model 32 / 32B User's Manual 

Instrument Calibration 

## Instrument Calibration 

Calibration of the Model 32 controller requires the use of various voltage and resistance standards in order to generate calibration factors for the many measurement ranges available. 

Calibration is ‘Closed-Case’. There are no internal mechanical adjustments required. The Model 32 cannot be calibrated from the front panel. 

Calibration data is stored in the instrument’s non-volatile memory and is accessed only via the remote interfaces. Calibration of a measurement range is the simple process of generating an offset and gain value. However, since there are several input ranges available on each sensor input, the process can be time consuming. 

**Caution:** Any calibration procedure will require the adjustment of internal data that can significantly affect the accuracy of the instrument. Failure to completely follow the instructions in this chapter may result in degraded instrument performance. 

The Cryo-con utility software used in this procedure will first read all calibration data out of the instrument before any modifications. It is <u>good practice to record these values for future reference and backup.</u> 

### Cryo-con Calibration Services 

When the controller is due for calibration, contact Cryo-con for low-cost recalibration. The Model 32 is supported on our automated calibration systems which allow Cryocon to provide this service at competitive prices. 

### Calibration Interval 

The Model 32 should be calibrated on a regular interval determined by the measurement accuracy requirements of your application. 

A 90-day interval is recommended for the most demanding applications, while a 1- year or 2-year interval may be adequate for less demanding applications. Cryo-con does not recommend extending calibration intervals beyond 2 years. 

Whatever calibration interval you select, Cryo-con recommends that complete readjustment should always be performed at the calibration interval. This will increase your confidence that the instrument will remain within specification for the next calibration interval. This criterion for re-adjustment provides the best measure of the instrument’s long-term stability. Performance data measured using this method can easily be used to extend future calibration intervals. 

123 

Model 32 / 32B User's Manual 

Instrument Calibration 

### Minimum Required Equipment 

All calibrations require a computer with an RS-232 or IEEE-488 connection to the instrument. Additionally, reference standards are required for each input range as follows: 

- The Silicon Diode input range (Calibration Type I10UA and V10UA) requires voltage references of 0.5 and 1.5 Volts DC and a resistance standard of 100KΩ. 

- The Constant-Voltage AC resistance ranges (Type AC10UA, AC100UA and AC10UA) require the use of 100KΩ, 10KΩ, 1KΩ, 100Ω and 10Ω resistances. 

- The 100Ω Platinum range (Type R1MA) requires a 100Ω and a 10Ω resistor. 

- The 1000Ω range (Type R100UA) requires 1K Ω and 100 Ω resistors. 

- The 10,000Ω range (Type R10UA) requires 10KΩ and 1KΩ resistors. 

- The 80mV thermocouple (optional) range requires voltages of +0.075 and – 0.075 Volts. 

The test equipment recommended for complete calibration is a Fluke 5700A DMM calibrator. 

### The Basic Calibration Sequence 

You must first connect the Model 32 to a computer via the RS-232 (Serial) or IEEE488 (GPIB) interface and then run the Utility Software provided with the controller. The Utility Software must be version 7.4.2 or higher. 

From the start-up menu of the Utility Software, click the Connect button in the bottom of the Short Cuts toolbar. The software will connect to the instrument and display the connection status below the button. 

In case of an error, please correct the port connection settings and try again. 

From the main menu, select Operations->Unit Cal. The program will read the current calibration values from the instrument and display a calibration screen as shown below. All calibration operations can be performed by using this screen. 

124 

Instrument Calibration 

Model 32 / 32B User's Manual 

**Figure 8: Instrument Calibration Screen** 

 **Note:** Newer Cryo-con instruments will require a password before calibration data can be saved. The utility software will allow you to enter and change the password. The default password is: **cryocon** 

On the far right of the screen, a drop-down box selects the channel to be calibrated. Be sure you have selected the correct channel. In order to perform a complete calibration, you will need to calibrate each channel individually. 

Along the top of the screen, there are tabs that show the types of calibration that are supported by the instrument.  To perform a complete calibration of a single input channel, all calibration types must be calibrated. 

Note the **Calibration Results** box on the screen. The **Status** field will initially be set to ‘Current’ and the **Gain** and **Offset** values shown will be those read from the instrument. 

 **Note:** If your calibration procedure requires saving historical values, you will want to record the Gain and Offset values shown on the initial screen before proceeding with actual calibration. 

125 

Model 32 / 32B User's Manual 

Instrument Calibration 

There are two methods available for calibration: 

1. Automatic. The software will recommend voltages and resistances. You can set these values on the input channel and capture the instrument’s actual readings. Then, the software will automatically generate offset and gain values for you. 

2. Manual: You can manually enter Offset and Gain values and send them to the instrument. 

#### Manual Calibration 

To manually calibrate a range, select the desired range from the range type tabs and enter the desired Gain and Offset values in the boxes given and then, click the **APPLY** button. 

Gain is a unit-less gain factor that is scaled to a nominal value of 1.0. It is usually computed by: 

- gain = (UT – LT) / (UM – LM) 

where: 

UT is the upper target and LT is the lower target. UM is the upper measurement and LM is the lower measurement. 

Gain values greater than 1.2 or less than 0.8 are rejected as out of range. 

Offset is in units of Volts or Ohms depending on the calibration type. Nominal value is 0.0. Positive or negative numbers are accepted. It is usually calculated by: 

Offset = UT  - gain * UM 

126 

Model 32 / 32B User's Manual 

Instrument Calibration 

#### Automatic Calibration 

Automatic calibration uses the left-hand side of the calibration screen and is a fourstep process: 

1. Line 1 requires setting a upper target value on the input channel. Depending on the calibration range selected, this will be in Volts or Ohms. 

First, establish a voltage or resistance on the selected input channel that is near the recommended value. Then, enter the actual value in the box provided. 

2. Click the Capture button on Line 2. The software will wait for the reading to stabilize and then will capture the reading and display it in the edit box on Line 2. 

While waiting for a stable reading, the following dialog box will be displayed: 

When the capture is complete, dismiss the following dialog: 

3. Line 3 requires setting a lower target value on the input channel. Depending on the calibration range selected, this will be in Volts or Ohms. 

First, establish a voltage or resistance on the selected input channel that is near the recommended value. Then, enter the actual value in the box provided. 

4. Click the Capture button on Line 4. The software will wait for the reading to stabilize and then will capture the reading and display it in the edit box on Line 4. 

127 

Model 32 / 32B User's Manual 

Instrument Calibration 

When the above procedure is complete, you will have established upper and lower target values as well as upper and lower measurements. The edit boxes on lines 2 and 4 will contain the measured values. At this time, you may still change the target values on line 1 and 3 if desired. 

Now, you can automatically compute the required gain and offset values by clicking on the **Calibrate** button in the **Calibration Results box** . This will change the **Status** field from ‘Current’ to ‘Calibrated’ and will update the **Offset** and **Gain** values with those calculated. 

At this point, to values have been transmitted to the instrument! 

In order to send the offset and gain values to the instrument’s calibration memory, click the **APPLY** button. You will be required to confirm that you really want to update calibration memory. 

#### Summary of Calibration Types 

Calibration data must be generated for each input channel by sequencing through the various calibration types on each channel. A summary of types is given here: 

|**Calibration**<br>**Type**|**Voltage**<br>**Range**|**Output**<br>**Current**|**Description**|
|---|---|---|---|
|**SI DiodeV**|0 – 2.5V|N/A|Voltage measurement for use with<br>Silicon Diode temperature sensors.|
|**SI Diode I**|N/A|10µA|10µA constant-current source used<br>with Silicon Diode sensors.|
|**1mA AC**|10mV,<br>1.25Hz|Autoranged|1mA range used with constant-<br>voltage mode sensors.|
|**100uA AC**|10mV,<br>1.25Hz|Autoranged|100µA range used with constant-<br>voltage mode sensors.|
|**10uA AC**|10mV,<br>1.25Hz|Autoranged|10µA range used with constant-<br>voltage mode sensors.|
|**1mA DC**|0-2.5VDC|1.0mA|DC measurement of 100 Platinum<br>RTD sensors.|
|**100uA DC**|0-2.5VDC|100µA|DC measurement of 1K Ohm<br>Platinum RTDs|
|**10uA DC**|0-2.5VDC|10µA|DC measurement of 10K Ohm<br>Platinum RTDs or other resistor<br>sensors that use DC current<br>excitation|
|**VTC80**|+80mV to<br>–80mV|N/A|Thermocouple measurements. Valid<br>only when optional thermocouple<br>input is installed.|

128 

Model 32 / 32B User's Manual 

Instrument Calibration 

### Calibration of Silicon Diodes 

Silicon Diode sensors require the application of a precision 10μA current followed by reading the voltage-drop across the device. Therefore, calibration of a diode requires two steps: 1) Calibration of the input voltage reading and 2) Calibration of the 10μA current source. 

Note that the voltage calibration must always be done first since the current source calibration requires a precision voltage reading. 

#### Diode Voltage Calibration 

To calibrate the diode voltage range, click on the **SI Diode V** tab and follow the sequence described above to send Gain and Offset values to the instrument. 

The upper target requires connection of a 1.9 Volt source. The actual value is between 1.0 Volts and 2.4 Volts. If you do not have a precision voltage source, you can use a 1.5 Volt battery by using a high precision volt meter to measure it’s actual voltage. 

The lower target requires connection of a 0.5 Volt source. The actual value is between zero Volts and 0.6 Volts. If you do not have a precision voltage source, you can short the input channel for zero volts. 

#### Constant-current Source Calibration 

Calibration of the constant-current source is performed by using the **SI Diode I** tab. On this screen, only an upper target value is required since the current-source only requires a gain term. 

The upper target requires connection of a 100KΩ resistor. The actual value should be within 10% of 100KΩ. 

129 

Model 32 / 32B User's Manual 

Instrument Calibration 

### Calibration of DC resistors 

Resistor sensors that use direct current excitation are calibrated by using the **1mA DC** , **100uA DC** and **10uA DC** tabs. 

Resistors required for calibration are as follows: 

- **1mA DC:** Upper - 100Ω, Lower - 10Ω. 

- **100uA DC:** Upper 1,000 Ω, Lower - 100 Ω 

- **10uA DC:** Upper - 10,000 Ω, Lower - 1,000 Ω. 

### Calibration of AC resistors 

Resistor sensors that use auto-ranged AC excitation are calibrated by using the **1mA AC** , **100uA AC** and **10uA AC** tabs. 

Resistors required for calibration are as follows: 

- **1mA AC:** Upper - 100Ω, Lower - 10Ω. 

- **100uA AC:** Upper 1,000 Ω, Lower - 100 Ω 

- **10uA AC:** Upper - 10,000 Ω, Lower - 1,000 Ω. 

130 

Remote Operation 

Model 32 / 32B User's Manual 

## Remote Operation 

### Remote Interface Configuration 

The Model 32 has two remote interfaces: The GPIB (IEEE-488.2) and the RS-232. Connection to these interfaces is made on the rear panel of the instrument. For specifics about the connectors and cables required, refer to the section above on Rear Panel Connections. 

Configuration of the remote interfaces is done at the instrument's front panel by using the Remote I/O Setup Menu. 

All configuration information shown on this screen is stored in non-volatile memory and, once setup, will not change when power is turned off or a remote interface is reset. 

#### IEEE-488 (GPIB) Configuration 

The only configuration parameter for the GPIB interface is to set the address. This is done by using the System Functions Menu described above. 

Note that each device on the GPIB interface must have a unique address. You can set the instrument's address to any value between 1 and 31. The address is set to 12 when the unit is shipped from the factory. 

The controller's GPIB interface does not use a termination character, or EOS. Rather, it uses the EOI hardware handshake method to signal the end of a line. Therefore, the host must be configured to talk to the instrument using EOI and no EOS. 

|**Primary Address:**|1-31|
|---|---|
|**Secondary Address:**|None|
|**Timeout**|2S|
|**Terminate Read on EOS**|NO|
|**Set EOI with EOS on Writes**|YES|
|**EOS byte**|N/A|

**Table 36: Recommended GPIB Host Setup Parameters** 

131 

Remote Operation 

Model 32 / 32B User's Manual 

#### RS-232 Configuration 

The user can select RS-232 Baud Rates between 300 and 38,400. The factory default is 9600. 

The Baud Rate can be changed from the instrument's front panel by using the SYS menu. 

Other RS-232 communications parameters are fixed in the instrument. They are set as follows: 

Parity: None Bits: 8 Stop Bits: 1 Mode: Half Duplex 

The RS-232 interface uses a "New Line", or Line Feed character as a line termination. In the C programming language, this character is \n or hexadecimal 0xA. 

When sending strings to the controller, any combination of the following characters must be sent to terminate the line: 

1. Carriage Return, Hex 0xD. 

2. Line Feed, \n, Hex 0xA. 

3. Null, 0. 

The controller will always return the \n character at the end of each line. 

 **Note:** Some serial port software drivers allow the programmer to set a line termination character. This character is then appended to each string sent to the controller and stripped from returned strings. In this case, the \n (0xA) character should be selected. 

132 

Remote Operation 

Model 32 / 32B User's Manual 

### Introduction to Remote Programming 

#### Instructions 

Instructions (both commands and queries) normally appear as a string embedded in a statement of your host language, such as BASIC or C 

Instructions are composed of two main parts: The header, which specifies the command or query to be sent; and the parameters, which provide additional data needed to clarify the meaning of the instruction. 

An instruction header is comprised of one or more keywords separated by colons (:). Queries are indicated by adding a question mark (?) to the end of the header. Many instructions can be used as either commands or queries, depending on whether or not you have included the question mark. The command and query forms of an instruction usually have different parameters. Many queries do not use any parameters. 

The white space is used to separate the instruction header from the instruction parameters. If the instruction does not use any parameters, you do not need to include any white space. White space is defined as one or more spaces. ASCII defines a space to be character 32 (in decimal). 

Instruction parameters are used to clarify the meaning of the command or query. They provide necessary data, such as whether a function should be on or off, which input channel controls the heater output etc. Each instruction's syntax definition shows the parameters, as well as the values they accept. 

#### Headers 

There are three types of headers: Simple Command; Compound Command; and Common Command. 

Simple command headers contain a single keyword. CONTROL and STOP are examples of single command headers. The syntax is: 

<function><terminator> 

When parameters (indicated by <data>) must be included with the simple command header (for example, INPUT CHA) the syntax is: 

<function><white space><data><terminator> 

Compound command headers are a combination of two or more keywords. The first keyword selects the subsystem, and the last keyword selects the function within that subsystem. Sometimes you may need to list more than one subsystem before being allowed to specify the function. The keywords within the compound header are separated by colons. For example: 

#### SYSTEM:AMBIENT? 

To execute a single function within a subsystem, use the following: 

:<subsystem>:<function><white space><data><terminator> 

133 

Remote Operation 

Model 32 / 32B User's Manual 

Command headers control IEEE 488.2 defined functions within the instrument (such as clear status, etc.). Their syntax is: 

*<command header><terminator> 

No space or separator is allowed between the asterisk and the command header. *CLS is an example of a common command header. 

To execute more than one function within the same subsystem a semi-colon (;) is used to separate the functions: 

:<subsystem>:<function><white space><data> 

<function><white space><data><terminator> 

Command headers immediately followed by a question mark (?) are queries. After receiving a query, the instrument interrogates the requested function and places the response in it's output queue. The output message remains in the queue until it is read or another command is issued. 

Query commands are used to find out how the instrument is currently configured. They are also used to get results of measurements 

 **Note:** The output queue must be read before the next command is sent. For example, when you send the query, you must follow it with an input statement. 

#### Truncation of Keywords 

If a keyword contains more than four characters, it may be truncated to four or less characters to simplify programming. 

The truncated form of a keyword is the first four characters of the word, except if the last character is a vowel. If so, the truncated form is the first three characters of the word. 

### SCPI Status Registers 

#### The Instrument Status Register 

The Instrument Status Register (ISR) is queried using the SYSTEM:ISR? command. 

The ISR is commonly used to generate a service request (GPIB) when various status conditions occur. In this case, the ISR is masked with the Instrument Status Enable (ISE) register. 

The ISR is defined as follows: 

#### **ISR** 

|**Bit7**|**Bit6**|**Bit5**|**Bit4**|**Bit3**|**Bit2**|**Bit1**|**Bit0**|
|---|---|---|---|---|---|---|---|
|Alarm|||Htr|||SFB|SFA|

134 

Remote Operation 

Model 32 / 32B User's Manual 

Where: 

- **Bit7 – Alarm:** Indicates that an alarm condition is asserted. Use the ALARM commands to query individual alarms. 

**Bit4 – Htr:** Indicates a heater fault condition. Use the HEATER commands to query the heater. 

**Bit1 to Bit0 – SFx:** Indicates that a sensor fault condition is asserted on an input channel. Use the INPUT commands to query the input channels. 

#### The Instrument Status Enable Register 

The Instrument Status Enable (ISE) Register is a mask register. It is logically “anded” with the contents of the ISR in order to set the Instrument Event (IE) bit in the Status Byte (STB) register. This can cause a service request (GPIB) to occur. 

Bits in the ISE correspond to the bits in the ISR defined above. 

#### The Standard Event Register 

The Standard Event Register (ESR) is defined by the SCPI to identify various standard events and error conditions. It is queried using the Common Command *ESR? This register is often used to generate an interrupt packet, or service request when various I/O errors occur. 

Bits in the ESR are defined as follows: 

#### **ESR** 

|**Bit7**|**Bit6**|**Bit5**|**Bit4**|**Bit3**|**Bit2**|**Bit1**|**Bit0**|
|---|---|---|---|---|---|---|---|
|OPC||QE|DE|EE|CE||PWR|

Where: 

**Bit7 – OPC:** Indicates Operation Complete. 

**Bit5 – QE:** Indicates a Query Error. This bit is set when a syntax error has occurred on a remote query. It is often used for debugging. 

**Bit4 – DE:** Indicates a Device Error. 

**Bit3 – EE:** Indicates an Execution Error. This bit is set when a valid command was received, but could not be executed. An example is attempting to edit a factory supplied calibration table. 

**Bit2 – CE:** Indicates a Command Error. This bit is set when a syntax error was detected in a remote command. 

**Bit0 – PWR:** Indicates power is on. 

135 

Remote Operation 

Model 32 / 32B User's Manual 

#### The Standard Event Enable Register 

The Standard Event Enable Register (ESE) is defined by the SCPI as a mask register for the ESR defined above. It is set and queried using the Common Command *ESE. Bits in this register map to the bits of the ESR. The logical AND of the ESR and ESE registers sets the Standard Event register in the Status Byte (STB). 

#### The Status Byte 

The Status Byte (STB) is defined by the SCPI and is used to collect individual status bits from the ESE and the ISR as well as to identify that the instrument has a message for the host in it’s output queue. It is queried using the Common Command *STB?. Bits are defined as follows: 

#### **STB** 

|**Bit7**|**Bit6**|**Bit5**|**Bit4**|**Bit3**|**Bit2**|**Bit1**|**Bit0**|
|---|---|---|---|---|---|---|---|
||RQS|SE|MAV|IE||||

Where: 

**Bit6 – RQS:** Request for Service. 

- **Bit5 – SE:** Standard Event. This bit is set as the logical ‘AND’ of the ESR and ESE registers. 

**Bit4 – MAV:** Message Available 

**Bit3 – IE:** Instrument Event. This bit is set as the logical ‘AND’ of the ISR and ISE registers. 

#### The Status Byte Register 

The Status Enable Register (SRE) is defined by the mask register for the STB. It is set and queried using the Common Commands *SRE. 

The logical ‘AND’ of the SRE and STB registers is used to generate a service request on the GPIB interface. 

136 

Remote Operation 

Model 32 / 32B User's Manual 

### Remote Commands 

#### IEEE488 SCPI Common commands. 

The Common Commands are defined by the IEEE-488.2 standard and are supported by the Model 32 on the GPIB port as well as all of the remote interface ports. 

The common commands control some of the basic instrument functions, such as instrument identification and reset. They also provide an instrument status reporting mechanism. 

#### ***CLS Clear Status** 

Clear Status 

The *CLS common command clears the status data structures, including the device error queue and the MAV (Message Available) bit. 

**Command Syntax:** *CLS 

**Command Example:** *CLS 

#### ***ESE Event Status Enable** 

Event Status Enable. 

The *ESE command sets the Standard Event Status Enable (ESE) Register bits. The ESE Register contains a bit mask for the bits to be enabled in the Standard Event Status (SEV) Register. A one in the ESE register will enable the corresponding bit in the SEV register. A zero will disable the bit. 

The *ESE? Query returns the current contents of the ESE register. 

**Command Syntax:** *ESE <mask> 

**Query Syntax:** *ESE? 

**Command Example:** *ESE 32 

Query Response: <mask> 

This will set the CME, or Command Error, bit enable. Therefore, when a command error occurs, the event summary bit (ESB) in the Status Byte Register will also be set. 

#### **Query Example:** *ESE? 

Query Response: 16 

Bit 4, or the Execution Error bit has been enabled. All other standard events are disabled. 

137 

Remote Operation 

Model 32 / 32B User's Manual 

#### ***ESR Query Event Status Register** 

Query Event Status Register. 

The *ESR query returns the contents of the Standard Event (SEV) status register. 

#### **Query Syntax:** *ESR? 

Query Response: <status> 

Where status is a number between 0 and 255. 

#### ***IDN Query unit Identification** 

Query unit identification string. 

The *IDN? Query will cause the instrument to identify itself. The Model 32 will return the following string: 

“Cryocon Model 32 Rev <fimware rev code><hardware rev code>” 

Where <fimware rev code> is the revision level of the unit's firmware and <hardware rev code> is the hardware revision code. 

#### **Query Syntax:** *IDN? 

Query Response: <Instrument Identification String> 

#### ***OPC Operation Complete** 

The *OPC command will cause the instrument to set the operation complete bit in the Standard Event (SEV) status register when all pending device operations have finished. 

The *OPC Query places an ASCII ‘1’ in the output queue when all pending device operations have completed. 

**Command Syntax:** *OPC 

**Query Syntax:** *OPC? 

Query Response: 1 

#### ***RST Reset** 

Reset the controller. This will cause a hardware reset in the Model 32. The reset sequence will take about 15 seconds to complete. During that time, the instrument will not be accessible over any remote interface. 

The *RST command sets the Model 32 to it’s last power-up default setting. 

#### **Command Syntax** : *RST 

138 

Remote Operation 

Model 32 / 32B User's Manual 

#### Control Loop Start/Stop commands 

#### **STOP Disengage control loops** 

The STOP command will disengage all control loops and disconnect their heaters. 

**Command Syntax:** STOP 

#### **CONTROL: Engage Control Loops** 

The CONTROL command will cause the instrument to enter the control mode by activating enabled control loops. 

To disable an individual loop, set its control type to OFF. 

As a query, the command will report the status of the loops as ON or OFF. 

**Command Syntax** : CONTROL 

**Command Example** : CONT 

**Query Syntax:** CONTROL? 

Query Response: <status> Where <status> is ON or OFF. 

**Query Example:** CONT? Example Response: OFF Indicating that the control loops are OFF, or disengaged. 

#### **Short Form:** CONT 

139 

Remote Operation 

Model 32 / 32B User's Manual 

#### SYSTEM commands 

SYSTEM commands are a group of commands associated with the overall status and configuration of the Model 32 rather than a specific internal subsystem. 

#### **SYSTEM:LOCKOUT: Keypad Lockout.** 

Sets or queries the remote lockout status indicator. 

This command is used to enable or lock out the front panel keypad of the Model 32, thereby allowing or preventing keypad entry during remote operation. 

The default condition for this indicator is OFF. 

- **Command Syntax:** SYSTEM:LOCKOUT <status> 

   - Where <status> is either ON or OFF. A <status> of ON will lock out the front panel keypad. 

- **Query Syntax:** SYSTEM:LOCKOUT? Query Response: <status> 

- **Query Example:** SYSTEM:LOCKOUT? Example Response: OFF Indicating that the front panel keypad is enabled. 

   - **Short Form:** SYST:LOCK 

#### **SYSTEM:NVSAVE Save NVRAM to flash** 

Save NV RAM to Flash. This saves the entire instrument configuration to flash memory so that it will be restored on the next power-up. Generally only used in environments where AC power is not toggled from the front panel. This includes remote and rack-mount applications. 

#### **Command Syntax:** SYSTEM:NVSAVE 

#### **Short Form:** SYST: NVS 

140 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM :REMLED: Front Panel Remote LED** 

Sets or queries the remote LED status indicator on the Model 32 front panel. 

The default condition for this indicator is OFF. 

Note that the Remote LED is automatically handled by the GPIB interface but must be turned on and off when using the RS-232 interface. 

**Command Syntax:** SYSTEM:REMLED <status> 

Where <status> is either ON or OFF. A <status> of ON will illuminate the front panel Remote LED 

**Query Syntax:** SYSTEM:REMLED? Query Response: <status> 

**Query Example:** SYSTEM:REMLED? Example Response: OFF Indicating that the Remote LED is OFF. 

#### **Short Form:** SYST:REML 

#### **SYSTEM:LOOP: Control Loop On/Off** 

Reports the status of the two temperature control loops. 

A status of OFF indicates that both loops are disabled and the output power levels are zero. A status of ON indicates that the loops are engaged and actively controlling temperature. 

#### **Command Syntax:** N/A 

The CONTROL command is used to engage the control loops and the STOP command is used to disengage them. 

#### **Query Syntax:** SYSTEM:LOOP? 

Query Response: <status> 

**Query Example:** SYSTEM:LOOP? Example Response: OFF Indicating that both control loops are disengaged. 

#### **Short Form:** SYST:LOOP 

141 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:BEEP: Sound the audible alarm** 

Asserts the audible alarm for a specified number of seconds. 

#### **Command Syntax:** SYSTEM:BEEP <Sec> 

Where <Sec> is the number of seconds to beep the audible alarm. 

**Command Example:** SYSTEM:BEEP 10 

Sounds the audible alarm for 10 seconds. 

#### **Short Form:** SYST:BEEP 

#### **SYSTEM:DISTC: Display Filter Time Constant.** 

The SYSTEM:DISTC command is used to set or query the display filter time constant. 

The display filter is applied to all reported or displayed temperature data. Available time constants are 0.5, 1, 2, 4, 8, 16, 32 or 64 Seconds. 

#### **Command Syntax:** SYSTEM:DISTC <tc> 

Where <tc> is the display filter time constant, in seconds, selected from the following list: 0.5, 1, 2, 4, 8, 16, 32, 64. 

#### **Query Syntax:** SYSTEM:DISTC? 

Query Response: <tc> 

#### **Command Example:** SYSTEM:DISTC 8 

This command will set the display time constant to 8 Seconds. 

#### **Query Example:** SYSTEM:DISTC? 

Example Response: 2 Which indicates that the display filter has a 2 Second time constant. 

#### **Short Form:** SYST:DIST 

142 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:ADRS: GPIB address.** 

Selects the address that the IEEE-488.2 remote interface will use. 

The address is a numeric value between 1 and 31. The factory default is address 12. 

The addresses assigned to units must be unique on each GPIB bus structure. Multiple units with the same address on a single bus structure will cause errors. 

#### **Command Syntax:** SYSTEM:ADRS <adrs> 

Where <adrs> is the desired unit address. The IEEE-488.2 interface on the Model 32 will be re-initialized using <adrs> as it's address. 

**Query Syntax:** SYSTEM:ADRS? Query Response: <adrs> 

**Command Example:** SYSTEM:ADRS 14 Sets the Model 32 IEEE-488.2 address to 14. 

**Query Example:** SYSTEM:ADRS? Example Response: 12 Indicates that the current GPIB address is 12. 

#### **Short Form:** SYST:ADRS 

143 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:REMOTE: Select Remote Interface** 

Queries or selects the port that the Model 32 will use for all remote communication. 

#### Available ports are: 

GPIB for the IEEE-488.2 port. RS232 for the RS-232 port. 

#### **Command Syntax:** SYSTEM:REMOTE <port> 

Where <port> is the remote port selection. The Model 32 will first disable all remote ports, then initialize and re-enable the selected port. 

This command can be used as a port reset. 

**Query Syntax:** SYSTEM:REMOTE? Query Response: <port> 

#### **Command Example:** SYSTEM:REMOTE GPIB 

Selects the GPIB remote port. If the GPIB is already selected, it is re-initialized and enabled. 

**Query Example:** SYSTEM:REMOTE? Example Response: RS232 Indicates that the current remote port is RS-232 

#### **Short Form:** SYST:REMO 

#### **SYSTEM:RESEED: Re-seed the display filters** 

Re-seeds the input channel’s averaging filter, allowing the reading to settle significantly faster. 

The display filter may have filter time-constants that are very long. The RESEED command inserts the current instantaneous temperature value into the filter history, thereby allowing it to settle rapidly. 

#### **Command Syntax:** SYSTEM:RESEED 

**Command Example:** SYSTEM:RESEED 

#### **Short Form** : SYS:RES 

 **Note:** The RESEED command is very useful in systems where a computer is waiting for a reading to settle. Issuing the RESEED command will reduce the required settling time of the reading. 

144 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:AMBIENT Query Internal Temperature.** 

The Model 32 incorporates a temperature sensor into it's internal voltage reference. This temperature is essentially the internal temperature of the instrument and may be queried using the SYSTEM:AMBIENT command. 

#### **Query Syntax:** SYSTEM:AMBIENT? 

Query Response: <temp> 

Where <temp> is the internal temperature of the Model 32 in degrees Celsius. 

#### **Query Example:** SYSTEM:AMB? 

Example Response: +25C 

Indicates that the current temperature of the Model 32's internal voltage reference is 25 ° C. 

#### **Short Form:** SYST:AMB 

Where AMBIENT is truncated to four characters, then to three since the fourth character is a vowel. 

#### **SYSTEM:AUTOCAL Automatically recalibrate the input channels.** 

This command causes the Model 32 to execute an internal recalibration of both input channels. It is useful when the operating temperature has changed significantly. The process takes about ½ second to complete. 

Autocalibrate should not be executed when the Model 32 is controlling temperature because it may cause the control loops to disengage. 

#### **Command Syntax:** SYSTEM:AUTOCAL 

#### **Short Form:** SYST:AUT 

Where AUTOCAL is truncated to four characters, then to three since the fourth character is a vowel. 

145 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:HTRHST: Heater heat sink temperature.** 

The temperature of the Model 32's internal heater circuit heat sink is continuously monitored and used to initiate the automatic shutdown sequence when a heater fault is detected. This temperature may be queried using the SYSTEM:HTRHST command. 

#### **Query Syntax:** SYSTEM:HTRHST? 

Query Response: <temp> 

Where <temp> is the temperature of the internal heater output stage's heat sink in Celsius. 

#### **Query Example:** SYSTEM:HTRH? 

Example Response: +62C Indicates that the heat sink is at 62 ° C. 

#### **Short Form** : SYST:HTRH 

#### **SYSTEM:HOME: Display Operate Screen.** 

Causes the VFD display on the front panel to go to the Operate Screen. 

**Command Syntax:** SYSTEM:HOME 

**Command Example:** SYSTEM:HOME 

**Short Form** : SYST:HOME 

#### **SYSTEM:SYNCTAPS: Synchronous filter setup.** 

Sets or queries the number of taps in the synchronous filter. This is an advanced setup function. The default is 7 taps. 

**Command Syntax:** SYSTEM:SYNCTAPS <taps> 

Where <taps> is the number of taps. 

#### **Query Syntax:** SYSTEM:SYNCTAPS? 

Query Response: <taps> 

Where <taps> is number of taps used by the synchronous filter. 

#### **Query Example:** SYSTEM:SYNCTAPS? 

Example Response: 7 

#### **Short Form** : SYST:HTRH 

146 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:NAME Unit Name** 

The controller contains a unit name string that may be set or queried using this command. This can be used to assign a descriptive name to the instrument. 

Use the SYSTEM:ADRS command to assign a unique address. 

**Command Syntax:** SYSTEM:NAME <name> 

Where <name> is the desired system name string and is a maximum of 15 ASCII characters. 

#### **Command Example:** SYSTEM:NAME "Cryocooler Four" 

This assigns the name "Cryocooler Four" to the unit so that it may be uniquely identified. 

#### **Query Syntax:** SYSTEM:NAME? 

Query Response: <name> 

Where <name> is the temperature of the internal heater output stage's heat sink in Celsius. 

#### **Query Example:** SYSTEM:NAME? 

Example Response: Model 32 Unit 0 

#### **Short Form** : SYST:NAM 

#### **SYSTEM:HWREV: Instrument Hardware Revision Level** 

Queries the instrument’s hardware revision level. 

Query Syntax: SYSTEM:HWREV? 

Query Example: SYSTEM: HWREV? 

Example Response: A Indicating that the instrument’s hardware is revision level A. 

#### **Short Form** : SYST:HWR 

147 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:FWREV: Instrument Firmware Revision Level** 

Queries the instrument’s firmware revision level. 

**Query Syntax:** SYSTEM:FWREV? 

**Query Example:** SYSTEM:FWREV? Example Response: 3.18 Indicating that the instrument’s firmware is revision level 3.18. 

#### **Short Form** : SYST:FWR 

#### **SYSTEM:LINEFREQ: AC Power Line Frequency.** 

Sets or queries the AC Power Line frequency setting. 

#### **Command Syntax:** SYSTEM:LINEFREQ <freq> 

Where <freq> is the AC Power Line Frequency and may be either 50 or 60 for 50Hz or 60Hz. 

**Command Example:** SYSTEM:LINEFREQ 60 Sets the AC Power Line Frequency setting to 60 Hz. 

**Query Syntax:** SYSTEM: LINEFREQ? Query Response: <freq> Where <freq> is the line frequency setting **Query Example:** SYSTEM: LINEFREQ? Example Response: 50 

**Short Form** : SYST:LIN 

148 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM:DRES: Display Resolution.** 

Sets or queries the controller's display resolution. Choices are: 

FULL: The VFD will display temperature with the maximum possible resolution. 

- 1, 2 or 3: The VFD display will display the specified number of digits to the right of the decimal point. 

NOTE: This command only sets the number of digits displayed on the front panel VFD. It does NOT affect the internal accuracy of the instrument or the format of measurements reported on the remote interfaces. 

The main use for this command is to eliminate the flicker in low order digits when the controller is used in a noisy environment. 

**Command Syntax:** SYSTEM:DRES <res> 

Where <res> is the display resolution as follows: FULL, 1, 2, 3. 

#### **Command Example:** SYSTEM:DRES 2 

Causes the VFD display to show temperature with two digits to the right of the decimal point.. 

#### **Query Syntax:** SYSTEM:DRES? 

Query Response: <res> 

Where <res> is the display resolution 

#### **Query Example:** SYSTEM:DRES? 

Example Response: FULL 

**Short Form** : SYST:DRES 

149 

Remote Operation 

Model 32 / 32B User's Manual 

#### **SYSTEM: PUCONTROL: Power up in control mode** 

Sets or queries the controller's power up in control mode setting. 

Reference the section on power up in control mode. Default is OFF. 

- **Command Syntax:** SYSTEM:PUCONTROL <mode> Where <mode> is ON or OFF 

**Command Example:** SYSTEM: PUCONTROL OFF Causes the power up in control mode setting to select OFF. 

**Query Syntax:** SYSTEM:PUCONTROL? Query Response: <mode> Where <mode> is ON or OFF 

**Query Example:** SYSTEM:PUC? Example Response: OFF 

**Short Form** : SYST:PUC 

150 

Remote Operation 

Model 32 / 32B User's Manual 

#### CONFIG commands 

The CONFIG commands are used to save and restore any of the six available user instrument setups. Each setup contains the complete state of the controller. 

#### **CONFIG:NAME: User Setup Name** 

Instrument setups can be named for user convenience. The CONFIG:NAME command sets and queries the user configuration names. 

#### **Command Syntax:** CONFIG <ix>:NAME <name> 

Where <ix> is the index number of the desired instrument setup. Values may be 0 through 3. <name> is the desired name string and is a maximum of 15 ASCII characters. 

#### **Command Example:** CONFIG 3:NAME "Product Alpha" 

This assigns the name "Product Alpha" to instrument setup #3. 

#### **Query Syntax:** CONFIG <ix>:NAME? 

Query Response: <name> 

Where <name> is the temperature of the internal heater output stage's heat sink in Celsius. 

#### **Query Example:** CONFIG 0 NAME? 

Example Response: "Dewar Two" 

#### **Short Form** : CONFIG:NAM 

151 

Remote Operation 

Model 32 / 32B User's Manual 

#### **CONFIG:SAVE: Save User Configuration.** 

Saves an the current instrument setup to a user setup. 

#### **Command Syntax:** CONFIG <ix>:SAVE 

Where <ix> is the index number of the desired instrument setup. Values may be 0 through 5. 

#### **Command Example:** CONFIG 1:SAVE 

Saves the controller's current setup to user setup #1. 

#### **Short Form** : CONFIG:SAV 

#### **CONFIG:RESTORE: Restore User Configuration.** 

Restores a previously stored user instrument setup. 

**Command Syntax:** CONFIG <ix>:RESTORE 

Where <ix> is the index number of the desired instrument setup. Values may be 0 through 5. 

**Command Example** CONFIG 0:RESTORE 

Restores the controller's setup from user setup #0. 

#### **Short Form** : CONFIG:REST 

152 

Remote Operation 

Model 32 / 32B User's Manual 

#### INPUT commands 

The INPUT group of commands are associated with the configuration and status of the four input channels. 

INPUT may also be a stand alone query. 

Parameter references to the input channels may be: 

- Numeric ranging in value from zero to two. 

- Channel ID tags including CHA or CHB. 

- Alphabetic including A or B. 

#### **INPUT: Input Channel Temperature Query.** 

The INPUT query reports the current temperature reading on any of the input channels. 

Temperature is filtered by the display time constant filter and reported in display units. 

**Query Syntax:** INPUT ? <channel> 

Where <channel> is the input channel parameter. Query Response: <temp> 

Where <temp> is the temperature of the specified input channel in display units (K, F, C or S). Floating Point string. 

#### **Query Example:** INPUT? B 

Example Response: 123.4567 

**Alternate Form:** INPUT <channel>:TEMP? 

#### **Short Form:** INP 

153 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:TEMPER: Input Temperature.** 

The INPUT:TEMPER query is identical to the input query described above. It reports the current temperature reading on any of the input channels. 

Temperature is filtered by the display time constant filter and reported in display units. 

**Query Syntax:** INPUT <channel>:TEMPER? Where <channel> is the input channel parameter. Query Response: <temp> 

Where <temp> is the temperature of the specified input channel in display units (K, F, C or S). Floating Point string. 

**Query Example:** INP B:TEMP? 

Example Response: 12.45933 

**Short Form:** INP <channel>:TEMP? 

#### **INPUT:UNITS Input channel units** 

Sets or reports the display units of temperature used by the specified input channel. 

**Command Syntax:** INPUT <channel>:UNITS <units> 

Where <channel> is the input channel parameter and <units> is the display units indicator. 

<units> may be K for Kelvin, C for Celsius, F for Fahrenheit or S for primitive sensor units. In the case of sensor units, the instrument will determine if the actual units are Volts or Ohms based on the actual sensor type selected for the input channel. 

**Query Syntax:** INPUT <channel>:UNITS? 

Where <channel> is the input channel indicator. Query Response: <units> Where <units> is the display units indicator which will be K, C, F, V for Volts or O for Ohms. 

**Command Example:** INPUT B:UNITS F 

**Query Example:** INP A:UNIT? Example Response: K 

**Query Example:** INP A:TEMP?;UNIT? Example Response: 27.9906K 

#### **Short Form:** INP:UNIT 

154 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:SENPR: Input Reading in Sensor Units.** 

The INPUT:SENPR query reports the reading on a selected input channel. For diode and thermocouple sensors, the reading is in Volts while resistor sensors are reported in Ohms 

The reading is not filtered by the display time-constant filter. However, the synchronous input filter has been applied. 

**Query Syntax:** INPUT <channel>:SENPR? 

Where <channel> is the input channel parameter of A or B. Query Response: <rdg> 

Where <rdg> is the reading of the specified input channel in Ohms or Volts 

#### **Query Example:** INP B:SENPR? 

Example Response: 124.5933 meaning 124.5933 Ohms 

**Short Form:** INP <channel>:SENPR? 

#### **INPUT:VBIAS Input channel sensor bias voltage** 

Sets or queries the constant-voltage mode voltage used on the specified input channel. This value only applies to sensors that use constant-voltage excitation. They are indicated by a sensor type of ACR. 

If this query is used with a sensor type other than ACR, it will always return N/A for not applicable. 

**Command Syntax:** INPUT <channel>:VBIAS <volts> 

Where <channel> is the input channel parameter and <volts> is the bias voltage. Choices are: 

10mV – 10milliVolt. 3.3mV – 3.33milliVolt. 1mV – 1.0milliVolt. 

**Query Syntax:** INPUT <channel>:VBIAS? 

Where <channel> is the input channel indicator. Query Response: <volts> 

**Command Example:** INPUT B:VBIAS 3.3mV 

#### **Query Example:** INP A:VBias? 

Example Response: 1.0mV. Note: if the sensor on channel A is not a type ACR, the response will always be N/A. 

#### **Short Form:** INP:VBIAS 

155 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ISENIX Installed Sensor index** 

Sets or queries the sensor index number assigned to an input channel for factory installed sensors. 

Sensor index zero indicates that there is no sensor connected to the selected input channel. This will disable all readings on the channel. 

Refer to Appendix A for a description of sensors, indices etc. 

**Note:** The use of the ISENIX command to assign a factoryinstalled sensor and the USENIX command to assign a user sensor are preferred to the use of the obsolete SENIX command. 

The SENTYPE command may be used to query the name of a factory-installed sensor at a specific index. 

#### **Command Syntax:** INPUT <channel>:ISENIX <ix> 

Where <channel> is the input channel parameter and <ix> is the desired sensor index. 

#### **Query Syntax:** INPUT <channel>:ISENIX? 

Where <channel> is the input channel indicator. Query Response: <ix> 

Where <ix> is the sensor index for the selected input channel. If the index is invalid, a value of –1 will be returned. 

#### **Command Example:** INPUT B:SENIX 0 

This command sets the sensor index for input channel B to zero (disabled). 

#### **Query Example:** INP A:SENIX? 

Example Response: 02 

This indicates that sensor 02 is assigned to input channel A. The name of factory installed sensor 02 may be accessed using the SENTYPE commands. 

#### **Short Form:** INP:SEN 

156 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:USENIX User Sensor index** 

Sets or queries the sensor index number assigned to an input channel for user installed sensors. 

Refer to Appendix A for a description of sensors, indices etc. 

An index number of 0 through 3 indicates user sensor curves 0 through 3. 

**Note:** The use of the ISENIX command to assign a factory installed sensor and the USENIX command to assign a user sensor are <u>preferred to the use of the obsolete SENIX command.</u> 

The CALD command may be used to query information about the user installed sensor curves. 

**Command Syntax:** INPUT <channel>:USENIX <ix> 

Where <channel> is the input channel parameter and <ix> is the desired sensor index. 

**Query Syntax:** INPUT <channel>:USENIX? 

Where <channel> is the input channel indicator. Query Response: <ix> Where <ix> is the sensor index for the selected input channel. If the index is outside of the range 0 through 3, a value of –1 will be returned. 

#### **Command Example:** INPUT B:USENIX 0 

This command sets the sensor index for input channel B to zero (disabled). 

**Query Example:** INP A:USENIX? Example Response: 2 

This indicates that sensor 02 is assigned to input channel A. 

#### **Short Form:** INP:SEN 

157 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:SENIX Sensor index (obsolete)** 

Sets or queries the sensor index number assigned to an input channel. This command is used to assign the sensor type to a channel. Sensor types and configurations are accessed using the SENTYPE commands. 

Sensor index zero indicates that there is no sensor connected to the selected input channel. This will disable all readings on the channel. 

Refer to Appendix A for a description of sensors, indices etc. 

**Note:** To ensure portability of software written for the Model 32, you should use the ISENIX command to assign a factory installed sensor or USENIX to assign a user sensor. This way, the index will always correspond to the correct sensor regardless of the Model 32 firmware revision. 

**Command Syntax:** INPUT <channel>:SENIX <ix> 

Where <channel> is the input channel parameter and <ix> is the desired sensor index. 

#### **Query Syntax:** INPUT <channel>:SENIX? 

Where <channel> is the input channel indicator. Query Response: <ix> 

Where <ix> is the sensor index for the selected input channel. 

#### **Command Example:** INPUT B:SENIX 0 

This command sets the sensor index for input channel B to zero (disabled). 

#### **Query Example:** INP A:SENIX? 

Example Response: 02 

This indicates that sensor 02 is assigned to input channel A. The name and configuration of sensor 02 may be accessed using the SENTYPE commands. 

#### **Short Form:** INP:SEN 

158 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM?: Input Channel Alarm Status.** 

Queries the alarm status of the specified input channel. Status is a two character string where: 

|--|indicates that no alarms are asserted|
|---|---|
|SF|indicates a Sensor Fault condition.|
|HI|indicates a high temperature alarm|
|LO|indicates a low temperature alarm.|

There is a 0.25K hysteresis in the assertion of a high or low temperature alarm condition. 

The user selectable display time constant filter is applied to input channel temperature data before alarm conditions are tested. 

**Query Syntax:** INPUT <channel>: ALARM? 

Query Response: <alarm> 

Where <channel> is the input channel indicator and <alarm> is the alarm status indicators for that channel. 

#### **Query Example:** INP A:ALARM? 

Example Response: -- 

Which indicates that no alarm is asserted for input channel A. 

**Short Form:** INP <channel>:ALAR? 

159 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM:HIGHEST: Alarm High Setpoint.** 

Sets or queries the temperature setting of the high temperature alarm for the specified input channel. When this temperature is exceeded, an enabled high temperature alarm condition will be asserted. 

Temperature is assumed to be in the display units of the selected input channel. 

There is a 0.25K hysteresis in the assertion of a high or low temperature alarm condition. 

**Command Syntax:** INPUT <channel>:ALARM:HIGHEST <temp> 

Where <channel> is the input channel indicator and <temp> is the alarm setpoint temperature. . Temperature is a floating point string that may be up to 20 characters. 

**Query Syntax:** INPUT <channel>: ALARM:HIGHEST? 

Query Response: <temp> 

Where <channel> is the input channel indicator and <temp> is the temperature setting of the high temperature alarm for <channel>. Temperature is reported to the full precision of 32 bit floating point. 

**Command Example:** INP A:ALARM:HIGH 200.5 

Sets the high temperature alarm setpoint for input channel A to 200.5. 

**Query Example:** INP A:ALARM:HIGHEST? 

Example Response: 125.4321 

If the display units setting for input channel A are Kelvin, this response is also in units of Kelvin. 

**Short Form:** INP <channel>:ALAR:HIGH 

160 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM:LOWEST: Alarm Low Setpoint.** 

Sets or queries the temperature setting of the low temperature alarm for the specified input channel. When the input channel temperature is below this, an enabled low temperature alarm condition will be asserted. 

Temperature is assumed to be in the display units of the selected input channel. 

There is a 0.25K hysteresis in the assertion of a high or low temperature alarm condition. 

**Command Syntax:** INPUT <channel>:ALARM:LOWEST <temp> 

Where <channel> is the input channel indicator and <temp> is the alarm setpoint temperature. Temperature is a floating point string that may be up to 20 characters. 

**Query Syntax:** INPUT <channel>: ALARM:LOWEST? 

Query Response: <temp> 

Where <channel> is the input channel indicator and <temp> is the temperature setting of the low temperature alarm for <channel>. Temperature is reported to the full precision of 32 bit floating point. 

**Command Example:** INP A:ALARM:LOW 100.5 

Sets the low temperature alarm setpoint for input channel A to 100.5. 

#### **Query Example:** INP B:ALARM:LOW? 

Example Response: 25.43210 

If the display units setting for input channel B are Celsius, this response is also in units of Celsius. 

#### **Short Form:** INP <channel>:ALAR:LOW 

161 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM:HIENA: Alarm High Enable.** 

Sets or queries the high temperature alarm enable for the specified input channel. 

An alarm must be enabled before it can be asserted. 

#### **Command Syntax:** INPUT <channel>:ALARM:HIENA <status> 

Where <channel> is the input channel indicator and <status> is the status of the high temperature alarm enable. <status> may be either YES or NO. 

#### **Query Syntax:** INPUT <channel>: ALARM:HIENA? 

Query Response: <status> 

Where <channel> is the input channel indicator and <status> is the setting of the high temperature alarm enable for <channel>. <status> will be either YES or NO. 

#### **Command Example:** INPUT A:ALARM:HIENA NO 

Disables the high temperature alarm for input channel A. 

#### **Query Example:** INP B:ALARM:HIEN? 

Example Response: YES 

#### **Query / Command Example:** INP B:ALARM:HIGH?;HIEN NO 

Example Response: 154.2323 

The high temperature alarm setpoint for channel B is reported then the high temperature alarm for channel B is disabled. 

#### **Short Form:** INP <channel>:ALAR:HIEN 

162 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM:LOENA: Alarm Low Enable.** 

Sets or queries the low temperature alarm enable for the specified input channel. 

An alarm must be enabled before it can be asserted. 

**Command Syntax:** INPUT <channel>:ALARM:LOENA <status> Where <channel> is the input channel indicator and <status> is the status of the low temperature alarm enable. <status> may be either YES or NO. 

**Query Syntax:** INPUT <channel>: ALARM:LOENA? Where <channel> is the input channel indicator. 

#### Query Response: <status> 

Where <status> is the setting of the low temperature alarm enable for <channel>. <status> will be either YES or NO. 

**Command Example:** INPUT A:ALARM:LOENA YES 

Enables the low temperature alarm for input channel A. 

**Query Example:** INP B:ALARM:LOEN? Example Response: NO 

#### **Query Example:** INP B:ALARM:HIENA?;LOENA? 

Example Response: YES;NO 

The high temperature alarm enable for input channel B is reported followed by the low temperature alarm enable. 

#### **Short Form:** INP <channel>:ALAR:LOEN 

163 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM:FAULT: Alarm on Sensor Fault.** 

Sets or queries the sensor fault alarm enable for the specified input channel. 

An alarm must be enabled before it can be asserted. 

**Command Syntax:** INPUT <channel>:ALARM:FAULT <status> Where <channel> is the input channel indicator and <status> is the status of the sensor fault alarm enable. <status> may be either YES or NO. 

**Query Syntax:** INPUT <channel>: ALARM:FAULT? Where <channel> is the input channel indicator. 

- Query Response: <status> 

Where <status> is the setting of the sensor fault alarm enable for <channel>. <status> will be either YES or NO. 

- **Command Example:** INPUT A:ALARM:FAULT YES Enables the sensor fault alarm for input channel A. 

#### **Query Example:** INP B:ALARM:FAULT? 

Example Response: NO Indicating that the sensor fault alarm enable for channel B is disabled. 

#### **Query Example:** INP B:ALARM:HIENA?;LOENA?;FAULT? 

Example Response: YES;NO;NO 

Indicates that channel B high temperature alarm is enabled, low temperature alarm is disabled and sensor fault alarm is disabled. 

#### **Short Form:** INP <channel>:ALAR:FAUL 

164 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:ALARM:AUDIO: Audible Alarm Enable.** 

The Model 32 contains an audible alarm. This alarm may be optionally sounded when any alarm condition is asserted. 

The INPUT:ALARM:AUDIO command is used to set or query the audible alarm enable for the selected input channel. 

- **Command Syntax:** INPUT <channel>:ALARM:AUDIO <status> Where <channel> is the input channel indicator and <status> is the status of the audible alarm enable. <status> may be either YES or NO. 

#### **Query Syntax:** INPUT <channel>: ALARM:AUDIO? 

Where <channel> is the input channel indicator. 

#### Query Response: <status> 

Where <status> is the setting of the audible alarm enable for <channel>. <status> will be either YES or NO. 

#### **Command Example:** INPUT A:ALARM:AUDIO YES 

Enables the audible alarm for input channel A alarm conditions. 

- **Command Example:** INPUT A:ALARM:HIEN OFF;AUDIO OFF 

This command will disable the high temperature alarm and disable the audio alarm for input channel A. 

**Query Example:** INP B:ALARM:AUDIO? Example Response: NO 

#### **Short Form:** INP <channel>:ALAR:AUD? 

Where AUDIO can be truncated to four characters, then to three characters because the fourth character is a vowel. 

165 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:MINIMUM: Statistical Minimum.** 

Queries the minimum temperature that has occurred on an input channel since the STATS:RESET command was issued. 

**Query Syntax:** INPUT <channel>: MINIMUM? Where <channel> is the input channel indicator. 

Query Response: <temp> Where <temp> is the minimum temperature. 

**Query Example:** INP B:MIN? Example Response: 90.2322 

**Short Form:** INP <channel>:MIN? 

#### **INPUT:MAXIMUM MAXIMUM Statistical Maximum.** 

Queries the Maximum temperature that has occurred on an input channel since the STATS:RESET command was issued. 

**Query Syntax:** INPUT <channel>: MAXIMUM? 

Where <channel> is the input channel indicator. 

Query Response: <temp> Where <temp> is the maximum temperature. 

#### **Query Example:** INP B:MAX? 

Example Response: 90.2322 

**Short Form:** INP <channel>:MAX? 

166 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:VARIANCE: Statistical Variance.** 

Queries the temperature variance that has occurred on an input channel since the STATS:RESET command was issued. 

Variance is calculated as the Standard Deviation squared. 

**Query Syntax:** INPUT <channel>: VARIANCE? Where <channel> is the input channel indicator. 

Query Response: <temp> Where <temp> is the statistical variance of temperature. 

**Query Example:** INP B:VAR? 

Example Response: 1.2223 

**Short Form:** INP <channel>:VAR? 

#### **INPUT:SLOPE: Slope of best-fit straight line.** 

Queries the input channel statistics. SLOPE is the slope of the best fit straight line passing through all temperature samples that have been collected since the STATS:RESET command was issued. 

SLOPE is in degrees per Minute. 

**Query Syntax:** INPUT <channel>: SLOPE? Where <channel> is the input channel indicator. 

Query Response: <temp> Where <temp> is the temperature slope. 

**Query Example:** INP B:SLOPE? Example Response: 1.2323 

**Short Form:** INP <channel>:SLOP? 

167 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INPUT:OFFSET: Offset of best-fit straight line.** 

Queries the input channel statistics. OFFSET is the offset of the best fit straight line passing through all temperature samples that have been collected since the STATS:RESET command was issued. 

OFFSET is in degrees. 

**Query Syntax:** INPUT <channel>: OFFSET? Where <channel> is the input channel indicator. 

Query Response: <temp> Where <temp> is the temperature offset. 

**Query Example:** INP B: OFFSET? Example Response: 124.25 

**Short Form:** INP <channel>:OFFS? 

#### **INPUT:TIME? Accumulation time** 

Queries the time duration over which input channel statistics have been accumulated. 

TIME is reset by issuing the INPUT:RESET command. 

**Query Syntax:** INPUT <channel>:TIME? 

Where <channel> is the input channel indicator. 

Query Response: <time> 

Where <time> is the time, in Seconds, that has elapsed since the channel statistics were reset. 

#### **Query Example:** INPUT A:TIME? 

Example Response: 232 Indicating 232 seconds have elapsed. 

#### **Short Form: INP** :TIM? 

#### **INPUT:RESET Reset Statistics** 

Resets the accumulation of input channel statistical data. 

**Command Syntax:** INPUT <channel>:RESET 

Resets the accumulation of input channel statistics. 

**Command Example:** INPUT <channel>:RESET 

**Short Form:** INP:RES 

168 

Remote Operation 

Model 32 / 32B User's Manual 

#### LOOP commands 

Loop commands are used to configure and monitor Model 32’s control loops. 

Note: LOOP 1 may also be referred to as HEATER and LOOP 2 may be referred to as LOOP #2. 

Loop 1 is the controller’s primary heater output channel. In the Model 32 and 32B, this is a 50/25 Watt, three range linear heater. 

Loop 2 is a secondary output. In the Model 32, this is a 0-5V voltage output that can drive a strip-chart recorder or a booster power supply. Loop 2 of the Model 32B is a 10 Watt, single range linear heater. 

#### **LOOP:SOURCE: Control loop Source Input Channel.** 

Sets and queries the selected control loop's controlling input channel. 

**Command Syntax:** LOOP <no>:SOURCE <chan> 

Where <no> is the loop number, 1 or 2, and <chan> is the designator of the controlling input channel. 

**Query Syntax:** LOOP <no>::SOURCE? 

Query Response: <chan> 

Where <chan> is the designator of the controlling input channel. 

#### **Command Example:** LOOP 1:SOUR CHA 

Sets the control loop feedback loop to be controlled by input channel A. 

**Command Example:** LOOP 1:SOUR CHB;SETPT 123.4;PGAIN 120 

This command will set control loop 1’s setpoint to 123.4, the proportional gain term to 120 and the control input channel to B. 

#### **Query Example:** LOOP 2:SOURCE? 

Example Response: CHB 

Which indicates that the control loop 2 is being controlled by input channel B. 

#### **Short Form:** LOOP:SOUR 

169 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:SETPT: Control loop Setpoint.** 

Sets and queries the selected control loop’s setpoint. This is a numeric value that has units determined by the display units of the controlling input channel. 

#### Allowed values are 0K to 1000K. 

**Command Syntax:** LOOP <no>:SETPT <temp> 

Where <no> is the loop number, 1 or 2, and <temp> is the desired setpoint. 

#### **Query Syntax:** LOOP 1:SETPT? 

Query Response: <temp> Where <temp> is the setpoint temperature in units of the controlling input channel. 

#### **Command Example:** LOOP 1:SETPT 100.4 

Sets loop 1’s setpoint to 100.4. If the controlling input channel units are Kelvin, this command will result in a setpoint of 100.4K. 

#### **Multiple Command Example:** LOOP 2:SETPT 123.4;PGAIN 120 

This command will set the loop 2 setpoint to 123.4 and the proportional gain term to 120. 

#### **Query Example:** LOOP 1:SETPT? 

Example Response: 143.1293 

#### **Short Form:** LOOP:SETP 

170 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:TYPE: Control loop Control Type.** 

Sets and queries the selected control loop’s control type. Allowed values are: 

**Off** - loop disabled **PID** - loop control type is PID **Man** - loop is manually controlled **Table** - loop is controlled by PID Table lookup. **RampP** - loop is controlled by PID, but is in ramp mode. 

#### **Command Syntax:** LOOP <no>:TYPE <type> 

Where <no> is the loop number, 1 or 2, and <type> is the loop’s control type from the above list. 

#### **Query Syntax:** LOOP <no>:TYPE? 

Query Response: <type> Where <type> is the loop type from the above list. 

#### **Command Example:** LOOP 1:TYPE PID 

Sets the loop 1 control mode to PID. 

#### **Query Example:** LOOP 1:TYPE? 

Example Response: TABLE Which indicates that the Loop 1 is controlling based on PID Table lookup. 

#### **Short Form:** LOOP:TYPE 

171 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:TABLEIX: Control loop PID Table number** 

Sets and queries the number of the PID table used when controlling in **Table** mode. Six PID tables are available to store PID parameters vs. setpoint. 

**Command Syntax:** LOOP <no>:TABLEIX <number> Where <no> is the loop number, 1 or 2, and <number> is the loop’s control PID table number. 

**Query Syntax:** LOOP <no>:TABLEIX? Query Response: <number> Where <number> is the PID table number. 

**Command Example:** LOOP 1:TABLEIX 5 Sets the loop 1 PID table to table number 5. 

#### **Query Example:** LOOP 1:TABLE? 

Example Response: 3 Which indicates that the Loop 1 is controlling based on PID Table number 3. 

#### **Short Form:** LOOP:TYPE 

172 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP 1:RANGE: Control Loop 1 Output Range.** 

Sets or queries the control loop #1, or the primary heater, output range. 

Range determines the maximum output power available and is different for a 50 Ω load resistance than for a 25 Ω load. 

Values of heater range are: Hi, Mid and Low. These correspond to the output power levels shown here. 

|**Range**|**50**Ω**Load**|**25**Ω**Load**|
|---|---|---|
|**Hi**|50W|25W|
|**Mid**|5W|2.5W|
|**Low**|0.5W|0.25W|

**Command Syntax:** LOOP 1:RANGE 

<range> 

Where <range> is the desired heater output range from the above list. 

**Query Syntax:** LOOP 1:RANGE? 

Query Response: <range> 

**Command Example:** LOOP 1:RANGE LOW 

Sets the heater power output range to Low. 

**Query Example:** LOOP 1:RANGE? Example Response: Hi 

**Short Form:** LOOP:RANG 

173 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:RAMP?: Control Loop Ramp Status.** 

Queries the unit to determine if a temperature ramp is in progress on the specified control loop. 

Note that temperature ramps on the Loop 1 and Loop 2 channels are independent of each other. 

**Command Syntax:** N/A 

**Query Syntax:** LOOP <no>:RAMP? 

Where <no> is the loop number, 1 or 2. 

Query Response: ON or OFF. 

**Query Example:** LOOP 2:RAMP? Example Response: OFF 

#### **Short Form:** LOOP:RAMP 

#### **LOOP:RATE: Control Loop Ramp Rate.** 

Sets and queries the ramp rate used by the selected control loop when performing a temperature ramp. Rate is in Units per Minute. 

**Command Syntax:** LOOP <no>:RATE <Value> 

Where <no> is the loop number, 1 or 2, and <Value> is the ramp rate in Units / Minute. This may be a value between 0 and 100. 

#### **Command Example:** LOOP 1:RATE 0.02 

This will set the loop 1 temperature ramp rate to 0.02. If the controlling input channel has units of Kelvin, the heater rate will be set to 0.02K/min. 

**Query Syntax:** LOOP <no>:RATE? Query Response: <Value> 

#### **Query Example:** LOOP 2:RATE? 

Example Response: 0.0100 

#### **Short Form:** LOOP:RAMP 

174 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:PGAIN: Control Loop Proportional Gain term.** 

Sets or queries the selected control loop’s proportional gain term. This is the P term in PID and is a unit-less numeric field with values between 0 (off) and 1000. 

The P gain term is applied to the control loop when controlling in a PID mode. 

- **Command Syntax:** LOOP <no>:PGAIN <value> Where <no> is the loop number, 1 or 2, and <value> is the desired P term for the control loop. 

- **Query Syntax:** LOOP <no>:PGAIN? Query Response: <value> 

- **Command Example:** LOOP 1:PGAIN 123 Sets the heater P term to 123 

**Query Example:** LOOP 1:PGAIN? Example Response: 0.49723 

#### **Short Form:** LOOP:PGA 

#### **LOOP:IGAIN: Control Loop Integral Gain term.** 

Sets and queries the integrator gain term used by the selected control loop. This is a numeric field with units of seconds. Allowed values are 0 (off) through 1000 seconds. 

The integrator gain term is applied to the selected control loop when controlling in a PID mode. 

- **Command Syntax:** LOOP <no>:IGAIN <value> 

Where <no> is the loop number, 1 or 2, and <value> is the desired Integral Gain term for the control loop in seconds. 

**Query Syntax:** LOOP <no>:IGAIN? Query Response: <value> 

**Command Example:** LOOP 1:IGAIN 12.422 Sets the Loop 1 integrator feedback term to 12.422 Seconds. 

**Query Example:** LOOP 2:IGAIN? Example Response: 18.23 Indicates that the Loop 2 channel I feedback term is 18.23 Seconds. 

#### **Short Form:** LOOP:IGA 

175 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:DGAIN: Control Loop Derivative Gain term.** 

Sets and queries the differentiator gain term used by the selected control loop. This is a numeric field with units of inverse seconds. Allowed values are 0 (off) through 1000/Seconds. 

The D gain term is applied to the selected control loop when controlling in a PID mode. 

Note: Use of the D gain term can add significant noise. In most cryogenic applications, it is set to zero. 

#### **Command Syntax:** LOOP <no>:DGAIN <value> 

Where <no> is the loop number, 1 or 2, and <value> is the desired D term for the selected control loop in inverse Seconds. 

**Query Syntax:** LOOP <no>:DGAIN? 

Query Response: <value> 

**Command Example:** LOOP 1:DGAIN 4.3 

Sets control loop 1 differentiator feedback term to 4.3/Seconds. 

#### **Query Example:** LOOP 1:DGAIN? 

Example Response: 8.23 Indicates that the D feedback term for loop 1 is 8.23/Seconds. 

#### **Short Form:** LOOP:DGA 

#### **LOOP:OUTPWR: Control loop Output Power.** 

Queries the output power of the selected control loop. This is a numeric field that is a percent of full scale. 

#### **Query Syntax:** LOOP <no>:OUTPWR? 

Where <no> is the loop number, 1 or 2. Query Response: <value> 

Where <value> is the selected control loop output power setting in percent. 

#### **Query Example:** LOOP 2:OUTP? 

Example Response: 75.000 

Indicates that the control loop 2 is attempting to output 75% of full scale power. 

#### **Short Form:** LOOP:OUTP 

176 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:HTRREAD?: Heater read back current.** 

Queries the actual output power of either control loop. 

The output current of the heaters in the Model 32 is continuously monitored by an independent read-back circuit. Read-back power will be reported as a percent of full scale. The absolute value of full scale is determined by the selected heater range as shown in this table. 

Note that the read-back value is a percent of fullscale power. To compute the output current, you must first compute the square-root of the readback value. 

|<br>scale power. To compute the output current, you<br>must first compute the square-root of the read-|**Heater Range**|**Full Scale**<br>**Current**|
|---|---|---|
|<br>back value.|**50 / 25 Watt**|1.0A|
||**5 / 2.5 Watt**|0.333A|
|When using the second control loop of the Model<br>32B, the read-back value is always a percentage<br>of 10 Watts.|**0.5 / 0.25 Watt**|0.1A|

#### **Query Syntax:** LOOP <no>:HTRREAD? 

Where <no> is the loop number, 1 or 2. Query Response: <current> 

Where <current> is the heater output current as a percent of full scale. 

#### **Query Example:** LOOP 1:HTRR? 

Example Response: 33% 

Indicates that the heater output current has been measured at 33% of full scale by the heater read-back circuit. If the heater’s maximum output power is 50 Watts, the output power is 50 * 0.33 = 16.5 Watts. This corresponds to an output current of 1.0A * sqrt(0.33) = 0.57A 

#### **Short Form** : LOOP:HTRR 

177 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP 1:LOAD: Heater Load Resistance Select.** 

Sets or queries the load resistance setting of the primary heater (Loop 1). Selections are: 

50 for a 50 Ω load and a 50W maximum output power. 25 for a 25 Ω load and a 25W maximum output power. 

Note: Loop 2 of the Model 32B controller always assumes a 50 Ω load. 

**Command Syntax:** LOOP 1:LOAD <load> Where <load> is the desired resistance of the selected control loop load from the above list. 

**Query Syntax:** LOOP 1:LOAD? Query Response: <LOAD> 

**Command Example:** LOOP 1:LOAD 50 Sets the primary heater output for a 50 Ω load. 

**Query Example:** LOOP 1:LOAD? Example Response: 25 

**Short Form:** LOOP:LOAD 

178 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP : MAXPWR: Heater Maximum Output Power.** 

Sets or queries the maximum output power setting of the selected control loop. 

Please refer to the discussion on maximum output power in the Control Loop Setup Menu section. 

**Command Syntax:** LOOP <no>:MAXPWR <MaxPwr> 

Where <no> is the loop number and <MaxPwr> is the desired maximum output power limit expressed as a percentage of full scale. 

**Query Syntax:** LOOP <no>::MAXPWR? Query Response: <MaxPwr> 

**Command Example:** LOOP 1:MAXPWR 50 

Sets the maximum output power limit on loop 1 to 50% of full scale. 

**Query Example:** LOOP 1:MAXPWR? Example Response: 25 

#### **Short Form:** LOOP:MAXP 

#### **LOOP : MAXSET: Control Loop Maximum Setpoint.** 

Sets or queries the maximum allowed set point for the selected control loop. 

Please refer to the discussion on Maximum Setpoint in the Control Loop Setup Menu section. 

Setpoint units are the currently selected display units for the controlling input channel. 

**Command Syntax:** LOOP <no>:MAXSET <MaxSet> 

Where <no> is the loop number and <MaxSet> is the desired maximum set point. 

**Query Syntax:** LOOP <no>::MAXSET? Query Response: <MaxSet> 

**Command Example:** LOOP 1:MAXSET 300 

Sets the maximum allowed setpoint on Loop 1 to 300. 

**Query Example:** LOOP 1:MAXSET? Example Response: 250 

#### **Short Form:** LOOP:MAXS 

179 

Remote Operation 

Model 32 / 32B User's Manual 

#### **LOOP:PMANUAL: Control Loop Manual Power Output Setting.** 

Sets and queries the output power level used by the selected control loop feedback when it is in Manual control mode. This value may be changed at any time, but is only used during Manual operation. 

PMANUAL is a numeric field that is a percent of full scale selected control loop output current. Actual selected control loop output power will depend on the selected control loop range setting. 

#### **Command Syntax:** LOOP <no>:PMANUAL <value> 

Where <no> is the loop number, 1 or 2, and <value> is the desired selected control loop output current as a percent of full scale. 

#### **Query Syntax:** LOOP <no>:PMANUAL? 

Query Response: <value> 

Where <value> is the desired output power as a percent of full scale. 

#### **Command Example:** LOOP 1:PMAN 50 

Sets the control loop 1’s output power to 50% of full scale when the loop is in manual control mode. 

#### **Query Example:** LOOP 1:PMAN? 

Example Response: 25.000 Indicates that loop 1 has a manual output power setting of 25%. 

#### **Short Form:** LOOP:PMAN 

180 

Remote Operation 

Model 32 / 32B User's Manual 

#### OVERTEMP commands 

These commands are associated with the heater’s Over Temperature Disconnect feature. 

This feature is used to disconnect the heater if a specified temperature is exceeded on a selected input channel. 

#### **OVERTEMP:ENABLE: OTD Enable.** 

Sets and queries the over temperature disconnect enable. 

**Command Syntax:** OVERTEMP:ENABLE <enab> 

Where <enab> is the desired enable status, which may be ON or OFF. 

#### **Query Syntax:** OVERTEMP:ENABLE? 

Query Response: <enab> Where <enab> is the status of the over temperature disconnect enable. 

#### **Command Example:** OVERTEMP:ENABLE OFF 

Sets the over temperature disconnect feature to OFF. 

#### **Query Example:** OVERTEMP:ENABLE? 

Example Response: YES Indicating that the over temperature disconnect feature is enabled 

#### **Short Form:** OVER:ENAB 

181 

Remote Operation 

Model 32 / 32B User's Manual 

#### **OVERTEMP:SOURCE: OTD Source Input Channel.** 

Sets and queries the input channel that is used as the source for the Over Temperature Disconnect feature. 

**Command Syntax:** OVERTEMP:SOURCE <chan> Where <chan> is the designator of the controlling input channel. 

#### **Query Syntax:** OVERTEMP:SOURCE? 

Query Response: <chan> Where <chan> is the designator of the input channel. 

#### **Command Example:** OVER:SOUR A 

Sets the over temperature disconnect to monitor channel ChA. 

#### **Query Example:** OVERTEMP:SOURCE? 

Example Response: CHB 

Which indicates that the over temperature disconnect is set to monitor input channel ChB. 

#### **Short Form:** OVER:SOUR 

#### **OVERTEMP:TEMP: OTD Maximum Temperature.** 

Sets and queries the temperature used by the over temperature disconnect feature. 

Note that this temperature has the same units of the source input channel. 

#### **Command Syntax:** OVERTEMP:TEMP <temp> 

Where <temp> is the desired temperature. 

#### **Query Syntax:** OVERTEMP:TEMP? 

Query Response: <temp> Where <temp> is the setpoint temperature in units of the controlling input channel. 

#### **Command Example:** OVER:TEMP 123.4 

Sets the over temperature disconnect to trip when a temperature of 123.4 is exceeded.. 

#### **Query Example:** OVERTEMP:TEMP? 

Example Response: 54.23 

Which indicates that the over temperature disconnect is set to a temperature of 54.23. 

#### Short Form: OVER:TEMP 

182 

Remote Operation 

Model 32 / 32B User's Manual 

#### CALCUR commands 

The CALCUR commands are used to transfer sensor calibration curves between the controller and the host controller. 

Curves are referenced by an index number. In the Model 32, there are four user curves numbered 1 through 4. In the Model 34 and 62, there are 12 user curves, numbered 1 through 12. 

The CALCUR data block consists of a header, multiple curve entries and a terminator character. 

The header consists of four lines as follows: 

Sensor Name: Sensor name string, 15 characters max Sensor Type: Enumeration, See Sensor Types table Multiplier: Signed numeric Units: Units of calibration curve: OHMS, VOLTS or LOGOHM 

Each entry of a curve contains a sensor reading and the corresponding temperature. Sensor readings are in units specified by the units of the curve using the CALDATA:UNITS command. These units may be OHMS, VOLTS or LOGOHM. Temperature is always in Kelvin. 

The format of an entry is: 

<sensor reading> <Temperature> 

Where <sensor reading> is a floating-point sensor reading and <Temperature> is a floating-point temperature in Kelvin. 

Numbers are separated by one or more white spaces. 

**NOTE:** Using the RS-232 interface, each line must be terminated by a New Line, a Carriage Return, a Line Feed or a Null character. This character is not used with the GPIB interface since the end of a line is signaled by the interface itself. Here, lines are transmitted to the controller by using sequential write commands. 

Floating point numbers may be entered with many significant digits. They will be converted to 32 bit floating point. This supports about six significant digits. 

The last entry of a table is indicated by a semicolon (;) character with no values in the numeric fields. 

**NOTE:** All curves must have a minimum of two entries and a maximum of 200 entries. 

Entries may be sent to the controller in any order. The unit will sort the curve in ascending order of sensor reading before it is copied to Flash RAM. 

Entries containing invalid numeric fields will be deleted before they are stored. 

183 

Remote Operation 

Model 32 / 32B User's Manual 

The following is an example of a calibration curve transmitted to the controller via the GPIB interface: 

CALCUR 1 Good Diode Diode –1.0 volts 0.34295   300.1205 0.32042   273.1512 0.35832   315.0000 1.20000   3.150231 1.05150   8.162345 0.53234   460.1436 ; 

The controller would sort the above table in ascending order of volts, then write it to FLASH memory as user curve #1. The curve name will be "Good Diode" and the native units are volts. 

When a complete curve is received, it is conditioned, sorted and copied to FLASH memory. This process can take as long as 250 milliseconds with a long table. 

 **Note:** When using the RS-232 interface, a time delay should of about 500mS should be inserted after sending the last line of a calibration table. This will allow the flash memory update to complete. Other remote interfaces do not require a delay. 

 **Note:** Factory installed calibration curves may not be changed or deleted with these commands. 

184 

Remote Operation 

Model 32 / 32B User's Manual 

#### **CALCUR: Calibration Curve Set or Query.** 

Sets or queries sensor calibration curve data. 

**Command Syntax:** 

CALCUR <index> <sensor name> <sensor type> <multiplier> <curve units> <sensor reading 1> <Temperature 1> <sensor reading 2> <Temperature 2> • <sensor reading N> <Temperature N> ; 

 **Note:** A new line (\n) character must be appended to each line when using the RS-232 serial port. They should not be included when using the GPIB interface. 

The maximum number of entries in a curve is 200 and the minimum is 2. 

<index> is a numeric index to the user calibration curve list. Values are 1 through 4 in the Model 32 and 1 through 12 in the Model 34 and 62. 

<curve name> is a name to be assigned to the calibration curve. It is a minimum of 4 and a maximum of 15 ASCII characters. 

<sensor type> is from the following list: Diode, ACR, 31kR, 3.1kR, 312R, 625R, TC80, TC40 and None. If the sensor type cannot be identified, Diode is used. Sensor Types are described in the section on Supported Sensor Configurations above. 

<multiplier> is the temperature coefficient and curve multiplier. If this field cannot be identified, a value of –1.0 is assumed. This field is described in the section Sensor Setup Menu above. 

<curve units> is the units of the curve. Choices are OHMS, VOLTS or LOGOHM. 

The last entry in a calibration curve must be a single semicolon. 

**Query Syntax:** CALCUR? <index> 

Query Response: <calibration curve> 

Short Form: CALC 

185 

Remote Operation 

Model 32 / 32B User's Manual 

#### PIDTABLE commands 

The PIDTABLE commands are used to transfer PID tables between the Model 32 and the host controller. 

PID Tables are referenced by their index number, which is between 0 and 5. Table data corresponding to a specific index may be identified using the PIDTABLE? query. There is a maximum of 16 entries in each PID table. Each entry contains a setpoint, P, I and D coefficients and a heater range. 

Either output channel may use any table. 

The heater range field only applies to Loop #1. However, it must be specified in each entry. 

The format of an entry is: 

<setpoint> <P> <I> <D> <Heater Range> 

Fields are separated by a white space. The entry is terminated by a new line (\n) character if the table is transmitted via the RS-232 interface and is not terminated for all others. 

Floating point numbers may be entered with many significant digits. They will be converted to 32 bit floating point, which supports about six significant digits. 

The heater range is an enumeration field that may have the following values: 

Hi, Mid and Low 

The file format of a PID table is shown below: 

<name> <entry 0> <entry 1> * * * <entry N> ; 

Where: 

<name> is the name of the table and is a maximum of 16 ASCII characters. <entry> is a PID entry. 

A line that contains only a single semicolon indicates the end of the table. 

186 

Model 32 / 32B User's Manual 

Remote Operation 

|An example of a sixte|en entry PI|D Table is as follows:|
|---|---|---|
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||

 

Entries may be sent to the Model 32 in any order. The unit will sort the table in ascending order of setpoint before it is copied to Flash RAM. Entries containing invalid numeric fields will be deleted. 

187 

Remote Operation 

Model 32 / 32B User's Manual 

#### **PIDTABLE: PID Table Name Query.** 

Queries the name string of a PID table at a specified index. 

#### **Query Syntax:** PIDTABLE? <index> 

Query Response: <name> Where <index> is the index to the PID table list and <name> is the name string associated with the specified table. Index may be from zero to five. 

#### **Query Example:** PIDT? 2 

Example Response: Joe's Cooler Indicates that PID table #2 is named Joe's Cooler. 

#### **Short Form:** PIDT? 

#### **PIDTABLE:NAME: PID Table Name.** 

Sets or queries the name string of the PID Table at a specified index. 

The name string is used to associate a convenient name with a PID table. It may include up to 15 ASCII characters. 

#### **Command Syntax:** PIDTABLE <index>:NAME <name> 

Where <index> is a numeric index (0-3) to the PID table list and <name> is an ASCII name string in double quotes. 

#### **Query Syntax:** PIDTABLE <index>:NAME? 

Query Response: <name> 

Where <index> is the index to the calibration curve list. <name> is the name string associated with the specified curve. 

#### **Command Example:** PIDTABLE 1:NAME "Ed's table" 

This command will assign the name of "Ed's table" to PID table located at index number 1. 

#### **Query Example:** PIDTABLE 3:NAME? 

Example Response: Mary's project Indicates that the PID table at index 3 is named Mary's project. 

#### **Short Form:** PIDT:NAM 

188 

Remote Operation 

Model 32 / 32B User's Manual 

#### **PIDTABLE:NENTRY: Number of Entries.** 

Queries the number of entries in a PID Table. This number is generated from the table itself and cannot be changed using this command. 

The maximum number of entries in a table is 16. 

**Query Syntax:** PIDTABLE <index>:NENTRY? 

Query Response: <number> 

Where <index> is the index to the PID table list and <number> is the number of entries in the indexed table 

**Query Example:** PIDTABLE 1:NENTRY? 

Example Response: 5 Indicates that there are 5 entries in PID table 1. 

**Short Form:** PIDT:NENT 

#### **PIDTABLE:TABLE: PID Table Set/Query.** 

Sets or queries the entries in a PID table. 

#### **Command Syntax:** 

PIDTABLE <index>:TABLE 

<name> <setpoint> <P> <I> <D> <Heater Range> <setpoint> <P> <I> <D> <Heater Range> <setpoint> <P> <I> <D> <Heater Range> 

• • 

• 

<setpoint> <P> <I> <D> <Heater Range> ; 

Where <index> is a numeric index of the PID table and <name> is the table name (15 characters maximum). Table entries are made according to the above description. 

Fields within an entry are separated by one or more white space characters. The last entry in a calibration curve must be a single semicolon. 

**Query Syntax:** PIDTABLE <index>:TABLE 

Query Response: <Table entries> 

Where <Table entries> are the entries of the selected PID table. 

189 

Remote Operation 

Model 32 / 32B User's Manual 

#### CALDATA and SENTYPE Commands 

The CALDATA commands are used to add, delete or edit user-installed sensors. These commands are the remote equivalent of the front panel Sensor Setup menu. 

SENTYPE commands are used to query the name of a factory-installed sensor. 

User-installed sensors are indexed from zero to 3.  Factory installed sensors are indexed from zero to 60. For additional information, refer to Appendix A. 

#### **CALDATA:NAME: Name for a user-installed sensor.** 

Sets or queries the name of a user-installed sensor. 

#### **Command Syntax:** CALDATA <index>:NAME <val> 

Where <index> is the index of the user-installed sensor and <val> the sensor’s name string. The name string must be surrounded with double-quotation (“) marks. 

#### **Query Syntax:** CALDATA <index>:NAME? 

Query Response: <name> 

Where <index> is the index of the user-installed sensor and <name> is the name string for the indexed sensor. 

#### **Query Short Form:** CALD? <index> 

Where <index> is the index of the user-installed sensor and <val> the sensor’s name string. 

#### **Query Example:** CALDATA 3:NAME? 

Example Response: “User Curve 2”. 

#### **Short Form:** CALD? 

#### **SENT:NAME: Name for a factory-installed sensor.** 

Queries the name of a factory-installed sensor. 

#### **Query Syntax:** SENT <index>:NAME? Or SENT? <index> 

Query Response: <name> 

Where <index> is the index of the factory-installed sensor and <name> is the name string for the indexed sensor. 

#### **Query Example:** SENT? 1 

Example Response: “Cryocon S700”. 

#### **Short Form:** SENT? 

190 

Remote Operation 

Model 32 / 32B User's Manual 

#### **CALDATA:TYPE: Sensor Type.** 

Sets or queries the sensor type at a Sensor Table index. 

Supported sensor types are described above in the "Supported Sensors" section. 

**Command Syntax:** CALDATA <index>:TYPE <stype> Where <index> is the index to the user-installed sensor and <stype> the sensor type selected from the above list. 

**Query Syntax:** CALDATA <index>:TYPE? Query Response: <stype> Where <index> is the index and <stype> is the sensor type. 

**Command Example:** SENT 3:TYPE DIODE 

This command assigns the Silicon Diode sensor type to the user-installed sensor at index 3. 

**Query Example:** CALDATA 1:TYPE? Example Response: TC80 This response indicates that the sensor at index 1 is a thermocouple. 

#### **Short Form:** CALD:TYP 

191 

Remote Operation 

Model 32 / 32B User's Manual 

#### **CALDATA:MULTIPLY: Calibration Curve Multiplier.** 

Sets or queries the Multiplier field for a user-installed sensor. 

The multiplier field is a floating-point numeric entry and is used to specify the sensor's temperature coefficient and to scale the calibration curve. Negative multipliers imply that the sensor has a negative temperature coefficient. The absolute value of the multiplier scales the calibration curve. For example, the curve for a Platinum sensor that has 100 Ω of resistance at 0 ° C may be used with a 1000 Ω sensor by specifying a multiplier of 10.0. 

Default is 1.0 for sensors with a positive temperature coefficient and –1.0 for a negative coefficient. 

#### **Command Syntax:** CALDATA <index>:MULTIPLY <val> 

Where <index> is the index to user installed sensor (0 through 3) and <val> the multiplier. 

<index> is an integer and <val> is floating point with a range of ± 100.0. 

**Command Example:** CALD 1:MULT –10.1 

This command sets the calibration table multiplier for user-installed sensor 1 to 

–10.1 and identifies it as having a negative temperature coefficient. 

#### **Query Syntax:** CALDATA <index>:MULTIPLY? 

Query Response: <val> 

Where <index> is the index and <val> is the sensor type multiplier. 

#### **Query Example:** CALD 2:MULT? 

Example Response: 1.000000 

This response indicates that the sensor at index 2 has a positive temperature coefficient and a calibration curve multiplier of 1.0. 

#### **Short Form:** CALD:MULT 

192 

Remote Operation 

Model 32 / 32B User's Manual 

#### AUTOTUNE commands 

Autotuning via the remote interface requires the following sequence: 

1. The Model 32 must be controlling temperature and the loop must be stable in terms of both temperature and output power. 

2. Values for Delta Power and Timeout should be set. 

3. The Autotune process model is initiated by the command AUTOTUNE:START. 

4. Status can be monitored using the AUTOTUNE:STATUS command. 

5. When a status of complete is indicated, the generated values for P,I and D may be read. 

6. Execution of the AUTOTUNE:SAVE command will transfer the generated PID coefficients to the actual loop coefficients and continue controlling the process in PID mode. 

7. Execution of the AUTOTUNE:EXIT command at any time will abort the autotune process and discard any generated PID values. 

Refer to the section on autotuning for information about this process. 

193 

Remote Operation 

Model 32 / 32B User's Manual 

#### **AUTOTUNE:DELTAP: Maximum Delta in Power.** 

Sets and queries the maximum allowed change in heater output power that is allowed during the process modeling phase of the autotuning process. 

This a numeric field that is expressed as a percent of full scale heater output power. The actual power output depends on the range setting of the heater. If a value of 100% is used, the controller may use any output power within the current range. 

#### **Command Syntax:** <oc>:AUTOTUNE:DELTAP <value> 

Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 2. <value> is the maximum allowed change in output power expressed as a percent of full scale. 

#### **Query Syntax:** <oc>:AUTOTUNE:DELTAP? 

Query Response: <value> 

Where <oc> is the output channel to tune and may be either LOOP 1 or LOOP 2. <value> is the current Delta Power setting. 

#### **Command Example:** LOOP 1:AUTOTUNE:DELTAP 100 

This sets the maximum change in output power to 100% of full scale. This will allow the tuning process to use any output level. 

#### **Query Example:** LOOP 2:AUTOTUNE:DELTAP? 

Example Response: 25.0000 

This response says that the maximum change in output power used by autotune will be ± 25% of the current output power level. 

#### **Short Form:** AUT:DELT 

194 

Remote Operation 

Model 32 / 32B User's Manual 

#### **AUTOTUNE:TIMEOUT: Autotune Timeout.** 

Sets and queries the timeout value of the autotune process. This is a numeric field that specifies the maximum time, in seconds, that the autotune process model will wait for it's internal error vector to converge without declaring a timeout condition. 

#### **Command Syntax:** <oc>:AUTOTUNE: TIMEOUT <value> 

- Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 2. <value> is the timeout period in seconds. 

#### **Query Syntax:** <oc>:AUTOTUNE: TIMEOUT? 

Query Response: <value> 

Where <oc> is the output channel to tune and may be either LOOP 2or LOOP 

   2. <value> is the timeout period in seconds. 

- **Command Example:** LOOP 2:AUTOTUNE: TIMEOUT 200 

Sets the autotune timeout period to 200 Seconds. 

#### **Query Example:** LOOP 1:AUTOTUNE:TIME? 

Example Response: 250.000 Identifies the autotune timeout period as 250 seconds. 

#### **Short Form:** AUT:TIM 

#### **AUTOTUNE:START: Initiate Autotune.** 

Initiates the autotune sequence. 

#### **Command Syntax:** <oc>:AUTOTUNE:START 

Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 2. 

**Command Example:** LOOP 1:AUTOTUNE: START Initiates autotuning the heater. 

#### **Short Form:** AUT:STAR 

195 

Remote Operation 

Model 32 / 32B User's Manual 

#### **AUTOTUNE:EXIT: Abort Autotune.** 

Aborts and exits the autotune process. 

#### **Command Syntax:** <oc>:AUTOTUNE: EXIT 

Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 2. 

#### **Command Example:** LOOP 2:AUTOTUNE: EXIT 

Aborts autotuning. 

#### **Short Form:** AUT:EXIT 

#### **AUTOTUNE:SAVE: Save PID Coefficients.** 

When an autotune sequence has successfully completed, this command will save the generated PID values to the control loop PID values and change the autotune state from 'complete' to 'idle'. 

#### **Command Syntax:** <oc>:AUTOTUNE:SAVE 

Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 2. 

**Command Example:** LOOP 2:AUTO:SAVE 

#### **Short Form:** AUT:SAVE 

#### **AUTOTUNE:PGAIN: Proportional Gain.** 

When an autotune sequence has successfully completed, the AUTOTUNE:PGAIN command can be used to query the generated P, or P gain, term. 

#### **Query Syntax:** <oc>:AUTOTUNE:PGAIN? 

Query Response: <value> 

Where <oc> is the output channel to tune and may be either LOOP 1 or LOOP 2. <value> is the generated P gain feedback coefficient. 

#### **Query Example:** LOOP 2:AUTO:PGA? 

Example Response: 125.0000 

Indicates that the generated P gain term is 125. 

#### **Short Form:** AUT:PGA 

196 

Remote Operation 

Model 32 / 32B User's Manual 

#### **AUTOTUNE:IGAIN: Integral Gain** 

When an autotune sequence has successfully completed, the AUTOTUNE:IGAIN command can be used to query the generated I, or integrator gain, term. 

#### **Query Syntax:** <oc>:AUTOTUNE:IGAIN? 

Query Response: <value> 

Where <oc> is the output channel to tune and may be either LOOP 1 or LOOP 

2. <value> is the generated I feedback term in Seconds. 

#### **Query Example:** LOOP 1:AUTO:IGA? 

Example Response: 225.0000 Indicates that the generated I gain term is 225. Seconds. 

#### **Short Form:** AUT:IGA 

#### **AUTOTUNE: DGAIN: Derivative Gain.** 

When an autotune sequence has successfully completed, the AUTOTUNE:DGAIN command can be used to query the generated D, or differentiator gain, term. 

#### **Query Syntax:** <oc>:AUTOTUNE:GAIN? 

Query Response: <value> 

Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 

2. <value> is the generated D feedback term in inverse Seconds. 

#### **Query Example:** LOOP 2:AUTO:DGA? 

Example Response: 22.0000 Indicates that the generated D gain term is 22 / Seconds. 

#### **Short Form:** AUT:DGA 

197 

Remote Operation 

Model 32 / 32B User's Manual 

#### **AUTOTUNE:STATUS: Autotune Status.** 

Queries the status of the autotune process. Return values are: 

|Idle|- Autotune has not started.|
|---|---|
|Running|-Autotune is running.|
|Complete|-Autotune successfully completed.|
|Failed  -Una|ble to generate PID values.|
|Abort|-Aborted by operator intervention.|

#### **Query Syntax:** <oc>:AUTOTUNE:STATUS? 

Query Response: <status> Where <oc> is the output channel to tune and may be either LOOP 1or LOOP 2. <status> is the current status of the autotune process from the above list 

#### **Query Example:** LOOP 1:AUTO:STATUS? 

Example Response: COMPLETE 

Indicates that autotune has successfully completed and generated values for PID are available. 

#### **Short Form:** AUT:STAT? 

198 

Remote Operation 

Model 32 / 32B User's Manual 

#### INSTCAL commands 

The INSTCAL commands are used to calibrate the Model 32 input sensor measurement circuitry. They should only be used in association with the instrument's calibration procedure. 

Instrument calibration requires the use of various transfer standard resistance and voltage references. 

In order to calibrate the Model 32, the calibration mode must first be turned on by using the INST:MODE ON command. Issuing this command will cause the unit to copy the actual calibration data from flash memory to temporary RAM. Further, the unit will display raw voltage data that has had the RAM calibration coefficients applied. 

The temporary RAM calibration data is manipulated using the OFFSET and GAIN and TYPE commands for each input channel. RAM is copied back to the actual FLASH memory calibration data table using the SAVE command. 

The Model 32 is returned to normal operation by using the INSTCAL:MODE OFF command. Note that this does not write data to the calibration FLASH memory area. 

#### **INSTCAL:MODE** 

Queries or sets the instrument calibration mode. Calibration mode must be turned on before most instrument calibration commands are effective. 

**Command Syntax:** INSTCAL <chan>:MODE <mode> 

Where <chan> is the input channel number (required but not used) and <mode> is the desired mode, which may be either ON or OFF. 

**Command Example:** INST A:MODE ON 

Places the Model 32 in calibration mode. 

**Query Syntax:** INSTCAL <chan>:MODE? 

Where <chan> is the input channel number (required but not used). 

Query Response: <mode> 

Where <mode> is the calibration mode indicator and will be either ON or OFF. 

**Query Example:** INSTCAL <chan>:MODE? 

Example Response: OFF Indicates that the Model 32 is not in calibration mode 

**Short Form:** INST <chan>:MOD 

199 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INSTCAL:SAVE** 

This command copies the temporary RAM calibration data table to the actual FLASH memory instrument calibration area. It can only be used when the instrument is in calibration mode; Otherwise, it does nothing. 

#### **Command Syntax:** INSTCAL <chan>:SAVE 

Where <chan> is the input channel number (required but not used)  Note that, even though a channel indicator is specified, the entire RAM table for all four input channels is copied to FLASH memory. Therefore, this command should only be issued once when the entire procedure is complete. 

**Command Example** : INST A:SAVE 

**Short Form:** INST <chan>:SAVE 

#### **INSTCAL:TYPE** 

Sets or queries the type of calibration that is being applied to a specified input channel. This command is only effective when the unit is in calibration mode. 

Calibration types are shown below: 

V10UA - Voltage calibration. Full scale is 2.5V I10UA - 10UA constant-current source calibration. R1MA - Resistance calibration. Full scale is 2500 Ω . R100UA - Resistance calibration. Full scale is 25K Ω . R10UA - Resistance calibration. Full scale is 250K Ω . 

**Command Syntax:** INSTCAL <chan>:TYPE <type> 

Where <chan> is the input channel indicator and <type> is the desired calibration type from the above list. 

**Command Example** : INST A:TYPE R10UA Places the calibration type to R10UA. 

**Query Syntax:** INSTCAL <chan>:TYPE? 

Where <chan> is the input channel indicator. 

Query Response: <type> 

Where <type> is the calibration type from the above list. 

**Query Example:** INSTCAL <chan>:TYPE? Example Response: V10UA Indicates that the calibration type is V10UA 

**Short Form:** INST <chan>:TYP 

200 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INSTCAL:GAIN** 

Sets or queries gain calibration factor that is applied to the specified input channel. 

GAIN is a floating point number with a nominal value of 1.000. 

There is a GAIN factor for each calibration type within a channel. Therefore, before the INST:GAIN is used, the INST:TYPE command should be used to set the calibration type. 

**Command Syntax:** INSTCAL <chan>:GAIN <gain> Where <chan> is the input channel indicator and <gain> is the desired gain calibration factor. 

**Command Example** : INST A:GAIN 0.999423 Sets the gain calibration factor for input channel A to 0.999423. 

**Query Syntax:** INSTCAL <chan>:GAIN? Where <chan> is the input channel indicator. Query Response: <gain> Where <gain> is the gain calibration factor. 

**Query Example:** INSTCAL B:GAIN? Example Response: 0.994321 Indicates that the gain calibration factor for input channel B is 0.994321 

**Short Form:** INST <chan>:GAIN 

201 

Remote Operation 

Model 32 / 32B User's Manual 

#### **INSTCAL:OFFSET** 

Sets or queries offset calibration factor that is applied to the specified input channel. 

OFFSET is an integer that is in ADC counts and may be either positive or negative. 

There is an OFFSET factor for each calibration type within a channel. Therefore, before the INST:OFFSET is used, the INST:TYPE command should be used to set the calibration type. 

- **Command Syntax:** INSTCAL <chan>: OFFSET <offset> Where <chan> is the input channel indicator and <offset> is the desired offset calibration factor. 

**Command Example** : INST B: OFFSET -321 Sets the offset calibration factor for input channel B to -321. 

**Query Syntax:** INSTCAL <chan>: OFFSET? Where <chan> is the input channel indicator. 

Query Response: <offset> Where <offset> is the offset calibration factor. 

**Query Example:** INSTCAL B: OFFSET? Example Response: 23 Indicates that the offset calibration factor for input channel B is 23 

**Short Form:** INST <chan>:OFFS 

202 

Remote Operation 

Model 32 / 32B User's Manual 

### Remote Command Summary 

|**Command**|**Function**|
|---|---|
|**IEEE Common Commands**||
|*ESE,<br>*ESE?|The *ESE command sets and queries the Standard Event Status<br>Enable(ESE)Register bits.|
|*ESR?|Returns the Standard Event(SEV)register.|
|*IDN?|Returns Instrument Identification String.|
|*OPC?|Set the operation complete bit in the Standard Event (SEV) status<br>register when allpendingdevice operations have finished.|
|*RST|Reset the controller.|
|**Control Loop Start/Stop  com**|**mands**|
|STOP|Disengage all control loops.|
|CONTROL<br>CONTROL?|Engage all control Loops. Query if the loops are engaged.|
|**SYSTEM commands**||
|SYSTEM:LOCKOUT<br>SYSTEM:LOCKOUT?|Sets or queries the remote lockout status indicator.|
|SYSTEM:BEEP|Asserts the audible alarm.|
|SYSTEM:REMLED<br>SYSTEM:REMLED|Sets or queries the remote LED status indicator on the front panel.|
|SYSTEM:LOOP?|Reports the status of the two temperature control loops.|
|SYSTEM:DISTC<br>SYSTEM:DISTC?|Set or query the display filter time constant. Available time constants<br>are 0.5,1,2,4,8,16,32 or 64 Seconds.|
|SYSTEM:ADRS<br>SYSTEM:ADRS?|Set or query the address that the IEEE-488.2 interface will use.|
|SYSTEM:RESEED|Reseeds the display filter for all of the input channels,<br>resultingin faster settling.|
|SYSTEM:SYNCTAPS|Sets the number of taps used bythe synchronous filter.|
|SYSTEM:REMOTE|Sets the remote interfaceport. Choices are GPIB and RS232.|

203 

Remote Operation 

Model 32 / 32B User's Manual 

|**Command**|**Function**|
|---|---|
|SYSTEM:AMBIENT?|Query the temperature of the controller’s internal voltage<br>reference. Example Output: +25C|
|SYSTEM:AUTOCAL|Perform an autocalibrate sequence on both input channels.<br>Generally used only to correct for errors caused by significant<br>changes in operatingtemperature.|
|SYSTEM:HTRHST?|Query the temperature of the internal LOOP #1 heatsink.<br>Example output: +62C|
|SYSTEM:HOME|Causes the display on the front panel to go to the Operate<br>Screen.|
|SYSTEM:NAME<br>SYSTEM:NAME?|Set or query the instrument’s name string. Example:<br>SYSTEM:NAME "Cryocooler Four"|
|SYSTEM:DRES<br>SYSTEM:DRES?|Sets or queries the controller's display resolution. Choices are:<br>Full,1,2 or 3.|
|SYSTEM:HWREV?|Queries the instrument’s hardware revision level.|
|SYSTEM:FWREV?|Queries the instrument’s firmware revision level.|
|SYSTEM:ERROR?|Queries the instrument’s errorqueue.|
|SYSTEM:CJTEMP?|Queries the internal Cold Junction Compensation temperature<br>for thermocouple sensors.|
|SYSTEM:PUCONTROL<br>SYSTEM:PUCONTROL?|Sets or queries the power-up-in-control mode setting.|
|SYSTEM:LINEFREQ<br>SYSTEM:LINEFREQ?|Sets or queries the AC Power Line frequency setting.|
|SYSTEM:SETUP:RESTORE|Saves the current instrument setupto a user setup.|
|SYSTEM:NVSAVE|Save the instrument configuration to flash memory so that it will<br>be restored on the nextpower-up.|
|SYSTEM:CONTRAST<br>SYSTEM:CONTRAST?|Set or query the contrast of the front panel VFD display. (Model<br>34,62 Only)|

204 

Remote Operation 

Model 32 / 32B User's Manual 

|**Command**|**Function**|
|---|---|
|**CONFIG commands**||
|CONFIG:NAME|Sets orqueries the name of a user setup|
|CONFIG:SAVE|Saves the current instrument setupto a user setup.|
|CONFIG:RESTORE|Restores apreviouslysaved instrument configuration.|

|**Command**|**Function**|
|---|---|
|**Input Channel Commands**||
|INPUT?<br>INPUT:TEMPER?|Query the current temperature reading on any of the input<br>channels.|
|INPUT:UNITS<br>INPUT:UNITS|Sets or reports the display units of temperature used by the<br>specified input channel.|
|INPUT:ISENIX<br>INPUT:ISENIX|Sets or queries the sensor index number assigned to an input<br>channel. Applies to factoryinstalled sensors. Refer toAppendix A.|
|INPUT:USENIX<br>INPUT:USENIX|Sets or queries the sensor index number assigned to an input<br>channel. Applies to user installed sensors. Refer toAppendix A.|
|INPUT:SENIX<br>INPUT:SENIX|(Obsolete. Use USENIX or ISENIX commands described above)<br>Sets or queries the sensor index number assigned to an input<br>channel.|
|INPUT:VBIAS<br>INPUT:VBIAS?|Set or query the sensor voltage excitation used in the constant-<br>voltage mode. Applies to constant-voltage mode sensors only.|
|INPUT:NAME<br>INPUT:NAME?|Sets or queries the name string of the specified input channel.|
|INPUT:ALARM?|Queries the alarm status of the specified input channel.|
|INPUT:ALARM:HIGHEST<br>INPUT:ALARM:HIGHEST?|Sets or queries the temperature setting of the high temperature<br>alarm for the specified input channel.|
|INPUT:ALARM:LOWEST<br>INPUT:ALARM:LOWEST?|Sets or queries the temperature setting of the low temperature<br>alarm for the specified input channel.|
|INPUT:ALARM:HIENA<br>INPUT:ALARM:HIENA?|Sets or queries the high temperature alarm enable for the<br>specified input channel.|
|INPUT:ALARM:LOENA<br>INPUT:ALARM:LOENA?|Sets or queries the low temperature alarm enable for the specified<br>input channel.|
|INPUT:ALARM:FAULT<br>INPUT:ALARM:FAULT?|Sets or queries the sensor fault alarm enable for the specified<br>input channel.|
|INPUT:ALARM:AUDIO<br>INPUT:ALARM:AUDIO?|Set or query the audible alarm enable for the selected input<br>channel.|

205 

Remote Operation 

Model 32 / 32B User's Manual 

|**Command**|**Function**|
|---|---|
|**Input Channel Comma**|**nds**|
|INPUT:SENPR?|Queries an input channel reading in basic sensor units. Sensor units are<br>Volts for diode and thermocouple sensors and Ohms for resistor sensors.|
|**Input Channel Statisti**|**cs**|
|INPUT:MINIMUM?|Queries the minimum temperature that has occurred on an input channel<br>since the STATS:RESET command was issued.|
|INPUT:MAXIMUM?|Queries the Maximum temperature that has occurred on an input channel<br>since the STATS:RESET command was issued.|
|INPUT:VARIANCE?|Queries the temperature variance that has occurred on an input channel<br>since the STATS:RESET command was issued.|
|INPUT:SLOPE?|Queries the input channel statistics. SLOPE is the slope of the best fit<br>straight line passing through all temperature samples that have been<br>collected since the STATS:RESET command was issued.|
|INPUT:OFFSET?|Queries the input channel statistics. OFFSET is the offset of the best fit<br>straight line passing through all temperature samples that have been<br>collected since the STATS:RESET command was issued.|
|STATS:TIME?|Queries the time duration over which input channel statistics have been<br>accumulated.|
|STATS:RESET|Resets the accumulation of input channel statistical data.|

206 

Remote Operation 

Model 32 / 32B User's Manual 

|**Command**<br>**LOOP Commands**|**Function**|
|---|---|
|LOOP:SOURCE<br>LOOP:SOURCE?|Sets and queries the selected control loop's controlling input channel.|
|LOOP:SETPT<br>LOOP:SETPT?|Sets and queries the selected control loop’s setpoint.|
|LOOP:TYPE<br>LOOP:TYPE?|Sets and queries the selected control loop’s control type.|
|LOOP 1:RANGE<br>LOOP 1:RANGE?|Sets or queries the control loop #1, or the primary heater, output range.|
|LOOP:TABLEIX<br>LOOP:TABLEIX?|Sets or queries the table number that is used with control modes that use<br>PID tables.|
|LOOP:RAMP?|Queries the unit to determine if a temperature ramp is in progress on the<br>specified control loop.|
|LOOP:RATE<br>LOOP:RATE?|Sets and queries the ramp rate used by the selected control loop when<br>performinga temperature ramp.|
|LOOP:NAME<br>LOOP:NAME?|Sets or queries the name string for the selected control loop|
|LOOP:PGAIN<br>LOOP:PGAIN?|Sets or queries the selected control loop’s proportional gain term.|
|LOOP:IGAIN<br>LOOP:IGAIN|Sets and queries the integrator feedback term used by the selected control<br>loop.|
|LOOP:DGAIN<br>LOOP:DGAIN|Sets and queries the differentiator feedback term used by the selected<br>control loop.|
|LOOP:HTRREAD?|Queries the output current of the selected control loop.|
|LOOP:MAXPWR<br>LOOP:MAXPWR?|Sets and queries the maximum allowed output power.|
|LOOP:MAXSET<br>LOOP:MAXSET?|Sets and queries the maximum setpoint.|
|LOOP 1:LOAD<br>LOOP 1:LOAD?|Sets or queries the load resistance setting of the primary heater (Loop 1).|
|LOOP:PMANUAL<br>LOOP:PMANUAL?|Sets and queries the output power level used by the selected control loop<br>feedback when it is in Manual control mode.|

207 

Remote Operation 

Model 32 / 32B User's Manual 

|**Command**|**Function**|
|---|---|
|**Over Temperature Disconne**|**ct Commands**|
|OVERTEMP:ENABLE<br>OVERTEMP:ENABLE?|Sets and queries the over temperature disconnect enable.|
|OVERTEMP:SOURCE<br>OVERTEMP:SOURCE?|Sets and queries the input channel that is used as the source for the<br>Over Temperature Disconnect feature.|
|OVERTEMP:TEMP<br>OVERTEMP:TEMP?|Sets and queries the temperature used by the over temperature<br>disconnect feature.|
|**Sensor Calibration Curve Co**|**mmands**|
|CALCUR<br>CALCUR?|Sets or queries sensor calibration curve data.|
|**PID Table Commands**||
|PIDTABLE<br>PIDTABLE?|Queries the name string of a PID table at a specified index.|
|PIDTABLE:NENTRY<br>PIDTABLE:NENTRY?|Queries the number of entries in a PID Table.|
|PIDTABLE:TABLE<br>PIDTABLE:TABLE?|Sets or queries the entries in a PID table.|

|**Command**|**Function**|
|---|---|
|**Relay Commands(Model 34 a**|**nd 62 only)**|
|RELAYS?|RelayStatus Query.|
|RELAYS: SOURCE<br>RELAYS: SOURCE?|Sets or queries the source input channel for a specified relay.|
|RELAYS: HIGHEST<br>RELAYS: HIGHEST?|Sets or queries the temperature setting of the high temperature<br>setpoint for the specified relay.|
|RELAYS:LOWEST<br>RELAYS:LOWEST?|Sets or queries the temperature setting of the low temperature<br>setpoint for a specified relay.|
|RELAYS: HIENA<br>RELAYS: HIENA?|Sets or queries the high temperature enable for the specified relay.|
|RELAYS:LOENA<br>RELAYS:LOENA|Sets or queries the low temperature enable for the specified relay.|
|RELAYS:FAULT<br>RELAYS:FAULT|Sets or queries the sensor fault enable for the specified relay.|
|**Sensor Setup Commands**||
|CALDATA?<br>CALDATA:NAME<br>CALDATA:NAME?|Sets or queries the name string for a user-installed sensor.|
|CALDATA:TYPE<br>CALDATA:TYPE?|Sets or queries the sensor type for a user-installed sensor.|
|CALDATA:MULTIPLY<br>CALDATA:MULTIPLY?|Sets or queries the Multiplier for a user-installed sensor.|
|SENTYPE?<br>SENTYPE:NAME<br>SENTYPE:NAME?|Queries the name string for a factory-installed sensor. Please refer<br>toAppendix A.|

208 

Remote Operation 

Model 32 / 32B User's Manual 

|**Command**|**Function**|
|---|---|
|**Autotune Commands**||
|AUTOTUNE:DELTAP<br>AUTOTUNE:DELTAP?|Sets and queries the maximum allowed change in heater output<br>power that is allowed during the process modeling phase of the<br>autotuning process.|
|AUTOTUNE:TIMEOUT<br>AUTOTUNE:TIMEOUT?|Sets and queries the timeout value of the autotune process.|
|AUTOTUNE:START|Initiates the autotune sequence.|
|AUTOTUNE:EXIT|Aborts and exits the autotuneprocess.|
|AUTOTUNE:SAVE|When an autotune sequence has successfully completed, this<br>command will save the generated PID values to the control loop PID<br>values and change the autotune state from 'complete' to 'idle'.|
|AUTOTUNE:PGAIN?|Querythegenerated Pgain termgenerated byautotune.|
|AUTOTUNE:IGAIN?|Querythegenerated Igain termgenerated byautotune.|
|AUTOTUNE:DGAIN?|Querythegenerated Dgain termgenerated byautotune.|
|AUTOTUNE:STATUS?|Queries the status of the autotuneprocess.|
|**Cryocooler Filter Commands**||
|CCFILTER: STATUS?|QueryCryocooler filter status.|
|CCFILTER: TYPE<br>CCFILTER: TYPE?|Set or query filter type. Types are: OFF, Input or Cancel.|
|CCFILTER: STEP<br>CCFILTER: STEP?|Set or query the filter adaptation step size.|
|CCFILTER: LOOP<br>CCFILTER: LOOP?|Set or query the control loop number controlled by the cryocooler<br>filter.|
|CCFILTER: NTAPS<br>CCFILTER: NTAPS?|Set or query the number of taps in the filter.|
|CCFILTER:RESET|Reset the Cryocooler filter.|

**Table 37: Remote Command Summary** 

209 

Model 32 / 32B User's Manual 

EU Declaration of Conformity 

## EU Declaration of Conformity 

### **According to ISO/IEC Guide 22 and EN 45014** 

Product Category: Measurement, Control and Laboratory Product Type: Temperature Measuring and Control System Model Numbers: Model 32 

Manufacturer's Name: Cryogenic Control Systems, Inc. 

Manufacturer's Address: 

P. O. Box 7012 Rancho Santa Fe,  CA  92067 Tel: ( 858) 756- 3900,  Fax: 858. 759. 3515 

The before mentioned products comply with the following EU directives: 

**89/336/EEC** , "Council Directive of 3 May 1989 on the approximation of the laws of the Member States relating to electromagnetic compatibility" 

**73/23/EEC** , "Council Directive of 19 February 1973 on the harmonization of the laws of Member States relating to electrical equipment designed for use within certain voltage limits". 

The compliance of the above mentioned product with the Directives and with the following essential requirements is hereby confirmed: 

|Emissions|Immunity|Safety|
|---|---|---|
|EN 55011,1998|EN 50082-1, 1997|EN 61010-1, 2001|
|||IEC 61010-1, 2001|

The technical files and other documentation are on file with Mr. Guy Covert, President and CEO. 

As the manufacturer we declare under our sole responsibility that the above mentioned products comply with the above named directives. 

<!-- Start of picture text -->
_________________________________________<br><!-- End of picture text -->

Guy D. Covert President, Cryogenic Control Systems, Inc. October 15, 2005 

211 

Model 32 / 32B User's Manual 

Appendix A: Installed Curves 

## Appendix A: Installed Curves 

### Factory Installed Curves 

The following is a list of factory-installed sensors and the corresponding sensor index (ISENIX). 

|**isenix**|**Name**|**Description**|
|---|---|---|
|**0**|**None**|Input disabled|
|**1**|**Cryocon S700**|Cryo-con S700 series Silicon Diode. Range: 1.4 to 380K. 10µA<br>constant current excitation.|
|**2**|**LS DT-670**|Lakeshore Silicon Diode Curve 11 for DT-670 series diodes. Range:<br>1.4 to 500K. 10µA constant current excitation.|
|**3**|**LS DT-470**|Lakeshore Silicon Diode Curve 10 for DT470 series diodes. Range:<br>1.4 to 495K. 10µA constant current excitation.|
|**4**|**CD-12A Diode**|Cryo Industries CD-12A Silicon Diode. Range: 1.4 to 325K. 10µA<br>constant current excitation.|
|**5**|**SI 410 Diode**|Scientific Instruments, Inc. 410 Diode Curve. Range: 1.5 to 450K.<br>10µA excitation.|
|**6**|**Cryocon S800**|Cryo-con S800 series Silicon Diode. Range: 1.4 to 380K. 10µA<br>constant current excitation.|
|**7**|**Cryocon S900**|Cryo-con S900 series Silicon Diode. Range: 1.5 to 500K. 10µA<br>constant current excitation.|
|**8**|**CTI Diode**|CTI Cryopumpdiode. 10K to 325K|
|**20**|**Pt100 385**|DIN43760 standard 100ΩPlatinum RTD. Range: 23 to 1023K, 1mA<br>excitation.|
|**21**|**Pt1K 385**|1000Ωat 0°C Platinum RTD using DIN43760 standard calibration<br>curve. Range: 23 to 1023K,100µA excitation.|
|**22**|**Pt10K 385**|10KΩat 0°C Platinum RTD. Temperature coefficient 0.00385, Range:<br>23 to 475K,10µA excitation.|
|**23**|**RhFe 27, 1mA**|Rhodium-Iron resistor,27 Ohms at 0<sup>o</sup>C. 1mA DC excitation.|
|**31**|**RO-600 AC**|Scientific Instruments Inc. RO-600 Ruthenium Oxide sensor with<br>constant-voltage AC excitation.|
|**32**|**RO-105 DC 10μA**|Scientific Instruments Inc. RO-105 Ruthenium Oxide sensor with<br>constant-current10μA DC excitation|
|**33**|**R500**|Cryocon R500 Ruthenium Oxide sensor with constant-voltage AC<br>excitation.|
|**34**|**R400**|Cryocon R400 Ruthenium Oxide sensor with constant-current 10μA<br>DC excitation|
|**45**<br>**46**<br>**47**<br>**48**|**TC type K**<br>**TC type E**<br>**TC type T**<br>**AuFe 0.07%**|Only available when thermocouple option is installed thermocouples<br>type K, E and T, Direct input to the controller. Range: Type T: 3.5 to<br>673K, Type E: 3.5 to 1273K, Type K: 3.5 to 1643K.|

**Table 38: Factory Installed Sensors** 

Note that Thermocouple devices only appear on units ordered with the thermocouple option. 

213 

Model 32 / 32B User's Manual 

Appendix A: Installed Curves 

The isenix remote command is used to set factory installed sensors. For example, the command: 

INPUT B ISENIX 33 would set input B to use the RO-600 sensor. 

INPUT A:ISENIX 1 would set input A to use the S700 Diode. 

INPUT A:ISENIX 0 would turn input A off by setting the sensor to ‘none’. 

### User Installed Sensor Curves 

The user may install up to four custom sensors. This table shows the sensor index and default name of the user curves: 

|**usenix**<br>**index**|**User**<br>**Number**|**Default Name**|
|---|---|---|
|**0**|**0**|User Sensor 0|
|**1**|**1**|User Sensor 1|
|**2**|**2**|User Sensor 2|
|**3**|**3**|User Sensor 3|

When using the CALCUR commands, only user curves are addressed, therefore, the user index (usenix) shown above is used. 

The USENIX, remote commands address user installed curves. For example: 

CALCUR 2 would address user curve #2. 

INPUT A:USENIX 1 would set input A to use User Sensor 1. 

214 

Model 32 / 32B User's Manual 

Appendix A: Installed Curves 

### Sensor Curves on CD 

The following sensors are available on the CD supplied: 

|**File**|**Description**|
|---|---|
|**CryocalD3.crv**|Cryocal D3 Silicon Diode. Range: 1.5 to 300K|
|**CTIdiode.crv**|CTI cryo-pumpsilicon diode. Range: 10K to 325K|
|**SI410.crv**|Scientific Instruments, Inc. SI-410 Silicon Diode. Range: 1.5 to 450K|
|**Curve10.crv**|Lakeshore Curve 10 Silicon Diode curve for DT-470 series diodes. Range:  1.4<br>to 495K.|
|**Curve11.crv**|Lakeshore Curve 10 Silicon Diode curve for DT-670 series diodes. Range: 1.4 to<br>500K.|
|**PT100385.crv**|Cryocon CP-100, DIN43760 or IEC751 standard Platinum RTD, 100Ωat 0°C.<br>Range: 23 to 1023K|
|**PT1K385.crv**|DIN43760 or IEC751 standard Platinum RTD, 1000Ωat 0°C. Range: 23 to<br>1023K|
|**PT1003902.crv**|Platinum RTD, 100Ωat 0°C Temperature coefficient 0.003902Ω/C. Range: 73K<br>to 833K.|
|**PT1K375.crv**|Platinum RTD, 1000Ωat 0°C Temperature coefficient 0.00375Ω/C. Range: 73K<br>to 833K.|
|**aufe07cr.crv**|Chromel-AuFe 7% Thermocouple. Range: 3 to 610K|
|**TCTypeE.crv**|Thermocouple, Type E. Range: 3.2 to 1273K|
|**TCTypeK.crv**|Thermocouple, Type K. Range: 3.2 to 1643K|
|**TCTypeT.crv**|Thermocouple, Type T. Range: 3.2 to 673K|
|**CX1030E1.crv**|CernoxCX1030 example curve. Range: 4 to 325K|

215 

Model 32 / 32B User's Manual 

Appendix B: Troubleshooting Guide 

## Appendix B: Troubleshooting Guide 

### Error Displays 

|**Display**|**Condition**|
|---|---|
|Or,|Input channel voltage measurement is out of range.|
|an<br>|Ensure that the sensor is connected and properly wired.<br>Ensure that the polarity of the sensor connections is correct.<br>Refer to theSensor Connectionssection.|
|erratic display of temperature.|Many sensors can be checked with a standard Ohmmeter. For<br>resistor sensors, ensure that the resistance is correct by<br>measuring across both the Sense and Excitation contacts. For a<br>diode sensor, measure the forward and reverse resistance to<br>ensure a diode-type function.|
||Input channel is within range, but measurement is outside the<br>limits of the selected sensor’s calibration curve.<br>Check sensor connections as described above.<br>Ensure that the proper sensor has been selected. Refer to the<br>Input Channel Setup Menussection.<br>Change the sensor units to Volts or Ohms and ensure that the<br>resulting measurement is within the selected calibration curve.<br>Refer to the section onSensor Setupto display the calibration<br>curve.|

|**Display**|**Condition**|
|---|---|
||The controller’s firmware has been corrupted (Invalid<br>Checksum).|
|<br>|Re-load the unit’s firmware. Refer to the section<br>Downloading Instrument Firmware.|
||The input temperature measurement circuitry has<br>failed. Contact Cryo-con technical support.|
|||
||The self-test procedure detected an error in the<br>controller’s RAM memory. Contact Cryo-con Support.|
|||

217 

Model 32 / 32B User's Manual 

Appendix B: Troubleshooting Guide 

### Control Loop and Heater Problems 

|**Symptom**|**Condition**|
|---|---|
|**Overtemp**displayed.|The control loops were disengaged by detection of an excessive<br>internal temperature. Possible causes:<br>Shorted heater. Check heater resistance.<br>Selection of a heater resistance that is much greater than<br>the actual heater resistance. Refer to theControl Loop<br>Setup menusection.<br>Selection of an AC Power line voltage that is much less than<br>the actual voltage. Refer to theFuse Replacement and<br>Voltage Selectionsection.<br>Check that the instrument’s fan is running and that the sides<br>and rearpanel allow easyair flow.|
|**Readback**displayed.|The control loops were disengaged by the heater current read-back<br>monitor. Most likelycause is an open heater.|
|**SensorFLT**displayed.|The control loops were disengaged by a sensor fault condition. Correct<br>the input sensor fault condition to proceed. The control loops will only<br>engage when there is a valid temperature reading on their input. The<br>exception is when a loopis assigned a control mode of Off or Manual.|
|**OTDisconn**displayed.|The control loops were disengaged by the Over Temperature<br>Disconnect monitor. This was done to protect user equipment from<br>damage due to overheating. To configure the monitor, refer to the<br>System Functions Menusection.|
|The heater output current<br>monitor is jumping up and<br>down byabout 1%|This is normal and does not indicate unstable heater power. The<br>output current monitor is coarsely quantized and is displayed only for<br>an indication ofproper function.|
|The controller should be<br>applying power, but the<br>display is showing 0%<br>output.|The output indicated on the display is the actual measured output<br>power of the control loop. A reading of 0% while the controller is<br>attempting to output power usually indicates an open heater.|

218 

Model 32 / 32B User's Manual 

Appendix B: Troubleshooting Guide 

|**Symptom**|**Condition**|
|---|---|
|Unstable control.|If the system is oscillating, try de-tuning the PID values by decreasing<br>P, increasing I and setting D to zero. If the oscillations cannot be<br>stopped by this procedure, the cause is likely that your system has an<br>excessive time delay. Linear control algorithms, including PID, cannot<br>control systems with excessive time delay. These problems often occur<br>in systems that use heat pipes, or depend on gas flow between the<br>heater and temperature sensor elements. The only solution to such<br>systems is to re-design the equipment to reduce the time delay, or to<br>externally implement a time delay compensation algorithm, such as a<br>Smith Predictor.<br>Do not try to control on Ohms or Volts. The controller will work<br>correctly with either of these sensor units, but the PID values required<br>are significantly different and most sensors are non-linear. Furtherer,<br>there is no advantage to controlling in sensor units.<br>Optimize the control loop parameters by using the Autotune feature<br>described in theAutotuningsection.<br>Most cryogenic systems require significantly different PID parameters<br>at different temperatures. To ensure stable control over a wide<br>temperature range, use the PID Table feature described in thePID<br>Table Entrysection.<br>If the heater is controlling with an output power level less than 10%,<br>switch to the next lower heater range.|

|**Symptom**|**Condition**|
|---|---|
|Autotune indicates a status<br>of  ‘Abort’ or ‘Fail’.|Autotune will only abort if the control loops are not engaged or there is<br>an invalid temperature reading on the control input channel. If it cannot<br>generate a solution because of issues in the system dynamics, it will<br>indicate a status of ‘Fail’.|
|Autotune times out and does<br>not generate effective PID<br>parameters.|Extend the Display Filter time constant to reduce system level noise<br>and try autotune again. The display filter is described in theSystem<br>Functions Menusection. Systems using Diode type sensors above<br>50K will usually require a 4 or 8 second time constant. This setting<br>may be returned to any desired value once tuning is complete.<br>Switch to the lowest possible heater range that will control at the target<br>setpoint.<br>Try autotuning in the PI- mode instead of PID. Most cryogenic systems<br>do not benefit from the D term.<br>If a Cryo-cooler is being used, set the controller’s cryocooler filter to<br>Input mode. This may be returned to Off or Cancel mode once tuning<br>is complete.<br>Experiment with the DeltaP parameter. Increasing it often improves<br>autotune success.|

219 

Model 32 / 32B User's Manual 

Appendix B: Troubleshooting Guide 

### Temperature Measurement Errors 

|**Symptom**|**Condition**|
|---|---|
|Noise on temperature<br>measurements.|Possible causes:<br>Excessive noise pickup, especially AC power line noise.<br>Check your wiring and shielding. Sensors must be floating,<br>so check that there is no continuity between the sensor<br>connection and ground. Review theSystem Shielding and<br>Grounding Issuessection.|
||Note: Cryo-con controllers use a shielding scheme that is<br>slightly different than some other controllers. If you are using<br>cable sets made for use with other controllers, some shield<br>connections may need to change. If pin 3 of the input<br>connector is connected to the cable shield, disconnect it and<br>either re-connect the shield to the backshell contact or leave<br>the shield floating. No connection should ever be made to<br>pin 3 of the input connector.|
||Check for shielding problems by temporarily removing the<br>input connector’s backshell. If the noise changes<br>significantly, current is being carried by the shields and is<br>being coupled into the controller.<br>Use a longer display filter time constant to reduce displayed<br>noise.|

|**Symptom**|**Condition**|
|---|---|
|DC offset in temperature<br>measurements.|Possible causes:<br>The wrong sensor type or sensor calibration curve is being<br>used. Refer to theInput Channel Setup Menusection.<br>DC offset in cryostat wiring. Review theThermal EMF and<br>AC Bias Issuessection. Use AC bias, if necessary, to cancel<br>the offset error.<br>A four-wire measurement is not being used. Some cryostats<br>use a to a two-wire measurement internally. This can cause<br>offset errors due to lead resistance.<br>Thermocouples: These sensors will often have DC offset<br>errors. Use the CalGenfeature to generate a new sensor<br>calibration curve that corrects for these errors.|
|No temperature reading.|Review theError Displayssection above.|

220 

Model 32 / 32B User's Manual 

Appendix B: Troubleshooting Guide 

### Remote I/O problems 

|**Symptom**|**Condition**|
|---|---|
|Can’t talk to RS-232<br>interface.|Possible causes:<br>Ensure that the RS-232 port is selected. Press the Sys key<br>and scroll down to the RIO-Port: field.<br>Ensure that the baud rate of the controller matches that of<br>the host computer. To check the controller’s baud rate, press<br>the Sys key and scroll down to the RIO-RS232 field.<br>Ensure that the host computer settings are 8-bits, No parity,<br>one stop bit.<br>The RS-232 port does not have an effective hardware<br>handshake method. Therefore, terminator characters must<br>be used on all strings sent to the controller. Review theRS-<br>232 Configurationsection.<br>Ensure that you are using a Null-Modem type cable. There<br>are many variations of RS-232 cables and only the Null-<br>Modem cable will work with Cryo-con controllers. This cable<br>is detailed in theRS-232 Connectionssection.<br>Debugging tip: Cryo-con utility software can be used to talk to the<br>controller over the RS-232 port using the terminal mode. All command<br>and response strings are displayed. This is a good way to establish a<br>connection.|
|Intermittent lockup on RS-<br>232 interface.|Possible causes:<br>Long cables. Try using a lower baud rate. In some cases,<br>inserting a 50mS delay between commands will help.<br>Noise pickup. Try using shielded cables with the shield<br>connected to a metal backshell at both ends.<br>Don’t send reset (RST) commands to the controller before<br>reading.|

221 

Model 32 / 32B User's Manual 

Appendix B: Troubleshooting Guide 

|**Symptom**|**Condition**|
|---|---|
|Can’t talk to IEEE-488<br>interface.|Possible causes:<br>Ensure that the GPIB port is selected. Press the**Sys**key<br>and scroll down to the RIO-Port: field.<br>The IEEE-488 interface does not use terminator characters.<br>Rather, it uses the hardware EOI handshake. Please review<br>theGPIB Configurationsection.<br>Check that the controller’s address matches the host<br>computer’s assignment. Press the**Sys**key and scroll down<br>to the RIO-Address: field.<br>Debugging tip: Cryo-con utility software can be used to talk to the<br>controller over the IEEE-488 port using the terminal mode. All<br>command and response strings are displayed. Since the software<br>provides the proper interface setup, it is a good way to establish initial<br>connection.|
|Intermittent lockup on the<br>IEEE-488 interface.|Possible causes:<br>Bus cables too long or too many loads on a single bus.<br>Don’t send reset commands before each query. This was<br>common in early IEEE-488 systems.<br>Ground loops: Some equipment manufacturers improperly<br>connect the IEEE-488 Shield Ground wire to their circuit<br>board ground. This can cause ground loops with equipment<br>that is properly connected. Debug by disconnecting<br>instruments from the bus.<br>Use of unshielded bus cables.|

### General problems 

|**Symptom**|**Condition**|
|---|---|
|Controller periodically resets,<br>or resets when**Control**key<br>is pressed.|Generally caused by low AC line voltage. Check the AC voltage and<br>ensure that it matches the instrument’s voltage selection.<br>AC line voltage selection is described in theFuse Replacement and<br>Voltage Selectionsection.|
|Complete failure.|Possible cause:<br>Blown fuse. Check line voltage selection before installing<br>new fuses. Review theFuse Replacement and Voltage<br>Selectionsection.|
||Rack mounted instruments: Screws were used in the rack<br>mount shelf that are too long and have penetrated the<br>internal circuit board of the controller.|

222 

Model 32 / 32B User's Manual 

Appendix C: Application Note on Signal Dither. 

## Appendix C: Application Note on Signal Dither. 

### Using Dither in Digital Control Loops 

“Dither”, as a signal or image processing technique, is a method of extending dynamic range by first perturbing (dithering) then averaging. The technique was first developed to enhance the performance of RADAR target algorithms and is now applied to a wide range of applications including navigation systems and consumer audio CD recordings. 

Perhaps the most common example of a dithering technique is the synthesis of an artificial color on a computer screen by grouping available colors at adjacent pixels. When viewed by the user, the spatial averaging effect of the eye generates a color that is not available on the computer’s color palette. 

In Cryo-con’s temperature controllers, dither is used to extend the dynamic range of a temperature control loop by outputting available power levels in a controlled sequence so that the average power is somewhere between the levels available in the controller’s hardware. Here, the averaging function is performed by the system dynamics. 

#### Control Accuracy 

Major error sources in a digital control loop are: the input quantizer (ADC), the Digital Signal Processing mathematical operations and the output quantizer (DAC). 

Cryo-con controllers use a 24-bit Analog-to-Digital converter. This is the best available with modern components and it establishes the measurement resolution of the controller. If all other functions were perfect, this ADC would also establish the accuracy of the control loop. 

In order to preserve accuracy, the mathematical operations in a digital control loop must be performed to a much higher resolution than the input ADC. Therefore, Cryocon controllers all use 32-bit floating-point arithmetic. 

Finally, a high precision loop output value reaches the output quantizer, which is usually a 16- or 18- bit Digital-to-Analog converter. Since this DAC has much less resolution than the earlier stages, it generally establishes the accuracy of the accuracy of the entire loop. A loop output value has been generated to a very high precision, but the DAC throws away most of this precision to fit its available output levels. 

Like the color synthesis example above, signal dithering can be applied to the digital control loop so that the average output value converges to the high precision value computed before output quantization. The result is much greater control accuracy. 

#### Conventional Control Loop Output 

The diagram to the right shows the conventional method of  generating an analog output from a digital control loop. Here, a high precision loop output value is computed, then the value is truncated or rounded to fit the precision of the output DAC. Precision above the resolution of the DAC is lost. 

223 

#### Model 32 / 32B User's Manual 

Appendix C: Application Note on Signal Dither. 

In this example, the output DAC has four quantization levels labeled Q1 through Q4 Q4. Dashed lines show the mid-points between adjacent levels. Here, the desired high-precision control Q3 ~~~~ loop output  (o) is between levels Q2  and Q3. For simplicity, ten output intervals of a DC level are shown. Q2 Using an arithmetic ‘rounding’ scheme, if the desired output is above the midpoint between two quantization levels, Q1 the DAC output will be at the higher level. If the value is below the mid-point, the DAC will output the lower level. Therefore, the DAC output (x) for the input shown will simply be Q3. 

As can be seen, the average value of the DAC output is equal to the nearest quantization level. In this example, the output (Q3) is slightly higher than the value required to accurately control at the selected setpoint. Therefore, the control loop will integrate downwards until the DAC output jumps down to Q2. This process of jumping between Q2 and Q3 will continue, establishing an oscillation with an amplitude of one quantization level and a frequency related to the system’s closed-loop time constant. 

#### The Dither Algorithm 

The signal dithering algorithm used in Cryo-con’s digital control loop first generates a dither signal that is a random number within the range of ± 0.5 of a quantization level. This is then added to the loop output value just before placing it in the DAC. 

If the sum of the desired output plus the dither value is above the midpoint between Q2 and Q3, the DAC will output Q3. If it is below the midpoint, the DAC will Q4 output Q2. Therefore, the DAC output to toggles randomly between Q2 and Q3, but the number of times at one level vs. the other is weighted by how Q3 ~~~~ close the desired output is to the  nearest quantization level. 

<!-- Start of picture text -->
Q4<br>Q3 <br><br>Q2 <br>Q1<br><!-- End of picture text -->

In this example, the desired output is 25% of the distance from Q3 to Q2. Therefore, 75% of the DAC output samples will be Q3 and the remaining at Q2. 

Most importantly, the average value of the DAC output converges to the desired output loop value. 

224 

Model 32 / 32B User's Manual 

Appendix C: Application Note on Signal Dither. 

Using this dither technique, the control loop output accuracy will improve as the number of averages increases; up to the limits imposed by the other elements of the control loop. 

Fortunately, the number of samples averaged in a given system is proportional to its closed-loop bandwidth, which can be controlled by adjusting PID parameters. 

#### How much improvement does dither provide? 

Dither causes the average value of the control loop output to converge to the actual desired output. How close depends on the number of averages accumulated within the closed-loop system. 

The accuracy of an estimate of average value for a fixed number of samples is given by the Chi-squared distribution. The ‘degrees of freedom’ used by this function is the number of samples accumulated. 

Using the Cryo-con Model 32, the loop output rate is 10 samples per second. Therefore, if the process being controlled has a time constant on the order of 1.6 seconds, a total of 16 samples will be averaged, resulting in a factor of four improvement in control accuracy. This is equivalent to adding two bits to the output DAC. 

Since the Model 32 uses a 16-bit output DAC, a 1.6 second closed-loop time constant will result in the equivalent of an 18-bit DAC. Note that 1.6 seconds is an extremely short time constant for a cryogenic temperature process. 

**Further Reading:** “Introduction to Signal Processing”, Sophocles J. Orfanidis, August 1995. Prentice Hall **,** ISBN: 0-13-209172-0 http://www.ece.rutgers.edu/~orfanidi/intro2sp/ 

225 

Model 32 / 32B User's Manual 

Appendix D: Tuning Control Loops 

## Appendix D: Tuning Control Loops 

### Introduction 

Tuning PID loops to maintain high accuracy control can be a laborious process since the time-constants in cryogenic systems are often long. Further, some systems must operate over a very wide range of temperature, requiring different PID settings at different setpoints. 

The following is a guide to various methods of obtaining PID control loop coefficients. 

### Various methods for obtaining PID coefficients 

#### The system provider 

If your controller was received as part of a cryogenic system, the PID control loops should already be setup for optimum control. If the system operates over a wide range of temperature, it will use one of the available Table control modes where PID values are listed for different setpoints. 

If the installed PID values do not provide stable control, you should contact the system manufacturer for assistance. 

#### Taking PID values from a different controller 

If the PID values required to control a system are known from a different type controller, these values may be useful. 

The Proportional, or P term is a unit-less gain factor. There is no industry standard definition for it and, therefore, it can vary significantly from one manufacturer to another. If the P term does not work well when used directly, try a using the value divided by ten. For further assistance, please contact Cryo-con support. 

The Integral, or I term is in units of Seconds and should be the same for different controllers. Note however that some manufacturers use a ‘Reset’ value instead of directly using an Integral term. In this case, the Integral term is just the inverse of the Reset value. 

The Derivative, or D gain term is in units of inverse Seconds and should be the same for various controllers. 

#### Using Factory Default PID values 

Controllers are shipped from the factory with very conservative PID values. They will give stable control in a wide range of systems, but will have very slow response times. 

Often, the factory values provide a good start for the autotune process. The values are: P 0.1, I 5.0 and D 0.0. 

#### Autotuning 

Autotuning is the easiest way to obtain PID values, or optimize existing ones. Please review the Autotuning section of this manual. 

227 

Model 32 / 32B User's Manual 

Appendix D: Tuning Control Loops 

#### Manual Tuning 

The final, and most laborious method of tuning a control loop is manual tuning. This involves generating values for P, I and D by observing the system’s response to the stimulus of the heater output. 

Various methods of manually tuning the controller are described below. 

### Manual Tuning Procedures 

Manually tuning a PID control loop is relatively simple. It is greatly assisted by use of a data-logging program, such as the Cryo-con utility software package described in the Cryo-con Utility Software section. 

#### Ziegler-Nichols Frequency Response Method 

This method is based on the assumption that a critically damped system is optimal and the fact that stability and noise must be traded for response time. It requires driving your system into temperature oscillation. Care should be taken so that this oscillation does not cause damage. 

Enable the Over Temperature Disconnect feature of the controller if you are concerned about possible damage from overheating. 

1. Enter a setpoint value that is a typical for the envisaged use of the system. Select a heater range that is safe for your equipment. Set initial PID values of Pgain=0.1, Igain=0 and Dgain=0. 

2. Engage the control loops by pressing the **Control** key. 

3. Increase the Pgain term until the system is just oscillating. Note the Pgain setting as the Ultimate Gain, _Kc_ , and the period of oscillation as the Ultimate Period, _Tc_ . 

4. Set the PID values according to the following table: 

|Control Type|**Pgain**|**Igain**|**Dgain**|
|---|---|---|---|
|P only|0.5*_Kc_|0|0|
|**PI only**|0.4*_Kc_|0.8*_Tc_|0|
|**PID**|0.6*_Kc_|0.5*_Tc_|0.85*_Tc_|

5. Wait for the system to stabilize. If the resultant heater power output reading is less than 10% of full scale, select the next lower heater range setting. A range change will not require re-tuning. 

 **Note:** In systems where there is high thermal noise, including cryocoolers, a Dgain value of zero is often used. The Dterm is a derivative action, which can introduce additional noise into the control process. 

228 

Model 32 / 32B User's Manual 

Appendix D: Tuning Control Loops 

#### Alternate Methods 

There are various other methods to manually tune PID loops. Most are based on graphical techniques and all use a stimulus-response technique. 

For further reading: 

Automatic Tuning of PID controllers Instrument Society of America 67 Alexander Dr PO Box 12277 Research Triangle Park, NC 27709 

229 

Model 32 / 32B User's Manual 

Appendix E: Sensor Calibration Curve Tables 

## Appendix E: Sensor Calibration Curve Tables Cryocon S700 Silicon Diode 

The Cryocon S700 Silicon Diode sensor with a 10 µ A excitation current. 

||**Volts**|**Temp(K**)||**Volts**|**Temp(K**)||**Volts**|**Temp(K**)|
|---|---|---|---|---|---|---|---|---|
|1|0.1633|475.0000|41|0.6393|260.0000|81|1.2510|18.00000|
|2|0.1733|470.0000|42|0.6586|250.0000|82|1.2720|17.00000|
|3|0.1834|465.0000|43|0.6807|240.0000|83|1.2950|16.00000|
|4|0.1935|460.0000|44|0.7040|230.0000|84|1.3280|15.00000|
|5|0.2038|455.0000|45|0.7238|220.0000|85|1.3650|14.00000|
|6|0.2141|450.0000|46|0.7461|210.0000|86|1.4150|13.00000|
|7|0.2246|445.0000|47|0.7682|200.0000|87|1.4700|12.00000|
|8|0.2351|440.0000|48|0.7916|190.0000|88|1.5270|11.00000|
|9|0.2458|435.0000|49|0.8133|180.0000|89|1.5750|10.00000|
|10|0.2565|430.0000|50|0.8338|170.0000|90|1.5990|9.50000|
|11|0.2673|425.0000|51|0.8547|160.0000|91|1.6230|9.00000|
|12|0.2781|420.0000|52|0.8753|150.0000|92|1.6540|8.50000|
|13|0.2891|415.0000|53|0.8977|140.0000|93|1.6670|8.00000|
|14|0.3001|410.0000|54|0.9198|130.0000|94|1.6840|7.50000|
|15|0.3111|405.0000|55|0.9373|120.0000|95|1.7080|7.00000|
|16|0.3222|400.0000|56|0.9542|110.0000|96|1.7310|6.50000|
|17|0.3334|395.0000|57|0.9768|100.0000|97|1.7500|6.00000|
|18|0.3446|390.0000|58|0.9865|95.00000|98|1.7690|5.50000|
|19|0.3558|385.0000|59|0.9950|90.00000|99|1.7850|5.00000|
|20|0.3671|380.0000|60|1.0050|85.00000|100|1.7970|4.75000|
|21|0.3784|375.0000|61|1.0144|80.00000|101|1.8000|4.50000|
|22|0.3897|370.0000|62|1.0241|75.00000|102|1.8090|4.25000|
|23|0.4011|365.0000|63|1.0325|70.00000|103|1.8160|4.00000|
|24|0.4125|360.0000|64|1.0420|65.00000|104|1.8210|3.75000|
|25|0.4239|355.0000|65|1.0506|60.00000|105|1.8270|3.50000|
|26|0.4353|350.0000|66|1.0587|55.00000|106|1.8340|3.25000|
|27|0.4467|345.0000|67|1.0673|50.00000|107|1.8390|3.00000|
|28|0.4581|340.0000|68|1.0753|45.00000|108|1.8460|2.75000|
|29|0.4695|335.0000|69|1.0842|40.00000|109|1.8520|2.50000|
|30|0.4808|330.0000|70|1.0870|38.00000|110|1.8560|2.25000|
|31|0.4922|325.0000|71|1.0904|36.00000|111|1.8590|2.00000|
|32|0.5035|320.0000|72|1.0941|34.00000|112|1.8630|1.75000|
|33|0.5148|315.0000|73|1.0974|32.00000|113|1.8660|1.50000|
|34|0.5261|310.0000|74|1.1011|30.00000||||
|35|0.5373|305.0000|75|1.1054|28.00000||||
|36|0.5485|300.0000|76|1.1108|26.00000||||
|36|0.5596|295.0000|77|1.1238|24.00000||||
|38|0.5707|290.0000|78|1.1650|22.00000||||
|39|0.5900|280.0000|79|1.2070|20.00000||||
|40|0.6131|270.0000|80|1.2290|19.00000||||

#### S700 Silicon Diode Connections 

The S700BB is a Silicon Diode temperature sensor. Connection is made using a color-coded four-wire, 36 AWG cryogenic ribbon cable. 

Wires may be separated by dipping in Isopropyl Alcohol and then wiping clean. 

231 

Model 32 / 32B User's Manual 

Appendix E: Sensor Calibration Curve Tables 

Insulation is Formvar™ and is difficult to strip. Techniques include use of a mechanical stripper, scrapping with a razor blade and passing the wire quickly over a low flame. 

|**S700**|**Cable Color Codes**|
|---|---|
|**V+**|Clear|
|**V-**|Green|
|**I+**|Black|
|**I-**|Red|

**Table 39: S700 Cable Color Codes** 

#### S700 Mounting 

The S700BB bobbin is easily mounted with a #4-40 brass screw. A brass screw is recommended because thermal stress will be reduced at cryogenic temperature. 

The mounting surface should be clean. A rinse with Isopropyl Alcohol is recommended. 

First, apply a small amount of Apiezon™ N grease to the threads of the screw and on the mounting surface of the sensor package. 

Next, place the bobbin on the mounting surface, insert screw through bobbin and lightly tighten. 

232 

## INDEX 

|AC power.............................................17, 21, 74|
|---|
|connection....................................................68|
|cord.....................................................7, 74, 75|
|frequency........................5, 41, 43, 87, 88, 148<br>|
|fuses.............................................................69|
|low voltage..................................................222<br>|
|noise.............................................................93|
|power entry module....................................101|
|requirements.................................................54|
|smart on/off...................................................17|
|Voltage Selection..........................................69|
|Adding a new sensor.......................................78|
|alarm....................................................................|
|audible..........................................67, 165, 205|
|clearing.........................................................28|
|conditions......................................................32|
|enable...................................................30, 162|
|high setpoint.................................................30|
|hysteresis......................................................32|
|hysterisis.....................................159, 160, 161<br>|
|latched....................................................30, 32|
|LED...............................................................22|
|low setpoint...................................................30|
|output............................................................67|
|sensor fault.................................................164<br>|
|setpoint.................................30, 160, 161, 163|
|setup.............................................................32<br>|
|status....................................................19, 159|
|viewing..........................................................28|
|ASCII......................................................133, 138|
|autocalibrate..........................................145, 204|
|Autotune..........66, 194, 195, 196, 197, 198, 209|
|Autotune...............................................................<br>|
|remote commands......................................193|
|Autotuning........................................................80|
|modes...........................................................80|
|pre-tuning......................................................81|
|setup.............................................................82|
|Beep command..............................................142|
|bias voltage selection......................................32|
|CALCUR commands.....................................183|
|CALDATA commands....................................190|

|CalGen(..........................31, 63, 93, 96, 103, 114|
|---|
|CalGen(................................................................|
|Diode Sensor................................................97|
|Pt. Sensor.....................................................99<br>|
|setup.............................................................96|
|thermocouple................................................99<br>|
|calibration curve47, 92, 103, 185, 188, 189, 208<br>|
|CONFIG commands......................................151|
|constant-voltage...............................................55|
|CONTROL command............................139, 141|
|CONTROL key.................................................11|
|Control LED.....................................................22|
|control type selection.......................................36|
|control types...................................................171|
|CRV........................................................103, 106<br>|
|Cryocooler............................................................|
|synchronous subtraction..............................87|
|thermal signature..........................................87|
|current excitation..............................................55|
|Curve 340..............................................103, 106|
|data logging............................................103, 111|
|configuration................................................111|
|Derivative gain.................................................35<br>|
|differentiator gain term...................................176|
|Display.................................................................<br>|
|brightness.....................................................42<br>|
|configuration...........................................22, 29|
|Dual Input Status..........................................29|
|Dual Loop Status..........................................29|
|Loop Status...................................................29|
|resolution................................23, 42, 149, 204|
|Statistics.......................................................29|
|time-constant................................................41|
|Dither................................................................65|
|Electrical Isolation............................................63|
|Enclosure.........................................................74|
|Enclosure.............................................................|
|dimensions....................................................54|
|weight............................................................54|
|ENTER key......................................................20|
|enumeration fields...........................................19|
|ESC key...........................................................20|

|ESE................................................136, 137, 203|
|---|
|ESR.......................................135, 136, 138, 203|
|Factory Defaults.................................................5|
|restoring........................................................15|
|firmware...............................................................|
|forcing download...........................................16|
|revision level.......................1, 6, 138, 148, 204|
|update.................................................103, 118|
|fuse replacement.............................................69|
|fuses..........................................................69, 75|
|GPIB..........43, 67, 134, 135, 136, 137, 143, 144|
|Hardware Revision Level...........................6, 147|
|Heater..................................................................|
|control modes...............................................36|
|Dgain......................................................34, 35|
|fault.................................................65, 67, 146|
|Igain........................................................34, 35|
|load...............................................................38|
|load resistance.......................................34, 64|
|maximum output......4, 37, 173, 177, 178, 179|
|maximum setpoint..........................35, 37, 179|
|output......................................................64, 65|
|Pgain.......................................................34, 35|
|<br>Pman......................................................34, 35|
|range............................36, 44, 46, 64, 66, 173|
|read-back..............................................65, 177|
|resistance selection......................................38|
|Safe Operating Area.....................................64|
|setpoint.......11, 21, 34, 46, 169, 170, 207, 228|
|setpoint ........................................................35|
|setpoint entry................................................27|
|shut down.....................................................64|
|source selection............................................35|
|status............................................................23|
|HOME key........................................................22|
|IEEE-488....5, 67, 103, 131, 137, 143, 144, 203,<br>222|
|IEEE-488..............................................................|
|address.......................................................143|
|connection....................................................73|
|input channels..................................55, 153, 205|
|INPUT commands.........................................153|
|input protection................................................63|
|input setup.......................................................30|
|input statistics..................................................32|

|Instrument Calibration...........................123, 199|
|---|
|Instrument Calibration..........................................|
|Calibration Interval......................................123|
|Calibration Services....................................123|
|Password....................................................125|
|Procedure...................................................123|
|Instrument Status Enable......................134, 135|
|Instrument Status Register............................134|
|integrator gain term........................................175|
|ISE 134, 135, 136|
|ISR134, 135, 136|
|keypad keys.....................................................20|
|LogOhms.........................................................79|
|Loop #1........................................................4, 64|
|connection....................................................73|
|range selection.............................................36|
|setup.............................................................33|
|Loop #2............................................................33|
|connection....................................................73|
|LOOP commands..........................................169|
|loop status........................................................25|
|manual control mode...........35, 36, 66, 180, 181|
|Multiplier field.......................................47, 58, 78|
|NTC resistor.....................................................56|
|OPC command..............................................138|
|Operate Display...............................................22|
|OTD..................................................................42|
|OTD......................................................................|
|enable...........................................................40|
|setpoint.........................................................41|
|source...........................................................40|
|OTDisconn.......................................................25|
|output power limit.............................................37|
|Over Temperature Disconnect.........................25|
|Overtemp.........................................................25|
|OVERTEMP commands................................181|
|PID|
|coefficient.............................................44, 193|
|configuration.................................................35|
|control...................................................66, 171|
|loop...............................................................66|
|mode.............................................................64|
|Table..37, 44, 64, 66, 103, 110, 171, 172, 186,|
|188, 189, 208|
|<br>Table index selection....................................37|

|zone..............................................................44|
|---|
|PID Table..............................................................|
|File Format..................................................186|
|PIDTABLE commands...................................186|
|POWER key.....................................................11|
|proportional gain..............................35, 175, 207|
|Protective Ground............................................68|
|Ramping...........................................................85|
|Algorithm.......................................................86|
|operation.......................................................85|
|rate selection................................................38|
|Setup.............................................................86|
|Ratiometric.......................................................55|
|Readback.........................................................25|
|Real Time Monitor..........................................110|
|Remote LED............................................22, 141|
|remote transactions.............................................|
|viewing..........................................................43|
|RS-232...............................................43, 67, 144|
|RS-232.................................................................|
|connection....................................................73|
|RST command...............................................138|
|S700...........................................................8, 231|
|Color Codes................................................231|
|mounting.....................................................232|
|SCPI.................................................................67|
|command header...............................133, 134|
|common command.............................133, 137|
|compound command..................................133|
|keyword truncation......................................134|
|simple command........................................133|
|sensor..................................................................|
|calibration curve.........................................183|
|connection................................51, 63, 70, 217|
|self-heating.............................................55, 56|
|setup.............................................................47|
|table index....................................................47|
|type.....................................................191, 208|
|type selection..........................................31, 47|
|units......................................................31, 154|
|Sensor Calibration Curve......106, 109, 185, 208|
|Sensor Calibration Curve.....................................|
|file format....................................................183|
|Sensor Setup Menu.......................................190|
|SensorFlt..........................................................25|

|Single-Point-Ground..............................101, 102|
|---|
|Standard Event Register................................135|
|Standard Event Status Enable..............137, 203|
|STB........................................................135, 136|
|STOP command....................................139, 141|
|STOP key.........................................................11|
|Supported Sensors..........................................51|
|Synchronous Filter...........................................87|
|Configuration................................................43|
|Setup.............................................................88|
|Viewing.........................................................88|
|SYS-Auto Ctl....................................................43|
|SYSTEM commands.....................................140|
|Table control mode..............................37, 44, 66|
|Temperature.........................................................|
|coefficient......................................................47|
|history...........................................................32|
|ramp....................................................174, 207|
|units selection...............................................31|
|variance........................................................32|
|zones............................................................66|
|Temperature Sensors..........................................|
|CD-12A.................................................12, 213|
|Cernox(...............................51, 57, 58, 61, 215|
|DT-470..................................................12, 213|
|DT-670..................................................12, 213|
|Gallium-Arsenide..........................................57|
|Germanium...................................................58|
|NTC...............................................................57|
|NTC resistor..................................................58|
|Platinum........................................................58|
|PT10K...................................................12, 213|
|PT1K.....................................................12, 213|
|Rhodium-Iron..................................12, 57, 213|
|RO-600.................................................12, 213|
|RTD................................................12, 57, 213|
|Ruthenium Oxide......................12, 57, 58, 213|
|S700..............................................................12|
|SI-410...................................................12, 213|
|Silicon Diode.........................................57, 213|
|Thermistors...................................................58|
|thermocouple................................................57|
|Thermocouple......................92, 94, 96, 114, 204|
|Thermocouple......................................................|
|Addingnew types.........................................92|

|Calibration Errors..........................................93|
|---|
|Cold Junction Compensation.......................92|
|connection..............................................72, 92|
|Errors............................................................92|
|Grounded......................................................94|
|Offset Calibration..........................................93|
|Options...........................................................6|
|types.............................................................73|
|Unit Name......................................................147|

|User Configurations...................................19, 39|
|---|
|restore...........................................................39|
|save..............................................................39|
|select............................................................39|
|Utility Software.................................................79|
|VFD display......................................................17|
|zone table.........................................................44|
|*IDN?.....................................................138, 203|
|*OPC?....................................................138, 203|

