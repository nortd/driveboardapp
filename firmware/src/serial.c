/*
  serial.c - Low level functions for sending and recieving bytes via the serial port.
  Part of DriveboardFirmware

  Copyright (c) 2009-2011 Simen Svale Skogsrud
  Copyright (c) 2011 Sungeun K. Jeon
  Copyright (c) 2011-2016 Stefan Hechenberger

  Inspired by the wiring_serial module by David A. Mellis which
  used to be a part of the Arduino project.

  DriveboardFirmware is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  DriveboardFirmware is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
*/

#include <avr/interrupt.h>
#include <util/atomic.h>
#include <avr/sleep.h>
#include <avr/pgmspace.h>
#include <math.h>
#include "serial.h"
#include "config.h"
#include "stepper.h"
#include "protocol.h"



/** ring buffer **********************************
* [_][h][e][l][l][o][_][_][_] -> wrap around     *
*     |              |                           *
*    tail           head                         *
*    (read)        (write)                       *
*                                                *
* buffer empty condition: head == tail           *
* buffer full condition:  (head+1)%size == tail  *
* buffer write: if(!full) {buf[head] = item}     *
* buffer read:  if(!empty) {return buf[tail]}    *
*************************************************/
#define RX_BUFFER_SIZE 256
#define TX_BUFFER_SIZE 128
uint8_t rx_buffer[RX_BUFFER_SIZE];
volatile uint8_t rx_buffer_head = 0;
volatile uint8_t rx_buffer_tail = 0;

uint8_t tx_buffer[TX_BUFFER_SIZE];
volatile uint8_t tx_buffer_head = 0;
volatile uint8_t tx_buffer_tail = 0;

bool first_transmission = true;
uint8_t data_prev = 0;

bool buffer_underrun_marked = false;

#define RX_CHUNK_SIZE 16
volatile bool notify_chunk_processed = false;
uint8_t rx_buffer_processed = 0;

volatile bool raster_mode = false;
volatile bool consume_data = false;

uint8_t serial_read();


static void set_baud_rate(long baud) {
  uint16_t UBRR0_value = ((F_CPU / 16 + baud / 2) / baud - 1);
	UBRR0H = UBRR0_value >> 8;
	UBRR0L = UBRR0_value;
}



void serial_init() {
  set_baud_rate(BAUD_RATE);

	/* baud doubler off  - Only needed on Uno XXX */
  UCSR0A &= ~(1 << U2X0);

	// enable rx and tx
  UCSR0B |= 1<<RXEN0;
  UCSR0B |= 1<<TXEN0;

	// enable interrupt on complete reception of a byte
  UCSR0B |= 1<<RXCIE0;

	// defaults to 8-bit, no parity, 1 stop bit

  serial_write(INFO_HELLO);
}

void serial_stop() {
  raster_mode = false;
  consume_data = false;
}


inline void serial_write(uint8_t data) {
  // Calculate next head
  uint8_t next_head = tx_buffer_head + 1;
  if (next_head == TX_BUFFER_SIZE) { next_head = 0; }  // wrap around

  // wait, if buffer is full
  while (next_head == tx_buffer_tail) {
    // sleep_mode();
    // protocol_idle();  // don't call, may turn recursive
  }

  // Store data and advance head
  tx_buffer[tx_buffer_head] = data;
  tx_buffer_head = next_head;

	UCSR0B |=  (1 << UDRIE0);  // enable tx interrupt
}


inline void serial_write_param(uint8_t param, double val) {
  // val to be [-134217.728, 134217.727]
  // three decimals are retained
  int32_t numint = lround(val*1000)+134217728L;
  serial_write((numint&127UL)+128);
  serial_write(((numint&(127UL<<7))>>7)+128);
  serial_write(((numint&(127UL<<14))>>14)+128);
  serial_write(((numint&(127UL<<21))>>21)+128);
  serial_write(param);
}


// tx interrupt, called when UDR0 gets empty
SIGNAL(USART_UDRE_vect) {
  uint8_t tail = tx_buffer_tail;  // optimize for volatile

  if (notify_chunk_processed) {
    UDR0 = CMD_CHUNK_PROCESSED ;
    notify_chunk_processed = false;
  } else {                    // Send a byte from the buffer
    UDR0 = tx_buffer[tail];
    if (++tail == TX_BUFFER_SIZE) {tail = 0;}  // increment
    tx_buffer_tail = tail;
  }

  // disable tx interrupt, if buffer empty
  if (tail == tx_buffer_head) { UCSR0B &= ~(1 << UDRIE0); }
}


inline uint8_t serial_read() {
  // return data, advance tail
  uint8_t data = rx_buffer[rx_buffer_tail];
  if (++rx_buffer_tail == RX_BUFFER_SIZE) {rx_buffer_tail = 0;}  // increment
  // ATOMIC_BLOCK(ATOMIC_FORCEON) {
    rx_buffer_processed++;
    if (rx_buffer_processed == RX_CHUNK_SIZE) {
      notify_chunk_processed = true;
      UCSR0B |=  (1 << UDRIE0);  // enable tx interrupt
      rx_buffer_processed = 0;
    }
  // }
  return data;
}


