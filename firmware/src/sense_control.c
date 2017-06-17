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


// #ifdef STATIC_PWM_FREQ
#if PWM_MODE == STATIC_FREQ
  uint8_t pwmTop;
#elif PWM_MODE == SYNCED_FREQ
  static volatile uint8_t pwm_duty = 0;
#endif


void sense_init() {
  //// chiller, door
  SENSE_DDR &= ~(SENSE_MASK);  // set as input pins
  // SENSE_PORT |= SENSE_MASK;    //activate pull-up resistors

  //// x1_lmit, x2_limit, y1_limit, y2_limit, z1_limit, z2_limit
  LIMIT_DDR &= ~(LIMIT_MASK);  // set as input pins
  // LIMIT_PORT |= LIMIT_MASK;    //activate pull-up resistors
}


void control_init() {
  // #ifndef STATIC_PWM_FREQ
  #if PWM_MODE == SYNCED_FREQ
    ASSIST_DDR |= (1 << LASER_PWM_BIT);      // set as output pin
    // configure timer 0, pwm reset timer
    TCCR0A = 0; // Normal operation
    TCCR0B = 0; // Disable timer until needed.
    TIMSK0 |= (1<<TOIE0); // Enable Timer0 interrupt flag
    TCNT0 = 0;
  #elif PWM_MODE == STEPPED_FREQ_PD5
    ASSIST_DDR |= (1 << LASER_PWM_BIT);      // set as output pin
    // pwm mode 5, phase correct, TOP = OCR0A, set by WGMxx
    TCCR0B = _BV(WGM02);
    TCCR0A = _BV(WGM00);
    // output trigger, PD5 (OC0B), non-inverted, HIGH at bottom, LOW on Match
    TCCR0A |= _BV(COM0B1);
    OCR0A = 0xFF;                            // set TOP
    OCR0B = 0;                               // set PWM to a 0% duty cycle
  // #else
  #elif PWM_MODE == STEPPED_FREQ_PD6
    ASSIST_DDR |= (1 << LASER_PWM_BIT);      // set as output pin
    OCR0A = 0;                               // set PWM to a 0% duty cycle
    TCCR0A = _BV(COM0A1) | _BV(WGM00);       // phase correct PWM mode
    // TCCR0A = _BV(COM0A1) | _BV(WGM01) | _BV(WGM00);  // fast PWM mode
    // prescaler: PWMfreq = 16000/(2*256*prescaler)
    // TCCR0B = _BV(CS00);                // 1 => 31.3kHz
    // TCCR0B = _BV(CS01);                // 8 => 3.9kHz
    TCCR0B = _BV(CS01) | _BV(CS00);       // 64 => 489Hz
    // TCCR0B = _BV(CS02);                // 256 => 122Hz
    // TCCR0B = _BV(CS02) | _BV(CS00);    // 1024 => 31Hz
    // NOTES:
    // PPI = PWMfreq/(feedrate/25.4/60)
  // #else
  #elif PWM_MODE == STATIC_FREQ
    // Setup Timer0 for  to granular freq
    // also see: http://arduino.cc/en/Tutorial/SecretsOfArduinoPWM
    // see: https://sites.google.com/site/qeewiki/books/avr-guide/pwm-on-the-atmega328
    ASSIST_DDR |= (1 << LASER_PWM_BIT);   // set as output pin
    if (LASER_PWM_BIT == 5) {  // granular freq only works with PDS
      // pwm mode 5, phase correct, TOP = OCR0A, set by WGMxx
      TCCR0B = _BV(WGM02);
      TCCR0A = _BV(WGM00);
      // output trigger, PD5 (OC0B), non-inverted, HIGH at bottom, LOW on Match
      TCCR0A |= _BV(COM0B1);
      //// set frequency
      uint32_t cycles = (F_CPU/STATIC_PWM_FREQ);                            // cycles for counter to reach TOP (OCR0A)
      cycles >>= 1;                                                         // divide by 2, phase correct PWM implicitly doubles cycles
      if (cycles < 256) { TCCR0B |= _BV(CS00); }                            // no prescale, full xtal
      else if ((cycles >>= 3) < 256) { TCCR0B |= _BV(CS01); }               // prescale by /8
      else if ((cycles >>= 3) < 256) { TCCR0B |= _BV(CS01) | _BV(CS00); }   // prescale by /64
      else if ((cycles >>= 2) < 256) { TCCR0B |= _BV(CS02); }               // prescale by /256
      else if ((cycles >>= 2) < 256) { TCCR0B |= _BV(CS02) | _BV(CS00); }   // prescale by /1024
      else { cycles = 255, TCCR0B |= _BV(CS02) | _BV(CS00); }               // request was out of bounds, set as maximum
      OCR0A = pwmTop = cycles;                                              // OCR0A is TOP in p & f correct pwm mode
      // OCR0B in range 0-pwmTop sets the duty cycle
    }
  #endif

  //// air and aux assist control
  ASSIST_DDR |= (1 << AIR_ASSIST_BIT);   // set as output pin
  control_air_assist(false);
  ASSIST_DDR |= (1 << AUX_ASSIST_BIT);  // set as output pin
  control_aux_assist(false);
}


