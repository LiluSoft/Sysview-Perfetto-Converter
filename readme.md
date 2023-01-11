# SysView Perfetto Converter
[Segger SystemView](https://www.segger.com/products/development-tools/systemview/) is a system behavior analyzer, it shows the running task and timing in the system and can help find delays and tasks that hog the MCU. The ESP-IDF framework uses SystemView embedded component and OpenOCD to generate trace data for SystemView to display, However, Segger SystemView was not designed to view more than one core and some modules of ESP32 [have two cores](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/app_trace.html#data-visualization) which makes it less than an ideal tool.

Another alternative would be to use [toem Impulse](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/app_trace.html#configure-impulse-for-dual-core-traces), but Installing Eclipse just for that seemed like an overkill for me.

After looking at a few tools I've found [Perfetto](https://perfetto.dev/) for working with Linux trace files, which made it a candidate for showing SystemView data as well and it can handle multiple cores, complex events and interrupts and metrics.



# Missing Features
- Tracing Custom Metric is not currently supported. Both Sysview and Perfetto supports metrics.

# Alternatives
- Use Two instances of Segger SystemView, one for each core
- Use [toem Impulse](https://mcuoneclipse.com/2016/07/31/impulse-segger-systemview-in-eclipse/) to view multiple traces side by side
- Use [Percepio Tracealyzer](https://www.freertos.org/FreeRTOS-Plus/FreeRTOS_Plus_Trace/FreeRTOS_Plus_Trace.html) 