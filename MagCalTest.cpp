// Used in Arduino for the soft iron and hard iron test calibrations which will be used along with MotionCal
#include <Wire.h>
#include <Adafruit_LIS3MDL.h>
#include <Adafruit_Sensor.h>

Adafruit_LIS3MDL lis3mdl;

void setup(void) {
Serial.begin(115200);
while (!Serial) delay(10);

Serial.println(F("Initializing LIS3MDL Magnetometer for MotionCal..."));

// Initialize I2C for SDA=GP4 and SCL=GP5
Wire.setSDA(4);
Wire.setSCL(5);
Wire.begin();

// Initialize LIS3MDL sensor
if (!lis3mdl.begin_I2C()) {
Serial.println("Failed to find LIS3MDL chip");
while (1);
}

Serial.println("LIS3MDL Magnetometer found!");
}

void loop() {
sensors_event_t event;
lis3mdl.getEvent(&event);

// Send raw data for use in MotionCal
Serial.print("Raw:");
Serial.print(int(event.magnetic.x * 10)); Serial.print(",");
Serial.print(int(event.magnetic.y * 10)); Serial.print(",");
Serial.print(int(event.magnetic.z * 10)); Serial.println("");

delay(100);

}