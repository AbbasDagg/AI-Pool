import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("AI Pool")
clock = pygame.time.Clock()
running = True

FELT_GREEN = (0, 100, 0)
RAIL_BROWN = (139, 69, 19)
ROOM_GREY = (109, 109, 109)
TABLE_WIDTH = 800
TABLE_HEIGHT = 400
RAIL_WIDTH = 20

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  

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


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
