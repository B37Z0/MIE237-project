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

BG = (245, 245, 250)
WHITE = (255, 255, 255)
BLACK = (40, 40, 50)
GRAY = (210, 215, 225)
RED = (200, 75, 75)
GREEN = (75, 180, 110)
ACCENT = (70, 130, 210)
SUBTLE = (140, 145, 160)

clock = pygame.time.Clock()

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "session_data")
os.makedirs(SESSION_DIR, exist_ok=True)

import datetime
CSV_FILE = None

def create_csv():
    global CSV_FILE
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
STATE_DONE = 4
STATE_TUTORIAL = 5

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

# Task-switch banner
switch_banner_time = 0
SWITCH_BANNER_DURATION = 1.0

# Tutorial state
tutorial_step = 0  # 0=explain task1, 1=practice task1, 2=explain task2, 3=practice task2
tutorial_input = ""
tutorial_feedback = ""  # "correct" or "incorrect" or ""

# -----------------------------
# GENERATION FUNCTIONS
# -----------------------------
def generate_trial(complexity, length=10):
    global digit_string, target_digits

    while True:
        digit_string = "".join(str(random.randint(0, 9)) for _ in range(length))
        target_digits = random.sample(range(10), complexity)

        # Ensure the answer is never 10:
        # For task 2 (non-target count), ensure at least 1 target digit appears so the 
        # answer is at most 9. Task 1 has no restriction (0 is valid, 10 is impossibly rare).
        target_count = sum(digit_string.count(str(d)) for d in target_digits)
        if task_type == 1 or target_count > 0:
            break


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
    bar_height = 16

    elapsed = time.time() - condition_start_time
    progress = min(elapsed / TOTAL_TRIAL_TIME, 1)

    # background
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=8)

    # filled portion
    if int(bar_width * progress) > 0:
        pygame.draw.rect(
            screen,
            ACCENT,
            (bar_x, bar_y, int(bar_width * progress), bar_height),
            border_radius=8
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
    screen.fill(BG)

    title_surface = FONT.render("Break Time", True, BLACK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 180))
    screen.blit(title_surface, title_rect)

    remaining = BREAK_DURATION - int(time.time() - break_start_time)
    if remaining < 0:
        remaining = 0

    countdown_surface = FONT.render(
        f"Next block starts in {remaining} seconds",
        True,
        SUBTLE
    )
    countdown_rect = countdown_surface.get_rect(center=(WIDTH//2, 240))
    screen.blit(countdown_surface, countdown_rect)

    # Block progress
    block_label = SMALL_FONT.render(
        f"Completed {current_condition_index} of {len(conditions)} blocks",
        True, SUBTLE
    )
    block_rect = block_label.get_rect(center=(WIDTH//2, 300))
    screen.blit(block_label, block_rect)

    pygame.display.flip()

def draw_done_screen():
    screen.fill(BG)

    title_surface = FONT.render("Experiment Complete", True, BLACK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    screen.blit(title_surface, title_rect)

    sub_surface = SMALL_FONT.render("Thank you for participating! You may close this window.", True, SUBTLE)
    sub_rect = sub_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    screen.blit(sub_surface, sub_rect)

    pygame.display.flip()

def draw_start_screen():
    screen.fill(BG)

    # Title
    title_surface = FONT.render("Task-Switching Experiment (9 Blocks)", True, BLACK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 80))
    screen.blit(title_surface, title_rect)

    # Instructions
    lines = [
        "You will switch between 2 tasks:",
        "Task 1: Count total occurrences of specified digits in a string",
        "Task 2: Count total occurrences of digits NOT specified in a string",
        "Goal: Complete the task correctly as many times as possible.",
        "Type your answer and press ENTER to submit."
    ]

    for i, line in enumerate(lines):
        line_surface = SMALL_FONT.render(line, True, BLACK)
        line_rect = line_surface.get_rect(center=(WIDTH//2, 150 + i*40))
        screen.blit(line_surface, line_rect)

    # Tutorial Button (rounded)
    tutorial_rect = pygame.Rect(WIDTH//2 - 220, 400, 200, 55)
    pygame.draw.rect(screen, ACCENT, tutorial_rect, border_radius=10)

    tutorial_text = FONT.render("TUTORIAL", True, WHITE)
    tutorial_text_rect = tutorial_text.get_rect(center=tutorial_rect.center)
    screen.blit(tutorial_text, tutorial_text_rect)

    # Start Button (rounded)
    start_rect = pygame.Rect(WIDTH//2 + 20, 400, 200, 55)
    pygame.draw.rect(screen, GREEN, start_rect, border_radius=10)

    start_text = FONT.render("START", True, WHITE)
    start_text_rect = start_text.get_rect(center=start_rect.center)
    screen.blit(start_text, start_text_rect)

    pygame.display.flip()

    return start_rect, tutorial_rect

def draw_tutorial():
    screen.fill(BG)

    # Explanation steps (0 and 2)
    if tutorial_step == 0:
        title = FONT.render("Tutorial — Task 1", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))

        lines = [
            "You will see a string of digits and a set of target digits.",
            "Count how many times any of the target digits appear in the string.",
            "Example: String = 3 8 1 4 3 2 7 1 9 0   Targets: {1, 3}",
            "Answer: 4  (two 3s and two 1s)",
            "",
            "Press SPACE to try a practice round."
        ]
        for i, line in enumerate(lines):
            s = SMALL_FONT.render(line, True, BLACK)
            screen.blit(s, s.get_rect(center=(WIDTH//2, 140 + i * 35)))

    elif tutorial_step == 2:
        title = FONT.render("Tutorial — Task 2", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))

        lines = [
            "This time, count the digits NOT in the target set.",
            "Tip: count the targets and subtract from 10.",
            "Example: String = 3 8 1 4 3 2 7 1 9 0   Targets: {1, 3}",
            "Answer: 6  (10 total minus 4 targets)",
            "",
            "Press SPACE to try a practice round."
        ]
        for i, line in enumerate(lines):
            s = SMALL_FONT.render(line, True, BLACK)
            screen.blit(s, s.get_rect(center=(WIDTH//2, 140 + i * 35)))

    # Practice steps (1 and 3)
    elif tutorial_step in (1, 3):
        practice_task = 1 if tutorial_step == 1 else 2

        if practice_task == 1:
            label = FONT.render("Practice — Count target digits:", True, BLACK)
        else:
            part1 = FONT.render("Practice — Count digits ", True, BLACK)
            part2 = FONT_BOLD.render("NOT", True, RED)
            part3 = FONT.render(" in targets:", True, BLACK)

        if practice_task == 1:
            screen.blit(label, label.get_rect(center=(WIDTH//2, 60)))
        else:
            total_w = part1.get_width() + part2.get_width() + part3.get_width()
            sx = WIDTH//2 - total_w // 2
            screen.blit(part1, (sx, 48))
            screen.blit(part2, (sx + part1.get_width(), 48))
            screen.blit(part3, (sx + part1.get_width() + part2.get_width(), 48))

        # Targets
        targets_surface = FONT.render(f"Targets: {set(target_digits)}", True, BLACK)
        screen.blit(targets_surface, targets_surface.get_rect(center=(WIDTH//2, 120)))

        # Digit string
        digits_surface = FONT.render(digit_string, True, BLACK)
        screen.blit(digits_surface, digits_surface.get_rect(center=(WIDTH//2, 180)))

        # Input box
        input_box_rect = pygame.Rect(WIDTH//2 - 60, 220, 120, 50)
        pygame.draw.rect(screen, WHITE, input_box_rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, input_box_rect, 2, border_radius=8)

        input_surface = FONT.render(tutorial_input, True, BLACK)
        input_rect = input_surface.get_rect(center=input_box_rect.center)
        screen.blit(input_surface, input_rect)

        # Cursor
        if cursor_visible:
            if tutorial_input == "":
                cx = input_box_rect.centerx
            else:
                cx = input_rect.right + 2
            pygame.draw.line(screen, BLACK, (cx, input_box_rect.centery - 15),
                             (cx, input_box_rect.centery + 15), 2)

        # Feedback
        if tutorial_feedback == "correct":
            fb = FONT.render("Correct! Press SPACE to continue.", True, GREEN)
            screen.blit(fb, fb.get_rect(center=(WIDTH//2, 330)))
        elif tutorial_feedback == "incorrect":
            fb = FONT.render("Incorrect. Try again.", True, RED)
            screen.blit(fb, fb.get_rect(center=(WIDTH//2, 330)))

        # Hint
        hint = SMALL_FONT.render("Type your answer and press ENTER.", True, SUBTLE)
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, 400)))

    pygame.display.flip()

def draw_countdown():
    screen.fill(BG)

    elapsed = time.time() - countdown_start_time
    remaining = 5 - int(elapsed)

    if remaining < 0:
        remaining = 0

    countdown_surface = FONT.render(f"Starting in {remaining}", True, BLACK)
    countdown_rect = countdown_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(countdown_surface, countdown_rect)

    pygame.display.flip()

def draw_interface(duration):
    screen.fill(BG)
    Y_OFFSET = 30 # Change Y Position

    # -----------------------------
    # BLOCK PROGRESS (top-right)
    # -----------------------------
    block_label = SMALL_FONT.render(
        f"Block {current_condition_index + 1} / {len(conditions)}",
        True, SUBTLE
    )
    screen.blit(block_label, (WIDTH - block_label.get_width() - 20, 12))

    # -----------------------------
    # INSTRUCTION TEXT
    # -----------------------------
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
        part2 = FONT_BOLD.render("NOT", True, RED)
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
    # IF YOU WANT TO SEPARATE THE DIGITS WITH SPACES, USE THIS LINE:
    # digits_surface = FONT.render(" ".join(digit_string), True, BLACK)
    digits_surface = FONT.render(digit_string, True, BLACK)
    digits_rect = digits_surface.get_rect(center=(WIDTH//2, 170 + Y_OFFSET))
    screen.blit(digits_surface, digits_rect)

    # -----------------------------
    # INPUT BOX (rounded)
    # -----------------------------
    input_box_rect = pygame.Rect(WIDTH//2 - 60, 210 + Y_OFFSET, 120, 50)
    pygame.draw.rect(screen, WHITE, input_box_rect, border_radius=8)
    pygame.draw.rect(screen, GRAY, input_box_rect, 2, border_radius=8)

    # Render text centered
    input_surface = FONT.render(user_input, True, BLACK)
    input_rect = input_surface.get_rect(center=input_box_rect.center)
    screen.blit(input_surface, input_rect)

    # -----------------------------
    # BLINKING CURSOR (CENTERED)
    # -----------------------------
    if cursor_visible:

        if user_input == "":
            cursor_x = input_box_rect.centerx
        else:
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
    # TASK-SWITCH BANNER
    # -----------------------------
    if time.time() - switch_banner_time < SWITCH_BANNER_DURATION:
        banner_surface = FONT_BOLD.render("TASK SWITCH!", True, ACCENT)
        banner_rect = banner_surface.get_rect(center=(WIDTH//2, 300 + Y_OFFSET))
        screen.blit(banner_surface, banner_rect)

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

        start_button_rect, tutorial_button_rect = draw_start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    create_csv()
                    game_state = STATE_COUNTDOWN
                    countdown_start_time = time.time()
                elif tutorial_button_rect.collidepoint(event.pos):
                    tutorial_step = 0
                    tutorial_input = ""
                    tutorial_feedback = ""
                    game_state = STATE_TUTORIAL

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
            switch_banner_time = current_time

        # ----- END CONDITION -----
        if current_time - condition_start_time >= TOTAL_TRIAL_TIME:

            current_condition_index += 1

            if current_condition_index >= len(conditions):
                game_state = STATE_DONE
            else:
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

    # ============================
    # DONE SCREEN
    # ============================
    elif game_state == STATE_DONE:

        draw_done_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # ============================
    # TUTORIAL
    # ============================
    elif game_state == STATE_TUTORIAL:

        draw_tutorial()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                # Explanation steps (0, 2): press SPACE to start practice
                if tutorial_step in (0, 2):
                    if event.key == pygame.K_SPACE:
                        tutorial_step += 1
                        tutorial_input = ""
                        tutorial_feedback = ""
                        # Set task_type for practice
                        task_type = 1 if tutorial_step == 1 else 2
                        generate_trial(2)  # complexity 2 for tutorial

                # Practice steps (1, 3): type answer and submit
                elif tutorial_step in (1, 3):

                    if tutorial_feedback == "correct":
                        # SPACE to advance after correct answer
                        if event.key == pygame.K_SPACE:
                            tutorial_step += 1
                            tutorial_input = ""
                            tutorial_feedback = ""
                            if tutorial_step >= 4:
                                # Tutorial done, return to start
                                task_type = 1
                                game_state = STATE_START
                    else:
                        if event.key == pygame.K_RETURN:
                            if tutorial_input != "":
                                correct_answer = compute_answer()
                                try:
                                    response = int(tutorial_input)
                                except ValueError:
                                    response = -999

                                if response == correct_answer:
                                    tutorial_feedback = "correct"
                                else:
                                    tutorial_feedback = "incorrect"
                                    tutorial_input = ""

                        elif event.key == pygame.K_BACKSPACE:
                            tutorial_input = tutorial_input[:-1]

                        elif event.unicode.isdigit():
                            tutorial_input += event.unicode

pygame.quit()