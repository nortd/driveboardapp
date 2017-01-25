/*
  sense_control.h - sensing and controlling inputs and outputs
  Part of DriveboardFirmware

  Copyright (c) 2011-2016 Stefan Hechenberger

  DriveboardFirmware is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  DriveboardFirmware is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
*/

#include <avr/io.h>
#include <util/delay.h>
#include <math.h>
#include <stdlib.h>
#include "sense_control.h"
#include "stepper.h"
#include "planner.h"


static uint8_t pwmTop;
static uint8_t clockSelectBits;


void sense_init() {
  //// chiller, door
  SENSE_DDR &= ~(SENSE_MASK);  // set as input pins
  // SENSE_PORT |= SENSE_MASK;    //activate pull-up resistors

  //// x1_lmit, x2_limit, y1_limit, y2_limit, z1_limit, z2_limit
  LIMIT_DDR &= ~(LIMIT_MASK);  // set as input pins
  // LIMIT_PORT |= LIMIT_MASK;    //activate pull-up resistors
}


void control_init() {
  //// air and aux assist control
  ASSIST_DDR |= (1 << AIR_ASSIST_BIT);   // set as output pin
  control_air_assist(false);

  //// laser control
  #ifdef DRIVEBOARD_USB
    //// laser control
    // PWM with timer0 on PD5
    // see: http://arduino.cc/en/Tutorial/SecretsOfArduinoPWM
    // see: https://sites.google.com/site/qeewiki/books/avr-guide/pwm-on-the-atmega328
    DDRD |= _BV(PORTD5); // set PD5 as an output
    // use pwm mode 5, phase-corrected, non-inverted
    // count from 0 to OCR0A and OCR0A to 0, output LOW while counter above OCR0B
    TCCR0B = _BV(WGM02);
    TCCR0A = _BV(WGM00);
    // TCCR0A |= _BV(COM0A1);  // output to PD6 (OC0A), non-inverted
    TCCR0A |= _BV(COM0B1);  // output to PD5 (OC0B), non-inverted
    // counter and prescaler
    TCNT0 = 0;  // initialize counter to 0
    TCCR0B |= _BV(CS01);  // prescaler: 8
    // initial frequency
    control_laser_frequency(3910);
    // laser high/low mode
    ASSIST_DDR |= (1 << LASER_HIGHLOW_BIT);   // set as output pin
    control_laser_highlow(true);
  #else
    //// laser control
    // Setup Timer0 for a 488.28125Hz "phase correct PWM" wave (assuming a 16Mhz clock)
    // Timer0 can pwm either PD5 (OC0B) or PD6 (OC0A), we use PD6
    // TCCR0A and TCCR0B are the registers to setup Timer0
    // see chapter "8-bit Timer/Counter0 with PWM" in Atmga328 specs
    // OCR0A sets the duty cycle 0-255 corresponding to 0-100%
    // also see: http://arduino.cc/en/Tutorial/SecretsOfArduinoPWM
    DDRD |= (1 << DDD6);    // set PD6 as an output
    OCR0A = 0;              // set PWM to a 0% duty cycle
    TCCR0A = _BV(COM0A1) | _BV(WGM00);   // phase correct PWM mode
    // TCCR0A = _BV(COM0A1) | _BV(WGM01) | _BV(WGM00);  // fast PWM mode
    // prescaler: PWMfreq = 16000/(2*256*prescaler)
    // TCCR0B = _BV(CS00);                // 1 => 31.3kHz
    // TCCR0B = _BV(CS01);                // 8 => 3.9kHz
    TCCR0B = _BV(CS01) | _BV(CS00);    // 64 => 489Hz
    // TCCR0B = _BV(CS02);                // 256 => 122Hz
    // TCCR0B = _BV(CS02) | _BV(CS00);    // 1024 => 31Hz
    // NOTES:
    // PPI = PWMfreq/(feedrate/25.4/60)

    ASSIST_DDR |= (1 << AUX1_ASSIST_BIT);  // set as output pin
    control_aux1_assist(false);
    ASSIST_DDR |= (1 << AUX2_ASSIST_BIT);  // set as output pin
    control_aux2_assist(false);
  #endif
}

inline void control_laser_frequency(long freq) {
  long cycles = (F_CPU/freq);                                                   // cycles for counter to reach TOP (OCR0A)
  cycles >>= 1;                                                                 // divide by 2, phase correct PWM implicitly doubles cycles
  // TCCR0B = _BV(WGM02);                                                          // reset timer registers
  // TCCR0A = _BV(WGM00);                                                          // reset timer registers
  if(cycles < 256) { clockSelectBits = _BV(CS00); }                             // no prescale, full xtal
  else if((cycles >>= 3) < 256) { clockSelectBits = _BV(CS01); }                // prescale by /8
  else if((cycles >>= 3) < 256) { clockSelectBits = _BV(CS01) | _BV(CS00); }    // prescale by /64
  else if((cycles >>= 2) < 256) { clockSelectBits = _BV(CS02); }                // prescale by /256
  else if((cycles >>= 2) < 256) { clockSelectBits = _BV(CS02) | _BV(CS00); }    // prescale by /1024
  else { cycles = 256 - 1, clockSelectBits = _BV(CS02) | _BV(CS00); }           // request was out of bounds, set as maximum
  OCR0A = pwmTop = cycles;                                                      // OCR0A is TOP in p & f correct pwm mode
}

inline void control_laser_intensity(uint8_t intensity) {
  #ifdef DRIVEBOARD_USB
    // map intensity 0-255 to 0-TOP
    uint16_t temp = intensity*pwmTop;
    OCR0B = temp >> 8;  // div by 256
  #else
    OCR0A = intensity;
  #endif
}


inline void control_air_assist(bool enable) {
  if (enable) {
    ASSIST_PORT |= (1 << AIR_ASSIST_BIT);
  } else {
    ASSIST_PORT &= ~(1 << AIR_ASSIST_BIT);
  }
}

#ifdef DRIVEBOARD_USB
  inline void control_laser_highlow(bool enable) {
    if (enable) {
      ASSIST_PORT |= (1 << LASER_HIGHLOW_BIT);
    } else {
      ASSIST_PORT &= ~(1 << LASER_HIGHLOW_BIT);
    }
  }
#else
  inline void control_aux1_assist(bool enable) {
    if (enable) {
      ASSIST_PORT |= (1 << AUX1_ASSIST_BIT);
    } else {
      ASSIST_PORT &= ~(1 << AUX1_ASSIST_BIT);
    }
  }

  inline void control_aux2_assist(bool enable) {
    if (enable) {
      ASSIST_PORT |= (1 << AUX2_ASSIST_BIT);
    } else {
      ASSIST_PORT &= ~(1 << AUX2_ASSIST_BIT);
    }
  }
#endif
