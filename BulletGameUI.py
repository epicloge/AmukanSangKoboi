import cv2
import os
import pygame

source = './ASK/'

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
empty_bullet_sound_path = source + "morebullets.wav"
reload_sound_path = source + "Reload.wav"
empty_health_path = source + "Empty_health.wav"

if os.path.exists(bullet_sound_path):
    bullet_sound = pygame.mixer.Sound(bullet_sound_path)
if os.path.exists(empty_bullet_sound_path):
    empty_bullet_sound = pygame.mixer.Sound(empty_bullet_sound_path)
if os.path.exists(reload_sound_path):
    reload_sound = pygame.mixer.Sound(reload_sound_path)

if os.path.exists(health_sound_path):
    health_sound = pygame.mixer.Sound(health_sound_path)
if os.path.exists(empty_health_path):
    empty_health_sound = pygame.mixer.Sound(empty_health_path)

# Initialize bullet count and health bar
bullet_count = 5
health_count = 5
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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Calculate position for bottom left corner
    frame_h, frame_w, _ = frame.shape
    bullet_img_h, bullet_img_w, _ = bullet_images[bullet_count].shape
    health_img_h, health_img_w, _ = health_images[health_count].shape
    
    x_pos_bullet = 0
    y_pos_bullet = frame_h - bullet_img_h
    
    x_pos_health = 0
    y_pos_health = y_pos_bullet - health_img_h

    # Overlay the current health bar image above the bullet count image
    if health_count < len(health_images):
        frame = overlay_image_alpha(frame, health_images[health_count], x_pos_health, y_pos_health)

    # Overlay the current bullet count image
    if bullet_count < len(bullet_images):
        frame = overlay_image_alpha(frame, bullet_images[bullet_count], x_pos_bullet, y_pos_bullet)

    cv2.putText(frame, "YOU WIN!", (220, 350), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 255, 0), 4)
    #cv2.putText(frame, "YOU LOSE!", (160, 350), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 0, 255), 4)

    # Show the frame
    cv2.imshow('Camera View', frame)

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

cap.release()
cv2.destroyAllWindows()