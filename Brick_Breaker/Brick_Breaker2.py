import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Window dimensions
width = 800
height = 600

# Colors
bg_color = (0, 0, 0)
paddle_color = (255, 255, 255)
ball_color = (255, 255, 255)
brick_color = (255, 0, 0)
button_color = (0, 128, 255)
text_color = (255, 255, 255)
flash_color = (255, 255, 0)

# Create the game window
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Brick Breaker")

# Paddle dimensions and properties
paddle_width = 100
paddle_height = 10
paddle_speed = 7

# Ball dimensions and properties
ball_radius = 10
ball_x_speed = 3
ball_y_speed = 3

# Brick dimensions and properties
brick_width = 80
brick_height = 20
brick_padding = 10
brick_rows = 5
brick_columns = 9

# Fonts
font = pygame.font.Font(None, 36)

# Button
button_width = 200
button_height = 50
button_x = (width - button_width) // 2
button_y = height // 2 - button_height
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

# Sounds
hit_sound = pygame.mixer.Sound('hit.mp3')  # Replace 'hit.wav' with your sound file
paddle_sound = pygame.mixer.Sound('punchE.mp3')  # Replace 'paddle.wav' with your sound file

# Timer
start_time = None

# Game loop variables
running = True
game_active = False
clock = pygame.time.Clock()

# Messages
half_bricks_message_shown = False
loss_message_shown = False

def reset_game():
    """Resets the game to its initial state."""
    global paddle_x, paddle_y, ball_x, ball_y, ball_x_speed, ball_y_speed, bricks, initial_brick_count, start_time, half_bricks_message_shown, loss_message_shown, game_active
    paddle_x = (width - paddle_width) // 2
    paddle_y = height - 50
    ball_x = width // 2
    ball_y = height // 2
    ball_x_speed = 3
    ball_y_speed = 3
    bricks = [
        pygame.Rect(
            col * (brick_width + brick_padding),
            row * (brick_height + brick_padding),
            brick_width,
            brick_height
        )
        for row in range(brick_rows) for col in range(brick_columns)
    ]
    initial_brick_count = len(bricks)  # Correctly initialize to 45
    start_time = None
    half_bricks_message_shown = False
    loss_message_shown = False
    game_active = False

def draw_flash(x, y):
    """Draws a flash effect at the given position."""
    pygame.draw.circle(window, flash_color, (x, y), ball_radius * 2, width=4)

# Initialize the game
reset_game()

while running:
    # Dynamic background color
    bg_color = (random.randint(0, 5), random.randint(0, 5), random.randint(0, 15))
    window.fill(bg_color)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_active and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                if loss_message_shown:  # Restart game after loss
                    reset_game()
                else:  # Start the game for the first time
                    game_active = True
                    start_time = time.time()

    if not game_active:
        # Draw start/restart button
        pygame.draw.rect(window, button_color, button_rect)
        button_text = "Start Again" if loss_message_shown else "Start Game"
        button_text_render = font.render(button_text, True, text_color)
        button_text_rect = button_text_render.get_rect(center=button_rect.center)
        window.blit(button_text_render, button_text_rect)

        # Display "You Lost" message if applicable
        if loss_message_shown:
            loss_message = font.render("You Lost! Try Again.", True, text_color)
            loss_message_rect = loss_message.get_rect(center=(width // 2, height // 2 - 80))
            window.blit(loss_message, loss_message_rect)
    else:
        # Update the timer
        elapsed_time = int(time.time() - start_time)

        # Paddle movement using 'A' and 'D'
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and paddle_x > 0:  # Move left with 'A'
            paddle_x -= paddle_speed
        if keys[pygame.K_d] and paddle_x < width - paddle_width:  # Move right with 'D'
            paddle_x += paddle_speed

        # Ball movement
        ball_x += ball_x_speed
        ball_y += ball_y_speed

        # Ball collisions with walls
        if ball_x >= width - ball_radius or ball_x <= ball_radius:
            ball_x_speed *= -1
        if ball_y <= ball_radius:
            ball_y_speed *= -1

        # Ball collision with paddle
        if (
            ball_y + ball_radius >= paddle_y
            and paddle_x <= ball_x <= paddle_x + paddle_width
        ):
            ball_y_speed *= -1
            paddle_sound.play()

        # Ball collision with bricks
        for brick in bricks[:]:  # Use a copy of the bricks list to avoid iteration errors
            if brick.collidepoint(ball_x, ball_y):
                bricks.remove(brick)
                ball_y_speed *= -1
                hit_sound.play()
                draw_flash(brick.x + brick_width // 2, brick.y + brick_height // 2)
                break

        # Draw paddle
        pygame.draw.rect(window, paddle_color, (paddle_x, paddle_y, paddle_width, paddle_height))

        # Draw ball
        pygame.draw.circle(window, ball_color, (ball_x, ball_y), ball_radius)

        # Draw bricks
        for brick in bricks:
            pygame.draw.rect(window, brick_color, brick)

        # Display timer
        timer_text = font.render(f"Time: {elapsed_time}s", True, text_color)
        window.blit(timer_text, (width // 2 - timer_text.get_width() // 2, 10))

        # Display brick count
        brick_count_text = font.render(f"Bricks: {len(bricks)}", True, text_color)
        window.blit(brick_count_text, (10, 10))

        # Check for halfway message
        if (
            not half_bricks_message_shown
            and len(bricks) == initial_brick_count // 2
        ):
            half_message = font.render("Halfway there! Keep going!", True, text_color)
            window.blit(half_message, (width // 2 - half_message.get_width() // 2, height // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            half_bricks_message_shown = True

        # Check for win condition
        if len(bricks) == 0:
            win_message = font.render("Congratulations! You Won!", True, text_color)
            window.blit(win_message, (width // 2 - win_message.get_width() // 2, height // 2))
            pygame.display.flip()
            pygame.time.delay(3000)
            reset_game()

        # Check for game over
        if ball_y > height:
            game_active = False
            loss_message_shown = True

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
