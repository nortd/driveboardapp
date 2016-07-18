/*
 *  PWM utilities for 16 bit Timer1 and 8 bit Timer0 and Timer2 on ATmega168/328
 *  this is based on the Timer1 library
 *      Original code by Jesse Tane for http://labs.ideo.com August 2008
 *  Modified March 2009 by Jérôme Despatis and Jesse Tane for ATmega328 support
 *  Adaptation by Christophe Nicolas on April 2009
 *
 *  This is free software. You can redistribute it and/or modify it under
 *  the terms of Creative Commons Attribution 3.0 United States License.
 *  To view a copy of this license, visit http://creativecommons.org/licenses/by/3.0/us/
 *  or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
 *
 */

#include <avr/io.h>
#include <avr/interrupt.h>

#define RESOLUTION8 256          // Timer0 and Timer2 are 8 bit
#define RESOLUTION16 65536      // Timer1 is 16 bit

class TimerPWM
{
  public:
  
    // properties
    unsigned int pwmPeriod0;
    unsigned int pwmPeriod1;
    unsigned int pwmPeriod2;
    unsigned char clockSelectBits0;
    unsigned char clockSelectBits1;
    unsigned char clockSelectBits2;

    // methods
    void initialize(int timer,long microseconds=1000000);
    void start(int timer);
    void stop(int timer);
    void pwm(int timer,char pin, int duty, long microseconds=-1);
    void disablePwm(int timer, char pin);
    void setPeriod(int timer, long microseconds);
    void setPwmDuty(int timer,char pin, int duty);
};
extern TimerPWM Tpwm;



Code:

/*
 *  PWM utilities for 16 bit Timer1 and 8 bit Timer0 and Timer2 on ATmega168/328
 *  this is based on the Timer1 library
 *      Original code by Jesse Tane for http://labs.ideo.com August 2008
 *  Modified March 2009 by Jérôme Despatis and Jesse Tane for ATmega328 support
 *  Adaptation by Christophe Nicolas on April 2009
 *
 *  This is free software. You can redistribute it and/or modify it under
 *  the terms of Creative Commons Attribution 3.0 United States License.
 *  To view a copy of this license, visit http://creativecommons.org/licenses/by/3.0/us/
 *  or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
 *
 */

#include "TimerPWM.h"

TimerPWM Tpwm;              // preinstatiate


void TimerPWM::initialize(int timer,long microseconds)
{
  switch(timer){
      case 0 :
            TCCR0A = _BV(WGM00);        // set mode as phase and frequency correct pwm, stop the timer
            TCCR0B = _BV(WGM02);        
        break;
      case 1 :
            TCCR1A = 0;                 // clear control register A
            TCCR1B = _BV(WGM13);        // set mode as phase and frequency correct pwm, stop the timer
      break;
      case 2 :
            TCCR2A = _BV(WGM20);
            TCCR2B = _BV(WGM22);        // set mode as phase and frequency correct pwm, stop the timer
            ASSR = 0;
      break;
      }
  setPeriod(timer,microseconds);
}

void TimerPWM::setPeriod(int timer,long microseconds)
{
  long cycles = (F_CPU * microseconds) / 2000000;                                // the counter runs backwards after TOP, interrupt is at BOTTOM so divide microseconds by 2
  switch(timer){
      case 0 :
            TCCR0B = _BV(WGM02);
            TCCR0A = _BV(WGM00);                                                                       // reset clock select register
            if(cycles < RESOLUTION8)              clockSelectBits0 = _BV(CS00);                    // no prescale, full xtal
            else if((cycles >>= 3) < RESOLUTION8) clockSelectBits0 = _BV(CS01);                    // prescale by /8
            else if((cycles >>= 3) < RESOLUTION8) clockSelectBits0 = _BV(CS01) | _BV(CS00);        // prescale by /64
            else if((cycles >>= 2) < RESOLUTION8) clockSelectBits0 = _BV(CS02);                    // prescale by /256
            else if((cycles >>= 2) < RESOLUTION8) clockSelectBits0 = _BV(CS02) | _BV(CS00);        // prescale by /1024
            else        cycles = RESOLUTION8 - 1, clockSelectBits0 = _BV(CS02) | _BV(CS00);        // request was out of bounds, set as maximum
            OCR0A = pwmPeriod0 = cycles;                                                           // OCR0A is TOP in p & f correct pwm mode
        break;
      case 1 :
            TCCR1B = _BV(WGM13);                                                                       // reset clock select register
            if(cycles < RESOLUTION16)              clockSelectBits1 = _BV(CS10);                    // no prescale, full xtal
            else if((cycles >>= 3) < RESOLUTION16) clockSelectBits1 = _BV(CS11);                    // prescale by /8
            else if((cycles >>= 3) < RESOLUTION16) clockSelectBits1 = _BV(CS11) | _BV(CS10);        // prescale by /64
            else if((cycles >>= 2) < RESOLUTION16) clockSelectBits1 = _BV(CS12);                    // prescale by /256
            else if((cycles >>= 2) < RESOLUTION16) clockSelectBits1 = _BV(CS12) | _BV(CS10);        // prescale by /1024
            else          cycles = RESOLUTION16 - 1, clockSelectBits1 = _BV(CS12) | _BV(CS10);  // request was out of bounds, set as maximum
            ICR1 = pwmPeriod1 = cycles;                                                           // ICR1 is TOP in p & f correct pwm mode
      break;
      case 2 :
            TCCR2B = _BV(WGM22);                                                                                         // reset clock select register
            TCCR2A = _BV(WGM20);
            if(cycles < RESOLUTION8)              clockSelectBits2 = _BV(CS20);                                      // no prescale, full xtal
            else if((cycles >>= 3) < RESOLUTION8) clockSelectBits2 = _BV(CS21);                                      // prescale by /8
            else if((cycles >>= 2) < RESOLUTION8) clockSelectBits2 = _BV(CS21) | _BV(CS20);                          // prescale by /32
            else if((cycles >>= 1) < RESOLUTION8) clockSelectBits2 = _BV(CS22);                                      // prescale by /64
            else if((cycles >>= 1) < RESOLUTION8) clockSelectBits2 = _BV(CS22) | _BV(CS20);                          // prescale by /128
            else if((cycles >>= 1) < RESOLUTION8) clockSelectBits2 = _BV(CS22) | _BV(CS21);                          // prescale by /256
            else if((cycles >>= 2) < RESOLUTION8) clockSelectBits2 = _BV(CS22)  | _BV(CS21) | _BV(CS20);        // prescale by /1024
            else        cycles = RESOLUTION8 - 1, clockSelectBits2 = _BV(CS22)  | _BV(CS21) | _BV(CS20);        // request was out of bounds, set as maximum
            OCR2A = pwmPeriod2 = cycles;                                                                             // OCR2A is TOP in p & f correct pwm mode
      break;
      }
}

