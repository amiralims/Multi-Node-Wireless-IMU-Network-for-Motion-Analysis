/*
 * MPU.c
 *
 * Created: 9/17/2020 5:01:52 PM
 * Author : AmirAli
 */ 
#define F_CPU 8000000UL
#include <stdlib.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <util/delay.h>
#include <math.h>  
#include "mpu6050.h"
#include "nrf24l01.h"
#include "nrf24l01registers.h"

void sendc (char c);
void sends (char *s, int len);
void printinfo();

int main(void) {

	//nrf24l01 variables
	uint8_t bufferout[NRF24L01_PAYLOAD] ;
	uint8_t testUpOrDown = 0;
	uint8_t testSignal = 0;
	uint8_t buffer[14];
	
	
	//init uart
/*	  DDRD |= 1 << PIND1;
	  DDRD &= ~(1 << PIND0);
	  UBRRL = 51;
	  UCSRB = (1<<RXEN)|(1<<TXEN);
	  UCSRC = (1<<URSEL)|(3<<UCSZ0);
*/
	//init interrupt
	sei();

	//range switch
	DDRD &= ~((1<<DDRD2)|(1<<DDRD3)|(1<<DDRD4)|(1<<DDRD5));
	uint8_t gy_range = MPU6050_GYRO_FS_250;
	uint8_t ac_range = MPU6050_ACCEL_FS_2;
	if (PIND & (1<<PIND7)){
		if (PIND & (1<<PIND6)){
			ac_range = MPU6050_ACCEL_FS_16;
		}
		else{
			ac_range = MPU6050_ACCEL_FS_8;
		}
	}
	else{
		if (PIND & (1<<PIND6)){
			ac_range = MPU6050_ACCEL_FS_4;
		}
	}
	
	if (PIND & (1<<PIND3)){
		if (PIND & (1<<PIND2)){
			gy_range = MPU6050_GYRO_FS_2000;
		}
		else{
			gy_range = MPU6050_GYRO_FS_1000;
		}
	}
	else{
		if (PIND & (1<<PIND2)){
			gy_range = MPU6050_GYRO_FS_500;
		}
	}


	//init mpu6050
	mpu6050_init(gy_range,ac_range);
	_delay_ms(50);

	
	//init nrf24l01
	nrf24l01_init();
	nrf24l01_setTX();

	//sending buffer addresses
	uint8_t addrtx1[NRF24L01_ADDRSIZE] = NRF24L01_ADDRTX;
	nrf24l01_settxaddr(addrtx1);

	while(1) {

		uint8_t data[14] ={0};
		while(1) {
			mpu6050_readBit(MPU6050_RA_INT_STATUS, MPU6050_INTERRUPT_DATA_RDY_BIT, (uint8_t *)buffer);
			if(buffer[0])
			break;
		}
		mpu6050_readBytes(MPU6050_RA_ACCEL_XOUT_H, 14, (uint8_t *)buffer);
		
		uint8_t i = 0;
		for (i=0; i<6; i++){
			data[i] = buffer[i];
		}
		for (i=6; i<12; i++){
			data[i] = buffer[i+2];
		}
		
		// Sensor unit number (1...5). Must be the same NRF24L01_CH defined in nef24l01.h file
		data[12] = 2;
		
		// test signal
		if(testSignal == 100)
			testUpOrDown = 1;
		if(testSignal == 0)
			testUpOrDown = 0;
		if(!testUpOrDown)
			data[13] = testSignal++;
		else
			data[13] = testSignal--;
			
		nrf24l01_write(data);	
	}

}
/*
void sendc (char c)
{
	while (! (UCSRA & (1 << UDRE)) );
	{
		UDR = c;
	}
}

void sends (char *s, int len)
{
	for (int i=0; i<0; i++)
	sendc('.');
	for (int i=0; i<len; i++)
	{
		sendc(s[i]);
	}
}

void printinfo() {
	char buff[100];
	sends("info\r\n",6);
	sprintf(buff,"STATUS: %02X\r\n", nrf24l01_getstatus()); sends(buff,15);
	sprintf(buff,"CONFIG: %02X\r\n", nrf24l01_readregister(NRF24L01_REG_CONFIG)); sends(buff,15);
	sprintf(buff,"RF_CH: %02X\r\n", nrf24l01_readregister(NRF24L01_REG_RF_CH)); sends(buff,15);
	sprintf(buff,"RF_SETUP: %02X\r\n", nrf24l01_readregister(NRF24L01_REG_RF_SETUP)); sends(buff,15);
	sprintf(buff,"EN_AA: %02X\r\n", nrf24l01_readregister(NRF24L01_REG_EN_AA)); sends(buff,15);
	sprintf(buff,"EN_RXADDR: %02X\r\n", nrf24l01_readregister(NRF24L01_REG_EN_RXADDR)); sends(buff,15);
	sprintf(buff,"OBSERVE_TX: %02X\r\n", nrf24l01_readregister(NRF24L01_REG_OBSERVE_TX)); sends(buff,15);
	sprintf(buff,"TX_ADDR: %010X\r\n", nrf24l01_readregister(NRF24L01_REG_TX_ADDR)); sends(buff,25);
	sprintf(buff,"my_flag: %010X\r\n", NRF24L01_CH); sends(buff,25);
	sends("\r\n",3);
}*/