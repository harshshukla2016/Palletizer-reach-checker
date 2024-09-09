import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def get_input(prompt, data_type=float):
    while True:
        try:
            value = data_type(input(prompt))
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Invalid input. Please enter a positive number.")

def get_robot_input():
    while True:
        robot = input("Enter robot type (1 for CS612, 2 for CS620, 3 for CS625): ")
        if robot in ['1', '2', '3']:
            return int(robot)
        print("Invalid input. Please enter 1, 2, or 3.")

def get_coordinates_input(prompt):
    while True:
        try:
            x, y = map(float, input(prompt).split(','))
            return x, y
        except ValueError:
            print("Invalid input. Please enter two numbers separated by a comma.")

def calculate_reachability(box_height, box_width, box_length, pallet_height, pallet_width, pallet_length, layers, robot_type, master_point, robot_height, boxes_per_layer):
    robot_reach = {1: 1600, 2: 1800, 3: 2000}[robot_type]
    
    box_data = []

    for layer in range(1, layers + 1):
        for box in range(1, boxes_per_layer + 1):
            box_id = f"L{layer:02d}B{box:02d}"
            
            # Calculate box position
            x_pos = master_point[0] + ((box - 1) % (pallet_width / box_width)) * box_width
            y_pos = master_point[1] + ((box - 1) // (pallet_width / box_width)) * box_length
            z_pos = 60 + (box_height * (layer - 1))  # Start at 60 mm (pallet height)
            
            # Calculate distance from robot base to box
            distance = math.sqrt((x_pos ** 2) + (y_pos ** 2) + ((z_pos - robot_height) ** 2))
            
            is_reachable = distance <= robot_reach

            box_data.append({
                'id': box_id,
                'layer': layer,
                'reachable': is_reachable,
                'position': (x_pos, y_pos, z_pos)
            })

    return box_data

def plot_boxes(box_data, robot_reach, robot_height, pallet_width, pallet_length, box_width, box_length, box_height):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    def cuboid_data(o, size=(1, 1, 1)):
        X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
             [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
             [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
             [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
             [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
             [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
        X = np.array(X).astype(float)
        for i in range(3):
            X[:, :, i] *= size[i]
        X += np.array(o)
        return X

    for box in box_data:
        x, y, z = box['position']
        if box['reachable']:
            color = 'green'
        else:
            color = 'red'
        
        cube = cuboid_data((x, y, z), size=(box_width, box_length, box_height))
        faces = Poly3DCollection(cube, alpha=0.25, linewidths=1, edgecolors='k')
        faces.set_facecolor(color)
        ax.add_collection3d(faces)

    # Plot robot base
    ax.scatter([0], [0], [robot_height], c='b', marker='^', s=100, label='Robot Base')

    # Plot robot reach sphere (semi-transparent)
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = robot_reach * np.cos(u) * np.sin(v)
    y = robot_reach * np.sin(u) * np.sin(v)
    z = robot_reach * np.cos(v) + robot_height
    ax.plot_wireframe(x, y, z, color="b", alpha=0.1)

    # Plot pallet
    pallet_corners = [
        [0, 0, 0], [pallet_width, 0, 0], [pallet_width, pallet_length, 0], [0, pallet_length, 0],
        [0, 0, 60], [pallet_width, 0, 60], [pallet_width, pallet_length, 60], [0, pallet_length, 60]
    ]
    for i, j in [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]:
        ax.plot3D(*zip(pallet_corners[i], pallet_corners[j]), color="brown")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Box Positions and Reachability')
    
    # Create custom legend
    green_proxy = plt.Rectangle((0, 0), 1, 1, fc="green", alpha=0.25)
    red_proxy = plt.Rectangle((0, 0), 1, 1, fc="red", alpha=0.25)
    ax.legend([green_proxy, red_proxy, 'b^'], ['Reachable', 'Unreachable', 'Robot Base'])

    # Set axes limits
    ax.set_xlim(0, max(pallet_width, robot_reach))
    ax.set_ylim(0, max(pallet_length, robot_reach))
    ax.set_zlim(0, max(robot_height + robot_reach, 60 + box_height * len(set(box['layer'] for box in box_data))))

    plt.show()

def main():
    print("Enter dimensions in millimeters:")
    box_height = get_input("Box height: ")
    box_width = get_input("Box width: ")
    box_length = get_input("Box length: ")
    pallet_height = 60  # Fixed pallet height
    pallet_width = get_input("Pallet width: ")
    pallet_length = get_input("Pallet length: ")
    layers = get_input("Number of layers: ", int)
    robot_type = get_robot_input()
    
    master_point = get_coordinates_input("Enter master point of the pallet (x,y): ")
    robot_height = get_input("Enter robot height: ")
    
    boxes_per_layer = math.floor((pallet_width / box_width) * (pallet_length / box_length))
    
    box_data = calculate_reachability(
        box_height, box_width, box_length, pallet_height, pallet_width, pallet_length,
        layers, robot_type, master_point, robot_height, boxes_per_layer
    )
    
    print("\nResults:")
    reachable_boxes = 0
    unreachable_boxes = 0
    reachable_layers = [0] * (layers + 1)

    for box in box_data:
        status = "Reachable" if box['reachable'] else "Not Reachable"
        print(f"Box ID: {box['id']}, Layer: {box['layer']}, Status: {status}, Position: {box['position']}")
        
        if box['reachable']:
            reachable_boxes += 1
            reachable_layers[box['layer']] += 1
        else:
            unreachable_boxes += 1

    print(f"\nSummary:")
    print(f"Total number of boxes: {len(box_data)}")
    print(f"Number of boxes reachable: {reachable_boxes}")
    print(f"Number of boxes not reachable: {unreachable_boxes}")
    
    for layer, count in enumerate(reachable_layers[1:], 1):
        print(f"Layer {layer}: {count} reachable boxes")

    fully_reachable_layers = sum(1 for count in reachable_layers[1:] if count == boxes_per_layer)
    print(f"Number of fully reachable layers: {fully_reachable_layers}")
    print(f"Number of partially or not reachable layers: {layers - fully_reachable_layers}")

    # Plot the boxes
    robot_reach = {1: 1600, 2: 1800, 3: 2000}[robot_type]
    plot_boxes(box_data, robot_reach, robot_height, pallet_width, pallet_length, box_width, box_length, box_height)

if __name__ == "__main__":
    main()