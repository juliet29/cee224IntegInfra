from pint import UnitRegistry
import numpy as np

u = UnitRegistry()
kg = u.kilogram
m = u.meter 
s = u.second


def constants(rho, mu,  D, h, beta, override=False, perc_grade=0.015, alpha=2, g=9.8):

    # -----> to calculate pipe length, L
    
    h =  h * m
    beta = beta * m 
    H = h + beta 

    # max grade, slope s
    perc_grade = 0.015 

    # pipe horz distance travelled, x 
    x = h / perc_grade

    # angle required, theta 
    # TODO check if this is h/x or x/h 
    theta = np.rad2deg(np.arctan(x/h))

    # pipe length, L
    L = x / np.sin(theta) # m
    
    c = {
        # --- fluid ---------------> 
        # density of primary sludge
        "rho": rho * kg / (m**3),
        # dynamic viscosity
        "mu": mu * kg / (m*s),
        # ---- infra ------------->
        # pipe diameter 
        "D": D * m,  
        # lift height, h 
        "h": h,
        # tank height, beta 
        "beta": beta,
        # total height dif
        "H": H,
        # total horz distance 
        "x ": x,
        # angle 
        "theta": theta,
        # pipe length 
        "L": L,
        # ---- physics ----------->
        "g": g * m / (s**2),
        "alpha": alpha
        
    }

    if override:
        # use values from the Cengel example 8.1
        c["rho"] = 998 * kg / (m**3)
        c["mu"] = 0.00102 * kg / (m*s)
        c["D"] = 0.06 * m  
        c["L"] = 65 * m 
        c["H"] = 2.20 * m 

    return c

def solve_quad(a, b, c):
    # a = a
    # b = b.magnitude
    # c = c.magnitude
    # print(a,b,c)
    d = b ** 2 - 4 * a * c  # this part is called the discriminant

    if d < 0:
        print("The equation has no real solutions")
    elif d == 0:
        x = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        print(f"The equation has one solution: {x} ")
        return x
    else:
        x1 = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        x2 = (-b - np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        print(f"The equation has two solutions: {x1} or {x2}")
        return (x1,x2)

# fig = go.Figure()
# fig.add_trace(go.Scatter(
#     x=x.magnitude,
#     y=y.magnitude, 
#     mode='lines+markers',
# ))

# fig.update_layout(title='Examine Quad - Solving for V',
#                    xaxis_title='x ',
#                    yaxis_title='y')