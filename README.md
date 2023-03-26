# DORA
Official implementation of the MDPI IJERPH submitted paper: "Improving remote health care with collaborative agents on IoT drone-aided lora network" 

The first figure below shows an overview of the proposed Drone-aided system for health analytics in rural areas.
The second figure shows screenshots of the protoype and the Drona-Lora communication test experiment. 


<p align="center"> 
<img src="https://github.com/gadm21/DORA/blob/main/assets/DORA.png">
</p>

<p align="center"> 
<img src="https://github.com/gadm21/DORA/blob/main/assets/DORA_real.png">
</p>

# Project Structure
```
|-- src                     // Code 
    |-- __init__.py/	// main file of client 
    |-- data_utils.py/	// functins for data retrieval and preprocessing
    |-- doing_fl.py/		// Performs Federated Learning
    |-- doing_local_central.py/	// seed script for local and central training 
    |-- spider_plot.py/	// plot individual accuracy on a spider plot
    |-- DP_central.py/	// create and train a DP model 
    |-- DP_central_2.py/	// create and train a DP model 2
    |-- model_utils.py/	// functions for model creation and training
    |-- plot_utils.py/	// functions for plotting

|-- results                  // Federated learning results
    |-- accuracy/        // Accuracy on HAR datasets under different FL methods


|-- data                  // Human Activity Recognition datasets
    |-- large_scale_HARBox/         // HarBox dataset
    |-- imu_dataset/                // IMU dataset
    |-- depth_dataset/              // Depth dataset
    |-- HARS/                       // HARS dataset
    |-- HARB4/                      // part of HARB4 dataset
    |-- uwb_dataset/                // UWB dataset


|-- communication                  // LoRa libraries
    |-- LoRa.py        // LoRa class
    |-- ReliableLoRa.py        // ReliableLoRa class
    |-- MainFunctions.py/ // Helper functions for LoRa and ReliableLoRa
    |-- Helpers.py        // More helper functions for LoRa and ReliableLoRa
    |-- GlobalVariables.py        // Global variables for LoRa and ReliableLoRa
    |-- Examples.py        // An example showing how to send/receive a file 

|-- README.md

|-- assets               // figures used in this README.md
```
