# Requirements Document

## Introduction

This document specifies requirements for advanced simulation and tracking features in the Cat Health Copilot system. The system currently supports single-visit event simulation but lacks long-term pattern analysis capabilities. These enhancements will enable weight change tracking with alerts, realistic baseline fluctuation simulation, and extended multi-day simulation scenarios to better reflect real-world usage patterns.

The system is designed to support both simulated data for testing and real sensor data from physical weight sensors. The architecture ensures that simulation serves as a development and testing tool, while the production system seamlessly integrates with actual hardware sensors to monitor real cat litter box usage.

## Glossary

- **System**: The Cat Health Copilot application
- **Simulator**: The component that generates simulated sensor data for testing and demonstration
- **Weight_Tracker**: The component that monitors and analyzes cat weight changes over time
- **Alert_Generator**: The component that creates health alerts based on detected anomalies
- **Baseline_Simulator**: The component that simulates realistic litter box weight fluctuations
- **Long_Term_Simulator**: The component that generates multi-day simulation data
- **Cat_Profile**: A stored record containing a cat's identification and baseline health information
- **Visit_Event**: A detected occurrence of a cat using the litter box
- **Baseline_Weight**: The weight of the empty litter box including pad and litter
- **Measured_Weight**: The actual weight detected by sensors during a visit
- **Profile_Weight**: The expected weight stored in a Cat_Profile
- **Weight_Change_Rate**: The percentage change in weight over a time period
- **Normal_Weight_Change_Rate**: The expected weight change rate for healthy cats (typically ±2% per week)
- **Baseline_Fluctuation**: Natural variation in Baseline_Weight due to litter usage and maintenance
- **Simulation_Scenario**: A predefined pattern of events for testing (normal, polyuria, weight loss)
- **Polyuria_Pattern**: Abnormally frequent urination indicating potential health issues
- **Data_Source**: The origin of weight sensor data, either simulated or from a physical sensor
- **Sensor_Mode**: Operating mode where the system receives data from a physical weight sensor
- **Simulation_Mode**: Operating mode where the system generates synthetic data for testing
- **Data_Source_Interface**: An abstraction layer that provides uniform access to weight data regardless of source
- **Physical_Sensor**: A hardware weight sensor device that measures actual litter box weight
- **Sensor_Connection**: The communication link between the system and a Physical_Sensor
- **Sensor_Data_Format**: The standardized structure for weight measurements including weight value and timestamp
- **Connection_Status**: The current state of the Sensor_Connection (connected, disconnected, error)
- **Real_Time_Data**: Weight measurements received continuously from a Physical_Sensor during operation

## Requirements

### Requirement 1: Weight Change Tracking

**User Story:** As a cat owner, I want the system to track my cat's weight over time, so that I can detect gradual weight changes that might indicate health problems.

#### Acceptance Criteria

1. WHEN a Visit_Event is classified and a cat is identified, THE Weight_Tracker SHALL calculate the Measured_Weight by subtracting Baseline_Weight from the event's average weight
2. WHEN a Measured_Weight is calculated, THE Weight_Tracker SHALL compare it to the Profile_Weight stored in the Cat_Profile
3. WHEN multiple Visit_Events exist for the same cat, THE Weight_Tracker SHALL calculate the Weight_Change_Rate between the earliest and most recent measurements
4. THE Weight_Tracker SHALL store each Measured_Weight with its timestamp in the cat's weight history
5. WHEN retrieving weight history, THE Weight_Tracker SHALL return measurements sorted by timestamp in chronological order

### Requirement 2: Weight Change Alerts

**User Story:** As a cat owner, I want to receive alerts when my cat's weight changes abnormally, so that I can seek veterinary care promptly.

#### Acceptance Criteria

1. WHEN the Weight_Change_Rate exceeds 5% over a 7-day period, THE Alert_Generator SHALL create a warning-level alert
2. WHEN the Weight_Change_Rate exceeds 10% over a 7-day period, THE Alert_Generator SHALL create a critical-level alert
3. WHEN the Weight_Change_Rate exceeds 7.5% over any time period shorter than 7 days, THE Alert_Generator SHALL create a critical-level alert
4. THE Alert_Generator SHALL include the following information in weight change alerts: cat name, Profile_Weight, current Measured_Weight, Weight_Change_Rate, time period, and recommended action
5. WHEN a weight change alert is created, THE Alert_Generator SHALL compare the Weight_Change_Rate to Normal_Weight_Change_Rate and indicate whether the change is abnormal
6. THE Alert_Generator SHALL not create duplicate alerts for the same weight change condition within a 24-hour period

### Requirement 3: Baseline Fluctuation Simulation

**User Story:** As a developer, I want the simulator to reflect realistic baseline weight changes, so that the system can be tested under conditions similar to real-world usage.

#### Acceptance Criteria

