#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>


uint8_t data[14];
RF24 radio(9, 10);
uint16_t delay1 = 100;
uint16_t delay2 = 1;
unsigned long while_counter = 0;
uint8_t received = 1;
uint8_t chan_counter = 0;
const uint8_t channels_all[5] = {90,95,100,105,110};
uint8_t channels[5];
uint8_t sensors[5];
unsigned long t1;
unsigned long t2;
bool isReady = false;
uint8_t num = 0;

void setup(void) {
  // initiate USART with 1M baudrate
  Serial.begin(1000000);

  // initiate nRF24L01 
  radio.begin();
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_1MBPS);
  radio.setCRCLength(RF24_CRC_8);
  radio.setPayloadSize(14);
  radio.setAutoAck(false);
  radio.openReadingPipe(1, 0xC1C2C2C2C2LL);
  radio.startListening();


  // receiving a code from GUI for configuration of Timer and Channels
  TCNT0  = 0;
  TIMSK0 = 0;
  sei();
  String conf;
  while(!Serial.available());
  while (Serial.available()){
  if(Serial.available()){
    char c = Serial.read();
    conf += c;
  }}
  if (conf.length() >0)
  {

    if(conf[0] == 'n'){
      bool flag = true;
      switch(conf[1]){
        case '1':
          num = 1;
          break;
        case '2':
          num = 2;
          break;
        case '3':
          num = 3;
          break;
        case '4':
          num = 4;
          break;
        case '5':
          num = 5;
          break;
        default:
          flag = false;
          break;
      }
     
      if(flag){
        for(int i=0; i<num; i++){
          switch(conf[i+2]){
            case '1':
              channels[i] = channels_all[0];
              break;
            case '2':
              channels[i] = channels_all[1];
              break;
            case '3':
              channels[i] = channels_all[2];
              break;
            case '4':
              channels[i] = channels_all[3];
              break;
            case '5':
              channels[i] = channels_all[4];
              break;
          }
          isReady = true;
        //  Serial.println(conf[i+2]);
        }
              
        Serial.println("rrr");
        _delay_ms(3000);   
      }
    }
    
  }

  // initiate Timer 
  cli();
  if(isReady){

    if (num == 5)
      OCR0A = 124;
    if (num == 4)
      OCR0A = 155;
    if (num == 3)
      OCR0A = 207;
    if (num == 2){
      OCR0A = 77;
      TCCR0B |= (1 << CS00);}
    if (num == 1){
      OCR0A = 155;
      TCCR0B |= (1 << CS00);}
     
    TCCR0A |= (1 << WGM01); // ctc mode
    TCCR0B |= (1 << CS02);   // prescaler 256
    TIMSK0 |= (1 << OCIE0A);
    sei();
  }  
}


ISR(TIMER0_COMPA_vect)
{ 
  radio.setChannel(channels[chan_counter]);
  radio.startListening();
 // delayMicroseconds(delay1);
  while_counter = 0;
  received = 1;
  while ( !radio.available() )
  {
  //  delayMicroseconds(delay2);
    while_counter++;
    if (while_counter > 150)
     {
      received = 0;
      break;
     }
  }
  if (received)
  {
  radio.read(&data, sizeof(data));
  Serial.write(data[12]); Serial.write(data[13]);
  Serial.write(data[0]); Serial.write(data[1]);
  Serial.write(data[2]); Serial.write(data[3]);
  Serial.write(data[4]); Serial.write(data[5]);
  Serial.write(data[6]); Serial.write(data[7]);
  Serial.write(data[8]); Serial.write(data[9]);
  Serial.write(data[10]); Serial.write(data[11]);
  Serial.write(101);Serial.write(102);Serial.write(103);
  }
  else{
    Serial.write(101);Serial.write(102);Serial.write(103);
  }

  radio.stopListening();
  chan_counter++;
  if(chan_counter == num)
    chan_counter = 0; 
}


void loop(void)
{
}
  
  
