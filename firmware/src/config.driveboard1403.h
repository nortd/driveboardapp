/*
  config.h - compile time configuration
  Part of DriveboardFirmware

  Copyright (c) 2009-2011 Simen Svale Skogsrud
  Copyright (c) 2011 Sungeun K. Jeon
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

#ifndef config_h
#define config_h

#include <inttypes.h>
#include <stdbool.h>

#define VERSION 1705               // int or float
#define BAUD_RATE 57600
// #define ENABLE_3AXES            // enable/disable 3-axis mode (vs 2-axis)
#define ENABLE_LASER_INTERLOCKS    // enable/disable all interlocks

// PWM_MODE enumeration
#define STATIC_FREQ 0
#define STEPPED_FREQ_PD5 1
#define STEPPED_FREQ_PD6 2
#define SYNCED_FREQ 3
// #define STATIC_PWM_FREQ 5000    // only works with LASER_PWM_BIT == 5

// #define SENSE_INVERT                     // invert how sense input is interpreted
#define PWM_MODE STEPPED_FREQ_PD6
#define CONFIG_BEAMDYNAMICS              // adjust intensity during accel/decel
#define CONFIG_BEAMDYNAMICS_START 0.05   // 0-1.0, offset after which to apply
#define CONFIG_BEAMDYNAMICS_EVERY 16     // freq as multiples of steps impulses


#define CONFIG_X_STEPS_PER_MM 88.88888888 //microsteps/mm
#define CONFIG_Y_STEPS_PER_MM 90.90909090 //microsteps/mm
#define CONFIG_Z_STEPS_PER_MM 33.33333333 //microsteps/mm
#define CONFIG_PULSE_MICROSECONDS 5
#define CONFIG_FEEDRATE 8000.0 // in millimeters per minute
#define CONFIG_SEEKRATE 8000.0
#define CONFIG_HOMINGRATE 600  // ms/pulse
#define CONFIG_ACCELERATION 1800000.0 // mm/min^2, typically 1000000-8000000, divide by (60*60) to get mm/sec^2
#define CONFIG_JUNCTION_DEVIATION 0.006 // mm
#define CONFIG_X_ORIGIN_OFFSET 5.0  // mm, x-offset of table origin from physical home
#define CONFIG_Y_ORIGIN_OFFSET 5.0  // mm, y-offset of table origin from physical home
#define CONFIG_Z_ORIGIN_OFFSET 0.0   // mm, z-offset of table origin from physical home
#define CONFIG_INVERT_X_AXIS 0  // 0 is regular, 1 inverts the y direction
// jet's y-axis is backwards
#define CONFIG_INVERT_Y_AXIS 0  // 0 is regular, 1 inverts the y direction
#define CONFIG_INVERT_Z_AXIS 1  // 0 is regular, 1 inverts the y direction


#define SENSE_DDR               DDRD
#define SENSE_PORT              PORTD
#define SENSE_PIN               PIND
#define CHILLER_BIT             3           // Arduino: 3
#define DOOR_BIT                2           // Arduino: 2

#define ASSIST_DDR              DDRD
#define ASSIST_PORT             PORTD
#define AIR_ASSIST_BIT          4           // Arduino: 4
#define LASER_PWM_BIT           6           // Arduino: 6
#define AUX_ASSIST_BIT          7           // Arduino: 7

#define LIMIT_DDR               DDRC
#define LIMIT_PORT              PORTC
#define LIMIT_PIN               PINC
#define X1_LIMIT_BIT            0           // Arduino: A0
#define X2_LIMIT_BIT            1           // Arduino: A1
#define Y1_LIMIT_BIT            2           // Arduino: A2
#define Y2_LIMIT_BIT            3           // Arduino: A3
#define Z1_LIMIT_BIT            4           // Arduino: A4
#define Z2_LIMIT_BIT            5           // Arduino: A5

#define STEPPING_DDR            DDRB
#define STEPPING_PORT           PORTB
#define X_STEP_BIT              0           // Arduino: 8
#define Y_STEP_BIT              1           // Arduino: 9
#define Z_STEP_BIT              2           // Arduino: 10
#define X_DIRECTION_BIT         3           // Arduino: 11
#define Y_DIRECTION_BIT         4           // Arduino: 12
#define Z_DIRECTION_BIT         5           // Arduino: 13


#define SENSE_MASK ((1<<CHILLER_BIT)|(1<<DOOR_BIT))
#define LIMIT_MASK ((1<<X1_LIMIT_BIT)|(1<<X2_LIMIT_BIT)|(1<<Y1_LIMIT_BIT)|(1<<Y2_LIMIT_BIT)|(1<<Z1_LIMIT_BIT)|(1<<Z2_LIMIT_BIT))
#define STEPPING_MASK ((1<<X_STEP_BIT)|(1<<Y_STEP_BIT)|(1<<Z_STEP_BIT))
#define DIRECTION_MASK ((1<<X_DIRECTION_BIT)|(1<<Y_DIRECTION_BIT)|(1<<Z_DIRECTION_BIT))

// figure out INVERT_MASK
// careful! direction pins hardcoded here
// (1<<X_DIRECTION_BIT) | (1<<Y_DIRECTION_BIT) | (1<<Z_DIRECTION_BIT)
#if CONFIG_INVERT_X_AXIS && CONFIG_INVERT_Y_AXIS && CONFIG_INVERT_Z_AXIS
  #define INVERT_MASK 56U
#elif CONFIG_INVERT_X_AXIS && CONFIG_INVERT_Y_AXIS
  #define INVERT_MASK 24U
#elif CONFIG_INVERT_Y_AXIS && CONFIG_INVERT_Z_AXIS
  #define INVERT_MASK 48U
#elif CONFIG_INVERT_X_AXIS && CONFIG_INVERT_Z_AXIS
  #define INVERT_MASK 40U
#elif CONFIG_INVERT_X_AXIS
  #define INVERT_MASK 8U
#elif CONFIG_INVERT_Y_AXIS
  #define INVERT_MASK 16U
#elif CONFIG_INVERT_Z_AXIS
  #define INVERT_MASK 32U
#else
  #define INVERT_MASK 0U
#endif



// The temporal resolution of the acceleration management subsystem. Higher number give smoother
// acceleration but may impact performance.
// NOTE: Increasing this parameter will help any resolution related issues, especially with machines
// requiring very high accelerations and/or very fast feedrates. In general, this will reduce the
// error between how the planner plans the motions and how the stepper program actually performs them.
// However, at some point, the resolution can be high enough, where the errors related to numerical
// round-off can be great enough to cause problems and/or it's too fast for the Arduino. The correct
// value for this parameter is machine dependent, so it's advised to set this only as high as needed.
// Approximate successful values can range from 30L to 100L or more.
#define ACCELERATION_TICKS_PER_SECOND 200L

// Minimum planner junction speed. Sets the default minimum speed the planner plans for at the end
// of the buffer and all stops. This should not be much greater than zero and should only be changed
// if unwanted behavior is observed on a user's machine when running at very slow speeds.
#define ZERO_SPEED 0.0 // (mm/min)

// Minimum stepper rate. Sets the absolute minimum stepper rate in the stepper program and never runs
// slower than this value, except when sleeping. This parameter overrides the minimum planner speed.
// This is primarily used to guarantee that the end of a movement is always reached and not stop to
// never reach its target. This parameter should always be greater than zero.
#define MINIMUM_STEPS_PER_MINUTE 1600U // (steps/min) - Integer value only
// 1600 @ 32step_per_mm = 50mm/min


#define X_AXIS 0
#define Y_AXIS 1
#define Z_AXIS 2

#define clear_vector(a) memset(a, 0, sizeof(a))
#define clear_vector_double(a) memset(a, 0.0, sizeof(a))
#define max(a,b) (((a) > (b)) ? (a) : (b))
#define min(a,b) (((a) < (b)) ? (a) : (b))


#endif



// bit math
// see: http://www.arduino.cc/playground/Code/BitMath
// see: http://graphics.stanford.edu/~seander/bithacks.html
//
// y = (x >> n) & 1; // n=0..15. stores nth bit of x in y. y becomes 0 or 1.
//
// x &= ~(1 << n); // forces nth bit of x to be 0. all other bits left alone.
//
// x &= (1<<(n+1))-1; // leaves alone the lowest n bits of x; all higher bits set to 0.
//
// x |= (1 << n); // forces nth bit of x to be 1. all other bits left alone.
//
// x ^= (1 << n); // toggles nth bit of x. all other bits left alone.
//
// x = ~x; // toggles ALL the bits in x.
