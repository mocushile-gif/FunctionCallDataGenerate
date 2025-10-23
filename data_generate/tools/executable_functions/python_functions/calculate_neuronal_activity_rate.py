def calculate_neuronal_activity_rate(synaptic_input_rate: float = 1.0, synaptic_weight: float = 0.1, decay_constant: float = 1.0) -> float:
    """
    Calculates the neuronal activity rate based on the synaptic input rate, synaptic weight, and decay constant.
    
    Parameters:
    - synaptic_input_rate (float): The rate of synaptic inputs per second. Default is 1.0.
    - synaptic_weight (float): The weight of the synaptic input, denoting its influence. Default is 0.1.
    - decay_constant (float): The rate at which the neuron's potential decays. Default is 1.0.
    
    Returns:
    - float: The neuronal activity rate.
    """
    # Basic model for neuronal activity rate calculation
    activity_rate = (synaptic_input_rate * synaptic_weight) / (1 + decay_constant)
    
    return activity_rate

# Example usage:
if __name__ == "__main__":
    # Default parameters
    activity = calculate_neuronal_activity_rate()
    print(f"Neuronal activity rate (default): {activity}")

    # Custom parameters
    activity_custom = calculate_neuronal_activity_rate(synaptic_input_rate=2.0, synaptic_weight=0.5, decay_constant=0.8)
    print(f"Neuronal activity rate (custom): {activity_custom}")
