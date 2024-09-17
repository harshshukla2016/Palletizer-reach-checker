```markdown
# Palletizer Reach Checker

## Overview
The Palletizer Reach Checker is a Python application designed to calculate the reachability of boxes stacked on a pallet by different types of robots. It visualizes the box positions and their reachability status in a 3D plot.

## Features
- Input dimensions for boxes and pallets.
- Select robot type and height.
- Calculate reachability for each box based on robot specifications.
- Visualize box positions and reachability in a 3D plot.

## Requirements
- Python 3.x
- Libraries:
  - NumPy
  - Matplotlib

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Palletizer-reach-checker
   ```

2. Install the required libraries:
   ```bash
   pip install numpy matplotlib
   ```

## Usage
1. Run the application:
   ```bash
   python prc1.py
   ```

2. Follow the prompts to enter:
   - Box dimensions (height, width, length)
   - Pallet dimensions (height, width, length)
   - Number of layers
   - Robot type (1 for CS612, 2 for CS620, 3 for CS625)
   - Master point coordinates (x, y)
   - Robot height

3. The program will output the reachability status of each box and display a 3D plot of the boxes and their reachability.

## Output
The output includes:
- Reachability status for each box (Easy, Difficult, Unreachable)
- Summary of reachable and unreachable boxes
- Visualization of the pallet and boxes in 3D



## Acknowledgments
- Inspired by robotic automation and palletizing systems.
```
