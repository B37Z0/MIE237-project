# Imports
library(tidyverse)
library(emmeans)

# Read data
within_2f <- read_csv("participant_accuracy.csv")

# Convert to categorical variables
within_2f <- within_2f %>%
  mutate(
    participant = factor(participant),
    complexity = factor(complexity,
                        levels = c("Easy", "Medium", "Hard")),
    interval_length = factor(interval_length,
                             levels = c(10,20,30))
  )

# Exploring participant effects and accuracy
ggplot(within_2f, aes(x = participant, y = accuracy)) +
  geom_boxplot() +
  theme_minimal() +
  labs( x = "Participant" ,
        y = "Accuracy" )

# Exploring participant effects and number of tasks completed
ggplot(within_2f, aes(x = participant, y = tasks_completed)) +
  geom_boxplot() +
  theme_minimal() +
  labs( x = "Participant" ,
        y = "Number of Tasks Completed" )

# Interaction plot: roughly parallel lines may suggest little interaction, to be confirmed by ANOVA
ggplot(within_2f, aes(x = interval_length, y = accuracy, color = complexity, group = complexity)) +
  stat_summary(fun = mean, geom = "line") +
  stat_summary(fun = mean, geom = "point") +
  theme_minimal()

# complexity
ggplot(within_2f, aes(x = interval_length, y = tasks_completed, color = complexity, group = complexity)) +
  stat_summary(fun = mean, geom = "line") +
  stat_summary(fun = mean, geom = "point") +
  theme_minimal()

# CHECK INTERACTION EFFECTS (accuracy)
accuracy_blocked <- aov(accuracy~complexity*interval_length + participant, 
                        data=within_2f)
summary(accuracy_blocked) 
# Diagnostic
par(mfrow = c(2,2))
plot(accuracy_blocked)
# Sqrt
accuracy_blockedsqrt <- aov(sqrt(accuracy)~complexity*interval_length + participant, 
                        data=within_2f)
summary(accuracy_blockedsqrt) 
par(mfrow = c(2,2))
plot(accuracy_blockedsqrt)
# Log
accuracy_blockedlog <- aov(log(accuracy)~complexity*interval_length + participant, 
                            data=within_2f)
summary(accuracy_blockedlog)
par(mfrow = c(2,2))
plot(accuracy_blockedlog)

# CHECK INTERACTION EFFECTS (# completed tasks)
tasks_completed_blocked <- aov(tasks_completed~complexity*interval_length + participant, 
                        data=within_2f)
summary(tasks_completed_blocked) 
par(mfrow = c(2,2))
plot(tasks_completed_blocked)
# Sqrt
tasks_completed_blockedsqrt <- aov(sqrt(tasks_completed)~complexity*interval_length + participant, 
                             data=within_2f)
summary(tasks_completed_blockedsqrt) 
par(mfrow = c(2,2))
plot(tasks_completed_blockedsqrt)
# Log
tasks_completed_blockedlog <- aov(log(tasks_completed)~complexity*interval_length + participant, 
                                    data=within_2f)
summary(tasks_completed_blockedlog) 
par(mfrow = c(2,2))
plot(tasks_completed_blockedlog)

# Main effect - complexity
complexity_main <- emmeans(accuracy_blocked, ~ complexity)
pairs(complexity_main, adjust = "tukey")
complexity_main <- emmeans(tasks_completed_blocked, ~ complexity)
pairs(complexity_main, adjust = "tukey")
# All complexity pairs are significant

# Main effect - interval_length
interval_length_main <- emmeans(accuracy_blocked, ~ interval_length)
pairs(interval_length_main, adjust = "tukey")
interval_length_main <- emmeans(tasks_completed_blocked, ~ interval_length)
pairs(interval_length_main, adjust = "tukey")
# interval_length 20 and 30 are not significant