1. WHEN the Simulator generates a urination event, THE Baseline_Simulator SHALL increase the Baseline_Weight by a random value between 50g and 100g to simulate litter clumping
2. WHEN the Simulator generates a defecation event, THE Baseline_Simulator SHALL decrease the Baseline_Weight by a random value between 100g and 200g to simulate waste removal
3. WHEN the Simulator generates a litter refill event, THE Baseline_Simulator SHALL increase the Baseline_Weight by a random value between 500g and 1000g
4. WHEN the Simulator generates a cleaning event, THE Baseline_Simulator SHALL decrease the Baseline_Weight by a random value between 200g and 400g to simulate clump removal
5. THE Baseline_Simulator SHALL ensure Baseline_Weight never falls below 1.0kg or exceeds 5.0kg
6. WHEN Baseline_Weight reaches 1.5kg or lower, THE Baseline_Simulator SHALL automatically schedule a litter refill event within the next 24 simulated hours
7. WHEN Baseline_Weight reaches 4.5kg or higher, THE Baseline_Simulator SHALL automatically schedule a cleaning event within the next 12 simulated hours

### Requirement 4: Long-Term Simulation Scenarios

**User Story:** As a developer, I want to generate multi-day simulation data with predefined health scenarios, so that I can demonstrate the system's pattern detection capabilities.

#### Acceptance Criteria

1. THE Long_Term_Simulator SHALL support simulation periods of 7, 14, and 30 days
2. WHEN a simulation period is selected, THE Long_Term_Simulator SHALL generate Visit_Events distributed across all days in the period
3. THE Long_Term_Simulator SHALL support the following Simulation_Scenarios: normal pattern, polyuria onset, gradual weight loss, and combined polyuria with weight loss
4. WHERE the normal pattern scenario is selected, THE Long_Term_Simulator SHALL generate 2 to 4 Visit_Events per day with durations between 30 and 120 seconds
5. WHERE the polyuria onset scenario is selected, THE Long_Term_Simulator SHALL generate normal patterns for the first 3 days, then increase visit frequency to 6 to 10 events per day with durations between 15 and 45 seconds
6. WHERE the gradual weight loss scenario is selected, THE Long_Term_Simulator SHALL decrease the simulated cat weight by 0.5% to 1.0% per day starting from day 1
7. WHERE the combined scenario is selected, THE Long_Term_Simulator SHALL apply both polyuria onset and gradual weight loss patterns simultaneously
8. WHEN generating Visit_Events, THE Long_Term_Simulator SHALL distribute events across realistic time periods (avoiding nighttime hours between 23:00 and 06:00)
9. WHEN a simulation completes, THE Long_Term_Simulator SHALL save all generated events to the database with appropriate timestamps
10. THE Long_Term_Simulator SHALL apply Baseline_Fluctuation rules to all generated events

### Requirement 5: Multi-Cat Long-Term Simulation

**User Story:** As a developer, I want to simulate multiple cats over extended periods, so that I can test cat identification and individual health tracking in realistic multi-cat households.

#### Acceptance Criteria

1. WHERE multiple Cat_Profiles exist, THE Long_Term_Simulator SHALL generate Visit_Events for each cat according to their individual Simulation_Scenarios
2. WHEN generating multi-cat simulations, THE Long_Term_Simulator SHALL ensure Visit_Events from different cats do not overlap in time
3. THE Long_Term_Simulator SHALL assign each generated Visit_Event to the correct Cat_Profile based on the simulated weight
4. WHEN simulating multiple cats, THE Long_Term_Simulator SHALL maintain separate weight histories for each cat
5. THE Long_Term_Simulator SHALL distribute Visit_Events from different cats randomly throughout each day while respecting the non-overlap constraint

### Requirement 6: Simulation Configuration Interface

**User Story:** As a user, I want to configure simulation parameters through the UI, so that I can test different scenarios without modifying code.

#### Acceptance Criteria

1. THE System SHALL provide a user interface for selecting simulation duration (7, 14, or 30 days)
2. THE System SHALL provide a user interface for selecting one or more cats to include in the simulation
3. THE System SHALL provide a user interface for selecting a Simulation_Scenario for each cat
4. THE System SHALL provide a user interface for setting the simulation start date and time
5. WHEN simulation parameters are configured, THE System SHALL display a summary of what will be generated before execution
6. WHEN the user confirms the simulation, THE System SHALL execute the Long_Term_Simulator with the configured parameters
7. WHEN a simulation is running, THE System SHALL display progress information including current simulated date and number of events generated
8. WHEN a simulation completes, THE System SHALL display a summary including total events generated, alerts created, and weight change statistics for each cat

### Requirement 7: Weight History Visualization

**User Story:** As a cat owner, I want to see my cat's weight history in a chart, so that I can easily understand weight trends over time.

#### Acceptance Criteria

1. THE System SHALL display a line chart showing Measured_Weight over time for each cat
2. THE System SHALL display the Profile_Weight as a horizontal reference line on the weight chart
3. THE System SHALL display weight change alerts as markers on the weight chart at their corresponding timestamps
4. WHEN a user hovers over a data point on the weight chart, THE System SHALL display the exact Measured_Weight, timestamp, and Weight_Change_Rate since the previous measurement
5. THE System SHALL allow users to filter the weight chart by date range (7 days, 30 days, 90 days, or all time)
6. WHERE multiple cats exist, THE System SHALL allow users to select which cats to display on the weight chart
7. THE System SHALL use different colors for each cat when multiple cats are displayed on the same chart

