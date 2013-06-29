/*
  AnalogReadSerial
  Reads an analog input on pin 0, prints the result to the serial monitor.
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.
 
 This example code is in the public domain.
 */

const int BUFFER_SIZE = 10;
int buffer[BUFFER_SIZE];

const int THRESHOLD = 6;

int ticksSinceTriggered = 0;

int led = 13;
int MIN_WAIT = 30;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
}

// the loop routine runs over and over again forever:
void loop() {
  int minValue = 1024;
  int maxValue = 0;
  for(int i = 0; i < BUFFER_SIZE; ++i) {
    int value = analogRead(A0);
    //buffer[i] = value;
    minValue = min(minValue, value);
    maxValue = max(maxValue, value);
  }
  // print out the value you read:
  int diff = maxValue - minValue;
  boolean above = diff > THRESHOLD;
  if(above) {
    if(ticksSinceTriggered > MIN_WAIT) {
      ticksSinceTriggered = 0;
      Serial.println(diff);
    }
  }
  digitalWrite(led, ticksSinceTriggered <= MIN_WAIT ? HIGH : LOW);
  ++ticksSinceTriggered;
}

