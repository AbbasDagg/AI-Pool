import math
import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("AI Pool")
clock = pygame.time.Clock()
running = True

# background colors
FELT_GREEN = (0, 100, 0)
RAIL_BROWN = (139, 69, 19)
ROOM_GREY = (109, 109, 109)
TABLE_WIDTH = 800
TABLE_HEIGHT = 400
RAIL_WIDTH = 20

# ball stuff
FRICTION = 0.98  
BALL_RADIUS = 10
CURR_POWER = 0.5  # Default power for aiming
MAX_STEP_DISTANCE = BALL_RADIUS / 2  # no ball may move further than this in one substep
STOP_SPEED = 0.05  # below this speed a ball counts as stopped

# pockets
POCKET_RADIUS = 18  # size of the black hole that gets drawn
POCKET_OFFSET = 8   # how far the pocket center sits outside the felt edge
# Near a pocket there's no cushion, so balls don't bounce there. This is how close (to the pocket center) that is.
# Corner pockets have a wider opening than side pockets, like a real table.
CORNER_POCKET_MOUTH = 45
SIDE_POCKET_MOUTH = 30
SIDE_POCKETS = (1, 4)  # indexes of the side pockets in get_pocket_positions()

# Params
LOST = False  # True if the player has lost (potted the 8-ball early)
SCORE = 0
CUE_BALL_PENALTY = -5  # Penalty for potting the cue ball
EIGHT_BALL_PENALTY = -1000  # Penalty for potting the 8-ball early
BALL_POT_REWARD = 3  # Reward for potting a regular ball
SHOT_PENALTY = 0  # Penalty for taking a shot (to encourage efficiency)
SHOT_COUNT = 0  # Count of shots taken
GAME_SPEED = 1  # Speed multiplier for the game (1.0 = normal speed)

pool_balls = [
    {"number": None, "color": "White", "type": "Cue", "position": (0, 0), "velocity": (0, 0), "potted": False},  # Cue ball
    # Rack order: apex, then rows of 2, 3, 4, and 5 balls.
    # The 8-ball is centered and the two back corners are different types.
    {"number": 11, "color": "Red", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 2, "color": "Blue", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 13, "color": "Orange", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 3, "color": "Red", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 8, "color": "Black", "type": "8-Ball", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 15, "color": "Maroon", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 6, "color": "Green", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 7, "color": "Maroon", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 9, "color": "Yellow", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 1, "color": "Yellow", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 10, "color": "Blue", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 12, "color": "Purple", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 4, "color": "Purple", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 14, "color": "Green", "type": "Stripe", "position": (0, 0), "velocity": (0, 0), "potted": False},
    {"number": 5, "color": "Orange", "type": "Solid", "position": (0, 0), "velocity": (0, 0), "potted": False},
]

# Define drawing function for the room and table
def draw_room_and_table():
    # Draw the room
    screen.fill(ROOM_GREY)

    # Prepare table cords
    table_x = screen.get_width() // 2 - TABLE_WIDTH // 2
    table_y = screen.get_height() // 2 - TABLE_HEIGHT // 2

    # Draw the rails
    pygame.draw.rect(screen, RAIL_BROWN, (table_x - RAIL_WIDTH, table_y - RAIL_WIDTH, TABLE_WIDTH + 2 * RAIL_WIDTH, TABLE_HEIGHT + 2 * RAIL_WIDTH), border_radius=5)

    # Draw the pool table
    pygame.draw.rect(screen, FELT_GREEN, (table_x, table_y, TABLE_WIDTH, TABLE_HEIGHT))

    # Draw the pockets
    for pos in get_pocket_positions():
        pygame.draw.circle(screen, (0, 0, 0), pos, POCKET_RADIUS)

    # Draw the head string
    head_string_x = table_x + TABLE_WIDTH // 4
    pygame.draw.line(screen, (255, 255, 255), (head_string_x, table_y + 25), (head_string_x, table_y + TABLE_HEIGHT - 25), 2)

