import pygame
import random
import time
import sys
import csv

# -----------------------------
# INITIALIZE
# -----------------------------
pygame.init()

WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Task Switching Experiment")

FONT = pygame.font.SysFont("arial", 32)
SMALL_FONT = pygame.font.SysFont("arial", 24)
FONT_BOLD = pygame.font.SysFont("arial", 32, bold=True)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (220, 60, 60)
GREEN = (60, 180, 75)

clock = pygame.time.Clock()

# -----------------------------
# CREATE CSV FILE
# -----------------------------
import os # Change file to work directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "session_data")
os.makedirs(SESSION_DIR, exist_ok=True)

import datetime # Make a new file each time. Do not overwrite files
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"results_{timestamp}.csv"
CSV_FILE = os.path.join(SESSION_DIR, filename)

with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "trial",
        "complexity",
        "interval",
        "task_type",
        "actual_count",
        "user_answer",
        "correct"
    ])

# -----------------------------
# EXPERIMENT DESIGN (3x3)
# -----------------------------
complexities = [1, 2, 3]
intervals = [10, 20, 30]

# Randomize the ORDER of complexity blocks
complexity_order = complexities.copy()
random.shuffle(complexity_order)

conditions = []

# Randomize complexity for each level (i.e., 2 can be first) but complexity is constant for consecutive trials 1-3, 3-6, 7,-9
for c in complexity_order:
    shuffled_intervals = intervals.copy()
    random.shuffle(shuffled_intervals)

    for i in shuffled_intervals:
        conditions.append((c, i))

current_condition_index = 0

# -----------------------------
# TASK VARIABLES
# -----------------------------
digit_string = ""
target_digits = []
task_type = 1  # 1 = count targets, 2 = count non-targets
user_input = ""
tasks_completed = 0
TOTAL_TRIAL_TIME = 120  # seconds

# -----------------------------
# GAME/GLOBAL VARIABLES
# -----------------------------

STATE_START = 0
STATE_COUNTDOWN = 1
STATE_RUNNING = 2
STATE_BREAK = 3

BREAK_DURATION = 10
break_start_time = None

game_state = STATE_START
countdown_start_time = None

# Keep track of intervals
condition_start_time = time.time() 
interval_start_time = time.time()
last_switch_time = time.time()

# Cursor
CURSOR_BLINK_INTERVAL = 0.5  # seconds
cursor_visible = True
last_cursor_toggle = time.time()

# -----------------------------
# GENERATION FUNCTIONS
# -----------------------------
def generate_trial(complexity, length=10):
    global digit_string, target_digits

    digit_string = "".join(str(random.randint(0, 9)) for _ in range(length))
    target_digits = random.sample(range(10), complexity)


def compute_answer():
    if task_type == 1:
        return sum(digit_string.count(str(d)) for d in target_digits)
    else:
        total_targets = sum(digit_string.count(str(d)) for d in target_digits)
        return len(digit_string) - total_targets
    
def log_trial(correct_flag, actual_count, user_answer):
    global tasks_completed

    tasks_completed += 1

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            tasks_completed,
            complexity,
            duration,
            task_type,
            actual_count,
            user_answer,
            correct_flag
        ])

def switch_task():
    global task_type
    task_type = 2 if task_type == 1 else 1


# -----------------------------
# DRAW UI
# -----------------------------
def draw_progress_bar():
    bar_x = 50
    bar_y = HEIGHT - 60
    bar_width = WIDTH - 100
    bar_height = 20

    elapsed = time.time() - condition_start_time
    progress = min(elapsed / TOTAL_TRIAL_TIME, 1)

    # background
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))

    # filled portion
    pygame.draw.rect(
        screen,
        RED,
        (bar_x, bar_y, int(bar_width * progress), bar_height),
    )

    # -----------------------------
    # DRAW INTERVAL MARKS
    # -----------------------------
    num_marks = TOTAL_TRIAL_TIME // duration

    for i in range(1, int(num_marks)):
        mark_x = bar_x + (i / num_marks) * bar_width

        pygame.draw.line(
            screen,
            BLACK,
            (mark_x, bar_y - 5),
            (mark_x, bar_y + bar_height + 5),
            2,
        )

