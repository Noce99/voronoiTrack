import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
from utils import read_points

def get_pixels_of_a_line(x1, y1, x2, y2):
    x = x2-x1
    y = y2-y1
    distance = np.sqrt(x**2+y**2)
    pixels = []
    if distance >= 1:
        num_subpoints = int(distance)*4
        x = x / num_subpoints
        y = y / num_subpoints
        for i in range(num_subpoints):
            # my_matrix[int(x1+x*i), int(y1+y*i)] = 1.0
            if len(pixels) == 0 or (int(x1+x*i), int(y1+y*i)) != pixels[-1]:
                pixels.append((int(x1+x*i), int(y1+y*i)))
    else:
        # my_matrix[int(x1), int(y1)] = 1.0
        pixels.append((int(x1), int(y1)))
    return pixels

def draw_a_rectangle(my_matrix, line1, line2):

    # for x, y in line1+line2:
    #    my_matrix[x, y] = 1

    num_points_in_line1 = len(line1)
    num_points_in_line2 = len(line2)
    if num_points_in_line1 >= num_points_in_line2:
        bigger_line = line1
        smaller_line = line2
    else:
        bigger_line = line2
        smaller_line = line1
    num_points_bigger_line = max(num_points_in_line1, num_points_in_line2)
    num_points_smaller_line = min(num_points_in_line1, num_points_in_line2)
    for i, data in enumerate(bigger_line):
        x1, y1 = data
        smaller_line_index = int(i/num_points_bigger_line * num_points_smaller_line)
        x2, y2 = smaller_line[smaller_line_index]
        points_to_draw = get_pixels_of_a_line(x1, y1, x2, y2)
        for x, y in points_to_draw:
            my_matrix[x-1:x+2, y] = 1
            my_matrix[x, y-1:y+2] = 1
            
def calculate_borders(x1, y1, x2, y2, r):
    if x2 == x1:
        return None, None, None, None
    m = (y2-y1)/(x2-x1)
    m_p = -1/m
    xa = r / (np.sqrt(1+m_p**2))
    ya = m_p*xa
    xb = -xa
    yb = m_p*xb

    xa += x1
    ya += y1
    xb += x1
    yb += y1
    return xa, ya, xb, yb
    
def from_poits_to_matrix(data):
    RESOLUTION = 1000
    RADIUS = 30
    xs, ys = read_points(data)
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    print(f"x in [{min_x}; {max_x}], y in [{min_y}; {max_y}]")
    distances = []
    for i in range(len(xs)):
        if i != len(xs)-1:
            distances.append(np.sqrt((xs[i]-xs[i+1])**2+(ys[i]-ys[i+1])**2))
        else:
            distances.append(np.sqrt((xs[i]-xs[0])**2+(ys[i]-ys[0])**2))
        xs[i] = 1.5*RADIUS + (xs[i]-min_x)/(max_x-min_x) * (RESOLUTION-3*RADIUS)
        ys[i] = 1.5*RADIUS + (ys[i]-min_y)/(max_y-min_y) * (RESOLUTION-3*RADIUS)
    print(f"distances in [{min(distances)}; {max(distances)}], mean = {sum(distances)/len(distances)}")
    my_matrix = np.zeros((RESOLUTION+1, RESOLUTION+1))
    xas = []
    yas = []
    xbs = []
    ybs = []

    for i in range(len(xs)):
        if i != len(xs)-1:
            xa, ya, xb, yb = calculate_borders(xs[i], ys[i], xs[i+1], ys[i+1], RADIUS)
        else:
            xa, ya, xb, yb = calculate_borders(xs[i], ys[i], xs[0], ys[0], RADIUS)
        if xa is not None:
            xas.append(xa)
            yas.append(ya)
            xbs.append(xb)
            ybs.append(yb)
    for i in range(len(xas)):
        if i != len(xas)-1:
            if np.sqrt((xas[i]-xas[i+1])**2 + (yas[i]-yas[i+1])**2) > RADIUS:
                tmp = xas[i+1]
                xas[i+1] = xbs[i+1]
                xbs[i+1] = tmp
                tmp = yas[i+1]
                yas[i+1] = ybs[i+1]
                ybs[i+1] = tmp
            line_1 = get_pixels_of_a_line(xas[i], yas[i], xas[i+1], yas[i+1])
            line_2 = get_pixels_of_a_line(xbs[i], ybs[i], xbs[i+1], ybs[i+1])
            draw_a_rectangle(my_matrix, line_1, line_2)
        else:
            line_1 = get_pixels_of_a_line(xas[i], yas[i], xas[0], yas[0])
            line_2 = get_pixels_of_a_line(xbs[i], ybs[i], xbs[0], ybs[0])
            draw_a_rectangle(my_matrix, line_1, line_2)
    np.save(f"tracks/mat_{seed}.npy", my_matrix)
    plt.matshow(my_matrix)
    plt.savefig(f"tracks/mat_{seed}.png", dpi=800)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize a track previously stored in a file. If both -f and -s flags are present, only the -s one will be considered")
    parser.add_argument("-f", "--file", help="Input file from where to load the track data.", default="", type=str)
    parser.add_argument("-s", "--seed", help="Search the tracks/ directory for already generated tracks.", default="", type=str)
    parser.add_argument("-w", "--width", type=int, help="Width of the track (default: 5)", default=5)

    args = parser.parse_args()
    if args.seed:
        try:
            file = "tracks/track_"+str(int(args.seed))+".npy"
        except ValueError:
            print("The input is not a valid seed.")
            exit()
        seed = args.seed
    elif args.file:
        file = args.file
        seed = args.file.split("_")[1].split(".")[0]
    else:
        print("At least one flag must be specified.")
        exit()
    try:
        if not os.path.exists(file):
            raise IOError()
    except IOError:
        print("The track with that seed doesn't exists, please generate that file using: python3 generate.py -q -s SEED -b 1")
        exit()

    points = np.load(file)
    from_poits_to_matrix(points)
    
