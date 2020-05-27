require(data.table)
require(magrittr)
require(anytime)
require(tools)

# Configuration
exclude_logins <- c("ddhaese", "David D'Haese") # exclude this authors from revision list
source_file <- "githist.tsv"
target_file <- "githist.svg"
start_time <- as.POSIXct("2020-02-04")
end_time <- as.POSIXct("2020-04-04")

palette(c("darkgrey", "steelblue", "white"))

# Loading the data
tim <- fread(source_file)

# Parsing datetimes
tim[, Date := Date %>% anytime]

# Sort by date 
tim <- tim[order(Date)]

# Function to normalize file sizes
normalize <- function(x){
  if(length(x) == 1){
    return(1)
  }
  
  return ((x - min(x)) / (max(x) - min(x)))
}

# Function to plot a timeline of a single file
plot_time_line_file <- function (x, pos){
  abline(h=pos)
  px <- x$Date
  px <- px %>% c(px %>% rev)
  type <- head(x$Type, 1)
  
  if(type == "lines"){
    py <- x$Dat_1 - x$Dat2
    py_max <- max(py)
    py <- py %>% normalize %>% divide_by(2.3)
    py <- py %>% c(py %>% rev %>% multiply_by(-1)) %>% add(pos)
    
  } else if(type == "bytes"){
    py <- x$Dat2
    py_max <- max(py)
    py <- py %>% normalize %>% divide_by(2.3)
    py <- py %>% c(py %>% rev %>% multiply_by(-1)) %>% add(pos)
    points(px, py, pch = 19, col = 2)
  }
  
  polygon(px, py, col = 2, lwd = 2)
  
  tx <- par("usr")[1:2] %>% mean
  text(tx, pos, py_max %>% paste(type), adj = c(.5, 1.2), cex = .7, col = 3)
  text(tx, pos, x$File %>% tail(1), adj = c(.5, -.2), cex = .7, col = 3)
}

# Function to plot timelines of all files in repository
plot_time_line <- function (x){
  authors <- x$Author %>% unique %>% setdiff(exclude_logins)
  files <- x$File_Id %>% unique
  file_cnt <- length(files)
  
  x_lim <- c(start_time, end_time)
  x_ax <- x_lim %>% pretty
  y_ax <- seq(.5, file_cnt + .5, length.out = nrow(x))
  
  par(oma = rep(0, 4), mar = c(3, 3, 3, 3), bg = 1)
  plot(x$Date, y_ax, type = "n", xlab = "", ylab = "", xlim = x_lim, axes = FALSE)
  axis(1, x_ax, x_ax %>% strftime("%Y-%m-%d"), cex = .8)
  abline(v = x_lim, lwd = 2)
  
  if(length(files) == 0){
    text(mean(x_lim), mean(y_ax), "No files were found.")
    return()
  }
  
  if(length(authors) == 0){
    text(mean(x_lim), mean(y_ax), "No work done.")
    return()
  }
  
  title(authors %>% paste0(collapse = " - "))
  
  pos <- 1
  
  for (file in files){
    x[File_Id == file] %>% plot_time_line_file(pos)
    pos <- pos + 1
  }
}

# Loop to process all git repositories
for(repo in tim$Repo %>% unique){
  svg(paste0(repo, "/", target_file))
  tim[Repo == repo] %>% plot_time_line
  dev.off()
}