// rx interrupt, called whenever a new byte is in UDR0
SIGNAL(USART_RX_vect) {
  uint8_t data = UDR0;
  // transmission error check
  if (first_transmission) {  // ignore data
    first_transmission = false;
    data_prev = data;
    return;
  } else {  // use, but check with previous
    first_transmission = true;
    if (data != data_prev) {
      stepper_request_stop(STOPERROR_TRANSMISSION_ERROR);
    }
  }
  // handle char
  if (data < 16) {  // handle controls chars
    if (data == CMD_STOP) {
      // special stop character, bypass buffer
      stepper_request_stop(STOPERROR_SERIAL_STOP_REQUEST);
    } else if (data == CMD_RESUME) {
      // special resume character, bypass buffer
      raster_mode = false;
      consume_data = false;
      rx_buffer_head = rx_buffer_tail = 0;  // reset rx buffer
      rx_buffer_processed = 0;
      stepper_stop_resume();
    } else if (data == CMD_STATUS) {
      protocol_request_status();
    } else if (data == CMD_SUPERSTATUS) {
      protocol_request_superstatus();
    } else {
      stepper_request_stop(STOPERROR_INVALID_MARKER);
    }
  } else {
    uint8_t head = rx_buffer_head;  // optimize for volatile
    uint8_t next_head = head + 1;
    if (next_head == RX_BUFFER_SIZE) {next_head = 0;}
    if (next_head == rx_buffer_tail) {
      // buffer is full, other side sent too much data
      stepper_request_stop(STOPERROR_RX_BUFFER_OVERFLOW);
    } else {
      rx_buffer[head] = data;
      rx_buffer_head = next_head;
    }
  }
}


inline uint8_t serial_protocol_read() {
  // called from protocol loop
  while (raster_mode) {
    // Block while in raster mode.
    // In this mode the serial inerrupt provides data
    // in the rx_buffer which get directly consumed
    // by the stepper interrupt.
    // sleep_mode();  // sleep a tiny bit
    if (consume_data) {
      // wait, buffer empty
      buffer_underrun_marked = false;
      while (rx_buffer_tail == rx_buffer_head) {
        // sleep_mode();
        if (!buffer_underrun_marked) {
          protocol_mark_underrun();
          buffer_underrun_marked = true;
        }
        protocol_idle();
      }
      // read a byte from the rx buffer
      uint8_t data = serial_read();
      if (data == CMD_RASTER_DATA_END) {
        raster_mode = false;
      }
    }
    protocol_idle();
  }
  // wait, buffer empty
  buffer_underrun_marked = false;
  while (rx_buffer_tail == rx_buffer_head) {
    // sleep_mode();
    if (!buffer_underrun_marked) {
      protocol_mark_underrun();
      buffer_underrun_marked = true;
    }
    protocol_idle();
  }
  // read a byte from the rx buffer
  uint8_t data = serial_read();
  // we have non-raster data
  if (data == CMD_RASTER_DATA_START) {
    raster_mode = true;
    consume_data = false;
    // comsume the byte
    return CMD_NONE;
  } else {
    return data;
  }
}


inline uint8_t serial_raster_read() {
  /** raster buffer ********************************
  * The rx_buffer doubles as a raster buffer. This *
  * depends on the right sequence of commands:     *
  * accel-line, raster-line, decel-line            *
  * and then streaming of raster-data.             *
  * serial_protocol_read enters the raster_mode    *
  * serial_raster_read exits it. During the raster *
  * streaming serial_protocol_read is blocking and *
  * serial_raster_read gets called from the        *
  * interrupt while executing the raster line.     *
  * To exit the raster_mode, all the raster data   *
  * and one more needs to be read.                 *
  *************************************************/
  // called from stepper interrupt
  if (raster_mode && !consume_data) {
    if (rx_buffer_tail == rx_buffer_head) {
      // oops, no raster data, sending side is flaking
      // rastering too fast or serial transmission too slow
      protocol_mark_underrun();
      return 128;    // 128 encodes 0 intensity
    } else {
      uint8_t data = serial_read();
      if ((127 < data) && (data  < 256)) {
        return data;
      } else if (data == CMD_RASTER_DATA_END) {
        raster_mode = false;
        return 128;  // 128 encodes 0 intensity
      } else {
        stepper_request_stop(STOPERROR_INVALID_MARKER);
        return 128;
      }
    }
  } else {
    // oops, not even in raster mode
    // sending side seems to be flaking
    return 128;     // 128 encodes 0 intensity
  }
}


inline uint8_t serial_data_available() {
  return rx_buffer_tail != rx_buffer_head;
}


inline void serial_consume_data() {
  consume_data = true;
}


// void printString(const char *s) {
//   while (*s) {
//     serial_write(*s++);
//   }
// }

// // Print a string stored in PGM-memory
// void printPgmString(const char *s) {
//   char c;
//   while ((c = pgm_read_byte_near(s++))) {
//     serial_write(c);
//   }
// }

// void printIntegerInBase(unsigned long n, unsigned long base) {
//   unsigned char buf[8 * sizeof(long)]; // Assumes 8-bit chars.
//   unsigned long i = 0;

//   if (n == 0) {
//     serial_write('0');
//     return;
//   }

//   while (n > 0) {
//     buf[i++] = n % base;
//     n /= base;
//   }

//   for (; i > 0; i--) {
//     serial_write(buf[i - 1] < 10 ?
//     '0' + buf[i - 1] :
//     'A' + buf[i - 1] - 10);
//   }
// }

// void printInteger(long n) {
//   if (n < 0) {
//     serial_write('-');
//     n = -n;
//   }

//   printIntegerInBase(n, 10);
// }

// void printFloat(double n) {
//   if (n < 0) {
//     serial_write('-');
//     n = -n;
//   }
//   n += 0.5/1000; // Add rounding factor

//   long integer_part;
//   integer_part = (int)n;
//   printIntegerInBase(integer_part,10);

//   serial_write('.');

//   n -= integer_part;
//   int decimals = 3;
//   uint8_t decimal_part;
//   while(decimals-- > 0) {
//     n *= 10;
//     decimal_part = (int) n;
//     serial_write('0'+decimal_part);
//     n -= decimal_part;
//   }
// }