def draw_ball(ball):
    # Draw a single ball based on its type and color
    x, y = ball["position"]
    if ball["type"] == "Solid":
        pygame.draw.circle(screen, ball["color"], (x, y), BALL_RADIUS)
    elif ball["type"] == "Stripe":
        pygame.draw.circle(screen, ball["color"], (x, y), BALL_RADIUS)
        pygame.draw.rect(screen, (255, 255, 255), (x - BALL_RADIUS, y - BALL_RADIUS // 4, 2 * BALL_RADIUS, BALL_RADIUS // 2))
    elif ball["type"] == "8-Ball":
        pygame.draw.circle(screen, (0, 0, 0), (x, y), BALL_RADIUS)
    elif ball["type"] == "Cue":
        pygame.draw.circle(screen, (255, 255, 255), (x, y), BALL_RADIUS)

def initial_ball_positions():
    # Set the initial positions of the cue ball and object balls.
    table_x = screen.get_width() // 2 - TABLE_WIDTH // 2
    table_y = screen.get_height() // 2 - TABLE_HEIGHT // 2

    cue_ball_x = table_x + TABLE_WIDTH // 4 - BALL_RADIUS
    cue_ball_y = table_y + TABLE_HEIGHT // 2
    pool_balls[0]["position"] = (cue_ball_x, cue_ball_y)

    rack_x = table_x + (3 * TABLE_WIDTH) // 4
    rack_y = table_y + TABLE_HEIGHT // 2
    row_spacing = BALL_RADIUS * 2
    column_spacing = int(row_spacing * 0.866)

    ball_index = 1
    for row in range(5):
        ball_x = rack_x + row * column_spacing
        ball_y = rack_y - row * row_spacing // 2
        for col in range(row + 1):
            pool_balls[ball_index]["position"] = (ball_x, ball_y + col * row_spacing)
            ball_index += 1

def draw_balls():
    for ball in pool_balls:
        if not ball["potted"]:
            draw_ball(ball)
        else:
            # Draw potted balls in a separate area (e.g., top-left corner)
            potted_x = 50 + (ball["number"] - 1) * (BALL_RADIUS * 2 + 5)
            potted_y = 50
            pygame.draw.circle(screen, ball["color"], (potted_x, potted_y), BALL_RADIUS)

def draw_loss_message():
    font = pygame.font.Font(None, 74)
    text = font.render("You Lose!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, text_rect)
    global LOST
    LOST = True  # Set the LOST flag to True when the message is displayed

def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {SCORE}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

def draw_shot_count():
    font = pygame.font.Font(None, 36)
    shot_text = font.render(f"Shots Taken: {SHOT_COUNT}", True, (255, 255, 255))
    screen.blit(shot_text, (10, 50))

def draw_hit_power_bar(power):
    bar_width = 400
    bar_height = 20
    bar_x = screen.get_width() // 2 - bar_width // 2
    bar_y = screen.get_height() - 50

    # Draw the background of the power bar
    pygame.draw.rect(screen, (169, 169, 169), (bar_x, bar_y, bar_width, bar_height))

    # Draw the filled portion of the power bar based on the current power level
    filled_width = int(bar_width * power)
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))

def draw_que_ball_aim_line():
    cue_ball = pool_balls[0]
    cue_ball_x, cue_ball_y = cue_ball["position"]
    end_x, end_y = get_x_y()

    # Draw a line from the cue ball to the aim position (mouse or AI)
    pygame.draw.line(screen, (255, 255, 255), (cue_ball_x, cue_ball_y), (end_x, end_y), 2)

# Where the AI wants to aim. The AI will set this later; (0, 0) is just a placeholder.
ai_target = (0, 0)

def get_x_y():
    # The ONLY place that decides who is aiming: the mouse or the AI.
    if method == "normal":
        return pygame.mouse.get_pos()
    elif method == "AI":
        return ai_target

def eight_ball_potted():
    # Check if the 8-ball is potted
    eight_ball = next(ball for ball in pool_balls if ball["type"] == "8-Ball")
    return eight_ball["potted"]

def all_balls_potted():
    # Check if all balls except the cue ball are potted
    return all(ball["potted"] for ball in pool_balls[1:])

def get_pocket_positions():
    # The ONE list of pocket centers, used for drawing, bouncing and potting.
    table_x = screen.get_width() // 2 - TABLE_WIDTH // 2
    table_y = screen.get_height() // 2 - TABLE_HEIGHT // 2
    return [
        (table_x - POCKET_OFFSET, table_y - POCKET_OFFSET),  # Top-left
        (table_x + TABLE_WIDTH // 2, table_y - POCKET_OFFSET),  # Top-center
        (table_x + TABLE_WIDTH + POCKET_OFFSET, table_y - POCKET_OFFSET),  # Top-right
        (table_x - POCKET_OFFSET, table_y + TABLE_HEIGHT + POCKET_OFFSET),  # Bottom-left
        (table_x + TABLE_WIDTH // 2, table_y + TABLE_HEIGHT + POCKET_OFFSET),  # Bottom-center
        (table_x + TABLE_WIDTH + POCKET_OFFSET, table_y + TABLE_HEIGHT + POCKET_OFFSET),  # Bottom-right
    ]

def is_in_pocket_mouth(x, y):
    # True if (x, y) is close enough to a pocket that there's no cushion to bounce off.
    for i, (px, py) in enumerate(get_pocket_positions()):
        mouth = SIDE_POCKET_MOUTH if i in SIDE_POCKETS else CORNER_POCKET_MOUTH
        if (x - px) ** 2 + (y - py) ** 2 < mouth ** 2:
            return True
    return False

def is_ball_in_pocket(x, y):
    # A ball drops if its center is over the hole, OR if it got past the cushion line
    # (only possible through a pocket mouth, since everywhere else it bounces).
    table_x = screen.get_width() // 2 - TABLE_WIDTH // 2
    table_y = screen.get_height() // 2 - TABLE_HEIGHT // 2
    off_felt = x < table_x or x > table_x + TABLE_WIDTH or y < table_y or y > table_y + TABLE_HEIGHT
    if off_felt:
        return True
    for px, py in get_pocket_positions():
        if (x - px) ** 2 + (y - py) ** 2 < POCKET_RADIUS ** 2:
            return True
    return False

def check_potted_balls():
    # Check if any balls are potted (in pockets)
    global SCORE
    for ball in pool_balls:
        if not ball["potted"]:
            x, y = ball["position"]
            if is_ball_in_pocket(x, y):
                ball["potted"] = True
                ball["velocity"] = (0, 0)
                # Score handling: if the 8-ball is potted, check if the player has lost or won
                if ball["type"] == "8-Ball":
                    if not all_balls_potted():
                        SCORE = EIGHT_BALL_PENALTY
                    else:
                        SCORE += 100  # Reward for potting the 8-ball after all others
                elif ball["type"] == "Cue":
                    SCORE += CUE_BALL_PENALTY
                    ball["position"] = (screen.get_width() // 2 - TABLE_WIDTH // 4, screen.get_height() // 2)  # Reset cue ball position
                    ball["potted"] = False  # Reset cue ball to not potted
                else:
                    SCORE += BALL_POT_REWARD

def decrease_balls_velocity(friction=FRICTION):
    for ball in pool_balls:
        vx, vy = ball["velocity"]
        ball["velocity"] = (vx * friction, vy * friction)

def future_ball_pos(ball, step=1):
    # step = what fraction of the velocity to move by (e.g. 0.25 = a quarter of a frame)
    x, y = ball["position"]
    vx, vy = ball["velocity"]
    return x + vx * step, y + vy * step

def check_ball_collision(ball1, ball2):
    # Balls are already moved, so we just check if they overlap RIGHT NOW.
    x1, y1 = ball1["position"]
    x2, y2 = ball2["position"]
    distance_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return distance_squared < (BALL_RADIUS * 2) ** 2

def resolve_ball_collision(ball1, ball2):
    x1, y1 = ball1["position"]
    x2, y2 = ball2["position"]
    vx1, vy1 = ball1["velocity"]
    vx2, vy2 = ball2["velocity"]

    # 1. The normal: unit vector pointing from ball1's center to ball2's center
    dx = x2 - x1
    dy = y2 - y1
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance == 0:
        return  # exactly on top of each other, no direction to push, skip
    nx = dx / distance
    ny = dy / distance

    # 2. Push them apart so they just touch (each moves half the overlap)
    overlap = BALL_RADIUS * 2 - distance
    x1 -= nx * overlap / 2
    y1 -= ny * overlap / 2
    x2 += nx * overlap / 2
    y2 += ny * overlap / 2
    ball1["position"] = (x1, y1)
    ball2["position"] = (x2, y2)

    # 3. How fast are they approaching each other along the normal? (dot product)
    approach_speed = (vx1 - vx2) * nx + (vy1 - vy2) * ny
    if approach_speed <= 0:
        return  # already moving apart, don't bounce again

    # 4. Swap the velocity along the normal (equal mass, elastic collision)
    vx1 -= approach_speed * nx
    vy1 -= approach_speed * ny
    vx2 += approach_speed * nx
    vy2 += approach_speed * ny
    ball1["velocity"] = (vx1, vy1)
    ball2["velocity"] = (vx2, vy2)

def check_wall_collision(ball, step=1):
    x, y = ball["position"]
    vx, vy = ball["velocity"]
    table_x = screen.get_width() // 2 - TABLE_WIDTH // 2
    table_y = screen.get_height() // 2 - TABLE_HEIGHT // 2
    future_X, future_y = future_ball_pos(ball, step)

    collided = False

    left = table_x + BALL_RADIUS
    right = table_x + TABLE_WIDTH - BALL_RADIUS
    top = table_y + BALL_RADIUS
    bottom = table_y + TABLE_HEIGHT - BALL_RADIUS

    # In a pocket mouth there is no cushion: just move, no bounce.
    # (check_potted_balls will catch the ball once it reaches the hole.)
    if is_in_pocket_mouth(future_X, future_y):
        ball["position"] = (future_X, future_y)
        return False

    # with future pos, check if we collide, if we do, reflect the velocity and move back into the table CORRECTLY!
    # rail collision:
    if future_X < left or future_X > right:
        collided = True
        vx = -vx
        extra_x = abs(future_X - (left if future_X < left else right))
        if future_X < left:
            future_X     = left + extra_x
        else:
            future_X = right - extra_x
    if future_y < top or future_y > bottom:
        collided = True
        vy = -vy
        extra_y = abs(future_y - (top if future_y < top else bottom))
        if future_y < top:
            future_y = top + extra_y
        else:
            future_y = bottom - extra_y

    ball["position"] = (future_X, future_y)
    ball["velocity"] = (vx, vy)

    return collided

def physics_substep(step):
    # Potted balls are out of the game: no moving, no bouncing, no hitting other balls
    on_table = [ball for ball in pool_balls if not ball["potted"]]

    # 1 + 2: move every ball a little, bouncing off the rails
    for ball in on_table:
        check_wall_collision(ball, step)

    # 3: did anything drop into a pocket?
    check_potted_balls()
    on_table = [ball for ball in on_table if not ball["potted"]]

    # 4: resolve every overlapping pair (each pair checked once)
    for i in range(len(on_table)):
        for j in range(i + 1, len(on_table)):
            if check_ball_collision(on_table[i], on_table[j]):
                resolve_ball_collision(on_table[i], on_table[j])

def update_balls():
    # How far does the fastest ball move this frame?
    fastest = 0
    for ball in pool_balls:
        vx, vy = ball["velocity"]
        fastest = max(fastest, (vx ** 2 + vy ** 2) ** 0.5)

    # Split the frame into enough small steps that nobody moves too far per step.
    # e.g. fastest = 40 px/frame, MAX_STEP_DISTANCE = 5 -> 8 steps of 1/8 each
    substeps = max(1, math.ceil(fastest / MAX_STEP_DISTANCE))
    for _ in range(substeps):
        physics_substep(1 / substeps)

    # Friction once per frame (not per substep)
    decrease_balls_velocity()

    # Snap very slow balls to a full stop, otherwise they creep forever
    for ball in pool_balls:
        vx, vy = ball["velocity"]
        if (vx ** 2 + vy ** 2) ** 0.5 < STOP_SPEED:
            ball["velocity"] = (0, 0)

def are_balls_moving():
    return any(vx != 0 or vy != 0
               for vx, vy in (ball["velocity"] for ball in pool_balls))

def power_to_velocity(power):
    # Convert a power value (0 to 1) to a velocity magnitude for the cue ball.
    max_velocity = 50  # Adjust this value for desired maximum speed
    return power * max_velocity

def aim_cue_ball(power):
    cue_ball = pool_balls[0]
    cue_ball_x, cue_ball_y = cue_ball["position"]
    x, y = get_x_y()

    # Calculate the direction from the cue ball to the given position
    dx = x - cue_ball_x
    dy = y - cue_ball_y
    distance = (dx ** 2 + dy ** 2) ** 0.5

    if distance == 0:
        return  # Avoid division by zero

    # Normalize the direction vector
    direction_x = dx / distance
    direction_y = dy / distance

    # Calculate the velocity based on the power and direction
    velocity_magnitude = power_to_velocity(power)
    cue_ball["velocity"] = (direction_x * velocity_magnitude, direction_y * velocity_magnitude)

def get_power():
    # Get the current power level based on the aim position (mouse or AI)
    cue_ball = pool_balls[0]
    cue_x, cue_y = cue_ball["position"]
    x, y = get_x_y()
    # Calculate power based on the distance of the aim position from the center of the cue ball
    distance = (x - cue_x) ** 2 + (y - cue_y) ** 2
    return min(max(distance / 100000, 0), 1)  # Normalize to a value between 0 and 1

initial_ball_positions()
method = "normal"  # Change to "AI" for AI mode
GAME_SPEED = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  

    CURR_POWER = get_power()
    LOST = eight_ball_potted() and not all_balls_potted()
    
    for _ in range(int(GAME_SPEED)):
        update_balls()
        
    # Draw everything
    draw_room_and_table()
    draw_balls()
    draw_hit_power_bar(CURR_POWER)
    draw_que_ball_aim_line()
    draw_loss_message() if LOST else None
    draw_score()
    draw_shot_count()

    # Check for shooting
    if not are_balls_moving() and not LOST:
        # Can take input
        if pygame.mouse.get_pressed()[0]:
            SCORE += SHOT_PENALTY
            SHOT_COUNT += 1
            aim_cue_ball(CURR_POWER)

    # Update the display and control the frame rate
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
