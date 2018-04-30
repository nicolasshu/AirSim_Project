import numpy as np
from AirSimClient import *
import sys
import time

def gradient_descent_far(current_state, goal_state, dist_star):
    grad_vector = dist_star*(current_state - goal_state)
    dist = dist_between_nodes(current_state, goal_state)
    grad_vector = grad_vector / np.float(dist)
    return grad_vector

def gradient_descent_close(current_state, goal_state):
    grad_vector = current_state - goal_state
    return grad_vector

def projection(new_x, points_array):
    point_approx = np.array([])
    min_dist = np.inf

    for point in points_array:
        dist = dist_between_nodes(new_x, point)
        if dist < min_dist:
            point_approx = point
            min_dist = dist
    return point_approx

def dist_between_nodes(node1_val, node2_val):
    dist = np.sqrt(np.sum((node1_val - node2_val)**2))
    return dist


def point_is_not_in_set(current_location, px_max, px_min, py_max, py_min, pz_max, pz_min):
    if px_min <= current_location[0] <= px_max:
        if py_min <= current_location[1] <= py_max:
            if pz_min <= current_location[2] <= pz_max:
                return False
    else:
        return True

def calculate_points(position_vect):
    # this will iterate somehow
    px_min = -1*position_vect.x_val
    px_max = position_vect.x_val
    py_min = -1*position_vect.y_val
    py_max = position_vect.y_val
    pz_min = -1*position_vect.z_val
    pz_max = position_vect.z_val

    print("position x val: {0} \n position y val: {1} \n position z val: {2}".format(px_max, py_max, pz_max))

    # Create bounding cube with equal aspect ratio (defined by corners)
    #creates 1000 points in a bounded cube
    max_range = 50
    Xb = 0.5 * max_range * np.mgrid[px_min:px_max:10j, py_min:py_max:10j, pz_min:pz_max:10j][0].flatten()
    Yb = 0.5 * max_range * np.mgrid[px_min:px_max:10j, py_min:py_max:10j, pz_min:pz_max:10j][1].flatten()
    Zb = 0.5 * max_range * np.mgrid[px_min:px_max:10j, py_min:py_max:10j, pz_min:pz_max:10j][2].flatten() - 1

    # store points in an array (POINTS)
    POINTS = np.array([])
    count = 0
    for xb, yb, zb in zip(Xb, Yb, Zb):
        point = np.array([xb, yb, zb])
        if count == 0:
            POINTS = np.expand_dims(point, axis=0)
        POINTS = np.append(POINTS, np.expand_dims(point, axis=0), axis=0)
        count +=1
    return px_max, px_min, py_max, py_min, pz_max, pz_min, POINTS

if __name__ == "__main__":
    quad = MultirotorClient()
    quad.confirmConnection()
    quad.enableApiControl(True)
        
    quad.armDisarm(True)
    quad.takeoff()
    dist_star = 3.0
    too_close = 1.0
    real_close = 0.5
    goal = np.array([15, -10, -6])
    goal_1 = np.array([20, -10, -6])
    goal_2 = np.array([30, -10, -6])

    goals = np.array([goal, goal_1, goal_2])
    # gradient descent
    #eta: random number in open interval (0.1, 10]
    # x: current state
    # x_est: potential new state

    for goal in goals:
        position_vect = quad.getPosition()
        px_max, px_min, py_max, py_min, pz_max, pz_min, POINTS = calculate_points(position_vect)

        x = np.array([px_max, py_max, pz_max])
        t = 0
        distance = dist_between_nodes(x, goal)
        path = []
        velocity = np.array([])
        init_pos = np.array([px_max, py_max, pz_max])
        i = 0
        eta = 0.1

        while distance >= dist_star:
           # print ("dist :", distance)
                # (10 - 0.1)*np.random.sample() + 0.1 
            # eta = (10 - 0.1)*np.random.sample + 0.1 

            # should x be randomly choosen?n
            x = np.array([px_max, py_max, pz_max])
            #print("current x far: ", x)
            print("goal: ", goal)
            Delta = gradient_descent_far(x, goal, dist_star)
            #print("Delta far: ", Delta)
            vel = np.sqrt(np.sum((Delta)**2))
            #print("velocity: ", vel)
            x_est = x - eta*Delta
            if point_is_not_in_set(x_est, px_max, px_min, py_max, py_min, pz_max, pz_min) is False:
                #print("point is projected")
                quad_next_state = projection(x_est, POINTS)
            else:
                #print ("x est point in set")
                quad_next_state = x_est
            px_max = quad_next_state[0]
            py_max = quad_next_state[1]
            pz_max = quad_next_state[2]
            print("x est: ", x_est)
            desired_location = Vector3r(px_max, py_max, pz_max)
            position_vect = desired_location
            px_max, px_min, py_max, py_min, pz_max, pz_min, POINTS = calculate_points(position_vect)
        
            if i%5 == 0:
                velocity = np.append(velocity, vel)
                velocity = np.average(velocity)
                time_approx = float(dist_between_nodes(goal, init_pos)) / float(velocity)
                my_lookahead = velocity + (float(velocity)/float(2))
                path.append(desired_location)
            distance = dist_between_nodes(goal, quad_next_state)
            #print("distance: ", distance)
            i += 1
    
        quad.moveOnPath(path, velocity, time_approx, DrivetrainType.MaxDegreeOfFreedom, YawMode(True, 0), my_lookahead, 1)

        path = []
        velocity = np.array([])
        i = 0
        while real_close < distance < dist_star:
            x = np.array([px_max, py_max, pz_max])
            #print("current x close: ", x)
            Delta = gradient_descent_close(x, goal)
            #print("delta close: ", Delta)
            vel = np.sqrt(np.sum((Delta)**2))
            #print("vel close: ", vel)
            x_est = x - eta*Delta
            quad_next_state = projection(x_est, POINTS)
            if point_is_not_in_set(x_est, px_max, px_min, py_max, py_min, pz_max, pz_min) is False:
                #print("point is projected")
                quad_next_state = projection(x_est, POINTS)
            else:
                #print ("x est point in set")
                quad_next_state = x_est
            #print("quad next state close: ", quad_next_state)
            px_max = quad_next_state[0]
            py_max = quad_next_state[1]
            pz_max = quad_next_state[2]
            desired_location = Vector3r(px_max, py_max, pz_max)
            position_vect = desired_location
            px_max, px_min, py_max, py_min, pz_max, pz_min, POINTS = calculate_points(position_vect)
            
            if i%5 == 0:
                velocity = np.append(velocity, vel)
                velocity = np.average(velocity)
                time_approx = float(dist_between_nodes(goal, init_pos)) / float(velocity)
                my_lookahead = velocity + (float(velocity)/float(2))
                path.append(desired_location)
            distance = dist_between_nodes(goal, quad_next_state)
            #print("distance: ", distance)
            i += 1
    
    #print("path: ", path)
    #print("velocity: ", velocity)
    #print("time approx: ", time_approx)
    #print("my lookahead: ", my_lookahead)
        quad.moveOnPath(path, velocity, time_approx, DrivetrainType.MaxDegreeOfFreedom, YawMode(True, 0), my_lookahead, 1)
    quad.land()
    quad.armDisarm(False)
    quad.enableApiControl(False)