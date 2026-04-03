# Imports
library(tidyverse)
library(emmeans)

# Read data
within_2f <- read_csv("participant_accuracy.csv")

# Convert to categorical variables
within_2f <- data %>%
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

# Check interaction effects between complexity and interval_length on accuracy
accuracy_blocked <- aov(accuracy~complexity*interval_length + participant, 
                        data=within_2f)
summary(accuracy_blocked) 
# no interaction effect between complexity and interval length on number
# of tasks completed -> main effects

# Check interaction effects between complexity and interval_length on number of
# tasks completed
tasks_completed_blocked <- aov(tasks_completed~complexity*interval_length + participant, 
                        data=within_2f)
summary(tasks_completed_blocked) 
# no interaction effect between complexity and interval length on 
# number of task completed -> main effects

# Main effect - complexity
complexity_main <- emmeans(accuracy_blocked, ~ complexity)
complexity_main
pairs(complexity_main, adjust = "tukey")
# All complexity pairs are significant

# Main effect - interval_length
interval_length_main <- emmeans(accuracy_blocked, ~ interval_length)
interval_length_main
pairs(interval_length_main, adjust = "tukey")
# interval_length 20 and 30 are not significant

# Regression on accuracy
summary(lm(accuracy ~ complexity * interval_length + participant, data = within_2f))
# Regression on tasks completed
summary(lm(tasks_completed ~ complexity * interval_length + participant, data = within_2f))

# Run diagnostic plots
par(mfrow = c(2,2))
plot(accuracy_blocked)
# Residuals vs Fitted: slight curvature, linearity may be violated
# Q-Q Residuals: points fit along line, normality holds
# Scale-Location: most points form a horizontal band, variance is constant
# Residuals vs Leverage: no outliers so no influential points

par(mfrow = c(2,2))
plot(tasks_completed_blocked)
# Residuals vs Fitted: slight curvature, linearity may be violated
# Q-Q Residuals: points fit along line, normality holds
# Scale-Location: most points form a horizontal band, variance is constant
# Residuals vs Leverage: no outliers so no influential points

