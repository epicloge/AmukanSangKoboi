import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
from cvzone.HandTrackingModule import HandDetector
from ultralytics import YOLO
import torch
import numpy as np
import pygame
import random
import time

source = './ASK/'

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load a pretrained YOLO model
model = YOLO('faiz.pt')
model = model.to(device)

# Initialize pygame mixer
pygame.mixer.init()
# Load bullet count and health bar images
bullet_images = []
health_images = []
bullet_paths = [
    source + "Bullet Count 0.png",
    source + "Bullet Count 1.png",
    source + "Bullet Count 2.png",
    source + "Bullet Count 3.png",
    source + "Bullet Count 4.png",
    source + "Bullet Count 5.png"
]
health_paths = [
    source + "Health Bar 0.png",
    source + "Health Bar 1.png",
    source + "Health Bar 2.png",
    source + "Health Bar 3.png",
    source + "Health Bar 4.png",
    source + "Health Bar 5.png"
]
enemy_pics = [
    source + "EnemyCowboy1.png",
    source + "EnemyCowboy2.png",
    source + "EnemyCowboy3.png"
]

for path in bullet_paths:
    if os.path.exists(path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            # Resize the image to reduce its size
            img = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4))
            bullet_images.append(img)
        else:
            print(f"Error loading image at {path}")
    else:
        print(f"File not found: {path}")

for path in health_paths:
    if os.path.exists(path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            # Resize the image to reduce its size
            img = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4))
            health_images.append(img)
        else:
            print(f"Error loading image at {path}")
    else:
        print(f"File not found: {path}")

# Load sound files
bullet_sound_path = source + "BULLET SHOT.wav"
health_sound_path = source + "Pain_sound.wav"
enemy_health_sound_path = source + "ROBLOX-oof.wav"
empty_bullet_sound_path = source + "morebullets.wav"
reload_sound_path = source + "Reload.wav"
empty_health_path = source + "Empty_health.wav"
# Load the shooting sound effect
shoot_sound = pygame.mixer.Sound(source + "BULLET SHOT.wav")

if os.path.exists(bullet_sound_path):
    bullet_sound = pygame.mixer.Sound(bullet_sound_path)
if os.path.exists(empty_bullet_sound_path):
    empty_bullet_sound = pygame.mixer.Sound(empty_bullet_sound_path)
if os.path.exists(reload_sound_path):
    reload_sound = pygame.mixer.Sound(reload_sound_path)

if os.path.exists(health_sound_path):
    health_sound = pygame.mixer.Sound(health_sound_path)
if os.path.exists(enemy_health_sound_path):
    enemy_health_sound = pygame.mixer.Sound(enemy_health_sound_path)
if os.path.exists(empty_health_path):
    empty_health_sound = pygame.mixer.Sound(empty_health_path)

# Initialize bullet count and health bar
bullet_count = 5
health_count = 5
enemy_health_count = 5

# Initialize variables
pose_reset = True
orient = None
text = None
enemy_dead = False
player_dead = False

# Define text that is used
dead_text = ["Yer luck just ran out, partner.",
"The West ain't fer everyone... better saddle up and try again.",
"Looks like this trail ends here.",
"You're sleepin' under the stars now, cowboy."]

# Function to reload bullets
def reload_bullets():
    global bullet_count
    bullet_count = 5  # Reset bullet count to 5
    reload_sound.play()

