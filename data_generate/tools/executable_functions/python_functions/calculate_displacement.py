import math

def calculate_displacement(initial_velocity: float, acceleration: float, 
                                                              time: float, initial_position: float = 0.0, 
                                                              drag_coefficient: float = 0.1, mass: float = 1.0) -> float:
    """
    Calculates the displacement of an object considering constant acceleration, air resistance, and initial position.

    Parameters:
    - initial_velocity (float): The initial velocity of the object (m/s).
    - acceleration (float): The constant acceleration of the object (m/s²).
    - time (float): The time elapsed (s).
    - initial_position (float): The initial position of the object (m). Defaults to 0.
    - drag_coefficient (float): The drag coefficient (dimensionless). Defaults to 0.1.
    - mass (float): The mass of the object (kg). Defaults to 1.0.

    Returns:
    - float: The displacement of the object (meters).
    """
    
    # Initialize variables
    velocity = initial_velocity
    position = initial_position
    dt = 0.1  # Time step for simulation
    time_steps = int(time / dt)
    
    # Simulate displacement with time steps
    for t in range(time_steps):
        # Calculate the force of air resistance (F = 0.5 * C_d * rho * A * v^2)
        air_resistance = 0.5 * drag_coefficient * velocity**2  # Simplified drag force
        
        # Adjust acceleration with air resistance (F = ma => a = F/m)
        effective_acceleration = acceleration - air_resistance / mass
        
        # Update velocity and position using the effective acceleration
        velocity += effective_acceleration * dt
        position += velocity * dt

    return f"The displacement of the object is {round(position, 2)} meters."


# Example usage of the function with constant acceleration and air resistance
if __name__ == "__main__":
    initial_velocity = 10.0  # m/s
    acceleration = 2.0  # m/s² (constant acceleration)
    time = 5.0  # seconds
    initial_position = 0.0  # m

    # Calculate displacement with air resistance
    displacement_value = calculate_displacement(initial_velocity, acceleration, 
                                                                                  time, initial_position, drag_coefficient=0.1, mass=1.0)
    print(displacement_value)
