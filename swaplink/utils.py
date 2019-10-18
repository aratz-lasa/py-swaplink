import quantumrandom


def get_random_int(min, max):
    """
        Generates random integer in the range [min,max)
        :param min: range's smallest number
        :param max: range's biggest number
        :return: random integer
        """
    return int(quantumrandom.randint(min, max))


def get_random_int_min_zero(max):
    """
    Generates random integer in the range [0,max)
    :param max: range biggest number
    :return: random integer
    """
    return int(quantumrandom.randint(0, max))
