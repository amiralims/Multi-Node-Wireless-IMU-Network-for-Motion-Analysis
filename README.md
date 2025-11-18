# Multi-Node Wireless IMU Network for Motion Analysis

This repository contains the complete hardware, firmware, and software for a custom-built, end-to-end system for capturing real-time motion data from multiple wireless sensor nodes. The system was originally developed as my Bachelor of Science thesis project to explore the use of wearable MEMS sensor data in the diagnosis of Parkinson's Disease and was later expanded to increase node count and hardware robustness.

The platform consists of multiple wearable sensor nodes, a central receiver unit, and a desktop application for system configuration, live data monitoring, and logging.

![Thesis Cover](path/to/your/thesis_cover_image.jpg) 
*(Optional: Add a screenshot of your thesis cover page here. Replace `path/to/your/thesis_cover_image.jpg` with the actual path once you upload the image to your repository.)*

---

## System Architecture

The system is designed around a star network topology where multiple independent transmitter nodes send data to a single central receiver connected to a host computer.

![System Diagram](path/to/your/system_diagram.png)
*(Optional but highly recommended: Create a simple block diagram and add it here.)*

*   **Transmitter Nodes (9 units):** Each node is a self-contained, battery-powered wearable device.
    *   **Microcontroller:** Atmega8 (AVR)
    *   **Sensor:** MPU-6050 (3-axis Accelerometer + 3-axis Gyroscope)
    *   **Wireless:** nRF24L01 2.4GHz Transceiver
    *   **PCB:** Custom-designed in Altium Designer, later refined with surface-mount components for a smaller form factor.

*   **Receiver Unit:**
    *   **Platform:** Arduino Uno
    *   **Wireless:** nRF24L01 2.4GHz Transceiver
    *   **Host Communication:** Serial (USB)

*   **Host Application:**
    *   **Language:** Python
    *   **GUI Framework:** PyQt5
    *   **Functionality:** System configuration (setting sensor ranges), live data rate monitoring, and logging processed data to a text file.

---

## Key Technical Features

*   **End-to-End System Design:** Successfully architected and implemented the entire data acquisition pipeline, from hardware component selection and PCB design to low-level firmware and a high-level desktop application.
*   **Multi-Node Wireless Communication:** Developed a time-division multiplexing scheme to enable a single receiver to reliably capture data from up to 9 separate wireless transmitters by rapidly switching radio channels.
*   **Real-Time Embedded Firmware:** Wrote low-level C/C++ firmware for the Atmega8 microcontroller to read sensor data from the MPU-6050 via **I²C**, process it, and transmit it wirelessly via **SPI** to the nRF24L01 module. The system utilizes timer interrupts for precise data sampling.
*   **Custom Python GUI Application:** Built a user-friendly desktop application with PyQt5 that allows a user to configure the system, monitor the status and data rate of each individual sensor, and save the aggregated data for later analysis in MATLAB or Python.
*   **Hardware Industrialization:** Post-thesis, the initial through-hole PCB design was migrated to a more compact and robust version using surface-mount (SMD) components in Altium Designer.
*   **Data Analysis & Machine Learning:** The collected data was successfully used to train LSTM-based Recurrent Neural Networks to classify different motion patterns, achieving over 90% accuracy in proof-of-concept tests.

---
