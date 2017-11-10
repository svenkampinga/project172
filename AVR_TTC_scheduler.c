/*
 * AVR_TTC_scheduler.c
 *
 * Created: 10-11-2017
 *  Author: Gaauwe en Steven
 */ 

#include <avr/io.h> 
#include <util/delay.h>
#include "AVR_TTC_scheduler.h"
#include <serial_OUT.h>
#include <serial_IN.h>
#include <stdio.h>
#include <uart.h>



// The array of tasks
sTask SCH_tasks_G[SCH_MAX_TASKS];


#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#ifndef BAUD
#define BAUD 9600
#endif
#include <util/setbaud.h>





void SCH_Dispatch_Tasks(void)
{
   unsigned char Index;

   // Dispatches (runs) the next task (if one is ready)
   for(Index = 0; Index < SCH_MAX_TASKS; Index++)
   {
      if((SCH_tasks_G[Index].RunMe > 0) && (SCH_tasks_G[Index].pTask != 0))
      {
         (*SCH_tasks_G[Index].pTask)();  // Run the task
         SCH_tasks_G[Index].RunMe -= 1;   // Reset / reduce RunMe flag

         // Periodic tasks will automatically run again
         // - if this is a 'one shot' task, remove it from the array
         if(SCH_tasks_G[Index].Period == 0)
         {
            SCH_Delete_Task(Index);
         }
      }
   }
}

/*------------------------------------------------------------------*-
  SCH_Add_Task()
  Causes a task (function) to be executed at regular intervals 
  or after a user-defined delay
  pFunction - The name of the function which is to be scheduled.
              NOTE: All scheduled functions must be 'void, void' -
              that is, they must take no parameters, and have 
              a void return type. 
                   
  DELAY     - The interval (TICKS) before the task is first executed
  PERIOD    - If 'PERIOD' is 0, the function is only called once,
              at the time determined by 'DELAY'.  If PERIOD is non-zero,
              then the function is called repeatedly at an interval
              determined by the value of PERIOD (see below for examples
              which should help clarify this).
  RETURN VALUE:  
  Returns the position in the task array at which the task has been 
  added.  If the return value is SCH_MAX_TASKS then the task could 
  not be added to the array (there was insufficient space).  If the
  return value is < SCH_MAX_TASKS, then the task was added 
  successfully.  
  Note: this return value may be required, if a task is
  to be subsequently deleted - see SCH_Delete_Task().
  EXAMPLES:
  Task_ID = SCH_Add_Task(Do_X,1000,0);
  Causes the function Do_X() to be executed once after 1000 sch ticks.            
  Task_ID = SCH_Add_Task(Do_X,0,1000);
  Causes the function Do_X() to be executed regularly, every 1000 sch ticks.            
  Task_ID = SCH_Add_Task(Do_X,300,1000);
  Causes the function Do_X() to be executed regularly, every 1000 ticks.
  Task will be first executed at T = 300 ticks, then 1300, 2300, etc.            
 
-*------------------------------------------------------------------*/

unsigned char SCH_Add_Task(void (*pFunction)(), const unsigned int DELAY, const unsigned int PERIOD)
{
   unsigned char Index = 0;

   // First find a gap in the array (if there is one)
   while((SCH_tasks_G[Index].pTask != 0) && (Index < SCH_MAX_TASKS))
   {
      Index++;
   }

   // Have we reached the end of the list?   
   if(Index == SCH_MAX_TASKS)
   {
      // Task list is full, return an error code
      return SCH_MAX_TASKS;  
   }

   // If we're here, there is a space in the task array
   SCH_tasks_G[Index].pTask = pFunction;
   SCH_tasks_G[Index].Delay =DELAY;
   SCH_tasks_G[Index].Period = PERIOD;
   SCH_tasks_G[Index].RunMe = 0;

   // return position of task (to allow later deletion)
   return Index;
}

/*------------------------------------------------------------------*-
  SCH_Delete_Task()
  Removes a task from the scheduler.  Note that this does
  *not* delete the associated function from memory: 
  it simply means that it is no longer called by the scheduler. 
 
  TASK_INDEX - The task index.  Provided by SCH_Add_Task(). 
  RETURN VALUE:  RETURN_ERROR or RETURN_NORMAL
-*------------------------------------------------------------------*/

unsigned char SCH_Delete_Task(const unsigned char TASK_INDEX)
{
   // Return_code can be used for error reporting, NOT USED HERE THOUGH!
   unsigned char Return_code = 0;

   SCH_tasks_G[TASK_INDEX].pTask = 0;
   SCH_tasks_G[TASK_INDEX].Delay = 0;
   SCH_tasks_G[TASK_INDEX].Period = 0;
   SCH_tasks_G[TASK_INDEX].RunMe = 0;

   return Return_code;
}

/*------------------------------------------------------------------*-
  SCH_Init_T1()
  Scheduler initialisation function.  Prepares scheduler
  data structures and sets up timer interrupts at required rate.
  You must call this function before using the scheduler.  
-*------------------------------------------------------------------*/

