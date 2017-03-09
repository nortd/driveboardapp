

Atmega328 Memory
================

- The chip has 32K flash, 2K sram, and 1K EEPROM
- The avr-size command lists memory stats about the program (.elf file).
  - 'text' is the program instructions (in flash only)
  - 'data' is the constants (in flash and in sram)
  - 'bss' is uninitialized data (sram only)

The avr-size tool shows the percentage of flash ("Program") and sram ("Data") use. Assuming the program does not dynamically allocate memory (malloc) the only uncertainty left is the stack. Depending on the depth of function calls, functions' parameters, and functions' local variables the stack may use up the sram. The stack will then corrupt static data.

What to do about the stack growing too big:

- inline small functions (only works when not using size optimization -Os)


New Beam Dynamics Contemplations
================================

While previous laser control and beam dynamics workes quite well there are still some edge cases that could be handled better. The challenge is to control very low intensity output while still have perforation free output at higher speeds. Here we run against limitations of the laser system:

- The laser system has a ioniztion threshold. If the control pulse is too short we don't get any output.
- Short pulse duration are dependant on the PWM frequency and intensity setting (pulse_dur_in_sec = intensity/(frequency*top_intensity))
- Additionally the laser system can deal with slightly shorter pulse duration when frequency is higher (roughly: 100Hz -> 200us and 500Hz+ -> 100us).

Pegging the pulses to motor steps
---------------------------------

Initiating the pulses along with motor steps gives us automatic beam dynamics (PPI, so to say).

- ~ 100 uSteps/mm
- @6000mm/min -> 10000uSteps/sec
- @120mm/min -> 200uSteps/sec
- trigger every other step => 100 - 5000 Hz



Beam Dynamics Contemplations
============================

### intensity assumptions
intensity 100% = 100 pulses per 32us
intensity 20%  =  20 pulses per 32us
pulses_per_32us * 31250 = pulses_per_seconds
intensity 100% = 3125000 pulses per seconds

!! but pulse length not a good measure, because beginning of the pulse most energy !!


### nominal
nominal_intensity
nominal_steps_per_minute = nominal_feedrate * CONFIG_STEPS_PER_MM

nominal_pulses_per_second = nominal_intensity * 31250
nominal_step_dur_in_seconds = 60/nominal_steps_per_minute
nominal_pulses_per_step = nominal_step_dur_in_seconds / nominal_pulses_per_second

### actual
steps_per_minute
step_dur_in_seconds = 60/steps_per_minute
pulses_per_step = step_dur_in_seconds / pulses_per_second



### Q: what intensity so pulses_per_step == nominal_pulses_per_step?

pulses_per_step == nominal_pulses_per_step
step_dur_in_seconds / pulses_per_second == nominal_step_dur_in_seconds / nominal_pulses_per_second
step_dur_in_seconds / (intensity * 31250) == nominal_step_dur_in_seconds / (nominal_intensity * 31250)
(step_dur_in_seconds/31250) = (intensity*nominal_step_dur_in_seconds) / (nominal_intensity * 31250)

intensity = (step_dur_in_seconds/31250) / ((nominal_step_dur_in_seconds) / (nominal_intensity * 31250))
intensity = (step_dur_in_seconds/31250) * ((nominal_intensity * 31250) / (nominal_step_dur_in_seconds))
intensity = (step_dur_in_seconds * nominal_intensity) / nominal_step_dur_in_seconds
intensity = (60/steps_per_minute * nominal_intensity) / 60/nominal_steps_per_minute
intensity = ((60/steps_per_minute) * nominal_intensity) / (60/(nominal_feedrate*CONFIG_STEPS_PER_MM))
intensity = (nominal_intensity/steps_per_minute) / (1/(nominal_feedrate*CONFIG_STEPS_PER_MM))
intensity = (nominal_intensity/steps_per_minute) * (nominal_feedrate*CONFIG_STEPS_PER_MM)
intensity = (nominal_intensity * nominal_feedrate * CONFIG_STEPS_PER_MM) / steps_per_minute

intensity = (current_block->nominal_laser_intensity * current_block->nominal_speed * CONFIG_STEPS_PER_MM) / steps_per_minute

!! we actually need this based on the actual head speed !!

adjusted_intensity = nominal_intensity * (nominal_speed/actual_speed)
