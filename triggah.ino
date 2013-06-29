
const int BUFFER_SIZE = 100;

//const int THRESHOLD = 2 * BUFFER_SIZE;
const int THRESHOLD = 1;

const int led = 13;
const int MIN_WAIT = 200;

int position = 0;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
}

class Trigger {
public:
  byte id;
  long buffer[BUFFER_SIZE];
  int sum;
  int ticksSinceTriggered = 0;

  Trigger(byte id) : id(id), sum(0) {
    for(int i = 0; i < BUFFER_SIZE; ++i) {
      buffer[i] = 0;
    }
  }
  int process(int value) {
    sum -= buffer[position];
    buffer[position] = value;
    sum += value;

    int diff = value * BUFFER_SIZE - sum;
    boolean above = diff >= THRESHOLD;
    if(above && ticksSinceTriggered > MIN_WAIT) {
      ticksSinceTriggered = 0;
      Serial.print((char)id);
      Serial.print(' ');
      Serial.println(diff);
    }
    else {
      ++ticksSinceTriggered;
    }
  }
  boolean isTriggered() {
    return ticksSinceTriggered <= MIN_WAIT;
  }
};

// the loop routine runs over and over again forever:
void loop() {
  Trigger trigger0('0');
  while(true) {
    trigger0.process(analogRead(A0));
    position = (position + 1) % BUFFER_SIZE;
    digitalWrite(led, trigger0.isTriggered() ? HIGH : LOW);
  }
}