void SCH_Init_T1(void)
{
   unsigned char i;

   for(i = 0; i < SCH_MAX_TASKS; i++)
   {
      SCH_Delete_Task(i);
   }

   // Set up Timer 1
   // Values for 1ms and 10ms ticks are provided for various crystals

   // Hier moet de timer periode worden aangepast ....!
   OCR1A = (uint16_t)625;   		     // 10ms = (256/16.000.000) * 625
   TCCR1B = (1 << CS12) | (1 << WGM12);  // prescale op 64, top counter = value OCR1A (CTC mode)
   TIMSK1 = 1 << OCIE1A;   		     // Timer 1 Output Compare A Match Interrupt Enable
}

/*------------------------------------------------------------------*-
  SCH_Start()
  Starts the scheduler, by enabling interrupts.
  NOTE: Usually called after all regular tasks are added,
  to keep the tasks synchronised.
  NOTE: ONLY THE SCHEDULER INTERRUPT SHOULD BE ENABLED!!! 
 
-*------------------------------------------------------------------*/

void SCH_Start(void)
{
      sei();
}

/*------------------------------------------------------------------*-
  SCH_Update
  This is the scheduler ISR.  It is called at a rate 
  determined by the timer settings in SCH_Init_T1().
-*------------------------------------------------------------------*/

ISR(TIMER1_COMPA_vect)
{
   unsigned char Index;
   for(Index = 0; Index < SCH_MAX_TASKS; Index++)
   {
      // Check if there is a task at this location
      if(SCH_tasks_G[Index].pTask)
      {
         if(SCH_tasks_G[Index].Delay == 0)
         {
            // The task is due to run, Inc. the 'RunMe' flag
            SCH_tasks_G[Index].RunMe += 1;

            if(SCH_tasks_G[Index].Period)
            {
               // Schedule periodic tasks to run again
               SCH_tasks_G[Index].Delay = SCH_tasks_G[Index].Period;
               SCH_tasks_G[Index].Delay -= 1;
            }
         }
         else
         {
            // Not yet ready to run: just decrement the delay
            SCH_tasks_G[Index].Delay -= 1;
         }
      }
   }
}

// ------------------------------------------------------------------


               
			
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
	PORTB &= ~_BV(2);
	PORTB &= ~_BV(3);
	PORTB |= _BV(1);
	_delay_ms(10000);
}	

void ledBlauw(){
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(2);
	PORTB |= _BV(3);
	_delay_ms(10000);
	PORTB &= _BV(1);
	PORTB &= ~_BV(2);
	PORTB &= ~_BV(3);
	_delay_ms(10000);
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(2);
	PORTB |= _BV(3);
	_delay_ms(10000);
	PORTB &= _BV(1);
	PORTB &= ~_BV(2);
	PORTB &= ~_BV(3);
	_delay_ms(10000);
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(2);
	PORTB |= _BV(3);
	_delay_ms(10000);
	PORTB &= _BV(1);
	PORTB &= ~_BV(2);
	PORTB &= ~_BV(3);
	_delay_ms(10000);
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(2);
	PORTB |= _BV(3);
	_delay_ms(10000);
	PORTB &= _BV(1);
	PORTB &= ~_BV(2);
	PORTB &= ~_BV(3);
	_delay_ms(10000);
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(2);
	PORTB |= _BV(3);
	_delay_ms(10000);
}

void ledGroen(){
	PORTB &= ~_BV(1);
	PORTB &= ~_BV(3);
	PORTB |= _BV(2);
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

void read_serial(){
	char input2[1];
	char input;
	input = getchar();
	sprintf(input2, "%c", input);
	
	if (strchr(input2, '0') != NULL)
	{
		ledGroen();
	} else if (strchr(input2, '1') != NULL){
		ledRood();
	} else if (strchr(input2, '2') != NULL){
		ledBlauw();
		ledRood();
	} else if (strchr(input2, '3') != NULL){
		ledBlauw();
		ledGroen();
	}
}	
			
void read_light_sensor(){
	int reading = ReadADC(0);
	char reader[50];
	sprintf(reader, "%i", reading);

	puts(reader);
}


void read_temp(){
	ADMUX &= ~_BV(MUX0); // Set channel point to port 0
	ADCSRA |= _BV(ADSC); // Start adc measurement
	loop_until_bit_is_clear(ADCSRA, ADSC); // proceed when done

	int temp = (((float)ADCW * 5000 / 1024) - 500) / 10;
	
	char reader[50];
	sprintf(reader, "%i", temp);
	
	puts(reader);
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

int main(void){ 
				SCH_Init_T1();
				InitADC();
				uart_init();
				stdout = &uart_output;
				stdin  = &uart_input;
				DDRB = 0xFF;
				
				char input;
				
				
				ledTest();
				ledGroen();
				SCH_Add_Task(read_light_sensor, 100, 100);
				SCH_Add_Task(read_serial, 200, 100);
				
								
				SCH_Start();
				
				while(1){
				SCH_Dispatch_Tasks();
				}
				
				return 0;

            }
