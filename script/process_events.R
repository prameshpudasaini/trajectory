library(data.table)

# detector configuration for Indian School Rd
phase_eb <- 6L
phase_wb <- 2L

det_eb_stop <- c(17L, 18L, 19L)
det_eb_advance <- c(20L, 25L, 26L)

det_wb_stop <- c(9L, 10L, 11L, 12L)
det_wb_advance <- c(27L, 28L, 29L)

# read data
folder_name <- '20221214_IndianSchool'
file_name <- paste0("ignore/Phoenix/", folder_name, '.txt')

data <- fread(file_name)
data[, TimeStamp := as.POSIXct(TimeStamp, tz = '', format = '%m-%d-%Y %H:%M:%OS')]

options(digits.secs = 3L)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Events Pre-Processing --------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

seq_phase_event <- c(7L, 8L, 9L, 10L, 11L, 1L)

processEvents <- function(device, det_type, dir, hour, minute, exclude_SRT = TRUE) {
    
    # define parameters for detection type
    if (det_type == 'stop') {
        param_eb <- det_eb_stop
        param_wb <- det_wb_stop
    } else {
        param_eb <- det_eb_advance
        param_wb <- det_wb_advance
    }
    
    # define phase and parameter for direction
    if (dir == 'EB') {
        phase <- phase_eb
        param <- param_eb
    } else {
        phase <- phase_wb
        param <- param_wb
    }
    
    data <- data[DeviceID == device & hour(TimeStamp) == hour & minute(TimeStamp) <= minute, ]
    data$DeviceID <- NULL
    
    # process signal phase change events
    
    phase <- copy(data)[EventID %in% seq_phase_event & Parameter %in% phase, ][order(TimeStamp)]
    print("Check number of signal phase events:")
    print(phase[, .N, by = EventID])
    cat('\n')
    
    minCycleTime <- phase$TimeStamp[min(which(phase$EventID == 7L))]
    maxCycleTime <- phase$TimeStamp[max(which(phase$EventID == 7L))]
    
    phase <- phase[between(TimeStamp, minCycleTime, maxCycleTime), ]
    phase <- phase[EventID %in% c(8L, 10L, 1L), ]
    
    yellowStartTime <- phase$TimeStamp[phase$EventID == 8L]
    redStartTime <- phase$TimeStamp[phase$EventID == 10L]
    greenStartTime <- phase$TimeStamp[phase$EventID == 1L]
    
    Cycle <- seq(1L, length(yellowStartTime))
    CL <- round(as.numeric(difftime(shift(yellowStartTime, type = 'lead'), yellowStartTime, units = 'secs')), 3L)
    
    GreenTime <- round(as.numeric(difftime(greenStartTime, head(yellowStartTime, -1L)), units = 'secs'), 3L)
    GreenTime <- append(GreenTime, NA)
    
    # process detector actuation events
    
    det <- copy(data)[EventID %in% c(82L, 81L) & Parameter %in% param, ]
    det <- det[between(TimeStamp, minCycleTime, maxCycleTime, incbounds = FALSE), ][order(TimeStamp)]
    
    det_dir_loc <- sort(unique(det$Parameter))
    print("Detectors:")
    print(det_dir_loc)
    cat('\n')
    
    # get detection parameters for each lane-by-lane detector
    getOHG <- function(lane) {
        det_lane <- copy(det)[Parameter == lane, ]
        det_lane <- det_lane[min(which(EventID == 82L)):max(which(EventID == 81L)), ]
        
        detOn <- det_lane$TimeStamp[det_lane$EventID == 82L]
        detOff <- det_lane$TimeStamp[det_lane$EventID == 81L]
        
        Headway <- round(as.numeric(difftime(shift(detOn, type = 'lead'), detOn, units = 'secs')), 3L)
        ODT <- round(as.numeric(difftime(detOff, detOn, units = 'secs')), 3L)
        Gap <- round(as.numeric(difftime(shift(detOn, type = 'lead'), detOff, units = 'secs')), 3L)
        
        return(list(Headway = Headway, ODT = ODT, Gap = Gap))
    }
    
    # merge two events data sets
    
    DT <- rbindlist(list(phase, det))[order(TimeStamp)]
    
    DT[, Signal := fifelse(EventID %in% c(8L, 10L, 1L), EventID, as.integer(NA))]
    DT <- DT[, setnafill(.SD, type = 'locf', cols = 'Signal')]
    
    DT[, Signal := factor(as.factor(fcase(Signal == 1L, 'G',
                                          Signal == 8L, 'Y',
                                          Signal == 10L, 'R')), levels = c('G', 'Y', 'R'))]
    
    DT$Cycle[DT$EventID == 8L] <- Cycle
    DT$CL[DT$EventID == 8L] <- CL
    
    DT$YellowStart[DT$EventID == 8L] <- yellowStartTime
    DT$RedStart[DT$EventID == 8L] <- append(redStartTime, NA)
    DT$GreenStart[DT$EventID == 8L] <- append(greenStartTime, NA)
    DT$GreenTime[DT$EventID == 8L] <- GreenTime
    
    DT <- DT[, setnafill(.SD, type = 'locf', cols = c('Cycle', 'CL', 'GreenStart', 'YellowStart', 'RedStart', 'GreenTime'))]
    
    origin <- '1970-01-01'
    DT[, YellowStart := as.POSIXct(YellowStart, origin = origin)]
    DT[, RedStart := as.POSIXct(RedStart, origin = origin)]
    DT[, GreenStart := as.POSIXct(GreenStart, origin = origin)]
    
    YellowTime <- DT$RedStart - head(DT$YellowStart, -1L) # check yellow times
    print("Yellow time:")
    print(summary(as.numeric(head(YellowTime, -1L))))
    cat('\n')
    
    DT[, AIC := round(as.numeric(TimeStamp - YellowStart), 3L)]
    DT[, TUG := round(as.numeric(GreenStart - TimeStamp), 3L)]
    
    # signal status change by lane
    
    getSSC <- function(lane) {
        SSC82 <- as.character(DT$Signal[DT$EventID == 82L & DT$Parameter == lane])
        SSC81 <- as.character(DT$Signal[DT$EventID == 81L & DT$Parameter == lane])
        SSC_check <- length(SSC82) == length(SSC81)
        
        SSC <- paste0(SSC82, SSC81)
        
        return(list(SSC_check = SSC_check, SSC = SSC))
    }
    
    print("Check SSC for vector of detector on & off:")
    for (i in seq_along(det_dir_loc)) {
        print(paste0(i, ': ', det_dir_loc[i], ': ', getSSC(det_dir_loc[i])$SSC_check))
        
        DT$SSC[DT$EventID == 82L & DT$Parameter == det_dir_loc[i]] <- getSSC(det_dir_loc[i])$SSC
        
        DT$Headway[DT$EventID == 82L & DT$Parameter == det_dir_loc[i]] <- getOHG(det_dir_loc[i])$Headway
        DT$ODT[DT$EventID == 82L & DT$Parameter == det_dir_loc[i]] <- getOHG(det_dir_loc[i])$ODT
        DT$Gap[DT$EventID == 82L & DT$Parameter == det_dir_loc[i]] <- getOHG(det_dir_loc[i])$Gap
    }
    
    DT <- DT[EventID == 82L, ][order(TimeStamp)]
    
    SSC_levels <- c('YY', 'YR', 'RR', 'RG', 'GG', 'GY')
    DT[, SSC := factor(as.factor(SSC), levels = SSC_levels)]
    
    summary_SSC <- DT[, .(count = .N, 
                          min_ODT = min(ODT),
                          max_ODT = max(ODT),
                          mean_ODT = round(mean(ODT), 3L),
                          median_ODT = median(ODT), 
                          sd_ODT = round(sd(ODT), 4L)), by = c('SSC', 'Parameter')][order(SSC, Parameter)]
    
    cat('\n')
    print("Summary of signal status change for ODT:")
    print(summary_SSC)
    cat('\n')
    
    # exclude shared right-turn
    print('Exclude shared right-turn lane?')
    print(exclude_SRT)
    cat('\n')
    
    if (exclude_SRT == TRUE) {
        DT <- DT[Parameter != det_dir_loc[1], ]
    }
    
    # set time until green to zero for GG & GY
    DT[, TUG := fifelse(SSC %in% c('GG', 'GY'), 0L, TUG)]
    DT[, Parameter := as.factor(Parameter)]
    
    DT[SSC %in% c('GG', 'GY'), ODTR := round(ODT / shift(ODT, type = 'lead'), 4L), by = .(Cycle, Parameter)]
    DT[SSC %in% c('GG', 'GY'), GapR := round(Gap / shift(Gap, type = 'lead'), 4L), by = .(Cycle, Parameter)][]
    
    return(DT)
}

wb_3rd_stop <- processEvents(49L, 'stop', 'WB', 8L, 35L)
wb_3rd_stop[, Int := '3rd'][, Det := 'stop']

wb_7th_stop <- processEvents(48L, 'stop', 'WB', 8L, 35L)
wb_7th_stop[, Int := '7th'][, Det := 'stop']

wb_15th_stop <- processEvents(47L, 'stop', 'WB', 8L, 35L)
wb_15th_stop[, Int := '15th'][, Det := 'stop']

wb_19th_stop <- processEvents(46L, 'stop', 'WB', 8L, 35L, FALSE)
wb_19th_stop[, Int := '19th'][, Det := 'stop']

wb_7th_adv <- processEvents(48L, 'advance', 'WB', 8L, 35L, FALSE)
wb_7th_adv[, Int := '7th'][, Det := 'adv']

wb_19th_adv <- processEvents(46L, 'advance', 'WB', 8L, 35L, FALSE)
wb_19th_adv[, Int := '19th'][, Det := 'adv']

DT <- rbindlist(list(wb_3rd_stop, wb_7th_stop, wb_15th_stop, wb_19th_stop, wb_7th_adv, wb_19th_adv))

# fwrite(DT, "output/20221214_ISR_wb_3rd_19th.txt")
