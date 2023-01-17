library(data.table)
library(ggplot2)

# process min, max times for signal events

DT <- fread("ignore/Phoenix/20221214_IndianSchool.txt")
DT[, TimeStamp := as.POSIXct(TimeStamp, tz = '', format = '%m-%d-%Y %H:%M:%OS')]
DT <- DT[between(TimeStamp, '2022-12-14 07:58:00', '2022-12-14 08:20:00'), ]

options(digits.secs = 3L)

dist_3 <- 1219 + 99/2
dist_7 <- 1219 + 99 + 1509 + 105/2
dist_15 <- 1219 + 99 + 1509 + 105 + 2281 + 111/2
dist_19 <- 1219 + 99 + 1509 + 105 + 2281 + 111 + 2515 + 107/2

seq_phase_event <- c(7L, 8L, 9L, 10L, 11L, 1L)

get_min_max <- function(device, int_name, dist){
    
    dt <- copy(DT)[DeviceID == device & EventID %in% seq_phase_event & Parameter == 2L, ]
    
    minCycleTime <- dt$TimeStamp[min(which(dt$EventID == 7L))]
    maxCycleTime <- dt$TimeStamp[max(which(dt$EventID == 7L))]
    
    dt <- dt[between(TimeStamp, minCycleTime, maxCycleTime), ]
    dt <- dt[EventID %in% c(8L, 10L, 1L), ]
    
    yst <- dt$TimeStamp[dt$EventID == 8L]
    rst <- dt$TimeStamp[dt$EventID == 10L]
    gst <- dt$TimeStamp[dt$EventID == 1L]
    
    print(yst)
    cat('\n')
    print(rst)
    cat('\n')
    print(gst)
    cat('\n')
    
    print(c(length(yst), length(rst), length(gst)))
    
    data <- data.table(
        Int = int_name,
        x = dist,
        ymin = head(yst, -1L),
        ymax = rst,
        rmin = rst,
        rmax = gst,
        gmin = gst,
        gmax = tail(yst, -1L)
    )
    
    return(data)
}

DT3 <- get_min_max(49L, '3rd', dist_3)
DT7 <- get_min_max(48L, '7th', dist_7)
DT15 <- get_min_max(47L, '15th', dist_15)
DT19 <- get_min_max(46L, '19th', dist_19)

# trajectory data sets

traj1 = fread("script/sample_trajectories/trajectory_c1.txt")
traj2 = fread("script/sample_trajectories/trajectory_c2.txt")
traj3 = fread("script/sample_trajectories/trajectory_c3.txt")
traj4 = fread("script/sample_trajectories/trajectory_c4.txt")
traj5 = fread("script/sample_trajectories/trajectory_c5.txt")

traj = rbindlist(list(traj1, traj2, traj3, traj4, traj5))

traj[, TimeStamp := as.POSIXct('2022-12-14 08:00:00')]
traj[, TimeStamp := TimeStamp + t]

# plot
size <- 1.5

plot <- ggplot() + 
    # 3rd
    geom_linerange(aes(y = x, xmin = ymin, xmax = ymax), DT3, color = 'orange', size = size) + 
    geom_linerange(aes(y = x, xmin = rmin, xmax = rmax), DT3, color = 'red', size = size) + 
    geom_linerange(aes(y = x, xmin = gmin, xmax = gmax), DT3, color = 'limegreen', size = size) + 
    # 7th
    geom_linerange(aes(y = x, xmin = ymin, xmax = ymax), DT7, color = 'orange', size = size) + 
    geom_linerange(aes(y = x, xmin = rmin, xmax = rmax), DT7, color = 'red', size = size) + 
    geom_linerange(aes(y = x, xmin = gmin, xmax = gmax), DT7, color = 'limegreen', size = size) + 
    # 15th
    geom_linerange(aes(y = x, xmin = ymin, xmax = ymax), DT15, color = 'orange', size = size) + 
    geom_linerange(aes(y = x, xmin = rmin, xmax = rmax), DT15, color = 'red', size = size) + 
    geom_linerange(aes(y = x, xmin = gmin, xmax = gmax), DT15, color = 'limegreen', size = size) + 
    # 19th
    geom_linerange(aes(y = x, xmin = ymin, xmax = ymax), DT19, color = 'orange', size = size) + 
    geom_linerange(aes(y = x, xmin = rmin, xmax = rmax), DT19, color = 'red', size = size) + 
    geom_linerange(aes(y = x, xmin = gmin, xmax = gmax), DT19, color = 'limegreen', size = size) + 
    # trajectory
    geom_point(aes(TimeStamp, x), traj, size = 0.1) +
    # theme
    scale_y_continuous(breaks = c(dist_3, dist_7, dist_15, dist_19), 
                       labels = c('3rd Ave', '7th Ave', '15th Ave', '19th Ave')) + 
    labs(x = '', y = '') + 
    theme(axis.text = element_text(size = 12, face = 'bold'),
          axis.ticks = element_blank())
plot

ggsave(paste0("script/sample_trajectories/", "TSD.png"),
       plot = plot,
       units = "cm",
       width = 35,
       height = 21,
       dpi = 600)

# # calculations
# tt1 <- tail(traj1$t, 1L) - head(traj1$t, 1L)
# tt2 <- tail(traj2$t, 1L) - head(traj2$t, 1L)
# tt3 <- tail(traj3$t, 1L) - head(traj3$t, 1L)
# tt4 <- tail(traj4$t, 1L) - head(traj4$t, 1L)
# tt5 <- tail(traj5$t, 1L) - head(traj5$t, 1L)
# 
# tt <- c(tt1, tt2, tt3, tt4, tt5)
# mean(tt)
# sd(tt)