inline void control_laser_intensity(uint8_t intensity) {
  // #ifdef STATIC_PWM_FREQ
  #if PWM_MODE == STATIC_FREQ
    // adjust intensity
    #ifdef ENABLE_LASER_INTERLOCKS
      if (SENSE_DOOR_OPEN || SENSE_CHILLER_OFF) {
        OCR0B = 0;
      } else {
        OCR0B = (intensity*pwmTop)/255;
      }
    #else
      OCR0B = (intensity*pwmTop)/255;
    #endif
  #elif PWM_MODE == STEPPED_FREQ_PD5
    #ifdef ENABLE_LASER_INTERLOCKS
      if (SENSE_DOOR_OPEN || SENSE_CHILLER_OFF) {
        OCR0B = 0;
      } else {
        OCR0B = intensity;
      }
    #else
      OCR0B = intensity;
    #endif
    // depending on intensity adapt PWM freq
    // assuming phase correct PWM mode
    if (intensity > 40) {
      // set PWM freq to 3.9kHz
      TCCR0B = _BV(CS01);
    } else if (intensity > 10) {
      // set PWM freq to 489Hz
      TCCR0B = _BV(CS01) | _BV(CS00);
    } else {
      // set PWM freq to 122Hz
      TCCR0B = _BV(CS02);
    }
  // #else
  #elif PWM_MODE == STEPPED_FREQ_PD6
    #ifdef ENABLE_LASER_INTERLOCKS
      if (SENSE_DOOR_OPEN || SENSE_CHILLER_OFF) {
        OCR0A = 0;
      } else {
        OCR0A = intensity;
      }
    #else
      OCR0A = intensity;
    #endif
    // depending on intensity adapt PWM freq
    // assuming: TCCR0A = _BV(COM0A1) | _BV(WGM00);  // phase correct PWM mode
    if (intensity > 40) {
      // set PWM freq to 3.9kHz
      TCCR0B = _BV(CS01);
    } else if (intensity > 10) {
      // set PWM freq to 489Hz
      TCCR0B = _BV(CS01) | _BV(CS00);
    } else {
      // set PWM freq to 122Hz
      TCCR0B = _BV(CS02);
    }
  // #else
  #elif PWM_MODE == SYNCED_FREQ
    // adjust intensity
    #ifdef ENABLE_LASER_INTERLOCKS
      if (SENSE_DOOR_OPEN || SENSE_CHILLER_OFF || intensity == 0) {
        pwm_duty = 0;
        ASSIST_PORT &= ~(1 << LASER_PWM_BIT); // off
      } else {
        pwm_duty = intensity;
      }
    #else
      pwm_duty = intensity;
    #endif
  #endif
}


inline uint8_t control_get_intensity() {
  #if PWM_MODE == STATIC_FREQ
    return (OCR0B*255)/pwmTop;
  #elif PWM_MODE == STEPPED_FREQ_PD5
    return OCR0B;
  #elif PWM_MODE == STEPPED_FREQ_PD6
    return OCR0A;
  #elif PWM_MODE == SYNCED_FREQ
    return pwm_duty;
  #endif
}


inline void control_air_assist(bool enable) {
  if (enable) {
    ASSIST_PORT |= (1 << AIR_ASSIST_BIT);
  } else {
    ASSIST_PORT &= ~(1 << AIR_ASSIST_BIT);
  }
}

inline void control_aux_assist(bool enable) {
  if (enable) {
    ASSIST_PORT |= (1 << AUX_ASSIST_BIT);
  } else {
    ASSIST_PORT &= ~(1 << AUX_ASSIST_BIT);
  }
}
