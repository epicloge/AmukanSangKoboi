import cv2
import pygame
import random
import time

source = './ASK/'

enemy_pics = [
    source + "EnemyCowboy1.png",
    source + "EnemyCowboy2.png",
    source + "EnemyCowboy3.png"
]

# Initialize pygame mixer for sound effects
pygame.mixer.init()

# Load the shooting sound effect
shoot_sound = pygame.mixer.Sound(source + "BULLET SHOT.wav")


width = 1280
height = 720

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Capture video from the first laptop's camera
#cap = cv2.VideoCapture(0)

# Load a random enemy image
enemy_img = cv2.imread(random.choice(enemy_pics), -1)

# Check if the image was loaded successfully
if enemy_img is None:
    print("Error: Could not load the enemy image.")
    exit()

# Resize the enemy image to a slightly larger vertical size
enemy_img = cv2.resize(enemy_img, (50, 100), interpolation=cv2.INTER_AREA)

# Get dimensions of the resized enemy image
enemy_height, enemy_width, _ = enemy_img.shape

# Initialize position and velocity for the enemy image
x, y = 0, 0
vx, vy = 5, 5

# Initialize position and velocity for the reticule
reticule_x, reticule_y = 100, 100
reticule_vx, reticule_vy = 8, 8  # Slightly increased velocities

# Define safe margins to avoid hitting the borders
margin = 30

# Shooting variables
shooting = False
shooting_start_time = 0

# Function to log coordinates
def log_coordinates(x, y):
    print(f"Enemy coordinates: ({x}, {y})")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # Get dimensions of the frame
    frame_height, frame_width, _ = frame.shape
    
    # Update position of the enemy image
    x += vx
    y += vy

    # Bounce off the edges
    if x + enemy_width >= frame_width or x <= 0:
        vx = -vx
    if y + enemy_height >= frame_height or y <= 0:
        vy = -vy
    
    # Ensure the enemy image fits within the frame boundaries
    if y + enemy_height > frame_height:
        enemy_height = frame_height - y
        enemy_img = enemy_img[:enemy_height, :, :]
    
    if x + enemy_width > frame_width:
        enemy_width = frame_width - x
        enemy_img = enemy_img[:, :enemy_width, :]
    
    # Overlay the enemy image on the frame
    for c in range(0, 3):
        frame[y:y+enemy_height, x:x+enemy_width, c] = enemy_img[:, :, c] * (enemy_img[:, :, 3] / 255.0) + frame[y:y+enemy_height, x:x+enemy_width, c] * (1.0 - enemy_img[:, :, 3] / 255.0)
    
    # Draw the hitbox (rectangle) around the enemy image
    cv2.rectangle(frame, (x, y), (x + enemy_width, y + enemy_height), (0, 0, 255), 1)  # Red color with thin thickness
    
    # Log the coordinates of the enemy
    log_coordinates(x, y)
    
    # Check for specific conditions (example: reticule aligns with enemy)
    if (x < reticule_x < x + enemy_width) and (y < reticule_y < y + enemy_height):
        print("Reticule aligned with enemy!")
        # Perform any action here, e.g., play a sound, increase score, etc.
    
    # Update position of the reticule with smooth random movement if not shooting
    if not shooting:
        reticule_x += reticule_vx
        reticule_y += reticule_vy

        # Randomly change direction
        if random.randint(0, 20) == 0:
            reticule_vx = random.uniform(-5, 5)  # Slightly increased range for more speed
            reticule_vy = random.uniform(-5, 5)  # Slightly increased range for more speed

        # Ensure the reticule stays within the safe margins
        if reticule_x < margin:
            reticule_x = margin
            reticule_vx = abs(reticule_vx)
        if reticule_x > frame_width - margin:
            reticule_x = frame_width - margin
            reticule_vx = -abs(reticule_vx)
        if reticule_y < margin:
            reticule_y = margin
            reticule_vy = abs(reticule_vy)
        if reticule_y > frame_height - margin:
            reticule_y = frame_height - margin
            reticule_vy = -abs(reticule_vy)

        # Randomly start shooting
        if random.randint(0, 100) == 0:
            shooting = True
            shooting_start_time = time.time()

    # Draw the reticule (red circle)
    if shooting:
        # Flashing effect
        if int(time.time() * 10) % 2 == 0:
            cv2.circle(frame, (int(reticule_x), int(reticule_y)), 20, (0, 0, 255), 2)
            cv2.circle(frame, (int(reticule_x), int(reticule_y)), 5, (0, 0, 255), -1)
        # Stop shooting after 1 second
        if time.time() - shooting_start_time > 1:
            shooting = False
            shoot_sound.play()  # Play the shooting sound effect after flashing
    else:
        cv2.circle(frame, (int(reticule_x), int(reticule_y)), 20, (0, 0, 255), 2)
        cv2.circle(frame, (int(reticule_x), int(reticule_y)), 5, (0, 0, 255), -1)
    
    # Display the resulting frame
    cv2.imshow('Camera', frame)
    
    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and destroy all windows
cap.release()
cv2.destroyAllWindows()