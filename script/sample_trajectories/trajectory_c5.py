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

cycle = 5
lane = 11
SSC_AB_stop = 'GG' 
t_on = 10*60 + 23.4
AIC = 101.4
ODT = 0.8

s_est = round((len_eff_stop)/ODT, 2) # estimated speed based on ODT
d_acc_est = round((s_est**2 - s_psl**2) / (2*acc_stop), 2) # estimated distance of acceleration
d_acc_crit = d_Ab - len_det_stop - d_acc_est # distance from which acceleration starts

T = 10*60 + 0.9
x0 = 0
v0 = s_psl
d_total = d_Ab + d_bB

while x0 <= d_total:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_acc_crit:
        a0 = 0
    elif x0 > d_acc_crit and x0 <= d_Ab:
        a0 = acc_stop
    else:
        a0 = 0
        
    if x0 <= d_Ab - len_det_stop:
        det_time_stop_AB = T
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
rel_diff_det_time_stop_AB = round(t_on - det_time_stop_AB, 1)

# =============================================================================
# Segment: B-c-C (3rd to 7th)
# =============================================================================
print("Segment: B-C")

s_est = v0 # estimated speed at entrance
d_dec_est = round((s_psl**2 - s_est**2) / (2*dec_ent), 2) # estimated distance of deceleration from entrance to reach PSL

d_total = x0 + d_dec_est

while x0 <= d_total:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = dec_ent
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
# constant acceleration to advance detector
v0 = s_psl # update to PSL
d_total_adv = d_Ab + d_bB + d_Bc - dist_det_adv - len_det_adv

while x0 <= d_total_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = 0
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_total_adv:
        det_time_adv_BC = T
    
    x0 = x
    v0 = v
    T += dt

cycle = 6
SSC_BC_adv = 'RR'
green_start = 11*60 + 33
TUG = green_start - T

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

queue_pos_dist = d_Ab + d_bB + d_Bc - x0 # queueing position based on stopping point
queue_pos_num = math.floor(queue_pos_dist / k)
queue_pos_dist_adj = queue_pos_dist - 2*k

cycle = 6
SSC_BC_stop = 'GG'
t_on = 11*60 + 44
ODT = 1.8
green_start = 11*60 + 33

s_est = round((len_eff_stop)/ODT, 2) # estimated speed based on ODT
d_acc_est = queue_pos_dist_adj # estimated distance of acceleration
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

d_total = d_Ab + d_bB + d_Bc + d_cC

while x0 <= d_total:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = acc_est
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_Ab + d_bB + d_Bc:
        det_time_stop_BC = T
    
    x0 = x
    v0 = v
    T += dt


# =============================================================================
# Segment: C-d-D (7th to 15th)
# =============================================================================
print("Segment: C-D")
    
s_est = v0 # estimated speed at entrance
d_acc_est = round((s_psl**2 - s_est**2) / (2*acc_stop), 2) # estimated distance of acceleration from entrance to reach PSL

d_total = x0 + d_acc_est

while x0 <= d_total:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = acc_stop
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
# constant acceleration to advance detector
s_est = v0
d_total_adv = d_Ab + d_bB + d_Bc + d_cC + d_Cd - dist_det_adv

while x0 <= d_total_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = 0
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_total_adv:
        det_time_adv_BC = T
    
    x0 = x
    v0 = v
    T += dt
    
cycle = 6
green_start = 12*60 + 44.7
SSC_CD_vir_adv = 'RR'

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

queue_pos_dist = d_Ab + d_bB + d_Bc + d_cC + d_Cd - x0 # queueing position based on stopping point
queue_pos_num = math.floor(queue_pos_dist / k)

cycle = 6
SSC_CD_stop = 'GG'
t_on = 12*60 + 59.9
ODT = 1.2
green_start = 12*60 + 44.7

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

d_stop = d_Ab + d_bB + d_Bc + d_cC + d_Cd
d_entrance = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD

while x0 <= d_entrance:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_stop: # uniform acceleration till stop bar
        a0 = acc_est
    else: # constant acceleration from stop bar to entrance
        a0 = 0
    
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_stop:
        det_time_stop_CD = T
    
    x0 = x
    v0 = v
    T += dt

    
# =============================================================================
# Segment: D-e-E (15th to 19th)
# =============================================================================
print("Segment: D-E")

s_est = v0 # estimated speed at entrance
d_acc_est = round((s_psl**2 - s_est**2) / (2*acc_stop), 2) # estimated distance of deceleration from entrance to reach PSL

d_total = x0 + d_acc_est

while x0 <= d_total:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = acc_stop
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt
    
# constant acceleration to advance detector
v0 = s_psl # update to PSL
d_total_adv = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De - dist_det_adv - len_det_adv

while x0 <= d_total_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = 0
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_total_adv:
        det_time_adv_DE = T
    
    x0 = x
    v0 = v
    T += dt

cycle = 7
SSC_DE_adv = 'GG'
AIC = 71.3
time_until_cycle_ends = 120 - AIC # passes the intersection at free-flow

d_until_stop = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De
d_until_entrance = d_until_stop + d_eE
d_until_end = d_until_entrance + d_Ef

while x0 <= d_until_end:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_until_stop:
        det_time_stop_DE = T
    
    x0 = x
    v0 = v
    T += dt   


# =============================================================================
# Results
# =============================================================================
DT = pd.DataFrame({'t': t_list, 'x': x_list})

plt.scatter(DT.t, DT.x, s = 0.1)
plt.show()

DT.to_csv(r"D:\GitHub\trajectory\script\sample_trajectories\trajectory_c5.txt", sep = '\t', index = False)
