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
        y = "Number of Task Completed" )

# Interaction Plot, parallel lines indicate no significant interaction
# interval_length
ggplot(within_2f, aes(x = interval_length, y = accuracy, color = complexity, group = complexity)) +
  stat_summary(fun = mean, geom = "line") +
  stat_summary(fun = mean, geom = "point") +
  theme_minimal()

# complexity
ggplot(within_2f, aes(x = interval_length, y = tasks_completed, color = complexity, group = complexity)) +
  stat_summary(fun = mean, geom = "line") +
  stat_summary(fun = mean, geom = "point") +
  theme_minimal()

# CHECK PARTICIPANT BASELINE DIFFERENCES
# Accuracy
participant_diff_accuracy <- aov(asin(sqrt(accuracy)) ~ participant, data = within_2f)
summary(participant_diff_accuracy)
par(mfrow = c(2,2))
plot(participant_diff_accuracy)

# Tasks Completed
participant_diff_tasks_completed <- aov(sqrt(tasks_completed) ~ participant, data = within_2f)
summary(participant_diff_tasks_completed)
par(mfrow = c(2,2))
plot(participant_diff_tasks_completed)


# CHECK INTERACTION EFFECTS (accuracy)
accuracy_blocked <- aov(accuracy~complexity*interval_length + participant, 
                        data=within_2f)
summary(accuracy_blocked) 
# Diagnostic
par(mfrow = c(2,2))
plot(accuracy_blocked)

# CHECK INTERACTION EFFECTS (# completed tasks)
tasks_completed_blocked <- aov(tasks_completed~complexity*interval_length + participant, 
                        data=within_2f)
summary(tasks_completed_blocked) 
par(mfrow = c(2,2))
plot(tasks_completed_blocked)
# Square root transformation (addresses unequal variance)
# test if significant values in ANOVA results in original and sqrt transform correspond 
tasks_completed_blocked_sqrt <- aov(sqrt(tasks_completed)~complexity*interval_length + participant, 
                             data=within_2f)
summary(tasks_completed_blocked_sqrt) 
par(mfrow = c(2,2))
plot(tasks_completed_blocked_sqrt) # sqrt fixes variance and normality (mostly)

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

