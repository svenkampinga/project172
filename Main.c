/*
 * GccApplication1.c
 *
 * Created: 2-11-2017 11:45:50
 *  Author: gaauwe
 */ 
//tx serial

#include <avr/io.h> 
#include <util/delay.h>
#include <AVR_TTC_scheduler.h>
#include <serial_OUT.h>
#include <serial_IN.h>

#include <stdio.h>


#include <uart.h>



#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#ifndef BAUD
#define BAUD 9600
#endif
#include <util/setbaud.h>



#define BUAD_RATE_CALC ((F_CPU/16/BUAD) - 1)  
#define buffer_size 128
#define boolen 0



            int main(void){ 
				InitADC();
				uart_init();
				stdout = &uart_output;
				stdin  = &uart_input;
				DDRB = 0xFF;
				
				char input;
				
				ledTest();
				
				while(1){
				int x;
				
				//input = getchar();
				
				/*
				if (strchr(input, '0') != NULL)
				{
					printf("%c\n", input);
					ledTest();
				}
				*/
				
				
				//char str[6];
				//snprintf(str, 6, "%d", x); 
				//read_light_sensor();
				//_delay_ms(10000);
				
				char reader[50];
				sprintf(reader, "%i", gettemp());

				//strcat(reader, " C");
				puts(reader);
				
				/*
				if(gettemp() >= 26){
					ledRood();
				} else if (gettemp() >= 24){
					ledGeel();
				} else if (gettemp() >= 20){
					ledGroen();
				}*/
				
				
				if(read_light_sensor() >= 300){
					PORTB &= ~_BV(2);
					PORTB &= ~_BV(3);
					PORTB |= _BV(1);
					_delay_ms(10000);
				} else if (read_light_sensor() >= 100){
					PORTB &= ~_BV(1);
					PORTB &= ~_BV(3);
					PORTB |= _BV(2);
					_delay_ms(10000);
				} else if (read_light_sensor() == 0){
					ledTest();
				} else if (read_light_sensor() >= 0){
					PORTB &= ~_BV(1);
					PORTB &= ~_BV(2);
					PORTB |= _BV(3);
					_delay_ms(10000);
				}					
				
				//getdistance();
				
				}

            }   
			
void ledTest(){
	PORTB &= ~_BV(2);
	PORTB &= ~_BV(3);
	PORTB |= _BV(1);
	_delay_ms(5000);
	PORTB &= ~_BV(3);
	PORTB |= _BV(1);
	PORTB |= _BV(2);
	_delay_ms(5000);
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(3);
	PORTB |= _BV(2);
	_delay_ms(5000);
	PORTB &= ~_BV(1);
	PORTB |= _BV(2);
	PORTB |= _BV(3);
	_delay_ms(5000);
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(2);
	PORTB |= _BV(3);
	_delay_ms(5000);
	PORTB &= ~_BV(2);
	PORTB |= _BV(1);
	PORTB |= _BV(3);
	_delay_ms(5000);

	
	
	
}	

void ledRood(){
	PORTB |= _BV(0);
	_delay_ms(10000);
	PORTB &= ~_BV(0);
	_delay_ms(10000);
}	

void ledGeel(){
	PORTB |= _BV(1);
	_delay_ms(10000);
	PORTB &= ~_BV(1);
	_delay_ms(10000);
}

void ledGroen(){
	PORTB |= _BV(2);
	_delay_ms(10000);
	PORTB &= ~_BV(2);
	_delay_ms(10000);
}
	
			
uint16_t ReadADC(uint8_t ADCchannel)
{
	//select ADC channel with safety mask
	ADMUX = (ADMUX & 0xF0) | (ADCchannel & 0x0F);
	//single conversion mode
	ADCSRA |= (1<<ADSC);
	// wait until ADC conversion is complete
	while( ADCSRA & (1<<ADSC) );
	return ADC;
}

void InitADC()
{
	// Select Vref=AVcc
	ADMUX |= (1<<REFS0);
	//set prescaller to 128 and enable ADC
	ADCSRA |= (1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0)|(1<<ADEN);
}
			
int read_light_sensor(){
	int reading = ReadADC(0);
	
	/*
	char reader[50];
	sprintf(reader, "%i", reading);
	
	serialWrite("|L");
	serialWrite(reader);
	serialWrite("|\n");
	*/
	return reading;
}


int gettemp(){
	ADMUX &= ~_BV(MUX0); // Set channel point to port 0
	ADCSRA |= _BV(ADSC); // Start adc measurement
	loop_until_bit_is_clear(ADCSRA, ADSC); // proceed when done

	int temp = (((float)ADCW * 5000 / 1024) - 500) / 10;
	
	return temp;
}

void getdistance(){
	DDRB = 0x00;
	PORTB |= _BV(PB0);
	_delay_us(10);
	PORTB &= ~_BV(PB0);

	loop_until_bit_is_set(PINB, PB1);
	TCNT1 = 0;
	loop_until_bit_is_clear(PINB, PB1);
	unsigned int count = TCNT1;
	
	int distance = ((int)count / 16) / 58;

	//char reader[50];
	//sprintf(reader, "%i", distance);
	
	send_serial("hello");
}

void uart_init(void) {
	UBRR0H = UBRRH_VALUE;
	UBRR0L = UBRRL_VALUE;
	
	#if USE_2X
	UCSR0A |= _BV(U2X0);
	#else
	UCSR0A &= ~(_BV(U2X0));
	#endif

	UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); /* 8-bit data */
	UCSR0B = _BV(RXEN0) | _BV(TXEN0);   /* Enable RX and TX */
}

void uart_putchar(char c, FILE *stream) {
	if (c == '\n') {
		uart_putchar('\r', stream);
	}
	loop_until_bit_is_set(UCSR0A, UDRE0);
	UDR0 = c;
}

char uart_getchar(FILE *stream) {
	loop_until_bit_is_set(UCSR0A, RXC0);
	return UDR0;
}
			
void send_serial(char text[]){
				char br;
                char ar[]= "Hello";
                char buffer[10]; 
                //High and low bits
                UBRR0H = (BUAD_RATE_CALC >> 8); 
                UBRR0L = BUAD_RATE_CALC; 
                //////////////// 
                //transimit and recieve enable
                UCSR0B = (1 << TXEN0)| (1 << TXCIE0) | (1 << RXEN0) | (1 << RXCIE0); 
                UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);  //8 bit data format
                ////////////////////////////////////////////////////////////////
                int i = 0;

                while (1){  
                /*while( (UCSR0A & (1<<RXC0))  == 0 ){}; 
                    br = UDR0;
                */

                while (( UCSR0A & (1<<UDRE0))  == 0){};

                        for (i = 0; i < strlen(text); i++){ 
                            while (( UCSR0A & (1<<UDRE0))  == 0){};
                            UDR0 = text[i]; 
                            if (i == (strlen(text) - 1)){ 
                                return 0;
                            }
                        } 
                }
}

