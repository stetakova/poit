#define vystup 3
float value = 5;

void setup()
{
  Serial.begin(9600);
  pinMode(vystup, OUTPUT); 
}

void loop(){
  float voltage1, voltage2, value;
  int low=1;
  
  voltage1 = (float)analogRead(A2)*5/1023;
  voltage2 = (float)analogRead(A4)*5/1023;
  float rozdiel=voltage1-voltage2;

  delay(500);
  if(rozdiel<0.02){
  digitalWrite(vystup, LOW);
  int low=1;
  }
  if(rozdiel == 0.00 && low==1){
    digitalWrite(vystup, HIGH);
  }
  delay(500);
  Serial.println(rozdiel);
  
 if(Serial.read() != -1){
    value = Serial.read();
  } 
}
