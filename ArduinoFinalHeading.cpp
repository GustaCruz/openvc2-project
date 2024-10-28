// Final Heading Code used to test in Arduino IDE, other Final Heading Code writen in python
#define DEBUG 1

#include <Wire.h>
#include <Adafruit_LIS3MDL.h>
#include <Adafruit_Sensor.h>

// Hard-iron calibration settings (Change to values in MotionCal)
const float hard_iron[3] = {
0, 0, 0
};

// Soft-iron calibration settings (Change to values in MotionCal)
const float soft_iron[3][3] = {
{ 1, 0, 0 },
{ 0, 1, 0 },
{ 0, 0, 1 }
};

// Magnetic declination from magnetic-declination.com
const float mag_decl = 1.650;

Adafruit_LIS3MDL lis3mdl;

void setup() {
#if DEBUG
Serial.begin(115200);
while (!Serial) delay(10);
Serial.println("LIS3MDL compass test");
#endif

// Initialize I2C on GP4 (SDA) and GP5 (SCL)
Wire.setSDA(4);
Wire.setSCL(5);

// Initialize magnetometer
if (!lis3mdl.begin_I2C()) {
#if DEBUG
Serial.println("ERROR: Could not find magnetometer");
#endif
while (1) {
delay(1000);
}
}
}

void loop() {

static float hi_cal[3];
static float heading = 0;
sensors_event_t event;
lis3mdl.getEvent(&event);

float mag_data[] = {event.magnetic.x,
event.magnetic.y,
event.magnetic.z};

// Apply hard-iron offsets
for (uint8_t i = 0; i < 3; i++) {
hi_cal[i] = mag_data[i] - hard_iron[i];
}

for (uint8_t i = 0; i < 3; i++) {
mag_data[i] = (soft_iron[i][0] * hi_cal[0]) +
(soft_iron[i][1] * hi_cal[1]) +
(soft_iron[i][2] * hi_cal[2]);
}

// Calculate heading
heading = -1 * (atan2(mag_data[0], mag_data[1]) * 180) / M_PI;

// Apply magnetic declination
heading += mag_decl;

// Convert heading to 0..360 degrees
if (heading < 0) {
heading += 360;
}

#if DEBUG
Serial.print("[");
Serial.print(mag_data[0], 1);
Serial.print("\t");
Serial.print(mag_data[1], 1);
Serial.print("\t");
Serial.print(mag_data[2], 1);
Serial.print("] Heading: ");
Serial.println(heading, 2);
#endif

delay(100);

}