### Requirement 8: Baseline History Tracking

**User Story:** As a developer, I want to track baseline weight changes over time, so that I can verify the baseline fluctuation simulation is working correctly.

#### Acceptance Criteria

1. WHEN the Baseline_Simulator modifies Baseline_Weight, THE System SHALL record the change in a baseline history log
2. THE System SHALL store the following information for each baseline change: timestamp, previous Baseline_Weight, new Baseline_Weight, change amount, and reason (urination, defecation, cleaning, refill)
3. THE System SHALL provide a user interface to view baseline history as a timeline
4. WHEN displaying baseline history, THE System SHALL use different visual indicators for increases (refill) and decreases (cleaning, waste)
5. THE System SHALL calculate and display the average Baseline_Weight over selectable time periods (24 hours, 7 days, 30 days)

### Requirement 9: Simulation Data Validation

**User Story:** As a developer, I want the simulator to generate realistic and consistent data, so that testing results are meaningful and reliable.

#### Acceptance Criteria

1. THE Long_Term_Simulator SHALL ensure all generated Visit_Events have durations within the range of 10 to 300 seconds
2. THE Long_Term_Simulator SHALL ensure all generated Measured_Weights are within ±20% of the cat's Profile_Weight unless simulating weight loss
3. WHERE weight loss is simulated, THE Long_Term_Simulator SHALL ensure the final weight is not less than 70% of the starting Profile_Weight
4. THE Long_Term_Simulator SHALL ensure visit frequency does not exceed 15 events per day for any cat
5. THE Long_Term_Simulator SHALL ensure at least 2 hours of simulated time pass between consecutive Visit_Events for the same cat
6. WHEN generating event timestamps, THE Long_Term_Simulator SHALL use realistic time distributions (more visits during morning and evening, fewer during midday and night)
7. IF the Long_Term_Simulator detects invalid parameters or constraints that cannot be satisfied, THEN THE System SHALL display an error message and prevent simulation execution

### Requirement 10: Simulation Reset and Cleanup

**User Story:** As a user, I want to clear simulated data without affecting real data, so that I can run multiple test scenarios cleanly.

#### Acceptance Criteria

1. THE System SHALL provide a user interface option to delete all events within a specified date range
2. WHEN deleting events, THE System SHALL display a confirmation dialog showing the number of events that will be deleted
3. THE System SHALL allow users to filter deletion by event source (simulated vs real sensor data)
4. WHEN events are deleted, THE System SHALL also delete associated weight measurements and alerts
5. THE System SHALL preserve Cat_Profiles when deleting simulated events
6. WHEN a deletion completes, THE System SHALL display a summary of deleted items (events, measurements, alerts)
7. THE System SHALL provide an option to reset Baseline_Weight to a user-specified value after deleting simulated data

### Requirement 11: Real Sensor Data Integration

**User Story:** As a user, I want to connect a real weight sensor to the system, so that I can monitor my cat's actual litter box usage in real-time.

#### Acceptance Criteria

1. THE System SHALL provide a Data_Source_Interface that abstracts the origin of weight measurements
2. THE Data_Source_Interface SHALL support both Simulation_Mode and Sensor_Mode without requiring changes to data processing components
3. WHEN operating in Sensor_Mode, THE System SHALL receive Real_Time_Data from a Physical_Sensor through a Sensor_Connection
4. THE System SHALL define a Sensor_Data_Format containing weight value (in kilograms with 0.001kg precision), timestamp (ISO 8601 format), and device identifier
5. WHEN a Physical_Sensor sends data, THE System SHALL validate the Sensor_Data_Format before processing
6. THE System SHALL monitor Connection_Status and update it based on sensor communication (connected when data is received within the last 30 seconds, disconnected when no data for 30-60 seconds, error when invalid data is received)
7. WHEN Connection_Status changes to disconnected or error, THE System SHALL log the status change and display a notification to the user
8. THE System SHALL provide a user interface to switch between Simulation_Mode and Sensor_Mode
9. WHEN displaying data in the user interface, THE System SHALL clearly indicate the current Data_Source (simulation or sensor) with a visible status indicator
10. THE System SHALL tag all stored events with their Data_Source to enable filtering and separate analysis of simulated vs real data
11. WHEN in Sensor_Mode, THE System SHALL process incoming Real_Time_Data using the same event detection, classification, and health monitoring pipeline as Simulation_Mode
12. THE System SHALL provide a user interface to view Sensor_Connection details including Connection_Status, last received data timestamp, and device identifier
13. WHERE the Physical_Sensor connection is lost, THE System SHALL retain the last known Baseline_Weight and continue to accept manual baseline updates
14. THE System SHALL support reconnection to a Physical_Sensor without requiring application restart
15. WHEN switching from Sensor_Mode to Simulation_Mode, THE System SHALL preserve all real sensor data in storage and clearly separate it from subsequently generated simulated data