# Function to overlay image with alpha channel
def overlay_image_alpha(background, overlay, x, y):
    h, w, _ = overlay.shape
    overlay_image = overlay[:, :, :3]
    mask = overlay[:, :, 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image
    return background

width = 1280
height = 720

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detector = HandDetector(maxHands=1, detectionCon=0.9)

# Initialize landmarks history
HISTORY_POINTS = 5  # Number of frames to keep in history
landmark_history = []


def smooth_landmarks(current_landmarks, history):
	"""Apply weighted moving average to landmarks"""
	# Add current landmarks to history
	history.append(current_landmarks)

	# Keep only the last HISTORY_POINTS frames
	if len(history) > HISTORY_POINTS:
		history.pop(0)

	# Define weights (more recent frames have higher weights)
	weights = np.linspace(0.8, 1.0, len(history))
	weights = weights / np.sum(weights)

	# Calculate weighted average for each landmark
	smoothed_landmarks = []
	for i in range(len(current_landmarks)):
		x_coords = [frame[i][0] for frame in history]
		y_coords = [frame[i][1] for frame in history]

		smoothed_x = int(np.sum([x * w for x, w in zip(x_coords, weights)]))
		smoothed_y = int(np.sum([y * w for y, w in zip(y_coords, weights)]))

		smoothed_landmarks.append([smoothed_x, smoothed_y, current_landmarks[i][2]])

	return smoothed_landmarks

def GetOrient(orient, lmList):
    if lmList[8][0] > lmList[0][0]:
        orient = "right"
    elif lmList[8][0] < lmList[0][0]:
        orient = "left"
    return orient

def PullTrigger(lmList, orient, bullet_count, enemy_health_count, pose_reset, x, y, hitbox_x, hitbox_y, aim_x, aim_y):
    if pose_reset and (orient == "right" and lmList[8][0] < lmList[7][0]) or (orient == "left" and lmList[8][0] > lmList[7][0]):
        if bullet_count > 0:
            cv2.putText(img, "Bang!", (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            shoot_sound.play()
            bullet_count -= 1
            pose_reset = False
            if enemy_health_count > 0 and (x < aim_x < hitbox_x) and (y < aim_y < hitbox_y):
                print("Enemy hit!")
                enemy_health_sound.play()
                enemy_health_count -= 1
        else:
            empty_bullet_sound.play()
    if (orient == "right" and lmList[8][0] < lmList [5][0]) or (orient == "left" and lmList[8][0] > lmList [5][0]):
        bullet_count = 5
    if (orient == "right" and lmList[8][0] > lmList[7][0]) or (orient == "left" and lmList[8][0] < lmList[7][0]):
            pose_reset = True
    return bullet_count, enemy_health_count, pose_reset

def GunDetector(hitbox_start_x, hitbox_start_y, hitbox_end_x, hitbox_end_y, orient, lmList, bullet_count, enemy_health_count, pose_reset):
	orient = GetOrient(orient, lmList)
	aim_x, aim_y = int((lmList[6][0] - lmList[5][0]) * 5 + lmList[5][0]), int(
		(lmList[6][1] - lmList[5][1]) * 5 + lmList[5][1])

	if lmList[8][0] > lmList[0][0] and (lmList[12][0] < lmList[10][0] and lmList[16][0] < lmList[14][0]) or\
        lmList[8][0] < lmList[0][0] and (lmList[12][0] > lmList[10][0] and lmList[16][0] > lmList[14][0]):
		# Draw gun outline
		gun_points = [
			(lmList[8][0], lmList[8][1]),
			(lmList[5][0], lmList[5][1]),
			(lmList[17][0], lmList[17][1]),
			(lmList[18][0], lmList[18][1]),
			(lmList[6][0], lmList[6][1])
		]

		for i in range(len(gun_points) - 1):
			cv2.line(img, gun_points[i], gun_points[i + 1], (255, 0, 0), 2)

		cv2.putText(img, "Gun Detected", (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
		cv2.circle(img, (aim_x, aim_y), 20, (0, 255, 0), 2)
		cv2.circle(img, (aim_x, aim_y), 5, (0, 255, 0), -1)

		bullet_count, enemy_health_count, pose_reset = PullTrigger(lmList, orient, bullet_count, enemy_health_count, pose_reset, hitbox_start_x, hitbox_start_y, \
                                        hitbox_end_x, hitbox_end_y, aim_x, aim_y)
        
	return bullet_count, enemy_health_count, pose_reset

def EnemyShoot(x, y, reticule_x, reticule_y, hitbox_x, hitbox_y, health_count):
    if health_count > 0 and (x < reticule_x < hitbox_x) and (y < reticule_y < hitbox_y):
        health_count -= 1
        print("You got hit!")
        health_sound.play()
    return health_count

def CheckEnemyHealth(enemy_dead, enemy_health_count):
    if enemy_dead:
        return enemy_dead
    elif enemy_health_count == 0:
        empty_health_sound.play()
        enemy_dead = True
    else:
        enemy_dead = False
    return enemy_dead

def CheckPlayerHealth(player_dead, health_count):
    if player_dead:
        return player_dead
    if health_count == 0:
        empty_health_sound.play()
        player_dead = True
    else:
        player_dead = False
    return player_dead

def PlayerDead():   
    """
    numbers = [0, 1, 2, 3]  # Replace these numbers with your desired numbers
    num = random.choice(numbers)
    text = dead_text[num]
    cv2.putText(img, f'{text}', (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
    """
    return

# Load a random enemy image
enemy_img = cv2.imread(random.choice(enemy_pics), -1)

# Check if the image was loaded successfully
if enemy_img is None:
    print("Error: Could not load the enemy image.")
    exit()

# Resize the enemy image to a slightly larger vertical size
enemy_img = cv2.resize(enemy_img, (100, 150), interpolation=cv2.INTER_AREA)

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

"""
# Function to log coordinates
def log_coordinates(x, y):
    print(f"Enemy coordinates: ({x}, {y})")
"""

while True:
    # Get the frame from the webcam
    success, img = cap.read()
    if not success:
        break

    # Get dimensions of the frame
    frame_height, frame_width, _ = img.shape

    enemy_dead = CheckEnemyHealth(enemy_dead, enemy_health_count)
    player_dead = CheckPlayerHealth(player_dead, health_count)

    if enemy_dead:
        cv2.putText(img, "YOU WIN!", (220, 350), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 255, 0), 4)
    elif player_dead:
        cv2.putText(img, "YOU LOSE!", (180, 350), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 0, 255), 4)
    else:
    
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
            img[y:y+enemy_height, x:x+enemy_width, c] = enemy_img[:, :, c] * (enemy_img[:, :, 3] / 255.0) + img[y:y+enemy_height, x:x+enemy_width, c] * (1.0 - enemy_img[:, :, 3] / 255.0)

        # Hitbox of enemy
        hitbox_x, hitbox_y = x + enemy_width, y + enemy_height

        # Draw the hitbox (rectangle) around the enemy image
        cv2.rectangle(img, (x, y), (hitbox_x, hitbox_y), (0, 0, 255), 1)  # Red color with thin thickness
    
        # Log the coordinates of the enemy
        # log_coordinates(x, y)
        
        # Check for specific conditions (example: reticule aligns with enemy)
        if (x < reticule_x < x + enemy_width) and (y < reticule_y < y + enemy_height):
            print("Reticule aligned with enemy!")
            # Perform any action here, e.g., play a sound, increase score, etc.

        # Get face detection
        results = model(img)  # list of Results objects

        # View results
        for r in results:
            # print(r.boxes)
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cls_idx = int(box.cls[0])
                cls_names = model.names[cls_idx]

                conf = round(float(box.conf[0]), 2)  # round off to 2 significant numbers

                if conf >= 0.8:
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 4) # openCV is BGR
                    cv2.putText(img, f'{cls_names} {conf}', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

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
                cv2.circle(img, (int(reticule_x), int(reticule_y)), 20, (0, 0, 255), 2)
                cv2.circle(img, (int(reticule_x), int(reticule_y)), 5, (0, 0, 255), -1)
            # Stop shooting after 1 second
            if time.time() - shooting_start_time > 1:
                shooting = False
                health_count = EnemyShoot(x1, y1, reticule_x, reticule_y, x2, y2, health_count)
                shoot_sound.play()  # Play the shooting sound effect after flashing
        else:
            cv2.circle(img, (int(reticule_x), int(reticule_y)), 20, (0, 0, 255), 2)
            cv2.circle(img, (int(reticule_x), int(reticule_y)), 5, (0, 0, 255), -1)

        # Calculate position for bottom left corner
        frame_h, frame_w, _ = img.shape
        bullet_img_h, bullet_img_w, _ = bullet_images[bullet_count].shape
        health_img_h, health_img_w, _ = health_images[health_count].shape
        
        x_pos_bullet = 0
        y_pos_bullet = frame_h - bullet_img_h
        
        x_pos_health = 0
        y_pos_health = y_pos_bullet - health_img_h

        x_pos_enemy_health = 1050
        y_pos_enemy_health = y_pos_health

        # Overlay the current health bar image above the bullet count image
        if health_count < len(health_images):
            img = overlay_image_alpha(img, health_images[health_count], x_pos_health, y_pos_health)

        # Overlay the current bullet count image
        if bullet_count < len(bullet_images):
            img = overlay_image_alpha(img, bullet_images[bullet_count], x_pos_bullet, y_pos_bullet)

        # Overlay enemy health
        if enemy_health_count < len(health_images):
            img = overlay_image_alpha(img, health_images[enemy_health_count], x_pos_enemy_health, y_pos_health)

        # Hands
        hands, img = detector.findHands(img, draw=False)

        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            bullet_count, enemy_health_count, pose_reset = GunDetector(x, y, hitbox_x, hitbox_y, orient, lmList, bullet_count, enemy_health_count, pose_reset)


    cv2.imshow("Image", img)
    cv2.waitKey(1)

    """
    # Check for key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        if bullet_count > 0:
            bullet_count -= 1  # Decrease bullet count on 'S' press
            if 'bullet_sound' in locals():
                bullet_sound.play()
        else:
            if 'empty_bullet_sound' in locals():
                empty_bullet_sound.play()

    elif key == ord('h'):
        if health_count > 0:
            health_count -= 1  # Decrease health count on 'H' press
            if 'health_sound' in locals():
                health_sound.play()
        else:
            if 'empty_health_sound' in locals():
                empty_health_sound.play()
    elif key == ord('r'):
        reload_bullets()  # Reload bullets on 'R' press
    elif key == ord('q'):
        break
    """

cap.release()
cv2.destroyAllWindows()

