/*
  AnalogReadSerial
  Reads an analog input on pin 0, prints the result to the serial monitor.
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.
 
 This example code is in the public domain.
 */

const int BUFFER_SIZE = 10;
int buffer[BUFFER_SIZE];

const int THRESHOLD = 12;

int ticksSinceTriggered = 0;

const int led = 13;
const int MIN_WAIT = 300;

int position = 0;
int sum = 0;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  for(int i = 0; i < BUFFER_SIZE; ++i) {
    buffer[i] = 0;
  }
}

// the loop routine runs over and over again forever:
void loop() {
  int value = analogRead(A0);
  sum -= buffer[position];
  buffer[position] = value;
  sum += value;
  position = (position + 1) % BUFFER_SIZE;

  int diff = value * BUFFER_SIZE - sum;

  boolean above = diff >= THRESHOLD * BUFFER_SIZE;
  if(above && ticksSinceTriggered > MIN_WAIT) {
    ticksSinceTriggered = 0;
    Serial.println(diff);
  }
  digitalWrite(led, ticksSinceTriggered <= MIN_WAIT ? HIGH : LOW);
  ++ticksSinceTriggered;
}

