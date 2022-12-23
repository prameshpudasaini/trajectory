library(data.table)
library(plotly)

folder_name <- 'output/20221214_ISR'

processPlots <- function(dir, intersection, det_type) {

    file_name <<- paste0(dir, '_', intersection, '_', det_type)
    path <<- paste0(folder_name, '/', file_name, '.txt')
    
    DT <- fread(path)[order(TimeStamp)]
    DT$EventID <- NULL
    
    options(digits.secs = 3L)
    
    DT[, TimeStamp := TimeStamp - 7 * 3600]
    
    SSC_levels <- c('YY', 'YR', 'RR', 'RG', 'GG', 'GY')
    DT[, SSC := factor(as.factor(SSC), levels = SSC_levels)]
    
    summary_SSC <- DT[, .(count = .N, 
                          min_ODT = min(ODT),
                          max_ODT = max(ODT),
                          mean_ODT = round(mean(ODT), 3L),
                          median_ODT = median(ODT), 
                          sd_ODT = round(sd(ODT), 4L)), by = c('SSC', 'Parameter')][order(SSC, Parameter)]
    
    print("Summary of signal status change for ODT:")
    print(summary_SSC)
    cat('\n')
    
    det_dir_loc <- sort(unique(DT$Parameter))
    print('Detectors:')
    print(det_dir_loc)
    cat('\n')
    
    # exclude shared right-turn
    if (dir == 'wb') {
        if (intersection %in% c('3rd', '7th', '15th')) exclude_SRT <- TRUE
        else exclude_SRT <- FALSE
    } else exclude_SRT <- TRUE
    
    print('Exclude shared-right turn lane?')
    print(exclude_SRT)
    cat('\n')
    
    if (exclude_SRT == TRUE) {
        DT <- DT[Parameter != det_dir_loc[1], ]
    }
    
    # set time until green to zero for GG & GY
    DT[, TUG := fifelse(SSC %in% c('GG', 'GY'), 0L, TUG)]
    DT[, Parameter := as.factor(Parameter)][]
    
    print('SSC levels:')
    print(levels(DT$SSC))
    print('Detectors:')
    print(levels(DT$Parameter))
    
    # plots
    signal_color <- c('orange', 'brown', 'red', 'black', 'forestgreen', 'limegreen')
    
    ODT_SSC <- plot_ly(DT, type = 'box', y = ~ODT, color = ~SSC, colors = signal_color, boxmean = TRUE)
    
    ODT_Gap <- plot_ly(DT, type = 'scatter', x = ~ODT, y = ~Gap, color = ~SSC,
                       mode = 'markers', colors = signal_color, marker = list(size = 5))
    
    ODT_TUG <- plot_ly(DT[!(SSC %in% c('GG', 'GY')), ], type = 'scatter', x = ~ODT, y = ~TUG, color = ~SSC,
                       mode = 'markers', colors = signal_color, marker = list(size = 5))
    
    ODT_AIC <- plot_ly(DT, type = 'scatter', x = ~ODT, y = ~AIC, color = ~SSC,
                       mode = 'markers', colors = signal_color, marker = list(size = 5))
    
    return(list(DT = DT, ODT_SSC = ODT_SSC, ODT_Gap = ODT_Gap, ODT_TUG = ODT_TUG, ODT_AIC = ODT_AIC))
}

DT <- processPlots('wb', '19th', 'advance')$DT
