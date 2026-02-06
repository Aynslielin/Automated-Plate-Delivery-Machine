# Automated-Plate-Delivery-Machine
**Current Status:** Hardware Deployed on Jetson Nano
* Validated mechanical design and YOLOv8 model performance.
* Transitioned the computing core from **Raspberry Pi 4** to **NVIDIA Jetson Orin Nano** to address computational bottlenecks encourntered during YOLOv8-based object detection.
* Achieved plate-grabbing action by integrating YOLOv8 object detection model and self-designed robotic arm.
---
## Project Overview
This project presents the design, fabrication, and implement of an **Automated Plate Delivery Machine**. The system integrates computer vision, robotic manipulation, and mobile mobility to achieve autonomous service tasks.  
Originally developed on a Raspberry Pi 4, the computing core has been successfully migrated to the **NVIDIA Jetson Orin Nano** to overcome the latency bottlenecks and enable real-time processing for the object detection and kinematic control.  
### Funding & Recognition
* **Program:** Undergraduate Research Project
* **Grant:** Funded by the **National Science and Technology Council (NSTC)** (fomerly MOST).  
* **Institution**: Department of Electrical Engineering, National Taiwan Ocean University
* **Advisor**: Prof. Chih-Yung Cheng
* **Researcher**: Hsin-Wei Lin
---
## System Architecture
### 1. Hardware Specifications
| Component | Specification | Function |
| :--- | :--- | :--- |
| **Computing Core** | **NVIDIA Jetson Orin Nano** | Deep learning inference **(YOLOv8)** & High-level control |  
| **Vision Sensor** | USB / CSI Camera | Real-time video stream acquisition |
| **Microcontroller** | Arduino Mega 2560 | Transmit commands to actuators |  
| **Manipulator** | Custom 2-DOF Robotic Arm | 3D printed structure designed in **SolidWorks** |  
| **Actuators** | DC Motor actuator L298N | Chassis movement control and Arm movement control |  
  
### 2. Software Stack
* **Language:** Python 3.8+, C++
* **Computer Vision:** OpenCV, Ultralytics YOLOv8  
* **Communication:** UART / I2C Protocols
* **OS:** Ubuntu 20.04
---
