import numpy as np

def agitation_liquid_level_compensator(volume, speed):  #Return the real liquid volume for any given reported liquid level and agitation speed

    #Volume not considered.
    #delta_V = 327e-6*pow(speed, 3) + 11.15e-3*pow(speed, 2) + 11.02e-3*speed    #Change in volume due to agitation

    poly_set={  #Polynomials fit to water level curve for any given initial volume. Explanation: delta_V(S) where delta_V is the increase in water level (L) for any agitation speed S (RPM).
        663.9: [.036, -.436, 0],
        552.1: [.030, .051, 0],
        455.3: [.031, .100, 0]
    }

    def nearest(a, x):
        diffs = [abs(y-x) for y in a]

        i = diffs.index(min(diffs))

        min_val = a[i]

        return min_val

    #for i in range(0, 1000, 100):
    #    print(f'{i} -> {nearest(list(poly_set.keys()), i)}')

    nearest_V_0 = nearest(list(poly_set.keys()), volume)

    poly = poly_set[nearest_V_0]

    #delta_V = (3.19e-2)*pow(speed, 2) - (1.69e-1)*speed
    delta_V = np.polyval(poly, speed)

    volume_compensated = volume - delta_V

    #print(f'[Compensator] V1: {volume} S1: {speed} V1c: {volume_compensated}')

    return volume_compensated