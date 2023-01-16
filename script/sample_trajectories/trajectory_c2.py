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
acc_stop = round(3.5*3.2808, 2) # acceleration from stop bar
k = 25 # jam space headway
t_sul = 2 # startup lost time

t_list = []
x_list = []


# =============================================================================
# Segment: A-b-B (Central to 3rd)
# =============================================================================
print("Segment: A-B")

SSC_AB_stop = 'RG' 
t_on = 2*60 + 53.5
AIC = 11.6
ODT = 48.7

v0 = 0
d_dec_est = round((v0**2 - s_psl**2) / (2*dec_stop), 2)
d_dec_crit = d_Ab - d_dec_est # distance from which deceleration starts

T = 2*60 + 30.1
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
    
green_start = 3*60 + 33.7
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

# check: free-flow as observed from advance detector data
cycle = 2
SSC_BC_adv = 'GG'
AIC = 109.3

d_until_stop = d_Ab + d_bB + d_Bc
d_until_entrance = d_until_stop + d_cC

while x0 <= d_until_entrance:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_until_stop - len_det_stop:
        det_time_stop_BC = T
        
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt


# =============================================================================
# Segment: C-d-D (7th to 15th)
# =============================================================================
print("Segment: C-D")

# constant acceleration to virtual advance detector
d_total_vir_adv = d_Ab + d_bB + d_Bc + d_cC + d_Cd - dist_det_adv - len_det_adv

while x0 <= d_total_vir_adv:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    a0 = 0
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_total_vir_adv:
        det_time_adv_CD = T
    
    x0 = x
    v0 = v
    T += dt
   
# check: potential deceleration to queueing position followed by acceleration
cycle = 2
green_start = 4*60 + 41.2
AIC = T - green_start
SSC_CD_vir_adv = 'GG'   
    
queue_pos_num = 5
queue_pos_dist = queue_pos_num * k

d_until_stop = d_Ab + d_bB + d_Bc + d_cC + d_Cd

# # check with free-flow speed
# while x0 <= d_until_stop:
#     print("Time:", round(T,1), x0, v0)
#     t_list.append(round(T,1))
#     x_list.append(round(x0,2))
    
#     a0 = 0
#     x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
#     v = round(v0 + a0*dt, 2)
    
#     if x0 <= d_until_stop - len_det_stop:
#         det_time_stop_CD = T
    
#     x0 = x
#     v0 = v
#     T += dt

SSC_CD_stop = 'GG'
ODT = 1.4

d_dec_crit = d_until_stop - queue_pos_dist - x0 # distance of deceleration
s_est = round((len_eff_stop)/ODT, 2) # estimated speed based on ODT
dec_est = (s_est**2 - s_psl**2) / (2*d_dec_crit)

d_until_entrance = d_until_stop + d_dD

while x0 <= d_until_entrance:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_until_stop - queue_pos_dist:
        a0 = dec_est
    else:
        a0 = 0
        
    if x0 <= d_until_stop - len_det_stop:
        det_time_stop_CD = T
    
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    x0 = x
    v0 = v
    T += dt

    
# =============================================================================
# Segment: D-e-E (15th to 19th)
# =============================================================================
print("Segment: D-E")

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

cycle = 3
SSC_DE_adv = 'RR'
AIC = 65.8
TUG = 10.9
green_start = 5*60 + 51.7

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

d_until_stop = d_Ab + d_bB + d_Bc + d_cC + d_Cd + d_dD + d_De
queue_pos_dist = d_until_stop - x0 # queueing position based on stopping point
queue_pos_num = math.floor(queue_pos_dist / k)

cycle = 3
SSC_BC_stop = 'GG'
t_on = 6*60 + 10.4
ODT = 1.4
green_start = 5*60 + 51.7

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

d_until_entrance = d_until_stop + d_eE

while x0 <= d_until_entrance:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
    if x0 <= d_until_stop - len_det_stop:
        a0 = acc_est
    else:
        a0 = acc_stop
    
    x = round(x0 + v0*dt + (1/2)*a0*dt*dt, 2)
    v = round(v0 + a0*dt, 2)
    
    if x0 <= d_until_stop - len_det_stop:
        det_time_stop_DE = T
    
    x0 = x
    v0 = v
    T += dt
    
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
    
# constant acceleration to point F
v0 = s_psl # update to PSL
d_until_end = d_until_entrance + d_Ef

while x0 <= d_until_end:
    print("Time:", round(T,1), x0, v0)
    t_list.append(round(T,1))
    x_list.append(round(x0,2))
    
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

DT.to_csv(r"D:\GitHub\trajectory\script\sample_trajectories\trajectory_c2.txt", sep = '\t', index = False)