def draw_break_screen():
    screen.fill(WHITE)

    title_surface = FONT.render("Break Time", True, BLACK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 180))
    screen.blit(title_surface, title_rect)

    remaining = BREAK_DURATION - int(time.time() - break_start_time)
    if remaining < 0:
        remaining = 0

    countdown_surface = FONT.render(
        f"Next block starts in {remaining} seconds",
        True,
        BLACK
    )
    countdown_rect = countdown_surface.get_rect(center=(WIDTH//2, 240))
    screen.blit(countdown_surface, countdown_rect)

    pygame.display.flip()

def draw_start_screen():
    screen.fill(WHITE)

    # Title
    title_surface = FONT.render("Task-Switching Experiment (9 Levels)", True, BLACK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 80))
    screen.blit(title_surface, title_rect)

    # Instructions
    lines = [
        "You will switch between 2 tasks:",
        "Task 1: Count total occurrences of specified target digits in a string",
        "Task 2: Count total occurrences of target digits NOT specified in a string",
        "Goal: Complete a task as many times as possible within an interval.",
        "Type your answer and press ENTER to submit."
    ]

    for i, line in enumerate(lines):
        line_surface = SMALL_FONT.render(line, True, BLACK)
        line_rect = line_surface.get_rect(center=(WIDTH//2, 150 + i*40))
        screen.blit(line_surface, line_rect)

    # Start Button
    button_rect = pygame.Rect(WIDTH//2 - 100, 400, 200, 60)
    pygame.draw.rect(screen, GREEN, button_rect)

    button_text = FONT.render("START", True, WHITE)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

    pygame.display.flip()

    return button_rect

def draw_countdown():
    screen.fill(WHITE)

    elapsed = time.time() - countdown_start_time
    remaining = 5 - int(elapsed)

    if remaining < 0:
        remaining = 0

    countdown_surface = FONT.render(f"Starting in {remaining}", True, BLACK)
    countdown_rect = countdown_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(countdown_surface, countdown_rect)

    pygame.display.flip()

def draw_interface(duration):
    screen.fill(WHITE)
    Y_OFFSET = 30 # Change Y Position
    # -----------------------------
    # INSTRUCTION TEXT
    # -----------------------------
    if task_type == 1:
        instruction = "Count digits in the target set:"
    else:
        instruction = "Count digits NOT in the target set:"

    if task_type == 1:
        instruction_surface = FONT.render(
            "Count how many times target digits appear:",
            True,
            BLACK
        )
        instruction_rect = instruction_surface.get_rect(center=(WIDTH//2, 50 + Y_OFFSET))
        screen.blit(instruction_surface, instruction_rect)

    else:
        # Split into three parts
        part1 = FONT.render("Count digits ", True, BLACK)
        part2 = FONT_BOLD.render("NOT", True, BLACK)
        part3 = FONT.render(" in the target set:", True, BLACK)

        total_width = part1.get_width() + part2.get_width() + part3.get_width()

        start_x = WIDTH//2 - total_width // 2
        y = 50 

        screen.blit(part1, (start_x, y))
        screen.blit(part2, (start_x + part1.get_width(), y))
        screen.blit(part3, (start_x + part1.get_width() + part2.get_width(), y))
    # -----------------------------
    # TARGET DIGITS
    # -----------------------------
    targets_surface = FONT.render(
        f"Targets: {set(target_digits)}", True, BLACK
    )
    targets_rect = targets_surface.get_rect(center=(WIDTH//2, 110 + Y_OFFSET))
    screen.blit(targets_surface, targets_rect)

    # -----------------------------
    # DIGIT STRING
    # -----------------------------
    digits_surface = FONT.render(digit_string, True, BLACK)
    digits_rect = digits_surface.get_rect(center=(WIDTH//2, 170 + Y_OFFSET))
    screen.blit(digits_surface, digits_rect)

    # -----------------------------
    # INPUT BOX
    # -----------------------------
    input_box_rect = pygame.Rect(WIDTH//2 - 60, 210 + Y_OFFSET, 120, 50)
    pygame.draw.rect(screen, BLACK, input_box_rect, 2)

    # Render text centered
    input_surface = FONT.render(user_input, True, BLACK)
    input_rect = input_surface.get_rect(center=input_box_rect.center)
    screen.blit(input_surface, input_rect)

    # -----------------------------
    # BLINKING CURSOR (CENTERED)
    # -----------------------------
    if cursor_visible:

        if user_input == "":
            # Cursor in exact center when empty
            cursor_x = input_box_rect.centerx
        else:
            # Cursor right after text
            cursor_x = input_rect.right + 2

        cursor_y_top = input_box_rect.centery - 15
        cursor_y_bottom = input_box_rect.centery + 15

        pygame.draw.line(
            screen,
            BLACK,
            (cursor_x, cursor_y_top),
            (cursor_x, cursor_y_bottom),
            2
        )

    # -----------------------------
    # PROGRESS BAR
    # -----------------------------
    draw_progress_bar()

    pygame.display.flip()


# -----------------------------
# START FIRST TRIAL
# -----------------------------
complexity, duration = conditions[current_condition_index]
generate_trial(complexity)

# -----------------------------
# MAIN LOOP
# -----------------------------

running = True

while running:
    clock.tick(60)

    current_time = time.time()

    # Cursor blinking
    if current_time - last_cursor_toggle >= CURSOR_BLINK_INTERVAL:
        cursor_visible = not cursor_visible
        last_cursor_toggle = current_time

    # ============================
    # START SCREEN
    # ============================
    if game_state == STATE_START:

        start_button_rect = draw_start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    game_state = STATE_COUNTDOWN
                    countdown_start_time = time.time()

    # ============================
    # COUNTDOWN SCREEN
    # ============================
    elif game_state == STATE_COUNTDOWN:

        draw_countdown()

        if current_time - countdown_start_time >= 5:
            game_state = STATE_RUNNING
            condition_start_time = time.time()
            last_switch_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # ============================
    # RUNNING EXPERIMENT
    # ============================
    elif game_state == STATE_RUNNING:

        # ----- TASK SWITCH -----
        if current_time - last_switch_time >= duration:
            switch_task()
            generate_trial(complexity)
            user_input = ""
            last_switch_time = current_time

        # ----- END CONDITION -----
        if current_time - condition_start_time >= TOTAL_TRIAL_TIME:

            current_condition_index += 1

            if current_condition_index >= len(conditions):
                print("Experiment complete!")
                pygame.quit()
                sys.exit()

            game_state = STATE_BREAK
            break_start_time = time.time()

        # ----- EVENT HANDLING -----
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    if user_input != "":
                        correct_answer = compute_answer()

                        try:
                            response = int(user_input)
                        except ValueError:
                            response = -999

                        correct_flag = 1 if response == correct_answer else 0
                        log_trial(correct_flag, correct_answer, response)

                        generate_trial(complexity)
                        user_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]

                elif event.unicode.isdigit():
                    user_input += event.unicode

        draw_interface(duration)
    
    # ============================
    # BREAK BETWEEN BLOCKS
    # ============================
    elif game_state == STATE_BREAK:

        draw_break_screen()

        if current_time - break_start_time >= BREAK_DURATION:

            complexity, duration = conditions[current_condition_index]
            generate_trial(complexity)

            condition_start_time = time.time()
            last_switch_time = time.time()
            user_input = ""

            game_state = STATE_RUNNING

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

pygame.quit()