void TimerPWM::setPwmDuty(int timer,char pin, int duty)
{
  unsigned long dutyCycle;
  switch(timer){
      case 0 :
            dutyCycle = pwmPeriod0;
            dutyCycle *= duty;
            dutyCycle >>= 10;
            if(pin == 5) OCR0B = dutyCycle;
        break;
      case 1 :
            dutyCycle = pwmPeriod1;
            dutyCycle *= duty;
            dutyCycle >>= 10;
            if(pin == 1 || pin == 9)       OCR1A = dutyCycle;
            else if(pin == 2 || pin == 10) OCR1B = dutyCycle;
      break;
      case 2 :
            dutyCycle = pwmPeriod2;
            dutyCycle *= duty;
            dutyCycle >>= 10;
            if(pin == 3) OCR2B = dutyCycle;
      break;
      }
}

void TimerPWM::pwm(int timer,char pin, int duty, long microseconds)  // expects duty cycle to be 10 bit (1024)
{
  if(microseconds > 0) setPeriod(timer,microseconds);
  switch(timer){
      case 0 :
            if(pin == 5) {
                  DDRD |= _BV(PORTD5);                  // sets data direction register for pwm output pin
                  TCCR0A |= _BV(COM0B1);                  // activates the output pin
                  }
            setPwmDuty(0,pin, duty);
            start(0);
        break;
      case 1 :
            if(pin == 1 || pin == 9) {
                  DDRB |= _BV(PORTB1);                  // sets data direction register for pwm output pin
                  TCCR1A |= _BV(COM1A1);               // activates the output pin
            }
            else if(pin == 2 || pin == 10) {
                  DDRB |= _BV(PORTB2);                  // sets data direction register for pwm output pin
                  TCCR1A |= _BV(COM1B1);                  // activates the output pin
            }
            setPwmDuty(1,pin, duty);
            start(1);
      break;
      case 2 :
            if(pin == 3) {
                  DDRD |= _BV(PORTD3);                  // sets data direction register for pwm output pin
                  TCCR2A |= _BV(COM2B1);                  // activates the output pin
            }
            setPwmDuty(2,pin, duty);
            start(2);
      break;
      }
}

void TimerPWM::disablePwm(int timer,char pin)
{
  switch(timer){
      case 0 :
            if(pin == 5) TCCR0A &= ~_BV(COM0B1);                                       // clear the bit that enables pwm on PD5
        break;
      case 1 :
            if(pin == 1 || pin == 9)       TCCR1A &= ~_BV(COM1A1);         // clear the bit that enables pwm on PB1
            else if(pin == 2 || pin == 10) TCCR1A &= ~_BV(COM1B1);         // clear the bit that enables pwm on PB2
      break;
      case 2 :
            if(pin == 3) TCCR2A &= ~_BV(COM2B1);                                       // clear the bit that enables pwm on PD3
      break;
      }
}

void TimerPWM::start(int timer)
{
  switch(timer){
      case 0 :
            TCNT0 = 0;
            TCCR0B |= clockSelectBits0;
      break;
      case 1 :
            TCNT1 = 0;
            TCCR1B |= clockSelectBits1;
      break;
      case 2 :
            TCNT2 = 0;
            TCCR2B |= clockSelectBits2;
      break;
      }
}

void TimerPWM::stop(int timer)
{
  switch(timer){
      case 0 :
            TCCR0B &= ~(_BV(CS00) | _BV(CS01) | _BV(CS02));          // clears all clock selects bits
      break;
      case 1 :
            TCCR1B &= ~(_BV(CS10) | _BV(CS11) | _BV(CS12));          // clears all clock selects bits
      break;
      case 2:
            TCCR2B &= ~(_BV(CS20) | _BV(CS21) | _BV(CS22));          // clears all clock selects bits
      break;
      }
}