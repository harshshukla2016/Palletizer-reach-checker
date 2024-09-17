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
    robot_reach = {
        1: (1000, 1200),  # CS612: Easy reach 1000mm, max reach 1200mm
        2: (1300, 1500),  # CS620: Easy reach 1300mm, max reach 1500mm
        3: (1500, 1800)   # CS625: Easy reach 1500mm, max reach 1800mm
    }[robot_type]
    
    box_data = []
    max_height_increase = 0

    for layer in range(1, layers + 1):
        for box in range(1, int(boxes_per_layer) + 1):
            box_id = f"L{layer:02d}B{box:02d}"
            
            # Calculate box position relative to the pallet
            x_rel = ((box - 1) % (pallet_width // box_width)) * box_width
            y_rel = ((box - 1) // (pallet_width // box_width)) * box_length
            z_rel = pallet_height + (box_height * (layer - 1))
            
            # Calculate absolute box position
            x_pos = master_point[0] + x_rel
            y_pos = master_point[1] + y_rel
            z_pos = z_rel
            
            # Check if the box is completely within the pallet dimensions
            if (x_rel + box_width <= pallet_width and 
                y_rel + box_length <= pallet_length):
                
                # Calculate distance from robot base to box center
                distance = math.sqrt((x_pos + box_width/2)**2 + (y_pos + box_length/2)**2 + (z_pos + box_height/2 - robot_height)**2)
                
                if distance <= robot_reach[0]:
                    reachability = 'easy'
                elif distance <= robot_reach[1]:
                    reachability = 'difficult'
                    max_height_increase = max(max_height_increase, 700)  # Trigger 7th axis
                else:
                    reachability = 'unreachable'
                    max_height_increase = max(max_height_increase, 700)  # Trigger 7th axis

                box_data.append({
                    'id': box_id,
                    'layer': layer,
                    'reachability': reachability,
                    'position': (x_pos, y_pos, z_pos)
                })

    return box_data, max_height_increase

def plot_boxes(box_data, robot_type, robot_height, pallet_width, pallet_length, box_width, box_length, box_height, master_point):
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
        color = {'easy': 'green', 'difficult': 'orange', 'unreachable': 'red'}[box['reachability']]
        
        cube = cuboid_data((x, y, z), size=(box_width, box_length, box_height))
        faces = Poly3DCollection(cube, alpha=0.25, linewidths=1, edgecolors='k')
        faces.set_facecolor(color)
        ax.add_collection3d(faces)

    # Plot robot base
    ax.scatter([0], [0], [robot_height], c='b', marker='^', s=100, label='Robot Base')

    # Plot robot stand base
    stand_radius = 200
    stand_height = robot_height
    theta = np.linspace(0, 2*np.pi, 100)
    z = np.linspace(0, stand_height, 100)
    theta, z = np.meshgrid(theta, z)
    x = stand_radius * np.cos(theta)
    y = stand_radius * np.sin(theta)
    ax.plot_surface(x, y, z, color='gray', alpha=0.5)

    # Plot robot reach spheres
    robot_reach = {
        1: (1000, 1200),
        2: (1300, 1500),
        3: (1500, 1800)
    }[robot_type]

    for reach in robot_reach:
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = reach * np.cos(u) * np.sin(v)
        y = reach * np.sin(u) * np.sin(v)
        z = reach * np.cos(v) + robot_height
        ax.plot_wireframe(x, y, z, color="b", alpha=0.1)

    # Plot pallet
    pallet_corners = [
        [master_point[0], master_point[1], 0], 
        [master_point[0] + pallet_width, master_point[1], 0], 
        [master_point[0] + pallet_width, master_point[1] + pallet_length, 0], 
        [master_point[0], master_point[1] + pallet_length, 0],
        [master_point[0], master_point[1], 60], 
        [master_point[0] + pallet_width, master_point[1], 60], 
        [master_point[0] + pallet_width, master_point[1] + pallet_length, 60], 
        [master_point[0], master_point[1] + pallet_length, 60]
    ]
    for i, j in [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]:
        ax.plot3D(*zip(pallet_corners[i], pallet_corners[j]), color="brown")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Box Positions and Reachability')
    
    # Create custom legend
    green_proxy = plt.Rectangle((0, 0), 1, 1, fc="green", alpha=0.25)
    orange_proxy = plt.Rectangle((0, 0), 1, 1, fc="orange", alpha=0.25)
    red_proxy = plt.Rectangle((0, 0), 1, 1, fc="red", alpha=0.25)
    gray_proxy = plt.Rectangle((0, 0), 1, 1, fc="gray", alpha=0.5)
    ax.legend([green_proxy, orange_proxy, red_proxy, 'b^', gray_proxy], 
              ['Easy Reach', 'Difficult/Unreachable', 'Unreachable', 'Robot Base', 'Robot Stand'])

    # Set axes limits
    max_reach = max(robot_reach)
    ax.set_xlim(-max_reach, max(master_point[0] + pallet_width, max_reach))
    ax.set_ylim(-max_reach, max(master_point[1] + pallet_length, max_reach))
    ax.set_zlim(0, max(robot_height + max_reach, 60 + box_height * len(set(box['layer'] for box in box_data))))

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
    
    box_data, max_height_increase = calculate_reachability(
        box_height, box_width, box_length, pallet_height, pallet_width, pallet_length,
        layers, robot_type, master_point, robot_height, boxes_per_layer
    )
    
    print("\nResults:")
    reachable_boxes = 0
    unreachable_boxes = 0
    reachable_layers = [0] * (layers + 1)

    for box in box_data:
        status = "Reachable" if box['reachability'] != 'unreachable' else "Not Reachable"
        print(f"Box ID: {box['id']}, Layer: {box['layer']}, Status: {status}, Position: {box['position']}")
        
        if box['reachability'] != 'unreachable':
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
    plot_boxes(box_data, robot_type, robot_height + max_height_increase, pallet_width, pallet_length, box_width, box_length, box_height, master_point)

if __name__ == "__main__":
    main()