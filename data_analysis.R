# Imports
library(tidyverse)
library(emmeans)

# Read data
data <- read_csv("participant_accuracy.csv")

# Convert to categorical variables
data <- data %>%
  mutate(
    participant = factor(participant),
    complexity = factor(complexity,
                        levels = c("Easy", "Medium", "Hard")),
    interval_length = factor(interval_length,
                             levels = c(10,20,30))
  )

# Exploring participant effects and accuracy
ggplot(data, aes(x = participant, y = accuracy)) +
  geom_boxplot() +
  theme_minimal() +
  labs( x = "Participant" ,
        y = "Accuracy" )

data %>%
  group_by(participant) %>%
  summarise(
    mean_cost = mean(accuracy),
    sd_cost = sd(accuracy)
    )

# Exploring participant effects and number of tasks completed
ggplot(data, aes(x = participant, y = tasks_completed)) +
  geom_boxplot() +
  theme_minimal() +
  labs( x = "Participant" ,
        y = "Number of Task Completed" )

data %>%
  group_by(participant) %>%
  summarise(
    mean_cost = mean(tasks_completed),
    sd_cost = sd(tasks_completed)
  )

# Blocked Two-Factor