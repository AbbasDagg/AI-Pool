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
pool_balls = [
    {"number": None, "color": "White", "type": "Cue", "position": (0, 0), "velocity": (0, 0)},  # Cue ball
    # Rack order: apex, then rows of 2, 3, 4, and 5 balls.
    # The 8-ball is centered and the two back corners are different types.
    {"number": 11, "color": "Red", "type": "Stripe", "position": (0, 0), "velocity": (40, 0)},
    {"number": 2, "color": "Blue", "type": "Solid", "position": (0, 0), "velocity": (0, 40)},
    {"number": 13, "color": "Orange", "type": "Stripe", "position": (0, 0), "velocity": (0, 0)},
    {"number": 3, "color": "Red", "type": "Solid", "position": (0, 0), "velocity": (40, 40)},
    {"number": 8, "color": "Black", "type": "8-Ball", "position": (0, 0), "velocity": (0, 0)},
    {"number": 15, "color": "Maroon", "type": "Stripe", "position": (0, 0), "velocity": (0, 0)},
    {"number": 6, "color": "Green", "type": "Solid", "position": (0, 0), "velocity": (0, 0)},
    {"number": 7, "color": "Maroon", "type": "Solid", "position": (0, 0), "velocity": (40, 0)},
    {"number": 9, "color": "Yellow", "type": "Stripe", "position": (0, 0), "velocity": (0, 0)},
    {"number": 1, "color": "Yellow", "type": "Solid", "position": (0, 0), "velocity": (40, 80)},
    {"number": 10, "color": "Blue", "type": "Stripe", "position": (0, 0), "velocity": (20, 50)},
    {"number": 12, "color": "Purple", "type": "Stripe", "position": (0, 0), "velocity": (0, 0)},
    {"number": 4, "color": "Purple", "type": "Solid", "position": (0, 0), "velocity": (10, 50)},
    {"number": 14, "color": "Green", "type": "Stripe", "position": (0, 0), "velocity": (0, 0)},
    {"number": 5, "color": "Orange", "type": "Solid", "position": (0, 0), "velocity": (0, 0)},
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
    pocket_radius = 12
    pocket_offset = 8
    pocket_positions = [
        (table_x - pocket_offset, table_y - pocket_offset),  # Top-left
        (table_x + TABLE_WIDTH // 2, table_y - pocket_offset),  # Top-center
        (table_x + TABLE_WIDTH + pocket_offset, table_y - pocket_offset),  # Top-right
        (table_x - pocket_offset, table_y + TABLE_HEIGHT + pocket_offset),  # Bottom-left
        (table_x + TABLE_WIDTH // 2, table_y + TABLE_HEIGHT + pocket_offset),  # Bottom-center
        (table_x + TABLE_WIDTH + pocket_offset, table_y + TABLE_HEIGHT + pocket_offset)  # Bottom-right
    ]

    for pos in pocket_positions:
        pygame.draw.circle(screen, (0, 0, 0), pos, pocket_radius)

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
        draw_ball(ball)

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

def draw_que_ball_aim_line(mode="normal", x = 0, y = 0):
    cue_ball = pool_balls[0]
    cue_ball_x, cue_ball_y = cue_ball["position"]
    
    if mode == "normal":
        end_x, end_y = pygame.mouse.get_pos()
    elif mode == "AI": # let AI pick the target position
        end_x, end_y = x, y

    # Draw a line from the cue ball to the mouse position
    pygame.draw.line(screen, (255, 255, 255), (cue_ball_x, cue_ball_y), (end_x, end_y), 2)

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

MAX_STEP_DISTANCE = BALL_RADIUS / 2  # no ball may move further than this in one substep
STOP_SPEED = 0.05  # below this speed a ball counts as stopped

def physics_substep(step):
    # 1 + 2: move every ball a little, bouncing off the rails
    for ball in pool_balls:
        check_wall_collision(ball, step)

    # 3: resolve every overlapping pair (each pair checked once)
    for i in range(len(pool_balls)):
        for j in range(i + 1, len(pool_balls)):
            if check_ball_collision(pool_balls[i], pool_balls[j]):
                resolve_ball_collision(pool_balls[i], pool_balls[j])

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


initial_ball_positions()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  
    # Draw everything
    draw_room_and_table()
    draw_balls()
    draw_hit_power_bar(0)
    draw_que_ball_aim_line()

    update_balls()


    # Update the display and control the frame rate
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
