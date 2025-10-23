def calculate_bayes_theorem_posterior_probability(prior: float, likelihood: float, evidence: float) -> float:
    """
    Applies Bayes' theorem to calculate posterior probability.

    Parameters:
    - prior (float): The prior probability (P(A)).
    - likelihood (float): The likelihood (P(B|A)).
    - evidence (float): The evidence (P(B)).

    Returns:
    - float: The posterior probability (P(A|B)).
    """
    posterior = (likelihood * prior) / evidence
    return round(posterior, 4)

if __name__ == "__main__":
    # Example usage
    prior = 0.01  # Prior probability
    likelihood = 0.9  # Likelihood of observing the evidence if hypothesis is true
    evidence = 0.1  # Probability of the evidence

    posterior = calculate_bayes_theorem_posterior_probability(prior, likelihood, evidence)
    print(f"Posterior Probability: {posterior}")
