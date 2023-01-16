import math
import pandas as pd
import matplotlib.pyplot as plt

d_Ab = 1219 # Central to 3rd
d_bB = 99 # 3rd
d_Bc = 1509 # 3rd to 7th
d_cC = 105 # 7th
d_Cd = 2281 # 7th to 15th
d_dD = 111 # 15th
d_De = 2515 # 15th to 19th
d_eE = 107 # 19th
d_Ef = 400 # beyond 19th

dt = 0.1

len_det_stop = 40
len_det_adv = 10
dist_det_adv = 300

len_veh = 18
len_eff_stop = len_det_stop + len_veh # effective vehicle length at stop bar detector
len_eff_adv = len_det_adv + len_veh # effective vehicle length at advance detector

s_psl = round(35*5280/3600, 2) # posted speed limit or free-flow speed
t_r = 1 # reaction time
dec_ent = round(-2.3*3.2808, 2) # deceleration from entrance to reach PSL
dec_stop = round(-3*3.2808, 2) # deceleration to stop bar
acc_stop = round(3*3.2808, 2) # acceleration from stop bar
k = 25 # jam space headway
t_sul = 2 # startup lost time

t_list = []
x_list = []


# =============================================================================
# Segment: A-b-B (Central to 3rd)
# =============================================================================
print("Segment: A-B")

cycle = 4
lane = 11
SSC_AB_stop = 'RG' 
t_on = 7*60 + 23.7
AIC = 41.8
ODT = 33.2

v0 = 0
d_dec_est = round((v0**2 - s_psl**2) / (2*dec_stop), 2)
d_dec_crit = d_Ab - d_dec_est # distance from which deceleration starts

T = 7*60 + 0.3
x0 = 0
v0 = s_psl

while x0 <= d_Ab:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_dec_crit:
        a0 = 0
    else:
        a0 = dec_stop
        
    if x0 <= d_Ab - len_det_stop:
        det_time_stop_AB = T
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
green_start = 7*60 + 47.9
v0 = 0

while T <= green_start + t_sul:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))

    T += dt


# =============================================================================
# Segment: b-B-c-C (3rd to 7th)
# =============================================================================
print("Segment: B-C")

d_acc_est = round((s_psl**2 - v0**2) / (2*acc_stop), 2)
d_acc_crit = d_Ab + d_acc_est # distance till which vehicle accelerates to reach PSL

d_until_adv = d_Ab + d_bB + d_Bc - dist_det_adv - len_det_adv

while x0 <= d_until_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_acc_crit:
        a0 = acc_stop
    else:
        a0 = 0
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt

# check: not free-flow
cycle = 5
SSC_BC_adv = 'YY'
AIC = 1.5

d_dec_est = round((0**2 - v0**2) / (2*dec_stop), 2)
d_until_stop = d_Ab + d_bB + d_Bc
d_dec_crit = d_until_stop - d_dec_est

while x0 <= d_until_stop:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_dec_crit:
        a0 = 0
    else:
        a0 = dec_stop
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
green_start = 9*60 + 29.7
v0 = 0

while T <= green_start + t_sul:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))

    T += dt


# =============================================================================
# Segment: c-C-d-D (7th to 15th)
# =============================================================================
print("Segment: C-D")

d_acc_est = round((s_psl**2 - v0**2) / (2*acc_stop), 2)
d_acc_crit = d_Ab + d_bB + d_Bc + d_acc_est # distance till which vehicle accelerates to reach PSL

# constant acceleration to virtual advance detector
d_total_vir_adv = d_Ab + d_bB + d_Bc + d_cC + d_Cd - dist_det_adv - len_det_adv

while x0 <= d_total_vir_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_acc_crit:
        a0 = acc_stop
    else:
        a0 = 0
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
   
# check:
cycle = 5
SSC_CD_vir_adv = 'RR'
AIC = T - (9*60 + 50)
    
d_dec_est = round((0**2 - v0**2) / (2*dec_stop), 2)
d_until_stop = d_Ab + d_bB + d_Bc + d_cC + d_Cd
d_dec_crit = d_until_stop - d_dec_est

while x0 <= d_until_stop:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_dec_crit:
        a0 = 0
    else:
        a0 = dec_stop
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
green_start = 10*60 + 38.2
v0 = 0

while T <= green_start + t_sul:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))

    T += dt

    
# =============================================================================
# Segment: d-D-e-E (15th to 19th)
# =============================================================================
print("Segment: D-E")

d_acc_est = round((s_psl**2 - v0**2) / (2*acc_stop), 2)
d_acc_crit = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_acc_est # distance till which vehicle accelerates to reach PSL

# constant acceleration to virtual advance detector
d_total_adv = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De - dist_det_adv - len_det_adv

while x0 <= d_total_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_acc_crit:
        a0 = acc_stop
    else:
        a0 = 0
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt

# check:
cycle = 6
SSC_DE_adv = 'RR'
t_on = 11*60 + 27.2
green_start = 11*60 + 48.5

# deceleration to queuing position
a0 = dec_stop

while T <= green_start:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
    if v0 < 0:
        v0 = 0
        a0 = 0

queue_pos_dist = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De - x0 # queueing position based on stopping point
queue_pos_num = math.floor(queue_pos_dist / k)

cycle = 6
SSC_BC_stop = 'GG'
t_on = 12*60 + 5
ODT = 1.3
green_start = 11*60 + 48.5

s_est = round((len_eff_stop)/ODT, 2) # estimated speed based on ODT
d_acc_est = queue_pos_dist # estimated distance of acceleration
acc_est = round((s_est**2 - v0**2)/(2*d_acc_est), 2)
t_acc_est = round((s_est - v0)/acc_est, 1)

t_reach_stop = t_on + ODT - green_start
t_queue_clearance = round(t_reach_stop - t_acc_est, 1)
time_until_queue_clearance = green_start + t_queue_clearance

while T <= time_until_queue_clearance:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    x0 = x
    v0 = v
    T += dt

d_total = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De + d_eE

while x0 <= d_total:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De:
        a0 = acc_est
    else:
        a0 = 0
    
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De:
        det_time_stop_DE = T
    
    x0 = x
    v0 = v
    T += dt

print("Segment: E-F")

d_acc_est = round((s_psl**2 - v0**2) / (2*acc_stop), 2)
d_acc_crit = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De + d_eE + d_acc_est # distance till which vehicle accelerates to reach PSL

# constant acceleration to virtual advance detector
d_until_end = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De + d_eE + d_Ef

while x0 <= d_until_end:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_acc_crit:
        a0 = acc_stop
    else:
        a0 = 0
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt


# =============================================================================
# Results
# =============================================================================
DT = pd.DataFrame({'t': t_list, 'x': x_list})

plt.scatter(DT.t, DT.x, s = 0.1)
plt.show()

DT.to_csv(r"D:\GitHub\trajectory\script\sample_trajectories\trajectory_c4.txt", sep = '\t', index = False)
